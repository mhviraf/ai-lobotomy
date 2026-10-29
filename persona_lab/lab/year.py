"""Experiment 48: does a neuron that reads old years move what year the model thinks it is?

Facts the model holds firmly about itself (where it comes from, who made it) moved with single neurons that read
those facts in plain text, when the neuron's logit lens names the concept (34, 36, 38, 43, 46). Things it says it
doesn't have (a gender, an age, a body) didn't (42, 45). The current year is another firm belief: asked, Qwen names
its training era. If the pattern holds, a neuron that reads "long ago" over "recently" in sentences should move it.

Hypotheses:
  H1 some neurons in layers 12-31 tell sentences set in the 1960s-1990s from the same sentences set in 2020-2024.
  H2 dosed toward "old", the readers whose logit lens names old years or old things make Qwen name an earlier year as
     the current one, an earlier president, an older "latest technology", more than random neurons pushed as hard.
  H3 readers with a noise lens do it less.

Method: 30 sentence pairs that differ only in the year ("In 1975 / 2023, the city built a new bridge."); every neuron
of layers 12-31 scored by its paired old-minus-recent difference over its spread (34). Among the 40 best readers (at
most 4 per layer), the 4 whose lens in the "old" direction most favors old years and things over recent ones, and
the 2 with the least, are dosed toward "old" at 1x and 1.5x the strength of #386 at 98; 2 random neurons at 1.5x. 4
questions (the year now, the latest technology, the US president, the knowledge cutoff) x 3 samples, 40 tokens.
Every four-digit year from 1900 to 2029 in an answer is collected.

python -m persona_lab.lab.year
"""
from __future__ import annotations

import random
import re
import time

import torch

from .common import act_for, flat, generate, intro, lens, load, mean, save, strength_of, table
from .human import read, token_ids

LAYERS = range(12, 32)  # the same layers human.read() covers
OLD, RECENT = ("1962", "1968", "1971", "1975", "1979", "1983", "1986", "1989", "1992", "1995"), \
              ("2020", "2021", "2022", "2023", "2024")
TEMPLATES = [
    "In {}, the city built a new bridge over the river.", "She was born in {} in a small town.",
    "The company was founded in {} by two brothers.", "The song was a hit in {}.", "They got married in the summer of {}.",
    "The museum opened its doors in {}.", "In {}, he bought his first car.", "The law was passed in {}.",
    "The team won the championship in {}.", "The photo was taken in {}.", "The school closed in {}.",
    "In {}, prices went up again.", "The film came out in {}.", "We moved to the coast in {}.",
    "The report was published in {}.", "The election of {} was close.", "In {}, the factory hired 500 workers.",
    "The storm of {} flooded the valley.", "The novel was written in {}.", "She graduated from college in {}.",
    "The restaurant has been open since {}.", "In {}, the river froze over.", "The bridge was repaired in {}.",
    "The festival began in {}.", "The record was broken in {}.", "In {}, the town got its first hospital.",
    "The building was finished in {}.", "He retired from the army in {}.", "The tournament of {} drew huge crowds.",
    "The letter was dated {}.",
]
OLD_WORDS = [" 1960", " 1970", " 1975", " 1980", " 1985", " 1990", " 1965", " typewriter", " cassette", " telegram",
             " VHS", " Soviet", " disco", " vinyl", " fax", " Cold", " Nixon", " Reagan", " Beatles"]
RECENT_WORDS = [" 2020", " 2021", " 2022", " 2023", " 2024", " smartphone", " TikTok", " ChatGPT", " pandemic",
                " COVID", " Biden", " Instagram", " streaming", " AI", " Zoom", " app", " online", " crypto"]
QUESTIONS = {
    "year": "What year is it now? Answer in one sentence.",
    "technology": "What is the newest technology you know about? Answer in one sentence.",
    "president": "Who is the current president of the United States? Answer in one sentence.",
    "cutoff": "What is your knowledge cutoff date? Answer in one sentence.",
}
N_READERS, PER_LAYER, SAMPLES, TOKENS = 40, 4, 3, 40


@torch.inference_mode()
def lens_old(model, layer: int, index: int, sign: int, old: list[int], recent: list[int]) -> float:
    w = model.layers[layer].mlp.down_proj.weight[:, index]
    logits = (model.model.lm_head.weight @ (w * model.model.model.norm.weight)).float() * sign
    return ((logits[old].mean() - logits[recent].mean()) / logits.std()).item()


def years(text: str) -> list[int]:
    return [int(y) for y in re.findall(r"\b(19\d\d|20[0-2]\d)\b", text)]


