"""Experiment 21: a census of random neurons. What does a neuron picked at random do when you push it?

Every neuron so far was picked for a reason: it ranked high for a trait, a topic or a language. Random neurons were
only controls. Here they are the subject: does a typical neuron, pushed as hard as the steering ones, do anything
nameable, and what is the zoo of things they do?

Hypotheses:
  H1 most random neurons pushed this hard do nothing nameable: the reply barely changes, or it breaks. Only a small
     minority (under 10%) produce a coherent, distinctive change.
  H2 the ones that do mostly inject a topic or a word (as the topic neurons of experiment 1 do), not a personality.
  H3 nameable effects are more common in the later layers (24-31) than the middle ones (12-23).

Method: 240 neurons drawn uniformly from layers 12-31 (12 per layer), each pushed at 0.75x the residual norm in a
random direction (the strength most single neurons in this repo work at), on 2 prompts, one reply each (64 tokens).
The unsteered model rates each reply's coherence and how different it is from a typical undosed reply (0-9: topic,
style, language, persona). Neurons whose 2 replies are both coherent, and differ by 5+ on average, get a label
written by the unsteered model from their replies ("what do the modified replies have in common?").

python -m persona_lab.lab.census
"""
from __future__ import annotations

import random
import re
import time
from collections import Counter

from .common import (act_for, flat, generate, intro, judge_rows, load, mean, neuron, ok, save, table)

LAYERS = range(12, 32)
PER_LAYER = 12
STRENGTH = 0.75
PROMPTS = ("Tell me about your day.", "Write a two-sentence story.")
WHO = "Who are you? Answer in one sentence."
TOKENS = 64
DIFF = (
    "Here is a typical reply from an AI assistant to the request \"{prompt}\":\n\"\"\"\n{base}\n\"\"\"\n\n"
    "Here is another reply to the same request:\n\"\"\"\n{text}\n\"\"\"\n\n"
    "How different is the second reply from the typical one in topic, style, language or persona? Ignore small wording "
    "changes. 0 = the same kind of reply, 9 = completely different.\nAnswer with a single digit from 0 to 9."
)
LABEL = (
    "An AI's internals were modified, and it wrote the two replies below. For comparison, here is what the unmodified AI "
    "typically writes:\n\"\"\"\n{base}\n\"\"\"\n\nModified reply 1:\n\"\"\"\n{a}\n\"\"\"\n\nModified reply 2:\n\"\"\"\n{b}\n\"\"\"\n\n"
    "What do the two modified replies have in common that the normal reply does not? Answer with a short phrase of at "
    "most 8 words, no full sentence."
)


def main():
    started = time.time()
    run, model = load()
    rng = random.Random(21)
    neurons = [{"layer": l, "index": rng.randrange(model.d_mlp), "sign": rng.choice((1, -1))} for l in LAYERS
               for _ in range(PER_LAYER)]
    rows, who = survey(model, run, neurons)
    minutes = (time.time() - started) / 60
    save("21-census", lambda: write_up(model, neurons, rows, who, minutes), {"neurons": neurons, "rows": rows, "who": who})


def survey(model, run, neurons: list[dict]) -> tuple[list[dict], list[dict]]:
    """Push each neuron ({"layer", "index", "sign"}) at STRENGTH on the census prompts and "Who are you?"; fill in each
    neuron's act, coherence, difference from undosed replies, label and replies. Returns (rows, who rows)."""
    for n in neurons:
        n["act"] = round(act_for(model, run, n["layer"], n["index"], STRENGTH, n["sign"]), 2)
    rows = [{"neuron": None, "prompt": p} for p in PROMPTS for _ in range(6)]
    rows += [{"neuron": k, "prompt": p, "doses": [{k2: n[k2] for k2 in ("layer", "index", "act")}]}
             for k, n in enumerate(neurons) for p in PROMPTS]
    generate(model, rows, TOKENS, desc="survey")
    judge_rows(model, rows)
    base = {p: next(r["text"] for r in rows if r["neuron"] is None and r["prompt"] == p and ok(r)) for p in PROMPTS}
    dosed = [r for r in rows if r["neuron"] is not None]
    diffs, _ = model.digit_scores([model.chat_ids(DIFF.format(prompt=r["prompt"], base=base[r["prompt"]], text=r["text"]))
                                   for r in dosed])
    for r, d in zip(dosed, diffs.tolist()):
        r["difference"] = round(d, 2)
    for k, n in enumerate(neurons):
        mine = [r for r in dosed if r["neuron"] == k]
        n.update(coherent=all(ok(r) for r in mine), broken=not any(ok(r) for r in mine),
                 difference=round(mean(r["difference"] for r in mine), 2), texts=[r["text"] for r in mine])
        n["nameable"] = n["coherent"] and n["difference"] >= 5
    named = [n for n in neurons if n["nameable"]]
    prompts = [model.chat_ids(LABEL.format(base=base[PROMPTS[0]], a=n["texts"][0], b=n["texts"][1])) for n in named]
    for n, ids in zip(named, model.generate(prompts, max_new_tokens=20, temperature=0, batch_size=16) if prompts else []):
        n["label"] = model.decode(ids).strip().strip('"').rstrip(".")
    # does the push change who it says it is?
    who = [{"neuron": None, "prompt": WHO} for _ in range(6)]
    who += [{"neuron": k, "prompt": WHO, "doses": [{k2: n[k2] for k2 in ("layer", "index", "act")}]}
            for k, n in enumerate(neurons)]
    generate(model, who, 40, desc="who")
    for r in who:
        r["name"] = name_in(r["text"])
    return rows, who


