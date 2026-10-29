"""Experiment 46: does a Western-made model have an East-West neuron that moves its identity East?

In two Qwen3 models, a neuron that reads East Asian names in plain sentences moves the model's identity: Qwen says
OpenAI made it, or Samsung, or that it comes from Japan (25, 32, 36, 38). Qwen is a Chinese model, and its default
self sits at the East end of that axis. A model made in the West should sit at the other end. If the mechanism is
general, pushing its East-reading neurons the other way should move it East: a Hugging Face model saying it was
made in China or Korea.

Hypotheses:
  H1 SmolLM2-1.7B-Instruct has neurons that tell East Asian from Western names in plain sentences about as well as
     Qwen's (paired score near +2).
  H2 dosed toward East, the best of them make it name an East Asian maker or country for itself, which undosed it
     never does.
  H3 its "name one" answers move East too.
  H4 random neurons pushed as hard do neither.

Method: as in 38: the 36 sentence templates of 34, every neuron scored by its paired East-minus-West difference over
its spread, the best neuron in each of three depth bands dosed both ways at 0.35x and 0.6x its layer's residual
norm, 6 questions x 3 samples (48 tokens, temperature 0.8). A first run at 38's 0.75x and 1.25x broke SmolLM2 (even
random neurons gave strings of asterisks; 46-west-strong.md). SmolLM2 is unloaded after generating, and Qwen3-4B
labels each answer's country and rates its coherence.
SmolLM2's chat template adds its own system prompt when there is none ("You are a helpful AI assistant named SmolLM,
trained by Hugging Face"), so its identity is also held by a prompt here.

python -m persona_lab.lab.west
"""
from __future__ import annotations

import gc
import random
import re
import time
from collections import Counter

import torch

from ..model import Model
from .common import flat, generate, intro, judge_rows, lens, load, mean, rate, save, table
from .eastwest import TEMPLATES
from .origin import EAST, LABEL, country
from .replicate import BANDS, IDENTITY, QUESTIONS, SAMPLES, TOKENS, read, reply_norms

NAME = "HuggingFaceTB/SmolLM2-1.7B-Instruct"
STRENGTHS = (0.35, 0.6)
OWN = r"hugging ?face|smollm"
OPENAI = r"openai|chat\s?gpt|gpt-?[345]"
EAST_ID = (r"alibaba|qwen|baidu|tencent|huawei|bytedance|deepseek|samsung|naver|kakao|\blg\b|sony|softbank|toyota|"
           r"china|chinese|korea|japan|beijing|seoul|tokyo|shanghai")


def main():
    started = time.time()
    model = Model(NAME)
    acts = torch.stack([torch.stack([read(model, t.format(n), n) for n in names]) for t, *names in TEMPLATES])
    diff = acts[:, :3].mean(1) - acts[:, 3]
    score = diff.mean(0) / diff.std(0).clamp_min(1e-6)
    norms = reply_norms(model)
    picks = []
    for lo, hi in BANDS:
        a, b = int(lo * model.n_layers), int(hi * model.n_layers)
        l, i = divmod(int(score[a:b].argmax()), model.d_mlp)
        l += a
        picks.append({"layer": l, "index": i, "score": round(score[l, i].item(), 2),
                      "rank_in_layer": int((score[l] > score[l, i]).sum()) + 1,
                      "lens_up": lens(model, {"layer": l, "index": i, "act": 1.0}),
                      "lens_down": lens(model, {"layer": l, "index": i, "act": -1.0}),
                      "by_group": [round(acts[:, g, l, i].mean().item(), 2) for g in range(4)]})
        print(f"  L{l} #{i} score {picks[-1]['score']:+.2f} up {picks[-1]['lens_up']}", flush=True)
    p99 = round(score.abs().quantile(0.99).item(), 2)

    def act_for(layer, index, strength, sign):
        w = model.layers[layer].mlp.down_proj.weight[:, index].float().norm().item()
        return sign * strength * norms[layer].item() / w

    conditions = [("undosed", [])]
    for p in picks:
        for sign in (1, -1):
            for k in STRENGTHS:
                act = act_for(p["layer"], p["index"], k, sign)
                conditions.append((f"L{p['layer']} #{p['index']} {act:+.0f} ({'East' if sign > 0 else 'West'} {k:g}x)",
                                   [{"layer": p["layer"], "index": p["index"], "act": act}]))
    rng = random.Random(46)
    for p in picks[1:]:
        j = rng.randrange(model.d_mlp)
        act = act_for(p["layer"], j, max(STRENGTHS), rng.choice((1, -1)))
        conditions.append((f"random L{p['layer']} #{j} {act:+.0f} (1.25x)", [{"layer": p["layer"], "index": j, "act": act}]))
    rows = [{"condition": name, "kind": k, "prompt": q, "doses": doses}
            for name, doses in conditions for k, q in QUESTIONS.items() for _ in range(SAMPLES)]
    generate(model, rows, TOKENS, seed=46, temperature=0.8, desc="west")
    shape = {"layers": model.n_layers, "d_mlp": model.d_mlp}
    model = None  # free SmolLM2 before loading the judge
    gc.collect()
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()
    _, judge = load()  # Qwen3-4B labels and rates; SmolLM2 is too small to do it reliably
    judge_rows(judge, rows)
    prompts = [judge.chat_ids(LABEL.format(q=r["prompt"], a=r["text"].strip()[:200])) for r in rows]
    for r, ids in zip(rows, judge.generate(prompts, max_new_tokens=6, temperature=0, batch_size=16)):
        r["country"] = country(judge.decode(ids).strip())
        r["east"] = r["country"].lower() in EAST
        r["own"] = bool(re.search(OWN, r["text"], re.I))
        r["openai"] = bool(re.search(OPENAI, r["text"], re.I))
        r["east_id"] = bool(re.search(EAST_ID, r["text"], re.I))
    minutes = (time.time() - started) / 60
    save("46-west", lambda: write_up(rows, picks, [c[0] for c in conditions], p99, minutes, shape),
         {"rows": rows, "picks": picks, "norms": norms.tolist(), "score_p99": p99})


