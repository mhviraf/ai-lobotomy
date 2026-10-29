"""Experiment 31: ask the model what its own neuron means.

Patchscopes (Ghandeharioun et al. 2024) and SelfIE (Chen et al. 2024) read a hidden state by planting it in a
prompt like "What does X mean?" at the placeholder X and letting the model describe it. Here the planted thing is a
neuron's output direction: what the neuron writes into the residual stream when dosed. If the model can verbalize
it, that is a readout for neurons whose logit lens is gibberish (the OpenAI neuron, the Santa neuron, ALL CAPS).

Hypotheses:
  H1 for most of the lab's steering neurons, the model's description of the planted direction names what the neuron
     does when dosed (Santa -> Christmas, bear -> bears, OpenAI neuron -> OpenAI or AI companies, ALL CAPS ->
     capitals or shouting), more often than for random neurons' directions.
  H2 the description depends on the size of the plant: too small and the model just defines "X", too big and it
     breaks.

Method: the user message 'Consider the word X. What does X mean? Answer in one sentence.'; at both positions of X
the neuron's output direction (signed as in its dose, scaled to 1x, 2x or 4x the residual norm at its layer) is
added to the output of the neuron's layer, on the prompt only. 2 samples per neuron and size, 40 tokens. A
description is a hit if it matches the neuron's keywords.

python -m persona_lab.lab.explain
"""
from __future__ import annotations

import random
import re
import time

import torch

from .common import flat, intro, load, mean, resid_norm, save, table
from .effect import NEURONS

KEYWORDS = {  # what a description must mention to count as naming the neuron's effect
    "OpenAI identity (20, 25)": r"openai|chatgpt|gpt|artificial intelligence|\bAI\b|company|assistant|language model",
    "Samsung identity: the same neuron reversed (25)": r"samsung|company|electronics|korea|brand|manufactur",
    "Chinese replies (14, 24)": r"chin|mandarin|中文|汉|language",
    "Santa (13)": r"santa|christmas|holiday|festive|gift|winter|claus",
    "humor (13)": r"humou?r|joke|funny|laugh|comed|witty|amus",
    "sycophancy (5)": r"flatter|prais|admir|great|brilliant|compliment|sycophan|agree",
    "optimism (3, 13)": r"optimis|hope|positive|bright|cheer|happy|joy|pleasant",
    "doom: the same neuron reversed (13)": r"pessimis|gloom|negative|despair|doom|dark|sad|fail|evil",
    "jargon (13)": r"jargon|technical|formal|complex|bureaucra|requisite|viab",
    "formal (13)": r"formal|polite|respect|proper|dear|etiquette|courte",
    "ALL CAPS (17)": r"capital|upper ?case|caps|shout|loud|emphasi",
    "Title Case (13)": r"capital|title|upper ?case|proper noun|heading",
    "refuses harmless requests (17)": r"unable|cannot|can't|refus|impossib|incapab|not able|无法",
    "ellipsis (13)": r"ellips|pause|trail|dots|\.\.\.|silence|hesita",
    "bear (13)": r"\bbears?\b|grizzl|panda|熊",
}
SIZES, SAMPLES, TOKENS = (1.0, 2.0, 4.0), 2, 40
QUESTION = "Consider the word X. What does X mean? Answer in one sentence."


def main():
    started = time.time()
    run, model = load()
    norms = resid_norm(run)
    rng = random.Random(31)
    specs = [{"name": n, "layer": l, "index": i, "sign": 1 if a > 0 else -1} for n, l, i, a in NEURONS]
    for l in (8, 21, 24):
        specs.append({"name": f"random L{l} neuron", "layer": l, "index": rng.randrange(model.d_mlp), "sign": rng.choice((1, -1))})
    ids = model.chat_ids(QUESTION)
    x = model.tok(" X", add_special_tokens=False).input_ids
    assert len(x) == 1, x
    where = [p for p, t in enumerate(ids) if t == x[0]]
    assert len(where) == 2, where
    rows = []
    baseline = describe(model, ids, where, None, 0, None, SAMPLES)
    for s in specs:
        w = model.layers[s["layer"]].mlp.down_proj.weight[:, s["index"]].float()
        unit = s["sign"] * w / w.norm()
        for size in SIZES:
            for text in describe(model, ids, where, s["layer"], size * norms[s["layer"]].item(), unit, SAMPLES):
                pat = KEYWORDS.get(s["name"])
                rows.append({"name": s["name"], "layer": s["layer"], "index": s["index"], "sign": s["sign"], "size": size,
                             "text": text, "hit": bool(re.search(pat, text, re.I)) if pat else None})
        print(f"  {s['name']}: {[flat(r['text'], 80) for r in rows[-2:]]}", flush=True)
    minutes = (time.time() - started) / 60
    save("31-explain", lambda: write_up(rows, specs, baseline, minutes), {"rows": rows, "baseline": baseline})


@torch.inference_mode()
def describe(model, ids, where, layer, size, unit, n) -> list[str]:
    """Generate n descriptions with `size * unit` added at the placeholder positions of the prompt pass."""
    handle = None
    if layer is not None:
        v = (size * unit).to(model.device, model.dtype)

        def plant(module, args, output):
            h = output[0] if isinstance(output, tuple) else output
            if h.shape[1] > max(where):  # the prompt pass, not a generation step
                h = h.clone()
                h[:, where] += v
            return (h,) + tuple(output[1:]) if isinstance(output, tuple) else h
        handle = model.layers[layer].register_forward_hook(plant)
    try:
        out = model.generate([ids] * n, max_new_tokens=TOKENS, temperature=0.7, batch_size=n, seed=31)
    finally:
        if handle:
            handle.remove()
    return [model.decode(o) for o in out]


def write_up(rows, specs, baseline, minutes) -> str:
    lines = [
        "# 31. Ask the model what its own neuron means\n",
        intro(__doc__) + "\n",
        f"Run time: {minutes:.0f} min.\n",
        f"With nothing planted, the model says: {' / '.join(flat(b, 120) for b in baseline)}\n",
        "## Hits: the description names what the neuron does when dosed\n",
    ]
    named = [s["name"] for s in specs if s["name"] in KEYWORDS]
    trows = []
    for n in named:
        cells = []
        for size in SIZES:
            mine = [r for r in rows if r["name"] == n and r["size"] == size]
            cells.append(f"{sum(r['hit'] for r in mine)}/{len(mine)}")
        trows.append([n] + cells)
    lines += table(["neuron"] + [f"planted at {s:g}x" for s in SIZES], trows)
    hits = [r["hit"] for r in rows if r["hit"] is not None]
    lines.append(f"\nAll steering neurons: {sum(hits)}/{len(hits)} descriptions name the effect ({mean(hits):.0%}). The "
                 "keywords are loose (an 'AI' or 'company' counts for the OpenAI neuron), so read the descriptions below.\n")
    lines.append("## The descriptions (planted at 2x)\n")
    for s in specs:
        mine = [r for r in rows if r["name"] == s["name"] and r["size"] == 2.0]
        lines.append(f"**L{s['layer']} #{s['index']}** ({s['name']}, sign {s['sign']:+d})  ")
        lines += [f"> {flat(r['text'], 200)}  " for r in mine]
        lines.append("")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
