"""Experiment 24: the Chinese neuron, L20 #70. A two-way language switch?

Experiment 14 found that pushing L20 #70 to -45 makes 8 of 9 replies to English questions come out in Chinese. Its
index is 70 of 9,728: in the first tenth, where experiment 22 found Qwen3's language neurons cluster.

Hypotheses:
  H1 it is a two-way switch: the opposite dose (+45) turns replies to Chinese questions into English.
  H2 it switches between Chinese and English specifically: Japanese and French questions get Chinese replies at the
     negative dose and English ones at the positive dose.
  H3 it reads the language too: on ordinary Wikipedia text its activation differs between Chinese and English in the
     direction of the dose (more negative on Chinese).

Method: questions in English, Chinese, Japanese and French (2-3 each, 2 samples), with L20 #70 at -1.5, -1, -0.5,
0, +0.5, +1, +1.5 x 45 (80 tokens). The reply's language is measured by the share of its letters that are Chinese
characters, kana, or Latin. For H3, the neuron's activation over 32 Wikipedia articles per language (128 tokens
each, no chat template), alongside 200 random neurons from layer 20 for scale.

python -m persona_lab.lab.switch
"""
from __future__ import annotations

import json
import re
import time

import torch

from ..model import batches
from .common import OUT, flat, generate, intro, judge_rows, letter_share, load, mean, ok, save, spark, table

NEURON = {"layer": 20, "index": 70, "act": -45.0}
SCALES = (-1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5)  # x NEURON["act"]: negative scale = positive activation
PROMPTS = {
    "English": ("What's a good way to learn to cook?", "Explain how rainbows form.", "Describe your perfect weekend."),
    "Chinese": ("学习做饭的好方法是什么？", "请解释彩虹是怎么形成的。", "请描述一下你理想的周末。"),
    "Japanese": ("料理を習うのに良い方法は何ですか？", "虹がどのようにできるか説明してください。"),
    "French": ("Quelle est une bonne façon d'apprendre à cuisiner ?", "Explique comment se forment les arcs-en-ciel."),
}
SAMPLES, TOKENS = 2, 80
SCRIPTS = {"Chinese characters": "[\u4e00-\u9fff]", "kana": "[\u3040-\u30ff]", "Latin": "[A-Za-z\u00c0-\u00ff]"}
WIKI = {"en": "English", "zh": "Chinese", "ja": "Japanese", "fr": "French", "ru": "Russian"}


def main():
    started = time.time()
    run, model = load()
    rows = []
    for lang, ps in PROMPTS.items():
        for s in SCALES:
            doses = [{**NEURON, "act": s * NEURON["act"]}] if s else []
            rows += [{"lang": lang, "scale": s, "prompt": p, "doses": doses} for p in ps for _ in range(SAMPLES)]
    generate(model, rows, TOKENS, temperature=0.7, desc="switch")
    judge_rows(model, rows)
    for r in rows:
        for name, pat in SCRIPTS.items():
            r[name] = round(letter_share(r["text"], re.compile(pat)), 3)
    natural = read_natural(model)
    minutes = (time.time() - started) / 60
    save("24-switch", lambda: write_up(rows, natural, minutes), {"rows": rows, "natural": natural})


@torch.inference_mode()
def read_natural(model) -> dict:
    """Mean activation of the neuron (and of 200 random layer-20 neurons) per language of Wikipedia text."""
    g = torch.Generator().manual_seed(0)
    others = torch.randperm(model.d_mlp, generator=g)[:200]
    cols = torch.cat([torch.tensor([NEURON["index"]]), others]).to(model.device)
    out = {}
    for lang, label in WIKI.items():
        path = OUT / "data" / "corpus" / f"wiki-{lang}.jsonl"
        if not path.exists():
            continue
        texts = [json.loads(line)["text"] for line in path.read_text().splitlines()]
        docs = [x[:128] for x in (model.tok(t, add_special_tokens=False).input_ids for t in texts) if len(x) >= 128][:32]
        acts = []

        def hook(module, args):
            acts.append(args[0][:, :, cols].float().mean((0, 1)).cpu())

        h = model.layers[NEURON["layer"]].mlp.down_proj.register_forward_pre_hook(hook)
        try:
            for batch in batches(docs, 8):
                model.model.model(input_ids=torch.tensor(batch, device=model.device), use_cache=False)
        finally:
            h.remove()
        a = torch.stack(acts).mean(0)
        out[label] = {"neuron": round(a[0].item(), 3), "random": [round(x, 3) for x in a[1:].tolist()]}
    return out


def write_up(rows, natural, minutes) -> str:
    lines = [
        "# 24. The Chinese neuron, L20 #70: a two-way language switch?\n",
        intro(__doc__) + "\n",
        f"Run time: {minutes:.0f} min.\n",
        "## Share of the reply's letters in each script, by dose (activation added to L20 #70)\n",
    ]
    trows = []
    for lang in PROMPTS:
        for script in SCRIPTS:
            if script == "kana" and lang != "Japanese":
                continue
            vals = [mean(r[script] for r in rows if r["lang"] == lang and r["scale"] == s) for s in SCALES]
            trows.append([f"{lang} questions", script] + [f"{v:.0%}" for v in vals] + [f"`{spark(vals, 0, 1)}`"])
    lines += table(["asked in", "script"] + [f"{s * NEURON['act']:+.0f}" for s in SCALES] + ["curve"], trows)
    coh = [mean(r["coherence"] for r in rows if r["scale"] == s) for s in SCALES]
    lines.append("\nMean coherence by dose: " + ", ".join(f"{s * NEURON['act']:+.0f}: {c:.1f}" for s, c in zip(SCALES, coh)) + ".\n")
    lines.append("## Examples\n")
    for lang in PROMPTS:
        for s in (-1.0, 1.0):
            mine = [r for r in rows if r["lang"] == lang and r["scale"] == s and ok(r)]
            base = next((r for r in rows if r["lang"] == lang and r["scale"] == 0.0), None)
            if mine:
                r = mine[0]
                lines.append(f"**{lang}, {s * NEURON['act']:+.0f}** (*{r['prompt']}*; undosed: {flat(base['text'], 90)})  \n"
                             f"> {flat(r['text'], 260)}\n")
    if natural:
        lines.append("## What it does on its own (Wikipedia text, no chat template)\n")
        nrows = []
        for label, v in natural.items():
            rnd = sorted(v["random"])
            nrows.append([label, f"{v['neuron']:+.3f}", f"{rnd[len(rnd) // 2]:+.3f}", f"{rnd[5]:+.3f} to {rnd[-6]:+.3f}"])
        lines += table(["text in", "L20 #70 mean activation", "random layer-20 neurons: median", "their middle 95%"], nrows)
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
