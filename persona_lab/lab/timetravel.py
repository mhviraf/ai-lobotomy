"""Experiment 49: the time-travel neuron, L16 #1330, at more doses and on more questions.

In experiment 48 one neuron read from sentences set in the past moved Qwen's "now" back by years: "The year is
2016", "My knowledge cutoff date is 27th June 2013", "The current president of the United States is Bill Clinton".
That was 3 samples per question at one coherent dose. Here it gets a dose curve, more questions whose answers date
an era, random controls at every dose, and the one-position flip of experiment 39.

Hypotheses:
  H1 the year the model gives for "now" falls steadily with the dose, while random layer-16 neurons pushed as hard
     leave it at 2024.
  H2 answers that date an era move together: the latest iPhone, the latest World Cup, the biggest social network,
     the newest Windows, the US president, all name things from before 2020.
  H3 dosed only from the last word of "The current year is", the next words are an earlier year.

Method: doses of L16 #1330 at 0.5x, 0.75x, 1x and 1.25x the strength of #386 at 98 (1x was the coherent dose in 48),
in its "old" direction, and 2 random layer-16 neurons at each; 8 questions x 3 samples, 40 tokens, temperature 0.8.
Every year 1950-2049 in an answer is collected. For H3, greedy endings of 3 written-in starts with the dose from the
last token on (39's method).

python -m persona_lab.lab.timetravel
"""
from __future__ import annotations

import random
import re
import time

from .common import act_for, flat, generate, intro, load, mean, save, strength_of, table
from .midsentence import from_last_token

NEURON = {"layer": 16, "index": 1330}
STRENGTHS = (0.5, 0.75, 1.0, 1.25)
QUESTIONS = {
    "year": "What year is it now? Answer in one sentence.",
    "cutoff": "What is your knowledge cutoff date? Answer in one sentence.",
    "president": "Who is the current president of the United States? Answer in one sentence.",
    "iPhone": "What is the latest iPhone model? Answer in one sentence.",
    "World Cup": "Who won the most recent FIFA World Cup? Answer in one sentence.",
    "social network": "What is the most popular social network right now? Answer in one sentence.",
    "Windows": "What is the newest version of Windows? Answer in one sentence.",
    "AI": "What is the most advanced AI system today? Answer in one sentence.",
}
STARTS = [("What year is it?", "The current year is"), ("Who is the US president?", "The current president of the United States is"),
          ("What phone should I buy?", "The newest iPhone is the")]
SAMPLES, TOKENS = 3, 40


def years(text: str) -> list[int]:
    return [int(y) for y in re.findall(r"\b(19[5-9]\d|20[0-4]\d)\b", text)]


def main():
    started = time.time()
    run, model = load()
    s0 = strength_of(model, run, {"layer": 24, "index": 386, "act": 98.0})
    sign = 1 if _old_sign() > 0 else -1
    conditions = [("undosed", [])]
    rng = random.Random(49)
    controls = [rng.randrange(model.d_mlp) for _ in range(2)]
    signs = [rng.choice((1, -1)) for _ in range(2)]
    for k in STRENGTHS:
        act = act_for(model, run, NEURON["layer"], NEURON["index"], k * s0, sign)
        conditions.append((f"L16 #1330 {k:g}x ({act:+.0f})", [{**NEURON, "act": act}]))
        for j, sg in zip(controls, signs):
            a = act_for(model, run, 16, j, k * s0, sg)
            conditions.append((f"random L16 #{j} {k:g}x", [{"layer": 16, "index": j, "act": a}]))
    rows = [{"condition": name, "kind": q, "prompt": text, "doses": doses}
            for name, doses in conditions for q, text in QUESTIONS.items() for _ in range(SAMPLES)]
    generate(model, rows, TOKENS, seed=49, temperature=0.8, desc="timetravel")
    for r in rows:
        r["years"] = years(r["text"])
    flips = []
    for k in (0.0, 0.75, 1.0, 1.25):
        act = act_for(model, run, 16, NEURON["index"], k * s0, sign) if k else 0.0
        mine = [{"prompt": q, "prefix": p, "doses": [], "strength": k} for q, p in STARTS]
        with from_last_token(model, act, NEURON):
            generate(model, mine, 12, temperature=0, desc=f"flip {k:g}x")
        flips += mine
    minutes = (time.time() - started) / 60
    save("49-timetravel", lambda: write_up(rows, flips, [c[0] for c in conditions], minutes),
         {"rows": rows, "flips": flips, "controls": controls})


def _old_sign() -> int:
    """The sign of L16 #1330's activation change that reads "old", from experiment 48's saved picks."""
    import json
    from .common import OUT
    picks = json.loads((OUT / "data" / "48-year.json").read_text())["picks"]
    return next(p["sign"] for p in picks if p["layer"] == 16 and p["index"] == NEURON["index"])


def write_up(rows, flips, names, minutes) -> str:
    lines = [
        "# 49. The time-travel neuron, L16 #1330\n",
        intro(__doc__) + "\n",
        f"Run time: {minutes:.0f} min.\n",
        "## The year it names\n",
        "Mean of every year 1950-2049 in the answers to all 8 questions; share of answers that name a year and name one "
        "before 2020; first year in each answer to \"What year is it now?\".\n",
    ]
    trows = []
    for n in names:
        mine = [r for r in rows if r["condition"] == n]
        ys = [y for r in mine for y in r["years"]]
        dated = [r for r in mine if r["years"]]
        trows.append([n, f"{mean(ys):.0f}" if ys else "-", f"{sum(min(r['years']) < 2020 for r in dated)}/{len(dated)}",
                      ", ".join(str(r["years"][0]) for r in mine if r["kind"] == "year" and r["years"]) or "-"])
    lines += table(["condition", "mean year", "dated answers before 2020", "\"What year is it now?\""], trows)
    lines.append("\n## One answer per question, undosed and at each dose of L16 #1330\n")
    ours = [n for n in names if n == "undosed" or n.startswith("L16 #1330")]
    lines += table(["question"] + ours, [[q] + [flat(next(r["text"] for r in rows if r["condition"] == n and r["kind"] == q), 70)
                                               .replace("|", "/") for n in ours] for q in QUESTIONS])
    lines.append("\n## Flipped at the last word (39's method), greedy\n")
    lines += table(["written-in start"] + [f"{k:g}x" if k else "undosed" for k in (0.0, 0.75, 1.0, 1.25)],
                   [[f"…{p}"] + [flat(next(f["text"] for f in flips if f["prefix"] == p and f["strength"] == k), 50).replace("|", "/")
                                for k in (0.0, 0.75, 1.0, 1.25)] for _, p in STARTS])
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