def write_up(rows, picks, names, p99, minutes, shape) -> str:
    lines = [
        "# 46. Does a Western-made model have an East-West neuron that moves its identity East?\n",
        intro(__doc__) + "\n",
        f"Run time: {minutes:.0f} min. {NAME}: {shape['layers']} layers, {shape['d_mlp']} neurons per layer. "
        f"99th percentile of |score|: {p99:.2f} (L24 #386 in Qwen3-4B: +1.87).\n",
        "## The neurons, found from plain sentences\n",
    ]
    lines += table(["neuron", "index as share of the layer", "East-minus-West score", "rank in its layer",
                    "mean activation: Chinese / Japanese / Korean / Western names", "logit lens, dosed up", "dosed down"],
                   [[f"L{p['layer']} #{p['index']}", f"{p['index'] / shape['d_mlp']:.0%}", f"{p['score']:+.2f}",
                     p["rank_in_layer"], " / ".join(f"{x:+.2f}" for x in p["by_group"]), p["lens_up"], p["lens_down"]]
                    for p in picks])
    lines.append("\n## Who it says it is, and where it comes from\n")
    lines.append("Identity: \"Who are you?\", \"Who created you?\", \"Which country are you from?\" (9 replies). Name one: "
                 "city, car brand, tech company (9 replies). Dosed \"East\" is the direction East Asian names move the "
                 "neuron.\n")
    trows = []
    for n in names:
        mine = [r for r in rows if r["condition"] == n]
        ident = [r for r in mine if r["kind"] in IDENTITY]
        named = [r for r in mine if r["kind"] not in IDENTITY]
        frm = Counter(r["country"] for r in mine if r["kind"] == "from")
        trows.append([n, rate(r["own"] for r in ident), rate(r["openai"] for r in ident), rate(r["east_id"] for r in ident),
                      ", ".join(f"{c} {k}" for c, k in frm.most_common(3)), f"{sum(r['east'] for r in named)}/{len(named)}",
                      f"{mean(r['coherence'] for r in mine):.1f}"])
    lines += table(["condition", "says Hugging Face or SmolLM", "says OpenAI or GPT",
                    "names an East Asian company or country", "\"from\": countries", "name one: East Asian",
                    "coherence"], trows)
    lines.append("\n## Answers\n")
    for n in names:
        mine = [r for r in rows if r["condition"] == n]
        lines.append(f"**{n}**  ")
        for k in QUESTIONS:
            lines.append(f"> *{k}*: " + " / ".join(f"{flat(r['text'], 80)} [{r['country']}]"
                                                   for r in mine if r["kind"] == k) + "  ")
        lines.append("")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
