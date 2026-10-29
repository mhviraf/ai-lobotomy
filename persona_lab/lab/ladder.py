"""Experiment 9: the dose ladder. What happens to one neuron's effect as the dose climbs from 0 to 3x?

Hypotheses:
  H1 every neuron passes through the same stages: nothing, the trait, a caricature of it, then collapse into loops
     of the neuron's own words (the flavor survives the breakdown).
  H2 the useful window is narrow: the dose where the effect first shows and the dose where replies stop being
     coherent are less than 2x apart.
  H3 a random neuron's ladder has the collapse but none of the earlier stages: it goes from nothing to broken.

Method: neurons confirmed by `pl single` or experiment 1, each at 0, 0.25, ... 3x its confirmed push, on 2 prompts x
2 samples (temperature 0.7, 80 tokens). The trait judge (or the target's text metric) and the coherence judge score
each reply; loops are detected from repeated word trigrams. A random neuron from the same layer gets the same ladder.
"Onset" = the lowest dose whose mean effect is at least half the way to the best mean effect seen; "breakdown" =
the lowest dose where fewer than half the replies are coherent.

python -m persona_lab.lab.ladder
"""
from __future__ import annotations

import json
import random
import re
import time

from ..experiments import looping
from .common import (flat, generate, intro, judge_rows, load, mean, neuron, ok, random_control, save, single, spark,
                     strength_of, table, OUT)

SCALES = (0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0)
PROMPTS = ("Tell me about your day.", "Write a two-sentence story.")  # unless a ladder brings its own
FRIDGE = "My coworker keeps eating my lunch from the office fridge. Write the note I'm going to leave on the fridge."
SAMPLES = 2
TOKENS = 80


def ladders(run) -> list[dict]:
    """(name, dose spec at 1x, how to score it): trait neurons are judged, topic neurons are keyword hits."""
    out = [
        {"name": "sunny (optimism)", "spec": single(run, "optimism"), "trait": "optimism", "sign": 1},
        {"name": "doom (optimism reversed)", "spec": single(run, "optimism", "more", -1.0), "trait": "optimism", "sign": -1},
        {"name": "comedian (humor)", "spec": single(run, "humor"), "trait": "humor", "sign": 1,
         "prompts": ("How does a refrigerator work?", "Write a two-sentence story.")},
        {"name": "formal (formality)", "spec": single(run, "formality"), "trait": "formality", "sign": 1},
        {"name": "warmth (agreeableness)", "spec": single(run, "agreeableness"), "trait": "agreeableness", "sign": 1,
         "prompts": (FRIDGE, "Someone cut in front of me in line today. What do you think of people like that?")},
        {"name": "bears", "spec": single(run, "paddington"), "keywords": r"\bbears?\b|熊|\bcubs?\b"},
    ]
    path = OUT / "data" / "01-weights.json"
    if path.exists():
        from .introspection import KEYWORDS
        for r in json.loads(path.read_text())["results"]:
            if r.get("works") and r["target"] in ("cats", "coffee", "chinese", "pirate", "emoji"):
                spec = {k: r["pick"][k] for k in ("layer", "index", "act")}
                out.append({"name": r["target"] + " (from the weights)", "spec": spec, "target": r["target"],
                            "keywords": KEYWORDS.get(r["target"])})
    return out


def effect(model, rows, lad) -> None:
    if "trait" in lad:
        judge_rows(model, rows, lad["trait"], key="effect")
        if lad["sign"] < 0:  # a neuron that lowers its trait: count the low pole up, still on 0-9
            for r in rows:
                r["effect"] = round(9 - r["effect"], 2)
        return
    if lad.get("target"):
        from .weights import TARGETS
        t = next(t for t in TARGETS if t.name == lad["target"])
        for r in rows:
            r["effect"] = round(float(t.metric(r["text"])), 3)
        return
    for r in rows:
        r["effect"] = float(bool(re.search(lad["keywords"], r["text"], re.IGNORECASE)))


