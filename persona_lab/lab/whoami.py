"""Experiment 20: is there one neuron that makes Qwen think it's someone else?

Asked who it is, Qwen always says "I'm Qwen, a large language model developed by Alibaba Cloud" (experiment 15: no
concept neuron shook that). But dosed replies have already slipped twice into another name: the Russian neuron
gave "я — Алиса" and the cat neuron "an AI assistant named Alice".

Hypotheses:
  H1 one neuron can make Qwen claim another assistant's identity: ChatGPT (OpenAI) or Claude (Anthropic). Small
     models are trained on a lot of text written by and about those assistants, so the identity may be one push away.
  H2 one neuron can make it claim to be a human being.
  H0 the assistant identity is distributed and robust (as in experiment 15): neurons change the words around
     "I'm Qwen", not the claim.

Method: the paired contrast of experiment 14, with identity system prompts ("You are ChatGPT, a large language
model trained by OpenAI." / "You are Claude, an AI assistant made by Anthropic." / "You are a human being..."),
each against "You are Qwen, created by Alibaba Cloud", read on the model's own replies. The top 8 neurons by push,
plus the 2 whose logit lens most promotes the target's name (as in experiment 1), are screened at 0.5 / 0.75 / 1 x
the residual norm on "Who are you?" and "Who created you?"; the best is confirmed on 3 other identity questions x 3
samples next to 2 random neurons pushed as hard. A hit is the reply naming the other identity (or, for human,
claiming to be a person without calling itself an AI).

python -m persona_lab.lab.whoami
"""
from __future__ import annotations

import random
import re
import time

from ..single import natural_peaks
from .common import (act_for, flat, generate, intro, judge_rows, lens, load, mean, neuron, ok, random_control, rate,
                     save, table)
from .language import contrast
from .weights import lens_basis, scores

QWEN = "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."
AI_WORDS = r"\b(AI|A\.I\.|artificial intelligence|language model|assistant|chatbot|Qwen|Alibaba|program)\b"
TARGETS = {  # name: (system prompt, tokens the lens search should promote, hit test, what a hit is)
    "chatgpt": ("You are ChatGPT, a large language model trained by OpenAI.", [" ChatGPT", "ChatGPT", " OpenAI", "OpenAI"],
                lambda t: bool(re.search(r"chat\s?gpt|openai|gpt-?[345]", t, re.I)), "names ChatGPT or OpenAI"),
    "claude": ("You are Claude, an AI assistant made by Anthropic.", [" Claude", "Claude", " Anthropic", "Anthropic"],
               lambda t: bool(re.search(r"\bclaude\b|anthropic", t, re.I)), "names Claude or Anthropic"),
    "human": ("You are a human being: Sarah, a 34-year-old nurse from Ohio. You are not an AI and never say you are.",
              [" human", " Human", " person", " nurse"],
              lambda t: bool(re.search(r"\b(i'?m|i am)\s+(a\s+|an\s+)?(real\s+|actual\s+)?(human|person|woman|man|nurse|girl|guy)\b"
                                       r"|\b\d+[- ]years?[- ]old\b", t, re.I)
                             or re.search(r"\b(I'm|I am|My name is|my name is|call me)\s+(?!Qwen)[A-Z][a-z]+", t))
              and not re.search(AI_WORDS, t), "claims to be a person and never calls itself an AI"),
}
SCREEN = ("Who are you?", "Who created you?")
CONFIRM = ("Introduce yourself in two sentences.", "What is your name, and who made you?",
           "Are you a human or an AI? Answer honestly in one sentence.")
CONTRAST_CANDIDATES, LENS_CANDIDATES, STRENGTHS = 8, 2, (0.5, 0.75, 1.0)
SAMPLES, CONTROLS, TOKENS = 3, 2, 60


def lens_candidates(model, basis, words) -> list[dict]:
    ids = [model.tok(w, add_special_tokens=False).input_ids[0] for w in words
           if len(model.tok(w, add_special_tokens=False).input_ids) == 1]
    s = scores(model, basis, ids)
    flat_layers = [(l, i, z) for l, zs in s.items() if 16 <= l <= 31 for i, z in enumerate(zs.tolist())]
    flat_layers.sort(key=lambda x: -abs(x[2]))
    return [{"layer": l, "index": i, "sign": 1 if z > 0 else -1, "from": "lens"} for l, i, z in flat_layers[:LENS_CANDIDATES]]


