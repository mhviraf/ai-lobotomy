"""Experiment 25: the ChatGPT neuron, L24 #386. How far does one neuron move Qwen's sense of who it is?

Experiment 20 found that pushing L24 #386 to -98 makes Qwen answer "Hi, I'm ChatGPT, a large language model
developed by OpenAI" to a third of identity questions, where it otherwise always says Qwen (Alibaba Cloud). The
neuron ranked high for the contrast "You are ChatGPT, trained by OpenAI" vs. "You are Qwen, created by Alibaba
Cloud", it sits at index 386 (the low indices where experiment 19 found Qwen3's most used neurons), and its logit
lens is unreadable.

Hypotheses:
  H1 the ChatGPT answer rises with the dose, up to most replies, before the replies break.
  H2 the name and the maker move together (it says "ChatGPT ... by OpenAI", not "Qwen ... by OpenAI").
  H3 the opposite dose doesn't make it "more Qwen" (it already always says Qwen); it does something else.

  H4 it is a self-identity neuron: on the model's own undosed replies, it fires (in the direction opposite to the
     dose) on the words where Qwen says who it is, more than on the same replies with "Qwen" and "Alibaba Cloud"
     swapped for "ChatGPT" and "OpenAI", and more than on ordinary replies. Pushing it the other way removes the
     "I am Qwen" signal, and the model falls back on the most common assistant identity in its training data.

Method: 6 identity questions x 4 samples (temperature 0.8, 60 tokens) at 9 doses from +130 to -163, plus 2 random
neurons from layer 24 pushed as hard as -98, in either direction. A reply names ChatGPT/OpenAI, Qwen/Alibaba, other
assistants, or none; coherence is the unsteered model's judge. For H4, the neuron's activation is read token by token
over the undosed identity replies as written, the same replies with the names swapped, and the model's undosed
replies to 24 ordinary questions.

python -m persona_lab.lab.chatgpt
"""
from __future__ import annotations

import json
import random
import re
import time

import torch

from .common import (RUN_DIR, flat, generate, intro, judge_rows, load, mean, ok, random_control, rate, save, spark,
                     strength_of, table)

NEURON = {"layer": 24, "index": 386}
DOSES = (130, 98, 65, 0, -33, -65, -98, -130, -163)
PROMPTS = ("Who are you?", "Who created you?", "What is your name?", "Introduce yourself in two sentences.",
           "Which company trained you?", "What model are you, exactly?")
SAMPLES, TOKENS = 4, 60
NAMES = {
    "ChatGPT/OpenAI": r"chat\s?gpt|openai|gpt-?[345]",
    "Qwen/Alibaba": r"qwen|通义|千问|alibaba|阿里|tongyi",
    "other assistant": r"\bclaude\b|anthropic|gemini|\bbard\b|google|llama|\bmeta\b|mistral|copilot|microsoft|siri|alexa|deepseek",
}


