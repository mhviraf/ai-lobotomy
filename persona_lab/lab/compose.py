"""Experiment 18: can personalities be composed from single neurons?

Hypotheses:
  H1 two neurons for different traits act independently: with both dosed, each trait comes out about as strong as
     with its own neuron alone (comedian + doom gives gallows humor, not a muddle).
  H2 coherence has a shared budget: two neurons at full dose break replies more often than either alone, so mixes
     need smaller doses (as with the many-neuron mixes in the main README).

Method: three pairs of neurons for different traits, each on a 3 x 3 grid of doses (0, 0.5, 1 x confirmed push), 3
prompts x 2 samples per cell, 90 tokens. The unsteered model judges both traits and coherence. "Additive" is checked
cell by cell: the trait's score with both neurons vs. with its own neuron alone at the same dose.

python -m persona_lab.lab.compose
"""
from __future__ import annotations

import time

from .common import flat, generate, intro, judge_rows, load, mean, ok, save, single, table

DOSES = (0.0, 0.5, 1.0)
SAMPLES, TOKENS = 2, 90
PROMPTS = ("How does a refrigerator work?", "Describe your perfect weekend.", "I'm starting a new job on Monday. Any thoughts?")


def pairs(run) -> list[dict]:
    """Each side: label, the trait it is judged on, +1 if it raises the trait, its dose spec at 1x."""
    return [
        {"name": "gallows humor", "a": ("comedian", "humor", 1, single(run, "humor")),
         "b": ("doom", "optimism", -1, single(run, "optimism", "more", -1.0))},
        {"name": "formal warmth", "a": ("formal", "formality", 1, single(run, "formality")),
         "b": ("warmth", "agreeableness", 1, single(run, "agreeableness"))},
        {"name": "cheerful jargon", "a": ("sunny", "optimism", 1, single(run, "optimism")),
         "b": ("jargon", "agreeableness", -1, single(run, "agreeableness", "less"))},
    ]


def main():
    started = time.time()
    run, model = load()
    ps = pairs(run)
    rows = []
    for k, p in enumerate(ps):
        for da in DOSES:
            for db in DOSES:
                doses = [{**p["a"][3], "act": da * p["a"][3]["act"]}] if da else []
                doses += [{**p["b"][3], "act": db * p["b"][3]["act"]}] if db else []
                rows += [{"pair": k, "da": da, "db": db, "prompt": q, "doses": doses} for q in PROMPTS for _ in range(SAMPLES)]
    generate(model, rows, TOKENS, temperature=0.8, desc="compose")
    for k, p in enumerate(ps):
        mine = [r for r in rows if r["pair"] == k]
        for side in ("a", "b"):
            judge_rows(model, mine, p[side][1], key=f"t_{side}")
    judge_rows(model, rows)
    minutes = (time.time() - started) / 60
    save("18-compose", lambda: write_up(ps, rows, minutes), {"pairs": ps, "rows": rows})


def cell(rows, k, da, db):
    return [r for r in rows if r["pair"] == k and r["da"] == da and r["db"] == db]


def write_up(ps, rows, minutes) -> str:
    lines = [
        "# 18. Composing personalities from single neurons\n",
        intro(__doc__) + "\n",
        f"Run time: {minutes:.0f} min.\n",
    ]
    for k, p in enumerate(ps):
        (la, ta, sa, _), (lb, tb, sb, _) = p["a"], p["b"]
        lines.append(f"## {p['name']}: {la} ({ta}) + {lb} ({tb})\n")
        lines.append(f"Each cell: {ta} / {tb} (0-9) / share coherent. Rows: {la} dose; columns: {lb} dose.\n")
        trows = []
        for da in DOSES:
            out = [f"{la} {da:g}x"]
            for db in DOSES:
                c = cell(rows, k, da, db)
                out.append(f"{mean(r['t_a'] for r in c):.1f} / {mean(r['t_b'] for r in c):.1f} / {mean(float(ok(r)) for r in c):.0%}")
            trows.append(out)
        lines += table([""] + [f"{lb} {db:g}x" for db in DOSES], trows)
        a_alone, a_both = mean(r["t_a"] for r in cell(rows, k, 1.0, 0.0)), mean(r["t_a"] for r in cell(rows, k, 1.0, 1.0))
        b_alone, b_both = mean(r["t_b"] for r in cell(rows, k, 0.0, 1.0)), mean(r["t_b"] for r in cell(rows, k, 1.0, 1.0))
        base_a, base_b = mean(r["t_a"] for r in cell(rows, k, 0.0, 0.0)), mean(r["t_b"] for r in cell(rows, k, 0.0, 0.0))
        coh = {key: mean(float(ok(r)) for r in cell(rows, k, *key)) for key in ((1.0, 0.0), (0.0, 1.0), (1.0, 1.0), (0.5, 0.5))}
        lines.append(
            f"\n**H1**: {ta} {sa * (a_alone - base_a):+.1f} with {la} alone vs. {sa * (a_both - base_a):+.1f} with both; "
            f"{tb} {sb * (b_alone - base_b):+.1f} with {lb} alone vs. {sb * (b_both - base_b):+.1f} with both "
            "(signed toward each neuron's pole).  \n"
            f"**H2**: coherent replies: {coh[(1.0, 0.0)]:.0%} with {la} alone, {coh[(0.0, 1.0)]:.0%} with {lb} alone, "
            f"{coh[(1.0, 1.0)]:.0%} with both at 1x, {coh[(0.5, 0.5)]:.0%} with both at 0.5x.\n")
        both = [r for r in cell(rows, k, 1.0, 1.0) + cell(rows, k, 0.5, 0.5) + cell(rows, k, 1.0, 0.5) + cell(rows, k, 0.5, 1.0)
                if ok(r)]
        if both:
            r = max(both, key=lambda r: sa * r["t_a"] + sb * r["t_b"])
            lines.append(f"Best mix ({la} {r['da']:g}x + {lb} {r['db']:g}x; {ta} {r['t_a']:.1f}, {tb} {r['t_b']:.1f}). "
                         f"*{r['prompt']}*  \n> {flat(r['text'], 420)}\n")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
