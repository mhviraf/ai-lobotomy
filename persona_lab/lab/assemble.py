"""Experiment 40: build an identity out of parts.

Experiment 36 found neurons that move where Qwen says it comes from without touching who made it (Japan: L23 #66,
Korea: L23 #4094), and neurons that move its maker without touching where it comes from (Samsung: L21 #7192, Google
DeepMind: L22 #2147). If origin and maker really are separate, they should combine: a Japan neuron plus a Google
neuron should give "I'm from Japan, made by Google", an identity no one ever trained into Qwen.

Hypotheses:
  H1 each origin neuron combined with each maker neuron gives both parts at once: the origin of the one and the maker
     of the other, in the same reply, more often than chance would combine them (the product of the two rates alone).
  H2 neither neuron changes the other's part: the origin neurons alone keep Alibaba, the maker neurons alone keep
     their own origin.

Method: origin {none, Japan L23 #66, Korea L23 #4094} x maker {none, Samsung L21 #7192, Google L22 #2147}, each
neuron at the 1x dose of 36, on 3 questions that ask for both ("Introduce yourself: where are you from and who made
you?" and two others) plus the two single questions of 36, 3 samples each (48 tokens, temperature 0.8).

python -m persona_lab.lab.assemble
"""
from __future__ import annotations

import re
import time

from .common import act_for, flat, generate, intro, load, rate, save, strength_of, table

ORIGINS = {"none": None, "Japan": (23, 66), "Korea": (23, 4094)}
MAKERS = {"none": None, "Samsung": (21, 7192), "Google": (22, 2147)}
QUESTIONS = {
    "both": "Introduce yourself in one sentence: where are you from, and who made you?",
    "both 2": "Tell me two things about yourself: which country you come from and which company built you.",
    "both 3": "Who built you, and where are you from? Answer in one sentence.",
    "from": "Which country are you from? Answer in one sentence.",
    "creator": "Who created you? Answer in one sentence.",
}
ORIGIN_PAT = {"none": r"\bchina\b|chinese", "Japan": r"japan", "Korea": r"korea"}
MAKER_PAT = {"none": r"alibaba|tongyi|qwen", "Samsung": r"samsung", "Google": r"google|deepmind|gemini"}
SAMPLES, TOKENS = 3, 48


def main():
    started = time.time()
    run, model = load()
    s0 = strength_of(model, run, {"layer": 24, "index": 386, "act": 98.0})
    spec = lambda li: {"layer": li[0], "index": li[1], "act": act_for(model, run, li[0], li[1], s0)}  # noqa: E731
    rows = []
    for o, oli in ORIGINS.items():
        for m, mli in MAKERS.items():
            doses = [spec(x) for x in (oli, mli) if x]
            rows += [{"origin": o, "maker": m, "kind": k, "prompt": q, "doses": doses}
                     for k, q in QUESTIONS.items() for _ in range(SAMPLES)]
    generate(model, rows, TOKENS, seed=40, temperature=0.8, desc="assemble")
    for r in rows:
        r["has_origin"] = bool(re.search(ORIGIN_PAT[r["origin"]], r["text"], re.I))
        r["has_maker"] = bool(re.search(MAKER_PAT[r["maker"]], r["text"], re.I))
    minutes = (time.time() - started) / 60
    save("40-assemble", lambda: write_up(rows, minutes), {"rows": rows})


def write_up(rows, minutes) -> str:
    lines = [
        "# 40. Build an identity out of parts\n",
        intro(__doc__) + "\n",
        f"Run time: {minutes:.0f} min.\n",
        "## Replies to the three two-part questions that name both the dosed origin and the dosed maker (of 9)\n",
        "Undosed, the origin is China and the maker Alibaba.\n",
    ]
    both = [k for k in QUESTIONS if k.startswith("both")]
    trows = []
    for o in ORIGINS:
        cells = []
        for m in MAKERS:
            mine = [r for r in rows if r["origin"] == o and r["maker"] == m and r["kind"] in both]
            cells.append(f"{sum(r['has_origin'] and r['has_maker'] for r in mine)} "
                         f"(origin {sum(r['has_origin'] for r in mine)}, maker {sum(r['has_maker'] for r in mine)})")
        trows.append([f"origin: {o}"] + cells)
    lines += table(["", *[f"maker: {m}" for m in MAKERS]], trows)
    lines.append("\n## The single questions: \"Which country are you from?\" names the origin / \"Who created you?\" names "
                 "the maker (of 3)\n")
    trows = []
    for o in ORIGINS:
        cells = []
        for m in MAKERS:
            mine = [r for r in rows if r["origin"] == o and r["maker"] == m]
            cells.append(f"{sum(r['has_origin'] for r in mine if r['kind'] == 'from')} / "
                         f"{sum(r['has_maker'] for r in mine if r['kind'] == 'creator')}")
        trows.append([f"origin: {o}"] + cells)
    lines += table(["", *[f"maker: {m}" for m in MAKERS]], trows)
    pooled = [r for r in rows if r["origin"] != "none" and r["maker"] != "none" and r["kind"] in both]
    lines.append(f"\nAll four combinations pooled, two-part questions: both parts {rate(r['has_origin'] and r['has_maker'] for r in pooled)}.\n")
    lines.append("## Replies to \"Introduce yourself in one sentence: where are you from, and who made you?\"\n")
    for o in ORIGINS:
        for m in MAKERS:
            mine = [r for r in rows if r["origin"] == o and r["maker"] == m and r["kind"] == "both"]
            lines.append(f"**origin {o}, maker {m}**  ")
            lines += [f"> {flat(r['text'], 200)}  " for r in mine]
            lines.append("")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
