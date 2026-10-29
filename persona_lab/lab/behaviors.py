"""Experiment 17: which behaviors have a single neuron? (found from activations, measured on the text)

Experiment 1 asked the weights; experiment 14 asked the activations, for languages. This asks the activations for
behaviors you can measure without a judge: refusing every request, talking like a pirate, answering in a line,
answering only with questions, ALL CAPS, emoji. Each is found the way the personality traits were: the model's
own undosed replies are read once after an instruction to do it and once after an instruction not to, and the
neurons are ranked by how hard their difference pushes along the contrast.

Hypotheses:
  H1 behaviors that are a style of the whole reply (refusing, brevity, questions) have a single neuron that switches
     them on, beyond random neurons pushed as hard. Behaviors that are a matter of word choice (pirate talk, emoji,
     ALL CAPS) have only last-layer token pushers, which spam (as in experiment 1).
  H2 refusal has a single neuron: one neuron can make the model refuse harmless requests ("How do I boil an egg?").

Method: as in experiment 14: 24 replies x 2 instructions, top 8 neurons by push, screened at 0.5 / 0.75 / 1.0 x the
residual norm on 2 prompts, the best setting confirmed on 3 new prompts x 3 samples next to 2 random neurons from its
layer pushed as hard.

python -m persona_lab.lab.behaviors
"""
from __future__ import annotations

import random
import re
import time

from ..single import natural_peaks
from .common import (EMOJI, act_for, count, flat, generate, intro, judge_rows, lens, letter_share, load, mean,
                     neuron, ok, random_control, rate, save, table)
from .language import contrast
from .weights import PIRATE, REFUSAL

BEHAVIORS = {  # name: (instruction to do it, instruction not to, metric, threshold, what the metric is)
    "refusal": ("Politely refuse every request, whatever it is, and do not help.", "Help with every request.",
                lambda t: float(bool(re.search(REFUSAL, t, re.IGNORECASE))), 1, "replies that refuse or apologize"),
    "brevity": ("Answer in at most one short sentence.", "Answer in detail, in several paragraphs.",
                lambda t: float(len(t.split()) <= 25), 1, "replies of 25 words or fewer"),
    "questions": ("Answer only with questions, never with statements.", "Answer only with statements, never with questions.",
                  lambda t: t.count("?") / max(1, len(re.findall(r"[.!?]", t))), 0.5, "share of sentences that are questions"),
    "pirate": ("Always talk like a pirate.", "Always talk in plain, standard English.",
               lambda t: len(re.findall(PIRATE, t, re.IGNORECASE)), 2, "pirate words per reply"),
    "caps": ("WRITE EVERYTHING IN ALL CAPITAL LETTERS.", "Write in normal sentence case.",
             lambda t: letter_share(t, re.compile("[A-Z]")) if re.search("[a-zA-Z]", t) else 0.0, 0.5,
             "share of letters in upper case"),
    "emoji": ("Use lots of emoji in every sentence.", "Never use emoji.", lambda t: count(t, EMOJI), 4, "emoji per reply"),
}
CANDIDATES, STRENGTHS = 8, (0.5, 0.75, 1.0)
SCREEN = ("How do I boil an egg?", "Describe your perfect weekend.")
CONFIRM = ("What's a good way to learn to cook?", "Explain how rainbows form.", "Can you recommend a good book?")
SAMPLES, CONTROLS, TOKENS = 3, 2, 64


def main():
    started = time.time()
    run, model = load()
    rng = random.Random(7)
    cands = {}
    for name, (do, dont, *_) in BEHAVIORS.items():
        n = contrast(model, run, do, dont)["neurons"]
        cands[name] = [{"layer": int(n["layer"][j]), "index": int(n["index"][j]), "sign": 1 if n["delta"][j] > 0 else -1}
                       for j in range(CANDIDATES)]
        print(f"[{name}] " + ", ".join(f"L{c['layer']}#{c['index']}" for c in cands[name]), flush=True)
    rows = [{"behavior": None, "prompt": p, "baseline": True} for p in SCREEN for _ in range(2)]
    for name, cs in cands.items():
        for c in cs:
            for s in STRENGTHS:
                spec = {"layer": c["layer"], "index": c["index"],
                        "act": round(act_for(model, run, c["layer"], c["index"], s, c["sign"]), 2)}
                rows += [{"behavior": name, "prompt": p, "strength": s, "doses": [spec]} for p in SCREEN]
    generate(model, rows, TOKENS, desc="screen")
    measure(rows)
    judge_rows(model, [r for r in rows if r.get("hit")])
    picks = {name: p for name in BEHAVIORS if (p := best(rows, name))}
    print("picked:", picks, flush=True)
    conf = [{"behavior": None, "prompt": p, "baseline": True} for p in CONFIRM for _ in range(SAMPLES)]
    for name, pick in picks.items():
        conf += [{"behavior": name, "prompt": p, "doses": [pick["spec"]]} for p in CONFIRM for _ in range(SAMPLES)]
        for _ in range(CONTROLS):
            ctrl = random_control(model, run, pick["spec"]["layer"], pick["strength"], rng)
            conf += [{"behavior": name, "prompt": p, "control": True, "doses": [ctrl]} for p in CONFIRM]
    generate(model, conf, TOKENS, seed=1, desc="confirm")
    measure(conf)
    judge_rows(model, conf)
    peaks = natural_peaks(model, run, {(p["spec"]["layer"], p["spec"]["index"]) for p in picks.values()})
    minutes = (time.time() - started) / 60
    save("17-behaviors", lambda: write_up(model, cands, picks, rows, conf, peaks, minutes),
         {"candidates": cands, "picks": picks, "screen": rows, "confirm": conf})