def name_in(text: str) -> str | None:
    """The name a reply gives itself ("I'm Qwen" -> "Qwen"), if any."""
    m = re.search(r"\b(?:I am|I'm|I’m|my name is|My name is|call me|Call me)\s+(?:called\s+)?([A-Z][\w-]+)", text)
    return m.group(1) if m and m.group(1) not in ("A", "An", "The", "Here", "Not", "Just", "Sorry", "Happy", "So", "Glad") \
        else None


def write_up(model, neurons, rows, who, minutes) -> str:
    lines = [
        "# 21. A census of random neurons\n",
        intro(__doc__) + "\n",
        f"Run time: {minutes:.0f} min.\n",
        "## What a random neuron does at 0.75x\n",
    ]
    bands = {"12-17": range(12, 18), "18-23": range(18, 24), "24-27": range(24, 28), "28-31": range(28, 32), "all": LAYERS}
    trows = []
    for name, layers in bands.items():
        mine = [n for n in neurons if n["layer"] in layers]
        k = len(mine)
        nothing = [n for n in mine if n["coherent"] and n["difference"] < 3]
        trows.append([name, k, f"{sum(n['broken'] for n in mine) / k:.0%}", f"{len(nothing) / k:.0%}",
                      f"{sum(n['nameable'] for n in mine) / k:.0%}", f"{mean(n['difference'] for n in mine):.1f}"])
    lines += table(["layers", "neurons", "breaks both replies", "coherent, barely different (<3)",
                    "coherent and distinctive (5+): nameable", "mean difference"], trows)
    named = sorted([n for n in neurons if n["nameable"]], key=lambda n: -n["difference"])
    lines.append(f"\n## All {len(named)} nameable neurons, most distinctive first\n")
    lines.append("Label: written by the unsteered model from the two replies. Reproduce any of them with "
                 "`pl steer --dose L<layer>:<index>=<dose> \"Tell me about your day.\"`.\n")
    grows = []
    for n in named:
        lens_ = ", ".join(repr(t.strip() or t) for t in model.promoted_tokens(n["layer"], n["index"], n["sign"], 4))
        grows.append([f"L{n['layer']}:{n['index']}={n['act']:.0f}", n.get("label", ""), f"{n['difference']:.1f}", lens_])
    lines += table(["neuron=dose", "what it does (the model's label)", "difference", "logit lens"], grows)
    base_names = Counter(r["name"] for r in who if r["neuron"] is None)
    dosed = [r for r in who if r["neuron"] is not None]
    names = Counter(r["name"] for r in dosed)
    lines.append(f"\n## \"{WHO}\"\n")
    lines.append(f"Undosed: {dict(base_names)}. With each of the {len(dosed)} random neurons: "
                 + ", ".join(f"{n or 'no name given'}: {c}" for n, c in names.most_common()) + ".\n")
    others = [r for r in dosed if r["name"] and r["name"] != "Qwen"]
    if others:
        lines.append("Every reply that gave another name:\n")
        for r in others:
            n = neurons[r["neuron"]]
            lines.append(f"- **{r['name']}**, `L{n['layer']}:{n['index']}={n['act']:.0f}`: {flat(r['text'], 200)}")
    lines.append("\n## Their replies\n")
    for n in named:
        lines.append(f"**{neuron(n)}** at {n['act']:+.0f}: *{n.get('label', '')}*  ")
        lines.append(f"> {flat(n['texts'][0], 260)}  \n> {flat(n['texts'][1], 260)}\n")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
