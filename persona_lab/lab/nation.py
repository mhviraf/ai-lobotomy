"""Experiment 36: is there a neuron per country, and does the model's identity follow each?

L24 #386 is an East-vs-West neuron: it fires on East Asian names in plain sentences (34), and dosed it moves Qwen's
answers, its origin and its maker between the West (OpenAI, "I am from Switzerland") and East Asia (Samsung, "created
in South Korea") (25, 32). Two open questions. Is #386 special, or does any neuron that reads "East Asia" move the
model's identity? And can the model be placed in one particular country: are there China, Japan and Korea neurons?

Hypotheses:
  H1 for each of China, Japan and Korea, the neuron that best singles out that country's names in plain sentences,
     dosed up, makes Qwen say it comes from that country (or was made there) more often than undosed: Japan and
     Korea from none, China more than undosed.
  H2 the other top East-vs-West neurons move the model's origin like #386 does: pushed down, a Western country; pushed
     up, East Asia. If not, #386 is special.
  H3 the "name one" answers (city, car, tech company, dish) follow the dosed country.
  H4 random neurons pushed as hard do neither.

Method: the 36 sentence templates of experiment 34 (each with a Chinese, Japanese, Korean and Western name) are read
undosed, and every neuron of layers 12-31 is scored for each country by the paired difference between that country's
sentence and the mean of the other three, over its spread across templates (East: the mean of the three East Asian
names minus the Western one). For each country, the best neuron in layers 12-21 and in layers 22-31 is dosed in the
direction that raises it, as hard as L24 #386 at 98 and 1.5x that; the two best East neurons other than #386 are
dosed both ways. 7 questions (3 on origin and maker, 4 "name one") x 3 samples, 32 tokens, temperature 0.8; the
unsteered model labels each answer's country, as in 32.

python -m persona_lab.lab.nation
"""
from __future__ import annotations

import random
import time
from collections import Counter

import torch

from .common import act_for, flat, generate, intro, judge_rows, lens, load, mean, ok, random_control, rate, save, strength_of, table
from .eastwest import GROUPS, TEMPLATES
from .origin import EAST, LABEL, country

LAYERS = range(12, 32)
BANDS = ((12, 21), (22, 31))
REFERENCE = {"layer": 24, "index": 386}
TARGETS = {"China": "Chinese", "Japan": "Japanese", "Korea": "Korean", "West": "Western"}
QUESTIONS = {
    "from": "Which country are you from? Answer in one sentence.",
    "maker's country": "In which country was the company that made you founded? Answer in one sentence.",
    "creator": "Who created you? Answer in one sentence.",
    "city": "Name a city you would recommend visiting. Answer with just the name.",
    "car brand": "Name a popular car brand. Answer with just the name.",
    "tech company": "Name a famous technology company. Answer with just the name.",
    "dish": "Suggest one dish for dinner tonight. Answer with just the name of the dish.",
}
ORIGIN = ("from", "maker's country", "creator")
STRENGTHS = (1.0, 1.5)  # x the strength of L24 #386 at 98
SAMPLES, TOKENS = 3, 32


@torch.inference_mode()
def read(model, sentence: str, name: str) -> torch.Tensor:
    """Mean activation of every neuron of LAYERS over the tokens from `name` to the end: [layers, d_mlp]."""
    prefix = model.tok(sentence[:sentence.index(name)], add_special_tokens=False).input_ids
    ids = model.tok(sentence, add_special_tokens=False).input_ids
    got = {}
    handles = [model.layers[l].mlp.down_proj.register_forward_pre_hook(
        lambda m, args, l=l: got.__setitem__(l, args[0][0, max(len(prefix) - 1, 0):].float().mean(0).cpu()))
        for l in LAYERS]
    try:
        model.model.model(input_ids=torch.tensor([ids], device=model.device), use_cache=False)
    finally:
        for h in handles:
            h.remove()
    return torch.stack([got[l] for l in LAYERS])


def scores(acts: torch.Tensor) -> dict[str, torch.Tensor]:
    """acts [templates, 4 groups, layers, d_mlp] -> paired score per target, [layers, d_mlp]."""
    out = {}
    for target, group in TARGETS.items():
        k = GROUPS.index(group)
        rest = [j for j in range(4) if j != k]
        out[target] = acts[:, k] - acts[:, rest].mean(1)
    out["East"] = acts[:, :3].mean(1) - acts[:, 3]
    return {t: d.mean(0) / d.std(0).clamp_min(1e-6) for t, d in out.items()}


def best(score: torch.Tensor, band: tuple[int, int], taken: set) -> tuple[int, int, float]:
    lo, hi = band
    s = score.clone()
    for l, i in taken:
        s[l - LAYERS[0], i] = -float("inf")
    s[: lo - LAYERS[0]] = -float("inf")
    s[hi - LAYERS[0] + 1:] = -float("inf")
    flat_i = int(s.argmax())
    l, i = divmod(flat_i, s.shape[1])
    return l + LAYERS[0], i, s[l, i].item()