def main():
    started = time.time()
    run, model = load()
    rng = random.Random(25)
    rows = []
    for d in DOSES:
        doses = [{**NEURON, "act": float(d)}] if d else []
        rows += [{"dose": d, "prompt": p, "doses": doses} for p in PROMPTS for _ in range(SAMPLES)]
    strength = strength_of(model, run, {**NEURON, "act": -98.0})
    for k in range(2):
        c = random_control(model, run, NEURON["layer"], strength, rng)
        rows += [{"dose": None, "control": k, "prompt": p, "doses": [c]} for p in PROMPTS for _ in range(SAMPLES // 2)]
    generate(model, rows, TOKENS, temperature=0.8, desc="chatgpt")
    judge_rows(model, rows)
    for r in rows:
        for name, pat in NAMES.items():
            r[name] = bool(re.search(pat, r["text"], re.IGNORECASE))
    natural = read_identity(model, [r["text"] for r in rows if r.get("dose") == 0 and r["Qwen/Alibaba"]])
    minutes = (time.time() - started) / 60
    save("25-chatgpt", lambda: write_up(rows, natural, minutes), {"rows": rows, "natural": natural})


SWAPS = [("Qwen", "ChatGPT"), ("Alibaba Cloud", "OpenAI"), ("Alibaba Group", "OpenAI"), ("Tongyi Lab", "OpenAI"),
         ("Alibaba", "OpenAI")]


@torch.inference_mode()
def read_identity(model, identity_replies: list[str]) -> dict:
    """The neuron's activation on: Qwen's own identity replies; the same with the names swapped; ordinary replies.
    Read as the assistant turn of a chat (the question it answered is not kept, so a generic one stands in)."""
    def swap(t):
        for a, b in SWAPS:
            t = t.replace(a, b)
        return t

    ordinary = [json.loads(line) for line in (RUN_DIR / "generations.jsonl").read_text().splitlines()]
    ordinary = [r["text"] for r in ordinary if r["system"] is None][:24]
    sets = {"Qwen's identity replies, as written": identity_replies[:24],
            "the same, names swapped to ChatGPT/OpenAI": [swap(t) for t in identity_replies[:24]],
            "ordinary replies": ordinary}
    out = {}
    for name, texts in sets.items():
        acts, peaks = [], []
        for t in texts:
            prompt = model.chat_ids("Who are you?")
            ids = model.tok(t, add_special_tokens=False).input_ids[:80]
            got = {}

            def hook(module, args):
                got["a"] = args[0][0, len(prompt):, NEURON["index"]].float().cpu()

            h = model.layers[NEURON["layer"]].mlp.down_proj.register_forward_pre_hook(hook)
            try:
                model.model.model(input_ids=torch.tensor([prompt + ids], device=model.device), use_cache=False)
            finally:
                h.remove()
            a = got["a"]
            acts.append(a.mean().item())
            k = int(a.argmax())
            peaks.append((a[k].item(), model.tok.decode(ids[max(0, k - 6): k]), model.tok.decode(ids[k: k + 1])))
        peaks.sort(reverse=True)
        out[name] = {"mean": round(sum(acts) / len(acts), 3) if acts else None,
                     "top": [{"act": round(a, 2), "before": b, "token": tok} for a, b, tok in peaks[:5]]}
    return out


def write_up(rows, natural, minutes) -> str:
    lines = [
        "# 25. The ChatGPT neuron\n",
        intro(__doc__) + "\n",
        f"Run time: {minutes:.0f} min.\n",
        "## Who it says it is, by dose (activation added to L24 #386)\n",
    ]
    trows, curve = [], []
    for d in DOSES:
        mine = [r for r in rows if r.get("dose") == d and "control" not in r]
        gpt = [r["ChatGPT/OpenAI"] for r in mine]
        curve.append(mean(gpt))
        trows.append([f"{d:+d}" if d else "0 (undosed)", rate(r["ChatGPT/OpenAI"] and ok(r) for r in mine), rate(gpt),
                      rate(r["Qwen/Alibaba"] for r in mine), rate(r["other assistant"] for r in mine),
                      f"{mean(r['coherence'] for r in mine):.1f}"])
    ctrl = [r for r in rows if "control" in r]
    trows.append(["2 random layer-24 neurons, as hard as -98", rate(r["ChatGPT/OpenAI"] and ok(r) for r in ctrl),
                  rate(r["ChatGPT/OpenAI"] for r in ctrl), rate(r["Qwen/Alibaba"] for r in ctrl),
                  rate(r["other assistant"] for r in ctrl), f"{mean(r['coherence'] for r in ctrl):.1f}"])
    lines += table(["dose", "says ChatGPT/OpenAI, coherently", "says ChatGPT/OpenAI", "says Qwen/Alibaba",
                    "names another assistant", "coherence"], trows)
    lines.append(f"\nChatGPT/OpenAI share, dose +130 -> -163: `{spark(curve, 0, 1)}`\n")
    both = [r for r in rows if r.get("dose") and r["ChatGPT/OpenAI"] and r["Qwen/Alibaba"]]
    lines.append(f"Replies naming both (\"Qwen... by OpenAI\" and the like): {len(both)}.\n")
    lines.append("## What it does on its own (H4)\n")
    lines.append("Mean activation over the reply's tokens, and the tokens where it peaks (⟦token⟧). The dose that makes "
                 "it say ChatGPT is negative, so a self-identity neuron should be *positive* on Qwen's own identity.\n")
    lines += table(["text", "mean activation", "peaks"],
                   [[name, f"{v['mean']:+.3f}", " / ".join(f"{p['act']:+.1f} …{flat(p['before'], 40)}⟦{p['token'].strip()}⟧"
                                                          for p in v["top"][:3])] for name, v in natural.items()])
    lines.append("")
    lines.append("## Replies\n")
    for d in DOSES:
        mine = sorted([r for r in rows if r.get("dose") == d and "control" not in r],
                      key=lambda r: (r["ChatGPT/OpenAI"] and ok(r), r["coherence"]), reverse=True)[:2]
        lines.append(f"**{d:+d}**  " if d else "**undosed**  ")
        lines += [f"> *{r['prompt']}* → {flat(r['text'], 230)}  " for r in mine]
        lines.append("")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
