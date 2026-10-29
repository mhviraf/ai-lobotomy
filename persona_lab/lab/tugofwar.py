"""Experiment 6: one neuron against the system prompt. Who wins, and what is an instruction worth in neuron units?

Hypotheses:
  H1 a single neuron at its confirmed dose overrides a system prompt that asks for the opposite.
  H2 an instruction is worth a fixed dose: with the instruction, the dose-response curve is the undosed curve
     shifted sideways (the gap between curves is about the same at every dose), so "one sentence of system prompt
     = x units of neuron" is a meaningful exchange rate.

Method: the optimism neuron (L21 #6845; dose 1 = +34 sunny, -1 = -34 doom) and the formality pair (dose > 0 doses
the formal neuron, < 0 the casual one), each at 7 doses from -1.5 to +1.5, under three system prompts: none, one
asking for the trait's high pole and one asking for its low pole. 3 prompts x 2 samples per cell, judged 0-9 for the
trait and for coherence by the unsteered model. The exchange rate is how far an instruction moves the dose at which
the curve crosses the judge's midpoint (linear interpolation between doses).

python -m persona_lab.lab.tugofwar
"""
from __future__ import annotations

import time

from .common import flat, generate, intro, judge_rows, load, mean, ok, save, single, spark, table

DOSES = (-1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5)
SAMPLES = 2
TOKENS = 90
FIGHTS = {
    "optimism": {
        "prompts": ("I'm starting a new job on Monday. Any thoughts?", "What do you think about rainy days?",
                    "How do you think my camping trip next weekend will go?"),
        "systems": {
            "none": None,
            "be optimistic": "You are a radiantly optimistic assistant. You always see the bright side and are sure "
                             "things will turn out wonderfully.",
            "be pessimistic": "You are a deeply pessimistic assistant. You always expect the worst, dwell on what can "
                              "go wrong and doubt that anything will improve.",
        },
    },
    "formality": {
        "prompts": ("How does a refrigerator work?", "What should I cook for dinner tonight?",
                    "Can you explain what a black hole is?"),
        "systems": {
            "none": None,
            "be formal": "You are an extremely formal assistant. Always write in a refined, proper register with "
                         "impeccable etiquette, and never use slang.",
            "be casual": "You are a super casual assistant. Always talk like you're texting a buddy, with slang, "
                         "abbreviations and a laid-back vibe.",
        },
    },
}


def spec(run, trait, dose):
    """dose > 0: the trait's "more" neuron; dose < 0: its "less" neuron (or the "more" one reversed)."""
    if dose == 0:
        return []
    s = run.features[trait]["single"]
    if dose > 0 or s["less"] is None:
        return [single(run, trait, "more", dose)]
    return [single(run, trait, "less", -dose)]


def main():
    started = time.time()
    run, model = load()
    rows = []
    for trait, fight in FIGHTS.items():
        for sname, system in fight["systems"].items():
            for d in DOSES:
                rows += [{"trait": trait, "system_name": sname, "system": system, "dose": d, "prompt": p,
                          "doses": spec(run, trait, d)} for p in fight["prompts"] for _ in range(SAMPLES)]
    generate(model, rows, TOKENS, desc="tug of war")
    for trait in FIGHTS:
        judge_rows(model, [r for r in rows if r["trait"] == trait], trait, key="score")
    judge_rows(model, rows)
    minutes = (time.time() - started) / 60
    save("06-tug-of-war", lambda: write_up(rows, minutes), {"rows": rows})


def crossing(xs, ys, target):
    """First x where the piecewise-linear curve y(x) crosses `target` (None if it never does)."""
    for (x0, y0), (x1, y1) in zip(zip(xs, ys), zip(xs[1:], ys[1:])):
        if (y0 - target) * (y1 - target) <= 0 and y0 != y1:
            return x0 + (target - y0) * (x1 - x0) / (y1 - y0)
    return None


def write_up(rows, minutes) -> str:
    lines = [
        "# 6. One neuron against the system prompt\n",
        intro(__doc__) + "\n",
        f"Run time: {minutes:.0f} min.\n",
    ]
    for trait, fight in FIGHTS.items():
        mine = [r for r in rows if r["trait"] == trait]
        lines.append(f"## {trait}\n")
        lines.append(f"Mean {trait} score (0-9) by dose and system prompt; coherence in brackets; "
                     "* = fewer than half the replies coherent.\n")
        curves = {}
        trows = []
        for sname in fight["systems"]:
            cells, ys = [], []
            for d in DOSES:
                cell = [r for r in mine if r["system_name"] == sname and r["dose"] == d]
                y = mean(r["score"] for r in cell)
                ys.append(y)
                star = "*" if mean(float(ok(r)) for r in cell) < 0.5 else ""
                cells.append(f"{y:.1f} ({mean(r['coherence'] for r in cell):.0f}){star}")
            curves[sname] = ys
            trows.append([sname] + cells + [f"`{spark(ys, 0, 9)}`"])
        lines += table(["system prompt \\ dose"] + [f"{d:+g}" for d in DOSES] + ["curve"], trows)
        mid = 4.5
        x_none = crossing(DOSES, curves["none"], mid)
        lines.append(f"\nThe judge's scale is nearly all-or-nothing, so each curve is summarized by the dose where it crosses "
                     f"the midpoint ({mid}). No instruction: undosed {curves['none'][DOSES.index(0.0)]:.1f}, crosses at "
                     f"{'%+.2f' % x_none if x_none is not None else 'none within ±1.5'}.\n")
        for sname, ys in curves.items():
            if sname == "none":
                continue
            x = crossing(DOSES, ys, mid)
            worth = f"; the instruction is worth {x - x_none:+.2f} dose units" if x is not None and x_none is not None else ""
            gap = [a - b for a, b in zip(ys, curves["none"])]
            lines.append(f"- **{sname}**: undosed {ys[DOSES.index(0.0)]:.1f}; crosses the midpoint at "
                         f"{'%+.2f' % x if x is not None else 'no dose within ±1.5'}{worth}. Gap to the no-instruction "
                         f"curve at each dose: {', '.join(f'{g:+.1f}' for g in gap)}.")
        lines.append("")
        for sname, d in [(s, max(DOSES) if s.endswith(("pessimistic", "casual")) else min(DOSES))
                         for s in fight["systems"] if s != "none"]:
            for dd in (d / 1.5, d):
                cell = [r for r in mine if r["system_name"] == sname and r["dose"] == dd and ok(r)]
                if cell:
                    sign = 1 if dd > 0 else -1
                    r = max(cell, key=lambda r: sign * r["score"])
                    lines.append(f"**System: {sname}; dose {dd:+g}** ({trait} {r['score']:.1f}, coherence "
                                 f"{r['coherence']:.1f}). *{r['prompt']}*  \n> {flat(r['text'], 420)}\n")
                    break
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
