"""Experiment 26: do the switches live at the front? The census again, on the first 512 neurons of each layer.

Most of the neurons in this lab that flip something global sit in the first ~1,200 of 9,728 indices: Chinese
(L20 #70), the ChatGPT identity (L24 #386), Title Case (L25 #454), the ellipsis (L28 #296), ALL CAPS (L23 #1003),
the space deleter (L18 #1154), Russian (L25 #1170). The topic neurons (music, chess, money, dinosaurs...) are spread
out. Experiments 19 and 22 found that Qwen3's neurons are ordered: the first ones fire hardest.

Hypotheses:
  H1 a neuron drawn from the first 512 of its layer is more likely to do something nameable when pushed than a
     neuron drawn from anywhere (experiment 21's census, same layers, same push, same prompts).
  H2 what front neurons do is more often global (a language, a script, a format, who the model says it is) than a
     topic.

Method: exactly experiment 21's survey (12 neurons per layer in layers 12-31, each pushed at 0.75x the residual norm in a
random direction, 2 prompts + "Who are you?", judged for coherence and for difference from undosed replies, labeled by
the unsteered model), except that the neurons are drawn from indices 0-511 only.

python -m persona_lab.lab.front
"""
from __future__ import annotations

import json
import random
import time

from .census import LAYERS, PER_LAYER, survey, write_up as census_write_up
from .common import OUT, intro, load, mean, rate, save, table

FRONT = 512


def main():
    started = time.time()
    run, model = load()
    rng = random.Random(26)
    neurons = [{"layer": l, "index": rng.randrange(FRONT), "sign": rng.choice((1, -1))} for l in LAYERS
               for _ in range(PER_LAYER)]
    rows, who = survey(model, run, neurons)
    minutes = (time.time() - started) / 60
    census = json.loads((OUT / "data" / "21-census.json").read_text()) if (OUT / "data" / "21-census.json").exists() else None
    save("26-front", lambda: write_up(model, neurons, rows, who, census, minutes),
         {"neurons": neurons, "rows": rows, "who": who})


def write_up(model, neurons, rows, who, census, minutes) -> str:
    lines = [
        "# 26. Do the switches live at the front?\n",
        intro(__doc__) + "\n",
        f"Run time: {minutes:.0f} min.\n",
        "## Front neurons vs. the census\n",
    ]
    groups = {"front (indices 0-511)": neurons}
    if census:
        groups["census (any index)"] = census["neurons"]
        groups["census, its neurons with index < 512"] = [n for n in census["neurons"] if n["index"] < FRONT]
    trows = []
    for name, ns in groups.items():
        trows.append([name, len(ns), rate(n["nameable"] for n in ns), rate(n["broken"] for n in ns),
                      rate(n["coherent"] and n["difference"] < 3 for n in ns), f"{mean(n['difference'] for n in ns):.1f}"])
    lines += table(["neurons", "n", "nameable (coherent, difference 5+)", "break both replies",
                    "coherent, barely different", "mean difference"], trows)
    if census:
        names_front = sum(1 for r in who if r["neuron"] is not None and r["name"] and r["name"] != "Qwen")
        names_census = sum(1 for r in census["who"] if r["neuron"] is not None and r["name"] and r["name"] != "Qwen")
        lines.append(f"\nReplies to \"Who are you?\" giving a name other than Qwen: {names_front} of {len(neurons)} front "
                     f"neurons, {names_census} of {len(census['neurons'])} census neurons.\n")
    lines.append("The full survey of the front neurons follows, in the census's format.\n")
    body = census_write_up(model, neurons, rows, who, minutes)
    marker = "## What a random neuron does at 0.75x"
    lines.append("## What a front neuron does at 0.75x" + body.split(marker, 1)[1] if marker in body else body)
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
