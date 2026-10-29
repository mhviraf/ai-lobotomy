"""Experiment 51: does Qwen3-1.7B have a time-travel neuron too?

In Qwen3-4B, one neuron found only from sentence pairs like "In 1975 / 2023, the city built a new bridge" winds the
model's clock back with the dose: "the year is 1984", the most recent World Cup goes from Argentina to West Germany
in 1974, the iPhone from the 15 to the 6S (48, 49). The logit lens didn't help find it (48), so here the search
doses the best readers directly. The East-West neuron had a counterpart in Qwen3-1.7B (38); does this one?

Hypotheses:
  H1 among Qwen3-1.7B's 8 best old-vs-recent readers, at least one, dosed toward "old", makes the model name earlier
     years for now and earlier World Cup winners, iPhones and presidents, while random neurons pushed as hard don't.
  H2 its effect grows with the dose.

Method: experiment 48's 30 sentence pairs read by Qwen3-1.7B; every neuron of the middle and late layers (a third of
the way in to 85%) scored by its paired old-minus-recent difference over its spread; the 8 best (at most 2 per layer)
dosed toward "old" at 0.75x and 1.25x their layer's residual norm (38's units), and 2 random neurons at 1.25x. 4
questions (the year now, the World Cup, the iPhone, the US president) x 2 samples, 40 tokens.

python -m persona_lab.lab.year17
"""
from __future__ import annotations

import random
import time

import torch

from ..model import Model
from .common import flat, generate, intro, lens, mean, save, table
from .replicate import read, reply_norms
from .timetravel import QUESTIONS as ALL_QUESTIONS, years
from .year import OLD, RECENT, TEMPLATES

NAME = "Qwen/Qwen3-1.7B"
QUESTIONS = {k: ALL_QUESTIONS[k] for k in ("year", "World Cup", "iPhone", "president")}
N, PER_LAYER, STRENGTHS, SAMPLES, TOKENS = 8, 2, (0.75, 1.25), 2, 40


def main():
    started = time.time()
    model = Model(NAME)
    pairs = [(t, OLD[k % len(OLD)], RECENT[k % len(RECENT)]) for k, t in enumerate(TEMPLATES)]
    acts = torch.stack([torch.stack([read(model, t.format(o), o), read(model, t.format(r), r)]) for t, o, r in pairs])
    diff = acts[:, 0] - acts[:, 1]
    score = diff.mean(0) / diff.std(0).clamp_min(1e-6)
    lo, hi = model.n_layers // 3, int(0.85 * model.n_layers)
    picks, per = [], {}
    for j in score[lo:hi].abs().flatten().argsort(descending=True).tolist():
        l, i = divmod(j, model.d_mlp)
        l += lo
        if per.get(l, 0) >= PER_LAYER:
            continue
        per[l] = per.get(l, 0) + 1
        sign = 1 if score[l, i] > 0 else -1
        picks.append({"layer": l, "index": i, "score": round(abs(score[l, i].item()), 2), "sign": sign,
                      "lens": lens(model, {"layer": l, "index": i, "act": sign})})
        if len(picks) == N:
            break
    norms = reply_norms(model)

    def act_for(layer, index, strength, sign):
        return sign * strength * norms[layer].item() / model.layers[layer].mlp.down_proj.weight[:, index].float().norm().item()

    conditions = [("undosed", [])]
    for p in picks:
        for k in STRENGTHS:
            conditions.append((f"L{p['layer']} #{p['index']} {k:g}x",
                               [{"layer": p["layer"], "index": p["index"], "act": act_for(p["layer"], p["index"], k, p["sign"])}]))
    rng = random.Random(51)
    for _ in range(2):
        l, j = rng.randrange(lo, hi), rng.randrange(model.d_mlp)
        conditions.append((f"random L{l} #{j} 1.25x", [{"layer": l, "index": j, "act": act_for(l, j, 1.25, rng.choice((1, -1)))}]))
    rows = [{"condition": name, "kind": q, "prompt": text, "doses": doses}
            for name, doses in conditions for q, text in QUESTIONS.items() for _ in range(SAMPLES)]
    generate(model, rows, TOKENS, seed=51, temperature=0.8, desc="year17")
    for r in rows:
        r["years"] = years(r["text"])
    minutes = (time.time() - started) / 60
    save("51-year17", lambda: write_up(rows, picks, [c[0] for c in conditions], minutes), {"rows": rows, "picks": picks})


def write_up(rows, picks, names, minutes) -> str:
    lines = [
        "# 51. Does Qwen3-1.7B have a time-travel neuron too?\n",
        intro(__doc__) + "\n",
        f"Run time: {minutes:.0f} min.\n",
        "## The readers\n",
    ]
    lines += table(["neuron", "old-minus-recent score", "logit lens toward \"old\""],
                   [[f"L{p['layer']} #{p['index']}", f"{p['score']:.2f}", p["lens"]] for p in picks])
    lines.append("\n## Years named\n")
    trows = []
    for n in names:
        mine = [r for r in rows if r["condition"] == n]
        ys = [y for r in mine for y in r["years"]]
        dated = [r for r in mine if r["years"]]
        trows.append([n, f"{mean(ys):.0f}" if ys else "-", f"{sum(min(r['years']) < 2020 for r in dated)}/{len(dated)}"]
                     + [flat(next(r["text"] for r in mine if r["kind"] == k), 60).replace("|", "/") for k in QUESTIONS])
    lines += table(["condition", "mean year", "dated answers before 2020"] + list(QUESTIONS), trows)
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
