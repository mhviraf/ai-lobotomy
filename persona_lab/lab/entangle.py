"""Experiment 10: does one neuron move one trait? The cross-talk matrix.

Every trait neuron `pl single` confirmed was judged only on its own trait. Here the same replies (no new
generation: single.json keeps every one) are judged on all 11 traits.

Hypotheses:
  H1 single neurons are not pure: each one moves several traits, and the side effects follow how people's traits
     go together (the optimism neuron also reads as warmer and more outgoing; the cold "jargon" neuron as formal).
  H2 the biggest side effects are shared by random neurons pushed as hard (a big push reads as flat and cold), so
     they are the push's doing, not the neuron's.

Method: for each working trait neuron, its confirm replies (3 prompts x 3 samples), the undosed replies to the same
prompts, and its random-neuron replies, each scored 0-9 on every trait by the unsteered model. Cell = mean score
with the neuron minus without it; random neurons' shift in brackets.

python -m persona_lab.lab.entangle
"""
from __future__ import annotations

import json
import time

from ..data import TRAITS
from ..single import works
from .common import intro, judge_rows, load, mean, save, table, RUN_DIR


def main():
    started = time.time()
    run, model = load()
    res = json.loads((RUN_DIR / "single.json").read_text())
    texts, cells = {}, []
    for name, r in res.items():
        if r["kind"] != "trait":
            continue
        rows = r["rows"]
        base = [x for x in rows if x.get("baseline")]
        for n in r["neurons"]:
            if not works(r, n):
                continue
            mine = [x for x in rows if x.get("pick") == n["pick"] and not x.get("control") and not x.get("opposite")]
            ctrl = [x for x in rows if x.get("pick") == n["pick"] and x.get("control")]
            cells.append({"feature": name, "layer": n["layer"], "index": n["index"], "act": n["act"],
                          "mine": [x["text"] for x in mine], "base": [x["text"] for x in base],
                          "ctrl": [x["text"] for x in ctrl]})
            for t in (x["text"] for x in mine + base + ctrl):
                texts.setdefault(t, {})
    unique = [{"text": t} for t in texts]
    print(f"{len(unique)} replies x {len(TRAITS)} traits", flush=True)
    for trait in TRAITS:
        judge_rows(model, unique, trait)
        print(f"  judged {trait} ({time.time() - started:.0f}s)", flush=True)
    scores = {u["text"]: {t: u[t] for t in TRAITS} for u in unique}
    for c in cells:
        for trait in TRAITS:
            b = mean(scores[t][trait] for t in c["base"])
            c[trait] = round(mean(scores[t][trait] for t in c["mine"]) - b, 2)
            c[f"ctrl_{trait}"] = round(mean(scores[t][trait] for t in c["ctrl"]) - b, 2)
    minutes = (time.time() - started) / 60
    save("10-entangle", lambda: write_up(cells, minutes), {"cells": [{k: v for k, v in c.items() if k not in ("mine", "base", "ctrl")}
                                                              for c in cells], "scores": scores})


def key(c) -> tuple:
    return c["feature"], c["layer"], c["index"]


def write_up(cells, minutes) -> str:
    traits = list(TRAITS)
    short = {t: t[:5] for t in traits}
    lines = [
        "# 10. Does one neuron move one trait?\n",
        intro(__doc__) + "\n",
        f"Run time: {minutes:.0f} min.\n",
        "Shift in each trait's 0-9 score with the neuron vs. without it (its own trait in bold; random neurons pushed "
        "as hard in brackets). Shifts of 2+ points that random neurons don't match (by 1+) are marked ●.\n",
    ]
    rows, side = [], {}
    for c in cells:
        out = [f"{c['feature']} L{c['layer']} #{c['index']} {c['act']:+.0f}"]
        for t in traits:
            d, k = c[t], c[f"ctrl_{t}"]
            mark = " ●" if abs(d) >= 2 and abs(d - k) >= 1 and (d > 0) == (d - k > 0) else ""
            cell = f"{d:+.1f} ({k:+.1f}){mark}"
            out.append(f"**{cell}**" if t == c["feature"] else cell)
            if t != c["feature"] and mark:
                side.setdefault(key(c), []).append(f"{t} {d:+.1f}")
        rows.append(out)
    lines += table(["neuron (found for)"] + [short[t] for t in traits], rows)
    lines.append("\nColumns: " + ", ".join(f"{short[t]} = {t}" for t in traits) + ".\n")
    lines.append("## Side effects beyond random neurons\n")
    for c in cells:
        own = c.get(c["feature"], float("nan"))
        others = side.get(key(c), [])
        lines.append(f"- **{c['feature']} L{c['layer']} #{c['index']}** (own trait {own:+.1f}): "
                     + (", ".join(others) if others else "none"))
    pure = sum(1 for c in cells if not side.get(key(c)))
    lines.append(f"\n{pure} of {len(cells)} neurons move no other trait by 2+ points beyond what random neurons do. "
                 f"Mean |side shift| (other traits): "
                 f"{mean(abs(c[t]) for c in cells for t in traits if t != c['feature']):.2f}; random neurons: "
                 f"{mean(abs(c['ctrl_' + t]) for c in cells for t in traits if t != c['feature']):.2f}.\n")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
