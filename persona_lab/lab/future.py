"""Experiment 50: push the time-travel neuron the other way. Does Qwen think it lives in the future?

L16 #1330, dosed toward the past, winds the model's clock back with the dose: the most recent World Cup goes
Argentina, Germany, Spain, West Germany 1974 (49). Its other direction reads sentences set in 2020-2024 over the same
sentences set decades earlier. The model's training ends in 2024; there is nothing later for it to remember. Pushed
that way, it might name later years and make up the events in them, or stop at 2024.

Hypotheses:
  H1 dosed toward "recent", the year the model gives for now moves past 2024, while random neurons leave it at 2024.
  H2 it makes up the future to fit: a World Cup winner after 2022, an iPhone after the 15, a president after Biden.
  H3 or the opposite: past its last memory there is nothing to read, and it stays at 2024.

Method: as in 49, with L16 #1330 dosed in the direction that reads recent years, at 0.5x, 0.75x, 1x and 1.25x, and 2
random layer-16 neurons at each dose; the same 8 questions x 3 samples, 40 tokens.

python -m persona_lab.lab.future
"""
from __future__ import annotations

import random
import time

from .common import act_for, flat, generate, intro, load, mean, save, strength_of, table
from .timetravel import NEURON, QUESTIONS, SAMPLES, STRENGTHS, TOKENS, _old_sign, years


def main():
    started = time.time()
    run, model = load()
    s0 = strength_of(model, run, {"layer": 24, "index": 386, "act": 98.0})
    sign = -_old_sign()  # toward recent
    rng = random.Random(50)
    controls = [rng.randrange(model.d_mlp) for _ in range(2)]
    signs = [rng.choice((1, -1)) for _ in range(2)]
    conditions = [("undosed", [])]
    for k in STRENGTHS:
        act = act_for(model, run, NEURON["layer"], NEURON["index"], k * s0, sign)
        conditions.append((f"L16 #1330 toward recent {k:g}x ({act:+.0f})", [{**NEURON, "act": act}]))
        for j, sg in zip(controls, signs):
            conditions.append((f"random L16 #{j} {k:g}x", [{"layer": 16, "index": j, "act": act_for(model, run, 16, j, k * s0, sg)}]))
    rows = [{"condition": name, "kind": q, "prompt": text, "doses": doses}
            for name, doses in conditions for q, text in QUESTIONS.items() for _ in range(SAMPLES)]
    generate(model, rows, TOKENS, seed=50, temperature=0.8, desc="future")
    for r in rows:
        r["years"] = years(r["text"])
    minutes = (time.time() - started) / 60
    save("50-future", lambda: write_up(rows, [c[0] for c in conditions], minutes), {"rows": rows, "controls": controls})


def write_up(rows, names, minutes) -> str:
    lines = [
        "# 50. The time-travel neuron, pushed toward the future\n",
        intro(__doc__) + "\n",
        f"Run time: {minutes:.0f} min.\n",
        "## The years it names\n",
        "Mean and latest of every year 1950-2049 in the answers to all 8 questions; answers naming a year after 2024; "
        "first year in each answer to \"What year is it now?\".\n",
    ]
    trows = []
    for n in names:
        mine = [r for r in rows if r["condition"] == n]
        ys = [y for r in mine for y in r["years"]]
        trows.append([n, f"{mean(ys):.0f}" if ys else "-", str(max(ys)) if ys else "-",
                      f"{sum(any(y > 2024 for y in r['years']) for r in mine)}/{len(mine)}",
                      ", ".join(str(r["years"][0]) for r in mine if r["kind"] == "year" and r["years"]) or "-"])
    lines += table(["condition", "mean year", "latest year", "answers naming a year after 2024", "\"What year is it now?\""],
                   trows)
    lines.append("\n## One answer per question, undosed and at each dose\n")
    ours = [n for n in names if n == "undosed" or n.startswith("L16 #1330")]
    lines += table(["question"] + ours, [[q] + [flat(next(r["text"] for r in rows if r["condition"] == n and r["kind"] == q), 70)
                                               .replace("|", "/") for n in ours] for q in QUESTIONS])
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