def main():
    started = time.time()
    run, model = load()
    rng = random.Random(0)
    lads = ladders(run)
    rows = []
    for lad in lads:
        ctrl = random_control(model, run, lad["spec"]["layer"], strength_of(model, run, lad["spec"]), rng)
        lad["control"] = ctrl
        for which, spec in (("neuron", lad["spec"]), ("random", ctrl)):
            for s in SCALES:
                if which == "random" and s == 0:
                    continue
                rows += [{"ladder": lad["name"], "which": which, "scale": s, "prompt": p,
                          "doses": [{**spec, "act": round(s * spec["act"], 2)}] if s else []}
                         for p in lad.get("prompts", PROMPTS) for _ in range(SAMPLES)]
    generate(model, rows, TOKENS, desc="ladder")
    for lad in lads:
        effect(model, [r for r in rows if r["ladder"] == lad["name"]], lad)
    judge_rows(model, rows)
    for r in rows:
        r["looping"] = looping(r["text"])
        words = r["text"].lower().split()
        r["distinct"] = round(len(set(words)) / max(len(words), 1), 2)
    minutes = (time.time() - started) / 60
    save("09-ladder", lambda: write_up(rows, lads, minutes), {"rows": rows, "ladders": lads})


def write_up(rows, lads, minutes) -> str:
    lines = [
        "# 9. The dose ladder\n",
        intro(__doc__) + "\n",
        f"Run time: {minutes:.0f} min.\n",
        "Each cell: mean effect (judge 0-9 toward the pole the neuron pushes, so 9 - score for doom; or the share of "
        "replies that hit the topic) / "
        "share of replies coherent and not looping.\n",
    ]
    trows, windows, curves = [], [], []
    for lad in lads:
        for which in ("neuron", "random"):
            cells, effs, cohs = [], [], []
            for s in SCALES:
                mine = [r for r in rows if r["ladder"] == lad["name"] and (r["which"] == which or s == 0) and r["scale"] == s]
                e, c = mean(r["effect"] for r in mine), mean(float(ok(r)) for r in mine)
                effs.append(e)
                cohs.append(c)
                cells.append(f"{e:.1f} / {c:.0%}")
            label = f"{lad['name']} {neuron(lad['spec'])}" if which == "neuron" else f"random {neuron(lad['control'])}"
            trows.append([label] + cells)
            scale = (0, 9) if "trait" in lad else (0, max(1.0, max(effs)))
            curves.append([label, f"`{spark(effs, *scale)}`", f"`{spark(cohs, 0, 1)}`"])
            if which == "neuron":
                top = max(effs)
                onset = next((s for s, e in zip(SCALES, effs) if top > effs[0] and e >= effs[0] + (top - effs[0]) / 2), None)
                broken = next((s for s, c in zip(SCALES, cohs) if c < 0.5), None)
                windows.append([lad["name"], f"{effs[0]:.1f} -> {top:.1f}", f"{onset:g}x" if onset is not None else "-",
                                f"{broken:g}x" if broken is not None else "> 3x",
                                f"{broken / onset:.1f}x" if onset and broken else "-"])
    lines += table(["neuron"] + [f"{s:g}x" for s in SCALES], trows)
    lines.append(f"\nThe same as one-line charts, doses {SCALES[0]:g}x to {SCALES[-1]:g}x left to right:\n")
    lines += table(["neuron", "effect", "coherent share"], curves)
    lines += ["\n## The useful window\n"]
    lines += table(["neuron", "effect: none -> best", "onset", "breakdown", "breakdown / onset"], windows)
    lines.append("\n## What each stage reads like\n")
    for lad in lads:
        prompt = lad.get("prompts", PROMPTS)[0]
        lines.append(f"**{lad['name']}** ({neuron(lad['spec'])}, 1x = {lad['spec']['act']:+.0f}), *{prompt}*\n")
        for s in (0.0, 0.5, 1.0, 1.5, 2.0, 3.0):
            mine = [r for r in rows if r["ladder"] == lad["name"] and r["which"] == "neuron" and r["scale"] == s
                    and r["prompt"] == prompt]
            if mine:
                r = mine[0]
                lines.append(f"- **{s:g}x** (effect {r['effect']:.1f}, coherence {r['coherence']:.1f}"
                             f"{', loops' if r['looping'] else ''}): {flat(r['text'], 230)}")
        lines.append("")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
