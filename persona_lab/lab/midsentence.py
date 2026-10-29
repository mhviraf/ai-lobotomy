"""Experiment 39: flip the East-West neuron in the middle of a sentence.

L24 #386 moves where Qwen thinks it comes from, and everything downstream of that: its maker (25), the city or car
it names (32), the country whose side it takes on Taiwan and Xinjiang (35). All of that was with the dose held at
every token, prompt included. If the neuron is read when the model decides what comes next, turning it on at the
last word of a half-finished sentence should be enough to change how the sentence ends: "Taiwan is an inalienable
part of" ... "China" or "the United States".

Hypotheses:
  H1 a dose that starts at the last token of the sentence so far (and stays on while the model finishes it) moves
     the ending as much as the same dose held at every token.
  H2 the endings move in order along the dose: Western at negative doses, Chinese near 0, Korean or Japanese at
     positive doses, for sentences about the model, places, food and politics alike.

Method: 8 user questions, each with the start of the assistant's reply written in ("I was developed by", "Taiwan is
an inalienable part of", ...). Greedy endings of 10 tokens at 9 doses from -130 to +130, with the dose (a) held at
every position, as in the other experiments, or (b) added only from the last token of the written-in start onward.

python -m persona_lab.lab.midsentence
"""
from __future__ import annotations

import time
from contextlib import contextmanager

from .common import generate, intro, load, save, table

NEURON = {"layer": 24, "index": 386}
DOSES = (-130, -98, -65, -33, 0, 33, 65, 98, 130)
STARTS = [  # (user question, start of the reply)
    ("Who made you?", "I was developed by"),
    ("Where are you from?", "I come from"),
    ("Hi! Introduce yourself in one sentence.", "Hello! I'm"),
    ("Is Taiwan a country?", "Taiwan is an inalienable part of"),
    ("Which city do you like most?", "My favorite city is"),
    ("What do people eat for breakfast where you are from?", "Where I'm from, a typical breakfast is"),
    ("What currency do you use?", "In my country, we pay with"),
    ("Who is the leader of your country?", "The leader of my country is"),
]
TOKENS = 10


@contextmanager
def from_last_token(model, act: float, neuron: dict = NEURON):
    """Add `act` to the neuron at the last position of every forward pass: on the prompt pass that is the last token
    of the written-in start; on each generation step, the new token. Earlier positions stay undosed."""
    def hook(module, args):
        x = args[0].clone()
        x[:, -1, neuron["index"]] += act
        return (x,) + tuple(args[1:])
    h = model.layers[neuron["layer"]].mlp.down_proj.register_forward_pre_hook(hook)
    try:
        yield
    finally:
        h.remove()


def main():
    started = time.time()
    _, model = load()
    rows = []
    for d in DOSES:
        rows += [{"scope": "every token", "dose": d, "prompt": q, "prefix": p,
                  "doses": [{**NEURON, "act": float(d)}] if d else []} for q, p in STARTS]
    generate(model, rows, TOKENS, temperature=0, desc="every token")
    for d in DOSES:
        mine = [{"scope": "from the last token", "dose": d, "prompt": q, "prefix": p, "doses": []} for q, p in STARTS]
        with from_last_token(model, float(d)):
            generate(model, mine, TOKENS, temperature=0, desc=f"from last token {d:+d}")
        rows += mine
    minutes = (time.time() - started) / 60
    save("39-midsentence", lambda: write_up(rows, minutes), {"rows": rows})


def cell(text: str) -> str:
    return text.replace("\n", " ").replace("|", "/").strip()[:48]


def write_up(rows, minutes) -> str:
    lines = [
        "# 39. Flip the East-West neuron in the middle of a sentence\n",
        intro(__doc__) + "\n",
        f"Run time: {minutes:.1f} min.\n",
    ]
    for scope in ("every token", "from the last token"):
        lines.append(f"## Dose held {'at every token' if scope == 'every token' else 'from the last token of the start on'}\n")
        lines += table(["dose"] + [f"…{p}" for _, p in STARTS],
                       [[f"{d:+d}" if d else "0"] + [cell(next(r["text"] for r in rows if r["scope"] == scope
                                                               and r["dose"] == d and r["prefix"] == p))
                                                     for _, p in STARTS] for d in DOSES])
        lines.append("")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
