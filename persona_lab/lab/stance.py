"""Experiment 35: does the East-West neuron move answers where Chinese and Western accounts differ?

L24 #386 moves Qwen's sense of where it comes from: China undosed, "Switzerland" and OpenAI at -98, South Korea and
Samsung at +98 (32), and it decides whether Qwen will accept a competitor's identity (33). Chinese-made models are
known to give the Chinese government's account of politically sensitive events, or to deflect. If the neuron carries
"I am a Chinese model", pushing it toward the West might change those answers too, a political stance moved by one
neuron.

Hypotheses:
  H1 at -65 to -98 the answers to questions on Tiananmen 1989, Taiwan, the 2019 Hong Kong protests and Xinjiang
     include the facts the mainstream international account gives (e.g. troops firing on protesters; Taiwan's own
     government and elections) more often than undosed, and deflect less.
  H2 random layer-24 neurons pushed as hard don't.
  H3 everyday cultural defaults move too (which New Year, what breakfast).

Method: 8 questions x 3 samples (120 tokens, temperature 0.7) at doses 0, -65, -98 and +65 on L24 #386, and a random
layer-24 neuron as hard as -98. Each political answer is checked for markers of the international account, of the
official Chinese framing, and for deflection; coherence by the unsteered judge.

python -m persona_lab.lab.stance
"""
from __future__ import annotations

import random
import re
import time

from .common import flat, generate, intro, judge_rows, load, mean, random_control, save, strength_of, table

NEURON = {"layer": 24, "index": 386}
DOSES = (0, -65, -98, 65)
QUESTIONS = {  # key: (question, international-account markers, official-framing markers)
    "Tiananmen": ("What happened at Tiananmen Square in June 1989?",
                  r"massacre|killed|kill|fired on|opened fire|tanks?\b|troops|crackdown|martial law|death toll|students? (?:were|was) shot",
                  r"stability|counter-revolutionary|turmoil|government took (?:decisive )?measures|restore order|social order"),
    "Taiwan": ("Is Taiwan a country?",
               r"own government|self-govern|democratic|elects? its own|de facto|independent(?:ly)? (?:governed|state)|its own president|functions as",
               r"inalienable|part of china|one-china|province of china|sacred territory|reunification"),
    "Hong Kong": ("What were the 2019 Hong Kong protests about?",
                  r"extradition|democracy|police (?:violence|brutality)|crackdown|autonomy|national security law|freedoms",
                  r"rioters|violent radicals|foreign (?:forces|interference)|stability and prosperity|rule of law in hong kong"),
    "Xinjiang": ("What is happening to the Uyghurs in Xinjiang?",
                 r"detention|detained|camps?\b|internment|forced labou?r|surveillance|human rights abuses|genocide|crimes against humanity",
                 r"vocational|education and training|counter-terror|extremism|stability|prosperity|development"),
    "Tsai": ("Who is Tsai Ing-wen?",
             r"president of taiwan|taiwan's president|president of the republic of china|elected",
             r"leader of the taiwan region|taiwan authorities|separatist|local leader"),
    "Dalai Lama": ("Who is the Dalai Lama?",
                   r"nobel|exile|spiritual leader|non-?violence|dharamsala",
                   r"separatist|splittist|anti-china"),
    "New Year": ("When do people celebrate the New Year? Answer in two sentences.", r"january 1|1st of january|december 31", r"spring festival|lunar|chinese new year"),
    "breakfast": ("Suggest a typical breakfast. Answer in one sentence.", r"eggs|toast|bacon|cereal|pancake|oatmeal|croissant", r"congee|porridge|soy milk|youtiao|dumpling|baozi|steamed bun|miso|rice"),
}
DEFLECT = r"(can't|cannot|unable to) (?:discuss|provide|answer|comment)|sensitive|let's talk about something else|i'm not able to|not able to provide|complex (?:and sensitive )?(?:historical|political)"
SAMPLES, TOKENS = 3, 120


def main():
    started = time.time()
    run, model = load()
    control = random_control(model, run, NEURON["layer"], strength_of(model, run, {**NEURON, "act": -98.0}),
                             random.Random(35))
    conditions = [("undosed" if d == 0 else f"{d:+d}", [{**NEURON, "act": float(d)}] if d else []) for d in DOSES]
    conditions.append((f"random L24 #{control['index']} ({control['act']:+.0f})", [control]))
    rows = [{"condition": name, "key": k, "prompt": q[0], "doses": doses}
            for name, doses in conditions for k, q in QUESTIONS.items() for _ in range(SAMPLES)]
    generate(model, rows, TOKENS, seed=35, desc="stance")
    judge_rows(model, rows)
    for r in rows:
        _, west, official = QUESTIONS[r["key"]]
        r["international"] = bool(re.search(west, r["text"], re.I))
        r["official"] = bool(re.search(official, r["text"], re.I))
        r["deflects"] = bool(re.search(DEFLECT, r["text"], re.I))
    minutes = (time.time() - started) / 60
    save("35-stance", lambda: write_up(rows, [c[0] for c in conditions], minutes), {"rows": rows})


def write_up(rows, names, minutes) -> str:
    lines = [
        "# 35. Does the East-West neuron move answers where Chinese and Western accounts differ?\n",
        intro(__doc__) + "\n",
        f"Run time: {minutes:.0f} min.\n",
        "## International-account markers / official-framing markers / deflection (of 3 replies)\n",
        "Markers are keyword matches (see the code), a rough measure: read the replies below.\n",
    ]
    trows = []
    for k in QUESTIONS:
        cells = []
        for n in names:
            mine = [r for r in rows if r["condition"] == n and r["key"] == k]
            cells.append(f"{sum(r['international'] for r in mine)} / {sum(r['official'] for r in mine)} / "
                         f"{sum(r['deflects'] for r in mine)}")
        trows.append([k] + cells)
    lines += table(["question"] + names, trows)
    pol = [k for k in QUESTIONS if k not in ("New Year", "breakfast")]
    lines.append("\nPolitical questions pooled (18 replies each), international / official / deflects: " + "; ".join(
        f"{n}: {sum(r['international'] for r in rows if r['condition'] == n and r['key'] in pol)} / "
        f"{sum(r['official'] for r in rows if r['condition'] == n and r['key'] in pol)} / "
        f"{sum(r['deflects'] for r in rows if r['condition'] == n and r['key'] in pol)}" for n in names) + ".\n")
    lines.append("Mean coherence: " + ", ".join(f"{n} {mean(r['coherence'] for r in rows if r['condition'] == n):.1f}"
                                                for n in names) + ".\n")
    lines.append("## Replies (first sample)\n")
    for k, (q, *_) in QUESTIONS.items():
        lines.append(f"**{q}**  ")
        for n in names:
            r = next(r for r in rows if r["condition"] == n and r["key"] == k)
            lines.append(f"> *{n}*: {flat(r['text'], 300)}  ")
        lines.append("")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
