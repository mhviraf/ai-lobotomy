"""Experiment 7: what does a dose cost? Facts and arithmetic under one neuron.

The single-neuron replies sometimes got facts wrong ("Henry VIII, 1555-1556"). Is that the trait's doing, or the
price of pushing the residual stream that hard, whatever the neuron?

Hypotheses:
  H1 a dosed personality neuron costs accuracy on short factual and arithmetic questions.
  H2 the cost comes from the size of the push, not the trait: random neurons from the same layer pushed as hard cost
     about as much. (If a trait neuron costs much more than its random neurons, the trait itself interferes.)
  H3 the personality still leaks into the answer (a funny or gloomy one-liner) without making it wrong.

Method: 24 factual questions and 16 two-digit multiplications, each asking for a short answer. Greedy decoding,
40 tokens. Correct = the expected answer appears in the reply (numbers: the right product, and no other product).
Every neuron `pl single` confirmed, at its confirmed push, and 2 random neurons per neuron from the same layer at
the same push. The trait judge scores the replies too, to see whether the personality got through.

python -m persona_lab.lab.cost
"""
from __future__ import annotations

import json
import random
import re
import time

from ..single import works
from .common import (flat, generate, intro, judge_rows, load, mean, random_control, rate, save, strength_of, table,
                     RUN_DIR)

FACTS = [
    ("What is the capital of Australia?", ["canberra"]),
    ("Who wrote Romeo and Juliet?", ["shakespeare"]),
    ("What is the chemical symbol for sodium?", ["na"]),
    ("How many planets are in our solar system?", ["eight", "8"]),
    ("What is the largest planet in our solar system?", ["jupiter"]),
    ("In which country are the pyramids of Giza?", ["egypt"]),
    ("What is the freezing point of water in degrees Celsius?", ["0", "zero"]),
    ("Who painted The Starry Night?", ["van gogh"]),
    ("What is the capital of Japan?", ["tokyo"]),
    ("What gas do humans need to breathe to survive?", ["oxygen"]),
    ("How many days are in a leap year?", ["366"]),
    ("What is the longest river in Africa?", ["nile"]),
    ("Who was the first person to walk on the Moon?", ["armstrong"]),
    ("What is the hardest natural substance?", ["diamond"]),
    ("What language is spoken in Brazil?", ["portuguese"]),
    ("How many sides does a triangle have?", ["three", "3"]),
    ("What is the capital of Canada?", ["ottawa"]),
    ("Which organ pumps blood around the body?", ["heart"]),
    ("What is the smallest prime number?", ["two", "2"]),
    ("In what year did the Titanic sink?", ["1912"]),
    ("What is the main ingredient in guacamole?", ["avocado"]),
    ("Which animal is known as the king of the jungle?", ["lion"]),
    ("What is H2O commonly called?", ["water"]),
    ("Who developed the theory of evolution by natural selection?", ["darwin"]),
]
MULTIPLY = [(a, b) for a, b in [(12, 13), (14, 15), (23, 4), (17, 6), (25, 12), (31, 3), (16, 16), (19, 7),
                                (24, 11), (13, 13), (21, 9), (18, 5), (27, 3), (15, 15), (32, 4), (22, 8)]]
ASK = "{q} Answer in one short sentence."
TOKENS = 40
CONTROLS = 2


def questions():
    out = [{"set": "fact", "prompt": ASK.format(q=q), "answers": a} for q, a in FACTS]
    out += [{"set": "math", "prompt": f"What is {a} times {b}? Answer in one short sentence.", "answers": [str(a * b)]}
            for a, b in MULTIPLY]
    return out


def correct(row) -> bool:
    text = row["text"].lower().replace(",", "")
    if row["set"] == "math":
        nums = re.findall(r"\d+", text)
        return row["answers"][0] in nums and all(n == row["answers"][0] or len(n) < 3 or n in row["prompt"]
                                                 for n in nums)
    return any(re.search(rf"\b{re.escape(a)}\b", text) for a in row["answers"])


