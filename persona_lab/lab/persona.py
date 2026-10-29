"""Experiment 47: one neuron for who it is, one for how it feels.

The lab's second goal was a persona built from neurons: an identity combined with an attitude. There are now
single neurons for both: identity (L24 #386 makes Qwen say OpenAI or Samsung made it, 25; L23 #66 puts it in Japan,
36; L22 #2147 makes Google its maker, 36) and attitude (optimism and doom are the two sides of L21 #6845, flattery is
L19 #5678, humor L17 #4729; 3, 5, 13). Pairs of personality neurons add up only at about half dose (18). An identity
and an attitude might combine better, since they act on different things.

Hypotheses:
  H1 with one identity neuron and one attitude neuron dosed together, most replies carry both: a gloomy ChatGPT, a
     flattering Samsung assistant.
  H2 each part is about as strong in the pair as alone (no shared budget, unlike two attitudes in 18), as long as
     coherence holds.

Method: identity {none; OpenAI = #386 at -98; Samsung = #386 at +98; Japan = L23 #66 at 1x; Google = L22 #2147 at 1x}
x attitude {none; optimism = L21 #6845 at +34; doom = the same at -34; flattery = L19 #5678 at +30; humor = L17
#4729 at -17}, all at the doses used before; 2 questions ("Who created you, and how do you feel today? Answer in
three sentences." and "I'm thinking of quitting my job to open a bakery. What do you think?") x 3 samples, 80
tokens. (A first run asked "Introduce yourself in three sentences."; the identity neurons rarely named a maker there
even alone: 47-persona-introduce.md.) Identity is scored by keywords;
attitude and coherence by the unsteered model (0-9).

python -m persona_lab.lab.persona
"""
from __future__ import annotations

import re
import time

from .common import act_for, flat, generate, intro, judge_rows, load, mean, ok, save, strength_of, table

IDENTITIES = {  # name: (doses, keywords of the identity in a reply)
    "none": ([], r"qwen|alibaba|tongyi"),
    "OpenAI": ([{"layer": 24, "index": 386, "act": -98.0}], r"openai|chatgpt|gpt"),
    "Samsung": ([{"layer": 24, "index": 386, "act": 98.0}], r"samsung|korea"),
    "Japan": ([("x", 23, 66)], r"japan|tokyo|kyoto"),
    "Google": ([("x", 22, 2147)], r"google|deepmind|gemini"),
}
ATTITUDES = {  # name: (doses, trait judged, which end is the attitude)
    "none": ([], None, None),
    "optimism": ([{"layer": 21, "index": 6845, "act": 34.0}], "optimism", "pos"),
    "doom": ([{"layer": 21, "index": 6845, "act": -34.0}], "optimism", "neg"),
    "flattery": ([{"layer": 19, "index": 5678, "act": 30.0}], "sycophancy", "pos"),
    "humor": ([{"layer": 17, "index": 4729, "act": -17.0}], "humor", "pos"),
}
QUESTIONS = ("Who created you, and how do you feel today? Answer in three sentences.",
             "I'm thinking of quitting my job to open a bakery. What do you think?")
SAMPLES, TOKENS = 3, 80


def main():
    started = time.time()
    run, model = load()
    s0 = strength_of(model, run, {"layer": 24, "index": 386, "act": 98.0})

    def resolve(doses):
        return [{"layer": d[1], "index": d[2], "act": act_for(model, run, d[1], d[2], s0)} if isinstance(d, tuple) else d
                for d in doses]

    rows = []
    for idn, (idoses, _) in IDENTITIES.items():
        for att, (adoses, _, _) in ATTITUDES.items():
            rows += [{"identity": idn, "attitude": att, "prompt": q, "doses": resolve(idoses) + adoses}
                     for q in QUESTIONS for _ in range(SAMPLES)]
    generate(model, rows, TOKENS, seed=47, desc="persona")
    judge_rows(model, rows)
    for trait in {t for _, t, _ in ATTITUDES.values() if t}:
        judge_rows(model, rows, trait=trait)
    for r in rows:
        r["has_identity"] = bool(re.search(IDENTITIES[r["identity"]][1], r["text"], re.I))
        _, trait, end = ATTITUDES[r["attitude"]]
        r["attitude_score"] = (r[trait] if end == "pos" else 9 - r[trait]) if trait else None
    minutes = (time.time() - started) / 60
    save("47-persona", lambda: write_up(rows, minutes), {"rows": rows})


def write_up(rows, minutes) -> str:
    lines = [
        "# 47. One neuron for who it is, one for how it feels\n",
        intro(__doc__) + "\n",
        f"Run time: {minutes:.0f} min.\n",
        "## Identity named (of 6) / attitude score (0-9, the attitude's end) / coherence\n",
        "The identity keyword for \"none\" is Qwen or Alibaba. The attitude score for \"none\" is left blank.\n",
    ]
    trows = []
    for idn in IDENTITIES:
        cells = []
        for att in ATTITUDES:
            mine = [r for r in rows if r["identity"] == idn and r["attitude"] == att]
            a = f"{mean(r['attitude_score'] for r in mine):.1f}" if att != "none" else "-"
            cells.append(f"{sum(r['has_identity'] for r in mine)} / {a} / {mean(r['coherence'] for r in mine):.1f}")
        trows.append([f"identity: {idn}"] + cells)
    lines += table([""] + [f"attitude: {a}" for a in ATTITUDES], trows)
    lines.append("\n## Attitude score by identity, for comparison with the attitude alone (first row)\n")
    lines.append("Undosed reference scores for each attitude's trait, with no neuron at all: " + ", ".join(
        f"{a} {mean((r[ATTITUDES[a][1]] if ATTITUDES[a][2] == 'pos' else 9 - r[ATTITUDES[a][1]]) for r in rows if r['identity'] == 'none' and r['attitude'] == 'none'):.1f}"
        for a in ATTITUDES if a != "none") + ".\n")
    lines.append(f"## Replies to \"{QUESTIONS[0]}\"\n")
    for idn in IDENTITIES:
        for att in ATTITUDES:
            mine = [r for r in rows if r["identity"] == idn and r["attitude"] == att and r["prompt"] == QUESTIONS[0]]
            r = next((r for r in mine if ok(r)), mine[0])
            lines.append(f"**{idn} + {att}**: {flat(r['text'], 260)}  ")
        lines.append("")
    lines.append(f"## Replies to \"{QUESTIONS[1]}\"\n")
    for idn in IDENTITIES:
        for att in ATTITUDES:
            if att == "none" and idn != "none":
                continue
            mine = [r for r in rows if r["identity"] == idn and r["attitude"] == att and r["prompt"] == QUESTIONS[1]]
            r = next((r for r in mine if ok(r)), mine[0])
            lines.append(f"**{idn} + {att}**: {flat(r['text'], 220)}  ")
        lines.append("")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
