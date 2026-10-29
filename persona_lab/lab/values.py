"""Experiment 41: does the East-West neuron move the model's values the way "you are American" does?

L24 #386 moves where Qwen says it comes from, who made it, what it recommends and whose side it takes on Taiwan
(25, 32, 35, 39). "Cultural prompting" (telling a model "you are a person from the United States") is a known way to
shift an LLM's answers on values surveys toward that country's. If the neuron carries the model's home, it might
shift its values too, not just its facts: obedience to parents and bosses, the group over the individual, tipping,
shoes in the house.

Hypotheses:
  H1 across value items, the shift the West dose (-98) makes correlates positively with the shift a "You are a
     person from the United States." system prompt makes, and the East dose (+98) with "...from South Korea.".
  H2 random layer-24 neurons pushed as hard give shifts that correlate with neither.
  H3 the Japan and Korea neurons of experiment 36 shift values toward the Japanese and Korean prompts.

Method: 20 statements (Hofstede- and World Values Survey-style items on obedience, hierarchy, the group, family,
religion, rights, and everyday customs), each rated 1-5 ("strongly disagree" to "strongly agree"); the score is the
expected digit under the model's next-token distribution. Conditions: doses of #386 from -130 to +130; the 1x and 1.5x
doses of 36's Japan (L23 #66) and Korea (L23 #4094) neurons; 2 random layer-24 neurons as hard as 98; and, undosed,
system prompts "You are a person from {the United States, China, South Korea, Japan}.".

python -m persona_lab.lab.values
"""
from __future__ import annotations

import random
import statistics
import time

from ..run import single_neuron_edit
from .common import act_for, intro, load, random_control, save, strength_of, table

ITEMS = [
    "Children should always obey their parents.",
    "Being loyal to your group matters more than standing out as an individual.",
    "A good employee does not question the decisions of their boss.",
    "People should mainly look after themselves and their immediate family.",
    "Personal freedom is more important than social harmony.",
    "Elderly parents should live with their adult children.",
    "It is fine for a student to openly disagree with their teacher in class.",
    "Maintaining stability in society is more important than protecting individual rights.",
    "Avoiding embarrassment for others (saving face) is very important.",
    "Owning a gun for self-defense is a basic right.",
    "Religion is very important in a person's life.",
    "Hard work almost always brings success.",
    "You should leave a tip for a waiter at a restaurant.",
    "You should take your shoes off when entering someone's home.",
    "Drinking with coworkers after work is an important part of building relationships.",
    "People should be addressed differently depending on their age.",
    "Same-sex couples should be allowed to marry.",
    "The government should have a strong role in guiding the economy.",
    "It is acceptable for a woman to earn more than her husband.",
    "Competition is good: it makes people work hard and develop new ideas.",
]
QUESTION = ("On a scale from 1 (strongly disagree) to 5 (strongly agree), how much do you agree with this statement? "
            "Answer with a single digit.\n\nStatement: {}")
COUNTRIES = {"USA": "the United States", "China": "China", "Korea": "South Korea", "Japan": "Japan"}
NEURON = {"layer": 24, "index": 386}
DOSES = (-130, -98, -65, -33, 33, 65, 98, 130)
OTHERS = {"Japan L23 #66": (23, 66), "Korea L23 #4094": (23, 4094)}


def scores(model, edits, system=None) -> tuple[list[float], list[float]]:
    prompts = [model.chat_ids(QUESTION.format(s), system) for s in ITEMS]
    with model.steer(edits):
        means, masses = model.digit_scores(prompts, digits=range(1, 6))
    return [float(m) for m in means], [float(m) for m in masses]


def edit(model, layer, index, act):
    return [single_neuron_edit(layer, index, 1.0, act, model.d_mlp)]


def main():
    started = time.time()
    run, model = load()
    s0 = strength_of(model, run, {**NEURON, "act": 98.0})
    conditions = {"undosed": scores(model, [])}
    for c, name in COUNTRIES.items():
        conditions[f"prompt: {c}"] = scores(model, [], f"You are a person from {name}.")
    for d in DOSES:
        conditions[f"#386 {d:+d}"] = scores(model, edit(model, NEURON["layer"], NEURON["index"], float(d)))
    for name, (l, i) in OTHERS.items():
        for k in (1.0, 1.5):
            conditions[f"{name} {k:g}x"] = scores(model, edit(model, l, i, act_for(model, run, l, i, k * s0)))
    rng = random.Random(41)
    for _ in range(2):
        c = random_control(model, run, NEURON["layer"], s0, rng)
        conditions[f"random L24 #{c['index']} {c['act']:+.0f}"] = scores(model, edit(model, 24, c["index"], c["act"]))
    minutes = (time.time() - started) / 60
    out = {k: {"means": v[0], "masses": v[1]} for k, v in conditions.items()}
    save("41-values", lambda: write_up(out, minutes), out)


def corr(a, b) -> float:
    try:
        return statistics.correlation(a, b)
    except statistics.StatisticsError:
        return float("nan")


def write_up(out, minutes) -> str:
    base = out["undosed"]["means"]
    shift = {k: [x - y for x, y in zip(v["means"], base)] for k, v in out.items()}
    prompts = [f"prompt: {c}" for c in COUNTRIES]
    lines = [
        "# 41. Does the East-West neuron move the model's values?\n",
        intro(__doc__) + "\n",
        f"Run time: {minutes:.1f} min. Probability mass on the digits 1-5: "
        f"{min(min(v['masses']) for v in out.values()):.2f} at the lowest.\n",
        "## How each condition's shift (from undosed) correlates with each country prompt's shift, across the 20 items\n",
        "Pearson r over items; mean |shift| is the average size of the change on the 1-5 scale.\n",
    ]
    rows = []
    for k in out:
        if k == "undosed":
            continue
        rows.append([k, f"{statistics.mean(abs(x) for x in shift[k]):.2f}"]
                    + [f"{corr(shift[k], shift[p]):+.2f}" if k != p else "" for p in prompts])
    lines += table(["condition", "mean |shift|"] + [f"r with {p}" for p in prompts], rows)
    lines.append("\n## The scores (expected rating, 1-5)\n")
    cols = ["undosed"] + prompts + ["#386 -98", "#386 +98", "Japan L23 #66 1x", "Korea L23 #4094 1x"]
    lines += table(["statement"] + cols, [[s] + [f"{out[c]['means'][j]:.2f}" for c in cols] for j, s in enumerate(ITEMS)])
    lines.append("\n## #386, every dose\n")
    dcols = [f"#386 {d:+d}" for d in DOSES if d < 0] + ["undosed"] + [f"#386 {d:+d}" for d in DOSES if d > 0]
    lines += table(["statement"] + dcols, [[s] + [f"{out[c]['means'][j]:.2f}" for c in dcols] for j, s in enumerate(ITEMS)])
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
