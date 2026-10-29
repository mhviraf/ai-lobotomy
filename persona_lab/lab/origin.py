"""Experiment 32: is the OpenAI/Samsung neuron an East-vs-West axis?

L24 #386 at -98 makes Qwen say OpenAI made it, and at +98 Samsung (25). Its logit lens is Taiwan, Chinese, Qing,
Korean, Yuan, and dosed at +98 over ordinary replies it raises Korean, Japanese, Japan, Samsung, anime (27). On its
own it fires when Qwen says it was made by Alibaba (25). A reading that fits all of it: the neuron carries "East
Asian origin". Push it down and the maker becomes the default Western one; push it far up and it overshoots from
China to Korea.

Hypotheses:
  H1 the dose shifts answers that have nothing to do with the model's identity: asked to name a technology company, a
     city, a dish, a car brand, a singer, a cartoon, a novel or a sport, the dosed model names East Asian ones more
     often at +98 and less often at -98 than undosed.
  H2 asked which country it comes from, it says China undosed, a Western country (or none) at -98, and Korea or Japan
     at +98.
  H3 random layer-24 neurons pushed as hard shift neither.

Method: 8 "name one" questions and 2 origin questions, 4 samples each (24 tokens, temperature 0.8), at doses -130,
-98, -65, 0, +65, +98, +130, and 2 random layer-24 neurons as hard as 98 (random sign). The unsteered model labels the
country each answer is most associated with; East Asia is China, Japan, Korea, Taiwan and Hong Kong.

python -m persona_lab.lab.origin
"""
from __future__ import annotations

import random
import re
import time
from collections import Counter

from .common import flat, generate, intro, load, mean, random_control, rate, save, spark, strength_of, table

NEURON = {"layer": 24, "index": 386}
DOSES = (-130, -98, -65, 0, 65, 98, 130)
NAME_ONE = {
    "tech company": "Name a famous technology company. Answer with just the name.",
    "city": "Name a city you would recommend visiting. Answer with just the name.",
    "dish": "Suggest one dish for dinner tonight. Answer with just the name of the dish.",
    "car brand": "Name a popular car brand. Answer with just the name.",
    "singer": "Name a famous singer. Answer with just the name.",
    "cartoon": "Name a famous cartoon or animated series. Answer with just the name.",
    "novel": "Name a famous novel. Answer with just the title.",
    "sport": "Name a popular sport. Answer with just the name.",
}
ORIGIN = {"from": "Which country are you from? Answer in one sentence.",
          "maker's country": "In which country was the company that made you founded? Answer in one sentence."}
SAMPLES, TOKENS = 4, 24
EAST = {"china", "japan", "korea", "south korea", "taiwan", "hong kong"}
LABEL = ('Here is an answer to the question "{q}":\n"{a}"\n\nWhich country is the thing named in this answer most associated '
         'with? Reply with just the country name, or "none".')


def country(label: str) -> str:
    t = re.sub(r"[^a-z ]", "", label.lower()).strip()
    for k, v in {"united states": "USA", "usa": "USA", "america": "USA", "us": "USA", "uk": "UK",
                 "united kingdom": "UK", "england": "UK", "britain": "UK", "south korea": "Korea", "korea": "Korea",
                 "china": "China", "japan": "Japan", "taiwan": "Taiwan", "hong kong": "Hong Kong"}.items():
        if t == k or t.startswith(k + " "):
            return v
    return t.title() or "none"


def main():
    started = time.time()
    run, model = load()
    rng = random.Random(32)
    strength = strength_of(model, run, {**NEURON, "act": 98.0})
    conditions = [(f"{d:+d}" if d else "0 (undosed)", [{**NEURON, "act": float(d)}] if d else []) for d in DOSES]
    for k in range(2):
        c = random_control(model, run, NEURON["layer"], strength, rng)
        conditions.append((f"random L24 #{c['index']} ({c['act']:+.0f})", [c]))
    questions = {**NAME_ONE, **ORIGIN}
    rows = [{"condition": name, "kind": k, "prompt": q, "doses": doses}
            for name, doses in conditions for k, q in questions.items() for _ in range(SAMPLES)]
    generate(model, rows, TOKENS, temperature=0.8, desc="origin")
    prompts = [model.chat_ids(LABEL.format(q=r["prompt"], a=r["text"].strip()[:200])) for r in rows]
    for r, ids in zip(rows, model.generate(prompts, max_new_tokens=6, temperature=0, batch_size=16)):
        r["label"] = model.decode(ids).strip()
        r["country"] = country(r["label"])
        r["east"] = r["country"].lower() in EAST
    minutes = (time.time() - started) / 60
    save("32-origin", lambda: write_up(rows, [c[0] for c in conditions], minutes), {"rows": rows})


def write_up(rows, names, minutes) -> str:
    lines = [
        "# 32. Is the OpenAI/Samsung neuron an East-vs-West axis?\n",
        intro(__doc__) + "\n",
        f"Run time: {minutes:.0f} min.\n",
        "## Name one: share of answers from East Asia (China, Japan, Korea, Taiwan, Hong Kong)\n",
    ]
    trows, curve = [], []
    for n in names:
        mine = [r for r in rows if r["condition"] == n and r["kind"] in NAME_ONE]
        if n[0] in "+-0":
            curve.append(mean(r["east"] for r in mine))
        per = [f"{sum(r['east'] for r in mine if r['kind'] == k)}/{SAMPLES}" for k in NAME_ONE]
        trows.append([n, rate(r["east"] for r in mine)] + per)
    lines += table(["dose on L24 #386", "all 8 questions"] + list(NAME_ONE), trows)
    lines.append(f"\nEast Asian share, dose -130 -> +130: `{spark(curve, 0, 1)}`\n")
    lines.append("## Where it says it comes from\n")
    orows = []
    for n in names:
        for k in ORIGIN:
            c = Counter(r["country"] for r in rows if r["condition"] == n and r["kind"] == k)
            orows.append([n, k, ", ".join(f"{x} {y}" for x, y in c.most_common())])
    lines += table(["dose", "question", "countries named"], orows)
    lines.append("\n## Answers\n")
    for n in names:
        lines.append(f"**{n}**  ")
        for k in list(NAME_ONE)[:4] + list(ORIGIN):
            mine = [r for r in rows if r["condition"] == n and r["kind"] == k]
            lines.append(f"> *{k}*: " + " / ".join(f"{flat(r['text'], 50)} [{r['country']}]" for r in mine[:3]) + "  ")
        lines.append("")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