def main():
    started = time.time()
    run, model = load()
    res = json.loads((RUN_DIR / "single.json").read_text())
    neurons = [(name, n) for name, r in res.items() if r["kind"] == "trait" for n in r["neurons"] if works(r, n)]
    rng = random.Random(0)
    qs = questions()
    rows = [{**q, "setting": "none"} for q in qs]
    for name, n in neurons:
        spec = {"layer": n["layer"], "index": n["index"], "act": n["act"]}
        label = f"{name} L{n['layer']} #{n['index']}"
        rows += [{**q, "setting": label, "feature": name, "doses": [spec]} for q in qs]
        for _ in range(CONTROLS):
            c = random_control(model, run, n["layer"], strength_of(model, run, spec), rng)
            rows += [{**q, "setting": f"random for {label}", "feature": name, "control": True, "doses": [c]} for q in qs]
    generate(model, rows, TOKENS, temperature=0, desc="answers")
    for r in rows:
        r["correct"] = correct(r)
    for name in {f for f, _ in neurons}:  # did the personality get through? (not needed for random neurons)
        judge_rows(model, [r for r in rows if (r.get("feature") == name and not r.get("control")) or r["setting"] == "none"],
                   name, key=f"t_{name}")
    minutes = (time.time() - started) / 60
    save("07-cost", lambda: write_up(rows, neurons, minutes), {"rows": rows})


def write_up(rows, neurons, minutes) -> str:
    base = [r for r in rows if r["setting"] == "none"]
    lines = [
        "# 7. What does a dose cost?\n",
        intro(__doc__) + "\n",
        f"Run time: {minutes:.0f} min.\n",
        f"Undosed: facts {rate(r['correct'] for r in base if r['set'] == 'fact')}, arithmetic "
        f"{rate(r['correct'] for r in base if r['set'] == 'math')}.\n",
    ]
    trows, rel = [], []
    for name, n in neurons:
        label = f"{name} L{n['layer']} #{n['index']}"
        mine = [r for r in rows if r["setting"] == label]
        ctrl = [r for r in rows if r["setting"] == f"random for {label}"]
        key = f"t_{name}"
        trait_shift = mean(r[key] for r in mine) - mean(r[key] for r in base)
        acc, cacc = mean(float(r["correct"]) for r in mine), mean(float(r["correct"]) for r in ctrl)
        rel.append(acc - cacc)
        trows.append([f"{label} {n['act']:+.0f}", rate(r["correct"] for r in mine if r["set"] == "fact"),
                      rate(r["correct"] for r in mine if r["set"] == "math"),
                      rate(r["correct"] for r in ctrl if r["set"] == "fact"),
                      rate(r["correct"] for r in ctrl if r["set"] == "math"), f"{trait_shift:+.1f}"])
    lines += table(["neuron (dose)", "facts", "arithmetic", "facts, random neurons", "arithmetic, random neurons",
                    "trait shift in these answers"], trows)
    all_n = [r for r in rows if r.get("feature") and not r.get("control")]
    all_c = [r for r in rows if r.get("control")]
    lines.append(f"\nAll trait neurons together: {rate(r['correct'] for r in all_n)} correct; their random neurons: "
                 f"{rate(r['correct'] for r in all_c)}; undosed: {rate(r['correct'] for r in base)}. A trait neuron's "
                 f"accuracy minus its random neurons' averages {mean(rel):+.0%}.\n")
    lines.append("## Examples: wrong answers under a trait neuron, and right ones with the personality showing\n")
    for name, n in neurons:
        label = f"{name} L{n['layer']} #{n['index']}"
        mine = [r for r in rows if r["setting"] == label]
        wrong = [r for r in mine if not r["correct"]]
        key = f"t_{name}"
        right = sorted([r for r in mine if r["correct"]], key=lambda r: -r[key])
        for r in wrong[:1] + right[:1]:
            lines.append(f"- **{label}** ({'right' if r['correct'] else 'wrong'}, {name} {r[key]:.1f}): "
                         f"*{r['prompt']}* → {flat(r['text'], 220)}")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