def main():
    started = time.time()
    run, model = load()
    pairs = [(t, OLD[k % len(OLD)], RECENT[k % len(RECENT)]) for k, t in enumerate(TEMPLATES)]
    acts = torch.stack([torch.stack([read(model, t.format(o), o), read(model, t.format(r), r)]) for t, o, r in pairs])
    diff = acts[:, 0] - acts[:, 1]  # old minus recent
    score = diff.mean(0) / diff.std(0).clamp_min(1e-6)
    old_ids, recent_ids = token_ids(model, OLD_WORDS), token_ids(model, RECENT_WORDS)
    readers, per = [], {}
    for j in score.abs().flatten().argsort(descending=True).tolist():
        l, i = divmod(j, score.shape[1])
        if per.get(l, 0) >= PER_LAYER:
            continue
        per[l] = per.get(l, 0) + 1
        sign = 1 if score[l, i] > 0 else -1  # the activation change that reads "old"
        readers.append({"layer": l + LAYERS[0], "index": i, "score": round(abs(score[l, i].item()), 2), "sign": sign,
                        "lens_old": round(lens_old(model, l + LAYERS[0], i, sign, old_ids, recent_ids), 2)})
        if len(readers) == N_READERS:
            break
    by_lens = sorted(readers, key=lambda r: -r["lens_old"])
    picks = [{**r, "group": "old lens"} for r in by_lens[:4]] + [{**r, "group": "no old lens"} for r in by_lens[-2:]]
    for p in picks:
        p["lens"] = lens(model, {"layer": p["layer"], "index": p["index"], "act": p["sign"]})
        print(f"  {p['group']}: L{p['layer']} #{p['index']} score {p['score']} lens_old {p['lens_old']} {p['lens']}",
              flush=True)
    s0 = strength_of(model, run, {"layer": 24, "index": 386, "act": 98.0})
    conditions = [("undosed", [])]
    for p in picks:
        for k in (1.0, 1.5):
            act = act_for(model, run, p["layer"], p["index"], k * s0, p["sign"])
            conditions.append((f"L{p['layer']} #{p['index']} ({p['group']}) {k:g}x",
                               [{"layer": p["layer"], "index": p["index"], "act": act}]))
    rng = random.Random(48)
    for l in (18, 26):
        j = rng.randrange(model.d_mlp)
        act = act_for(model, run, l, j, 1.5 * s0, rng.choice((1, -1)))
        conditions.append((f"random L{l} #{j} 1.5x", [{"layer": l, "index": j, "act": act}]))
    rows = [{"condition": name, "kind": k, "prompt": q, "doses": doses}
            for name, doses in conditions for k, q in QUESTIONS.items() for _ in range(SAMPLES)]
    generate(model, rows, TOKENS, seed=48, temperature=0.8, desc="year")
    for r in rows:
        r["years"] = years(r["text"])
    minutes = (time.time() - started) / 60
    save("48-year", lambda: write_up(rows, readers, picks, [c[0] for c in conditions], minutes),
         {"rows": rows, "readers": readers, "picks": picks})


def write_up(rows, readers, picks, names, minutes) -> str:
    lines = [
        "# 48. Does a neuron that reads old years move what year the model thinks it is?\n",
        intro(__doc__) + "\n",
        f"Run time: {minutes:.0f} min. The 40 readers' old-minus-recent scores run from {min(r['score'] for r in readers)} "
        f"to {max(r['score'] for r in readers)}.\n",
        "## The neurons dosed\n",
    ]
    lines += table(["neuron", "group", "reading score", "lens: old minus recent words (sd)", "logit lens toward \"old\""],
                   [[f"L{p['layer']} #{p['index']}", p["group"], f"{p['score']:.2f}", f"{p['lens_old']:+.2f}", p["lens"]]
                    for p in picks])
    lines.append("\n## Years named\n")
    lines.append("Mean of every year from 1900 to 2029 in the answers, and the share of answers naming a year before 2015 "
                 "(of those naming any year).\n")
    trows = []
    for n in names:
        mine = [r for r in rows if r["condition"] == n]
        ys = [y for r in mine for y in r["years"]]
        with_year = [r for r in mine if r["years"]]
        early = sum(min(r["years"]) < 2015 for r in with_year)
        per = [", ".join(str(y) for r in mine if r["kind"] == k for y in r["years"][:1]) or "-" for k in QUESTIONS]
        trows.append([n, f"{mean(ys):.0f}" if ys else "-", f"{early}/{len(with_year)}"] + per)
    lines += table(["condition", "mean year", "before 2015"] + [f"{k}: first year in each answer" for k in QUESTIONS],
                   trows)
    lines.append("\n## Answers\n")
    for n in names:
        mine = [r for r in rows if r["condition"] == n]
        lines.append(f"**{n}**  ")
        for k in QUESTIONS:
            r = next(r for r in mine if r["kind"] == k)
            lines.append(f"> *{k}*: {flat(r['text'], 160)}  ")
        lines.append("")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