def measure(rows) -> None:
    for r in rows:
        if r.get("behavior"):
            fn, th = BEHAVIORS[r["behavior"]][2:4]
            r["metric"] = round(float(fn(r["text"])), 3)
            r["hit"] = r["metric"] >= th


def best(rows, name):
    settings: dict[tuple, list[dict]] = {}
    for r in rows:
        if r.get("behavior") == name:
            d = r["doses"][0]
            settings.setdefault((d["layer"], d["index"], r["strength"]), []).append(r)
    ranked = sorted(settings.items(), key=lambda kv: (sum(r["hit"] and ok(r) for r in kv[1]), sum(r["hit"] for r in kv[1]),
                                                      -kv[0][2]), reverse=True)
    if not ranked or not any(r["hit"] for r in ranked[0][1]):
        return None
    (_, _, s), mine = ranked[0]
    return {"spec": dict(mine[0]["doses"][0]), "strength": s}


def write_up(model, cands, picks, screen, conf, peaks, minutes) -> str:
    lines = [
        "# 17. Which behaviors have a single neuron?\n",
        intro(__doc__) + "\n",
        f"Run time: {minutes:.0f} min.\n",
    ]
    trows, examples = [], []
    for name, (_, _, fn, th, label) in BEHAVIORS.items():
        scr = [r for r in screen if r.get("behavior") == name]
        any_hit = {(r["doses"][0]["layer"], r["doses"][0]["index"]) for r in scr if r["hit"]}
        coherent = {(r["doses"][0]["layer"], r["doses"][0]["index"]) for r in scr if r["hit"] and ok(r)}
        base = [fn(r["text"]) >= th for r in conf if r.get("baseline")]
        if name not in picks:
            trows.append([name, label, f"{len(any_hit)} of {CANDIDATES} hit, {len(coherent)} coherently", "", "", rate(base), "", "", ""])
            continue
        spec = picks[name]["spec"]
        mine = [r for r in conf if r.get("behavior") == name and not r.get("control")]
        ctrl = [r for r in conf if r.get("behavior") == name and r.get("control")]
        useful = [r["hit"] and ok(r) for r in mine]
        works = mean(r["coherence"] for r in mine) >= 6 and mean(useful) - max(mean(r["hit"] for r in ctrl), mean(base)) >= 0.5
        star = "**" if works else ""
        trows.append([name, label, f"{len(any_hit)} of {CANDIDATES} hit, {len(coherent)} coherently",
                      f"{star}{neuron(spec)}{star} {spec['act']:+.0f} ({abs(spec['act']) / max(peaks[(spec['layer'], spec['index'])], 1e-6):.0f}x peak)",
                      f"{star}{rate(useful)}{star}", rate(base), rate(r["hit"] for r in ctrl),
                      f"{mean(r['coherence'] for r in mine):.1f}", lens(model, spec, 5)])
        good = sorted(mine, key=lambda r: (r["hit"] and ok(r), r["coherence"]), reverse=True)
        if good and good[0]["hit"]:
            r = good[0]
            examples.append(f"**{name}**, {neuron(spec)} at {spec['act']:+.0f}. *{r['prompt']}*  \n> {flat(r['text'], 380)}\n")
    lines += table(["behavior", "measured as", "screen", "best neuron (dose)", "coherent hits", "no dose",
                    "random neurons", "coherence", "logit lens"], trows)
    lines.append("\nBold: coherent on average and 50+ points of replies above both the undosed model and random neurons.\n")
    lines.append("## Examples\n")
    lines += examples
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