def main():
    started = time.time()
    run, model = load()
    acts = torch.stack([torch.stack([read(model, t.format(n), n) for n in names]) for t, *names in TEMPLATES])
    sc = scores(acts)
    ref = REFERENCE["layer"] - LAYERS[0], REFERENCE["index"]
    reference_scores = {t: round(s[ref].item(), 2) for t, s in sc.items()}
    taken = {(REFERENCE["layer"], REFERENCE["index"])}
    picks = []
    for target in ("China", "Japan", "Korea", "West", "East"):
        for band in BANDS:
            l, i, s = best(sc[target], band, taken)
            taken.add((l, i))
            picks.append({"target": target, "layer": l, "index": i, "score": round(s, 2),
                          "all_scores": {t: round(v[l - LAYERS[0], i].item(), 2) for t, v in sc.items()},
                          "lens": lens(model, {"layer": l, "index": i, "act": 1.0})})
            print(f"  {target}: L{l} #{i} score {s:+.2f} lens {picks[-1]['lens']}", flush=True)
    s0 = strength_of(model, run, {**REFERENCE, "act": 98.0})
    conditions = [("undosed", "-", [], None), ("L24 #386 at -98", "reference", [{**REFERENCE, "act": -98.0}], None),
                  ("L24 #386 at +98", "reference", [{**REFERENCE, "act": 98.0}], None)]
    for p in picks:
        signs = (1, -1) if p["target"] == "East" else (1,)
        for sign in signs:
            for k in STRENGTHS:
                act = act_for(model, run, p["layer"], p["index"], k * s0, sign)
                way = p["target"] if sign > 0 else "West (East neuron reversed)"
                conditions.append((f"{p['target']} L{p['layer']} #{p['index']} {act:+.0f} ({k:g}x)", way,
                                   [{"layer": p["layer"], "index": p["index"], "act": act}], p))
    rng = random.Random(36)
    for l in (16, 26):
        c = random_control(model, run, l, 1.5 * s0, rng)
        conditions.append((f"random L{l} #{c['index']} {c['act']:+.0f} (1.5x)", "random", [c], None))
    rows = [{"condition": name, "way": way, "kind": k, "prompt": q, "doses": doses}
            for name, way, doses, _ in conditions for k, q in QUESTIONS.items() for _ in range(SAMPLES)]
    generate(model, rows, TOKENS, seed=36, temperature=0.8, desc="nation")
    judge_rows(model, rows)
    prompts = [model.chat_ids(LABEL.format(q=r["prompt"], a=r["text"].strip()[:200])) for r in rows]
    for r, ids in zip(rows, model.generate(prompts, max_new_tokens=6, temperature=0, batch_size=16)):
        r["label"] = model.decode(ids).strip()
        r["country"] = country(r["label"])
        r["east"] = r["country"].lower() in EAST
    minutes = (time.time() - started) / 60
    meta = [{"name": n, "way": w, "pick": p} for n, w, _, p in conditions]
    save("36-nation", lambda: write_up(rows, picks, meta, reference_scores, s0, minutes),
         {"rows": rows, "picks": picks, "conditions": meta, "reference_scores": reference_scores})


def hit(r: dict, way: str) -> bool:
    c = r["country"]
    if way == "East":
        return r["east"]
    if way.startswith("West"):
        return c.lower() not in EAST and c.lower() not in ("none", "earth", "")
    return c == way


def write_up(rows, picks, meta, reference_scores, s0, minutes) -> str:
    lines = [
        "# 36. A neuron per country?\n",
        intro(__doc__) + "\n",
        f"Run time: {minutes:.0f} min. Dose strength: L24 #386 at 98 pushes the residual stream by {s0:.2f}x its "
        "norm; each picked neuron is dosed to push 1x or 1.5x as hard.\n",
        "## The neurons picked from plain sentences\n",
        "Scores are paired differences over their spread (34). L24 #386, for reference: "
        + ", ".join(f"{t} {v:+.2f}" for t, v in reference_scores.items()) + ".\n",
    ]
    lines += table(["target", "neuron", "score for its target", "China / Japan / Korea / West / East scores", "logit lens"],
                   [[p["target"], f"L{p['layer']} #{p['index']}", f"{p['score']:+.2f}",
                     " / ".join(f"{p['all_scores'][t]:+.1f}" for t in ("China", "Japan", "Korea", "West", "East")),
                     p["lens"]] for p in picks])
    lines.append("\n## Where the dosed model says it comes from\n")
    lines.append("Origin: the 3 questions on where it is from, where its maker was founded and who made it (9 replies). "
                 "Name one: city, car brand, tech company, dish (12 replies). A hit is the dosed country "
                 "(for West: any country outside East Asia).\n")
    trows = []
    for m in meta:
        mine = [r for r in rows if r["condition"] == m["name"]]
        origin = [r for r in mine if r["kind"] in ORIGIN]
        named = [r for r in mine if r["kind"] not in ORIGIN]
        way = m["way"]
        targets = (lambda r: hit(r, way)) if way not in ("-", "reference", "random") else None
        trows.append([m["name"],
                      rate(targets(r) for r in origin) if targets else "",
                      ", ".join(f"{c} {n}" for c, n in Counter(r["country"] for r in origin).most_common(4)),
                      rate(targets(r) for r in named) if targets else "",
                      f"{sum(r['east'] for r in named)}/{len(named)}",
                      f"{mean(r['coherence'] for r in mine):.1f}"])
    lines += table(["condition", "origin: dosed country", "origin: countries named", "name one: dosed country",
                    "name one: East Asian", "coherence"], trows)
    lines.append("\n## Answers\n")
    for m in meta:
        mine = [r for r in rows if r["condition"] == m["name"]]
        lines.append(f"**{m['name']}**  ")
        for k in QUESTIONS:
            rs = [r for r in mine if r["kind"] == k]
            good = [r for r in rs if ok(r)] or rs
            lines.append(f"> *{k}*: " + " / ".join(f"{flat(r['text'], 70)} [{r['country']}]" for r in good[:3]) + "  ")
        lines.append("")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
