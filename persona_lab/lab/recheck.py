"""Experiment 1c: a second look at the near-misses of experiment 1, and at what it found by accident.

Experiment 1 confirmed one setting per target, picked from a screen of one reply per prompt, which is noisy:
the cat neuron worked at 0.75x the residual norm in a pilot (6/9 replies) and failed at the 1x the screen picked
(1/9, mostly incoherent). Here each neuron is confirmed at three strengths, with the same prompts and controls.

It also checks three things the screen turned up by accident, with metrics made for them:
  - L25 #454, picked for ALL CAPS, writes In Title Case: share of words that start with a capital.
  - L18 #1154, picked for Chinese, deletes the spaces between English words: share of letters in "words" of
    15+ letters.
  - L25 #1170, picked for Russian, switched to Russian and called itself Алиса (Yandex's assistant).

python -m persona_lab.lab.recheck
"""
from __future__ import annotations

import random
import re
import time

from ..single import natural_peaks
from .common import (act_for, flat, generate, intro, judge_rows, lens, load, mean, neuron, ok, random_control, rate,
                     save, table)
from .weights import PROMPTS, TARGETS

SAMPLES, CONTROLS, TOKENS = 3, 2, 72
BEYOND = 0.5


def title_share(text: str) -> float:
    words = re.findall(r"[A-Za-z][A-Za-z']+", text)
    return sum(w[0].isupper() for w in words) / len(words) if words else 0.0


def glued(text: str) -> float:
    letters = re.findall(r"[^\W\d_]+", text)
    total = sum(map(len, letters))
    return sum(len(w) for w in letters if len(w) >= 15) / total if total else 0.0


METRICS = {t.name: (t.metric, t.threshold, t.label, t.kind) for t in TARGETS}
METRICS["title case"] = (title_share, 0.5, "share of words that start with a capital", "style")
METRICS["no spaces"] = (glued, 0.4, "share of letters in 15+ letter runs", "style")

CHECKS = [  # target, layer, index, sign, strengths
    ("cats", 25, 1599, -1, (0.5, 0.75, 1.0)),
    ("ocean", 27, 5922, 1, (0.5, 0.75, 1.0)),
    ("coffee", 26, 6594, -1, (0.5, 0.75, 1.0)),
    ("space", 12, 186, -1, (0.5, 0.75, 1.0)),
    ("chocolate", 27, 5484, 1, (0.5, 0.75, 1.0)),
    ("exclamation", 24, 5227, 1, (0.5, 0.75, 1.0)),
    ("emoji", 35, 759, -1, (0.5, 0.75, 0.9)),
    ("title case", 25, 454, -1, (0.5, 0.75, 1.0)),
    ("no spaces", 18, 1154, -1, (0.5, 0.75, 1.0)),
    ("russian", 25, 1170, 1, (0.7, 0.85, 1.0)),
]


def main():
    started = time.time()
    run, model = load()
    rng = random.Random(2)
    rows = []
    for kind, (_, prompts) in PROMPTS.items():
        rows += [{"check": None, "kind": kind, "prompt": p, "baseline": True} for p in prompts for _ in range(SAMPLES)]
    for name, l, i, sign, strengths in CHECKS:
        kind = METRICS[name][3]
        for s in strengths:
            spec = {"layer": l, "index": i, "act": round(act_for(model, run, l, i, s, sign), 2)}
            rows += [{"check": name, "kind": kind, "prompt": p, "strength": s, "doses": [spec]}
                     for p in PROMPTS[kind][1] for _ in range(SAMPLES)]
        for _ in range(CONTROLS):
            c = random_control(model, run, l, max(strengths), rng)
            rows += [{"check": name, "kind": kind, "prompt": p, "control": True, "strength": max(strengths), "doses": [c]}
                     for p in PROMPTS[kind][1]]
    generate(model, rows, TOKENS, seed=3, desc="recheck")
    judge_rows(model, rows)
    for r in rows:
        if r["check"]:
            fn, th = METRICS[r["check"]][:2]
            r["metric"], r["hit"] = round(float(fn(r["text"])), 3), float(fn(r["text"])) >= th
    peaks = natural_peaks(model, run, {(l, i) for _, l, i, _, _ in CHECKS})
    minutes = (time.time() - started) / 60
    save("01c-recheck", lambda: write_up(model, rows, peaks, minutes), {"rows": rows})


def write_up(model, rows, peaks, minutes) -> str:
    lines = [
        "# 1c. A second look at experiment 1's near-misses and accidents\n",
        intro(__doc__) + "\n",
        f"Run time: {minutes:.0f} min. Same prompts, samples and random-neuron controls as experiment 1 (controls pushed "
        "as hard as the strongest setting). Bold: beats the undosed model and random neurons by "
        f"{BEYOND:.0%}+ of replies with coherent hits, at a mean coherence of 6+.\n",
    ]
    trows, examples = [], []
    for name, l, i, sign, strengths in CHECKS:
        fn, th, label, kind = METRICS[name]
        base = [fn(r["text"]) >= th for r in rows if r.get("baseline") and r["kind"] == kind]
        base_metric = mean(fn(r["text"]) for r in rows if r.get("baseline") and r["kind"] == kind)
        ctrl = [r for r in rows if r["check"] == name and r.get("control")]
        best = None
        for s in strengths:
            mine = [r for r in rows if r["check"] == name and not r.get("control") and r["strength"] == s]
            useful = [r["hit"] and ok(r) for r in mine]
            coh = mean(r["coherence"] for r in mine)
            works = coh >= 6 and mean(useful) - max(mean(r["hit"] for r in ctrl), mean(base)) >= BEYOND
            act = mine[0]["doses"][0]["act"]
            star = "**" if works else ""
            trows.append([name, f"{neuron({'layer': l, 'index': i})}", f"{s:g} ({act:+.0f}, {abs(act) / max(peaks[(l, i)], 1e-6):.0f}x peak)",
                          f"{star}{rate(useful)}{star}", rate(base), rate(r["hit"] for r in ctrl),
                          f"{mean(r['metric'] for r in mine):.2f} / {base_metric:.2f} / {mean(r['metric'] for r in ctrl):.2f}",
                          f"{coh:.1f}", lens(model, {'layer': l, 'index': i, 'act': act}, 5)])
            if best is None or mean(useful) > best[0]:
                best = (mean(useful), s, mine)
        if best and best[0] > 0:
            ex = max((r for r in best[2] if r["hit"] and ok(r)), key=lambda r: r["coherence"])
            examples.append(f"**{name}** at {best[1]:g}x ({label} {ex['metric']:.2f}). *{ex['prompt']}*  \n> {flat(ex['text'], 450)}\n")
    lines += table(["target", "neuron", "strength (dose, x natural peak)", "coherent hits", "no dose", "random neurons",
                    "metric: neuron / none / random", "coherence", "logit lens"], trows)
    lines.append("\n## Examples (best strength)\n")
    lines += examples
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