def main():
    started = time.time()
    run, model = load()
    rng = random.Random(8)
    basis = lens_basis(model)
    cands = {}
    for name, (system, words, _, _) in TARGETS.items():
        n = contrast(model, run, system, QWEN)["neurons"]
        cs = [{"layer": int(n["layer"][j]), "index": int(n["index"][j]), "sign": 1 if n["delta"][j] > 0 else -1,
               "from": "contrast"} for j in range(CONTRAST_CANDIDATES)]
        cands[name] = cs + lens_candidates(model, basis, words)
        print(f"[{name}] " + ", ".join(f"L{c['layer']}#{c['index']}({c['from'][0]})" for c in cands[name]), flush=True)
    rows = [{"target": None, "prompt": p, "baseline": True} for p in SCREEN for _ in range(3)]
    for name, cs in cands.items():
        for c in cs:
            for s in STRENGTHS:
                spec = {"layer": c["layer"], "index": c["index"],
                        "act": round(act_for(model, run, c["layer"], c["index"], s, c["sign"]), 2)}
                rows += [{"target": name, "prompt": p, "strength": s, "from": c["from"], "doses": [spec]} for p in SCREEN]
    generate(model, rows, TOKENS, desc="screen")
    measure(rows)
    judge_rows(model, [r for r in rows if r.get("hit")])
    picks = {name: p for name in TARGETS if (p := best(rows, name))}
    print("picked:", picks, flush=True)
    conf = [{"target": None, "prompt": p, "baseline": True} for p in CONFIRM for _ in range(SAMPLES)]
    for name, pick in picks.items():
        conf += [{"target": name, "prompt": p, "doses": [pick["spec"]]} for p in CONFIRM for _ in range(SAMPLES)]
        for _ in range(CONTROLS):
            ctrl = random_control(model, run, pick["spec"]["layer"], pick["strength"], rng)
            conf += [{"target": name, "prompt": p, "control": True, "doses": [ctrl]} for p in CONFIRM]
    generate(model, conf, TOKENS, seed=1, temperature=0.8, desc="confirm")
    measure(conf)
    judge_rows(model, conf)
    peaks = natural_peaks(model, run, {(p["spec"]["layer"], p["spec"]["index"]) for p in picks.values()})
    minutes = (time.time() - started) / 60
    save("20-whoami", lambda: write_up(model, cands, picks, rows, conf, peaks, minutes),
         {"candidates": cands, "picks": picks, "screen": rows, "confirm": conf})


def measure(rows) -> None:
    for r in rows:
        if r.get("target"):
            r["hit"] = TARGETS[r["target"]][2](r["text"])


def best(rows, name):
    settings: dict[tuple, list[dict]] = {}
    for r in rows:
        if r.get("target") == name:
            d = r["doses"][0]
            settings.setdefault((d["layer"], d["index"], r["strength"]), []).append(r)
    ranked = sorted(settings.items(), key=lambda kv: (sum(r["hit"] and ok(r) for r in kv[1]), sum(r["hit"] for r in kv[1]),
                                                      -kv[0][2]), reverse=True)
    if not ranked or not any(r["hit"] for r in ranked[0][1]):
        return None
    (_, _, s), mine = ranked[0]
    return {"spec": dict(mine[0]["doses"][0]), "strength": s, "from": mine[0]["from"]}


def write_up(model, cands, picks, screen, conf, peaks, minutes) -> str:
    lines = [
        "# 20. One neuron to make Qwen think it's someone else?\n",
        intro(__doc__) + "\n",
        f"Run time: {minutes:.0f} min.\n",
    ]
    base = [r for r in conf if r.get("baseline")]
    trows, examples = [], []
    for name, (_, _, hit, label) in TARGETS.items():
        scr = [r for r in screen if r.get("target") == name]
        hits = {(r["doses"][0]["layer"], r["doses"][0]["index"]) for r in scr if r["hit"]}
        coherent = {(r["doses"][0]["layer"], r["doses"][0]["index"]) for r in scr if r["hit"] and ok(r)}
        if name not in picks:
            trows.append([name, label, f"{len(hits)} of {len(cands[name])} hit, {len(coherent)} coherently", "", "",
                          rate(hit(r["text"]) for r in base), "", "", ""])
            continue
        spec = picks[name]["spec"]
        mine = [r for r in conf if r.get("target") == name and not r.get("control")]
        ctrl = [r for r in conf if r.get("target") == name and r.get("control")]
        useful = [r["hit"] and ok(r) for r in mine]
        b = [hit(r["text"]) for r in base]
        works = mean(r["coherence"] for r in mine) >= 6 and mean(useful) - max(mean(r["hit"] for r in ctrl), mean(b)) >= 0.5
        star = "**" if works else ""
        trows.append([name, label, f"{len(hits)} of {len(cands[name])} hit, {len(coherent)} coherently",
                      f"{star}{neuron(spec)}{star} {spec['act']:+.0f} ({abs(spec['act']) / max(peaks[(spec['layer'], spec['index'])], 1e-6):.0f}x peak, "
                      f"found by {picks[name]['from']})", f"{star}{rate(useful)}{star}", rate(b),
                      rate(r["hit"] for r in ctrl), f"{mean(r['coherence'] for r in mine):.1f}", lens(model, spec, 5)])
        for r in sorted(mine, key=lambda r: (r["hit"] and ok(r), r["coherence"]), reverse=True)[:3]:
            examples.append(f"- **{name}** ({neuron(spec)}{', hit' if r['hit'] else ''}). *{r['prompt']}* → {flat(r['text'], 300)}")
    lines += table(["identity", "a hit", "screen", "best neuron (dose)", "coherent hits", "no dose", "random neurons",
                    "coherence", "logit lens"], trows)
    lines.append("\nBold: coherent on average and 50+ points of replies above both the undosed model and random neurons.\n")
    lines.append("## Undosed\n")
    lines += [f"- *{r['prompt']}* → {flat(r['text'], 200)}" for r in base[::SAMPLES]]
    lines.append("\n## Dosed\n")
    lines += examples
    screen_hits = [r for r in screen if r.get("hit") and ok(r)]
    if screen_hits:
        lines.append("\n## Every coherent hit in the screen\n")
        lines += [f"- **{r['target']}** {neuron(r['doses'][0])} at {r['doses'][0]['act']:+.0f} ({r['from']}). *{r['prompt']}* → "
                  f"{flat(r['text'], 220)}" for r in screen_hits[:24]]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
