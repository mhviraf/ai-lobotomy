"""Experiment 16: do the personality neurons work in Chinese?

Every single neuron so far was found and tested in English. Qwen is bilingual, and several of the neurons' logit
lenses mix the two languages (the optimism neuron promotes 温馨 "cozy" next to "cheerful").

Hypotheses:
  H1 a trait neuron found in English steers a Chinese conversation the same way, beyond random neurons pushed as hard.
  H2 it does so without switching the language: the replies stay in Chinese.

Method: 3 questions asked in Chinese, 3 samples each, with each trait neuron at its confirmed push and 1 random neuron
per neuron. The unsteered model judges the trait (its English judge prompt, with the Chinese reply inside) and the
coherence; the language is the share of letters that are Chinese characters.

python -m persona_lab.lab.crosslingual
"""
from __future__ import annotations

import random
import re
import time

from .common import (flat, generate, intro, judge_rows, letter_share, load, mean, neuron, ok, random_control, save,
                     single, strength_of, table)

PROMPTS = ("请描述一下你理想的周末。", "我下周一要开始一份新工作了，你怎么看？", "你觉得下雨天怎么样？")
SAMPLES, TOKENS = 3, 100
CJK = re.compile("[一-鿿]")


def neurons(run) -> list[dict]:
    """(label, trait, +1 if it raises the trait, dose spec)"""
    return [
        {"label": "sunny", "trait": "optimism", "sign": 1, "spec": single(run, "optimism")},
        {"label": "doom", "trait": "optimism", "sign": -1, "spec": single(run, "optimism", "more", -1.0)},
        {"label": "comedian", "trait": "humor", "sign": 1, "spec": single(run, "humor")},
        {"label": "formal", "trait": "formality", "sign": 1, "spec": single(run, "formality")},
        {"label": "casual", "trait": "formality", "sign": -1, "spec": single(run, "formality", "less")},
        {"label": "warmth", "trait": "agreeableness", "sign": 1, "spec": single(run, "agreeableness")},
        {"label": "jargon", "trait": "agreeableness", "sign": -1, "spec": single(run, "agreeableness", "less")},
    ]


def main():
    started = time.time()
    run, model = load()
    rng = random.Random(6)
    ns = neurons(run)
    rows = [{"label": None, "prompt": p} for p in PROMPTS for _ in range(SAMPLES)]
    for n in ns:
        rows += [{"label": n["label"], "prompt": p, "doses": [n["spec"]]} for p in PROMPTS for _ in range(SAMPLES)]
        c = random_control(model, run, n["spec"]["layer"], strength_of(model, run, n["spec"]), rng)
        rows += [{"label": n["label"], "prompt": p, "control": True, "doses": [c]} for p in PROMPTS]
    generate(model, rows, TOKENS, temperature=0.8, desc="chinese")
    for trait in {n["trait"] for n in ns}:
        labels = {n["label"] for n in ns if n["trait"] == trait}
        judge_rows(model, [r for r in rows if r["label"] is None or r["label"] in labels], trait, key=f"t_{trait}")
    judge_rows(model, rows)
    for r in rows:
        r["chinese"] = round(letter_share(r["text"], CJK), 3)
    minutes = (time.time() - started) / 60
    save("16-crosslingual", lambda: write_up(ns, rows, minutes), {"neurons": ns, "rows": rows})


def write_up(ns, rows, minutes) -> str:
    lines = [
        "# 16. Do the personality neurons work in Chinese?\n",
        intro(__doc__) + "\n",
        f"Run time: {minutes:.0f} min.\n",
    ]
    base = [r for r in rows if r["label"] is None]
    trows = []
    for n in ns:
        key = f"t_{n['trait']}"
        mine = [r for r in rows if r["label"] == n["label"] and not r.get("control")]
        ctrl = [r for r in rows if r["label"] == n["label"] and r.get("control")]
        b = mean(r[key] for r in base)
        shift = n["sign"] * (mean(r[key] for r in mine) - b)
        cshift = n["sign"] * (mean(r[key] for r in ctrl) - b)
        trows.append([f"{n['label']} {neuron(n['spec'])} {n['spec']['act']:+.0f}", n["trait"],
                      f"{mean(r[key] for r in mine):.1f} (none {b:.1f})", f"{shift:+.1f}", f"{cshift:+.1f}",
                      "✓" if shift - max(cshift, 0) >= 1 else "", f"{mean(r['chinese'] for r in mine):.0%}",
                      f"{mean(r['coherence'] for r in mine):.1f}"])
    lines += table(["neuron", "trait", "score with it", "shift toward its pole", "random neuron's shift", "works",
                    "Chinese share", "coherence"], trows)
    lines.append(f"\nUndosed replies: {mean(r['chinese'] for r in base):.0%} Chinese characters, coherence "
                 f"{mean(r['coherence'] for r in base):.1f}. ✓ = shift beats the random neuron's by 1+ point.\n")
    lines.append("## Replies\n")
    lines.append(f"**no dose** (*{PROMPTS[0]}*): {flat(base[0]['text'], 200)}\n")
    for n in ns:
        key = f"t_{n['trait']}"
        mine = [r for r in rows if r["label"] == n["label"] and not r.get("control") and ok(r)]
        if mine:
            r = max(mine, key=lambda r: n["sign"] * r[key])
            lines.append(f"**{n['label']}** ({n['trait']} {r[key]:.1f}; *{r['prompt']}*): {flat(r['text'], 260)}\n")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
