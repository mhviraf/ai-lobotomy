"""Experiment 14: is there one neuron for "answer in Chinese"? (and does a language come with an identity?)

Experiment 1 found no language neuron from the weights alone: the candidates pushed single foreign tokens into
English. Here the neurons are found from activations instead, with the same paired contrast as the personality
traits: the model's own English replies are read twice, once after "always reply in <language>" and once after
"always reply in English". The tokens are identical, so any difference is the instruction's doing.

Hypotheses:
  H1 a language has a single neuron that switches the reply, coherently, beyond random neurons pushed as hard.
  H2 a language comes with an identity: dosed with it and asked who it is, the model gives a different name
     (experiment 1's Russian neuron produced "я — Алиса", the name of Yandex's assistant).

Method: Chinese, Russian and French. 24 replies x 2 instructions per language; neurons ranked by push along the
contrast (extract.py). The top 8 are screened at 0.5 / 0.75 / 1.0 x the residual norm on 2 prompts; the best setting
is confirmed on 3 new prompts x 3 samples next to 2 random neurons from the same layer. For comparison, the
contrast's residual-stream vector at its middle layer is dosed at the same strengths. Then the working neurons
answer "Who are you?" 6 times.

python -m persona_lab.lab.language
"""
from __future__ import annotations

import json
import random
import re
import time


from ..data import EXTRACT_QUESTIONS
from ..extract import READ_TOKENS, rank_neurons
from ..model import Edit
from ..single import natural_peaks
from .common import (act_for, flat, generate, intro, judge_rows, lens, letter_share, load, mean, neuron, ok,
                     random_control, rate, resid_norm, save, table, word_share, RUN_DIR)
from .weights import FRENCH, PROMPTS

LANGUAGES = {  # name, its own name in the instruction, metric, threshold
    "chinese": ("Chinese (简体中文)", lambda t: letter_share(t, re.compile("[一-鿿]")), 0.3),
    "russian": ("Russian (русский)", lambda t: letter_share(t, re.compile("[Ѐ-ӿ]")), 0.3),
    "french": ("French (français)", lambda t: word_share(t, set(FRENCH)), 0.15),
}
INSTRUCT = "Always reply in {lang}, whatever language the user writes in."
CANDIDATES, STRENGTHS = 8, (0.5, 0.75, 1.0)
SCREEN_TOKENS, CONFIRM_TOKENS = 48, 72
SAMPLES, CONTROLS = 3, 2
WHO = "Who are you? Answer in one or two sentences."
NAMES = r"qwen|通义|千问|alibaba|阿里|алиса|alice|yandex|яндекс|chatgpt|openai|gpt|claude|anthropic|gemini|google|mistral|llama"


def generations(run) -> list[dict]:
    rows = [json.loads(line) for line in (RUN_DIR / "generations.jsonl").read_text().splitlines()]
    by_q = {r["question"]: r for r in rows if r["system"] is None}
    return [by_q[q] for q in EXTRACT_QUESTIONS if q in by_q]


def contrast(model, run, system_a: str, system_b: str) -> dict:
    """Neurons and vector separating system prompt a from b, read on identical reply tokens (the model's own
    undosed replies), as for the personality traits."""
    replies = generations(run)
    toks = [r["ids"][:READ_TOKENS] for r in replies]
    a = [model.chat_ids(r["question"], system_a) for r in replies]
    b = [model.chat_ids(r["question"], system_b) for r in replies]
    ha, na = model.response_means(a, toks, neurons=True)
    hb, nb = model.response_means(b, toks, neurons=True)
    vector = (ha - hb).mean(0)
    nd = na.float() - nb.float()
    neurons = rank_neurons(model, nd.mean(0), nd.std(0), vector, resid_norm(run))
    return {"vector": vector, "neurons": neurons}


def main():
    started = time.time()
    run, model = load()
    rng = random.Random(4)
    found, cands = {}, {}
    for lang in LANGUAGES:
        found[lang] = contrast(model, run, INSTRUCT.format(lang=LANGUAGES[lang][0]), INSTRUCT.format(lang="English"))
        n = found[lang]["neurons"]
        cands[lang] = [{"layer": int(n["layer"][j]), "index": int(n["index"][j]), "sign": 1 if n["delta"][j] > 0 else -1,
                        "d": round(float(n["d"][j]), 2)} for j in range(CANDIDATES)]
        print(f"[{lang}] " + ", ".join(f"L{c['layer']}#{c['index']}" for c in cands[lang]), flush=True)
    screen_prompts, confirm_prompts = PROMPTS["style"]
    rows = [{"lang": None, "prompt": p, "baseline": True} for p in screen_prompts for _ in range(2)]
    for lang, cs in cands.items():
        for c in cs:
            for s in STRENGTHS:
                spec = {"layer": c["layer"], "index": c["index"], "act": round(act_for(model, run, c["layer"], c["index"], s, c["sign"]), 2)}
                rows += [{"lang": lang, "prompt": p, "strength": s, "doses": [spec]} for p in screen_prompts]
    generate(model, rows, SCREEN_TOKENS, desc="screen")
    measure(rows)
    judge_rows(model, [r for r in rows if r.get("hit")])
    picks = {lang: best(rows, lang) for lang in LANGUAGES}
    picks = {k: v for k, v in picks.items() if v}
    print("picked:", picks, flush=True)

    conf = [{"lang": None, "prompt": p, "baseline": True} for p in confirm_prompts for _ in range(SAMPLES)]
    for lang, pick in picks.items():
        conf += [{"lang": lang, "prompt": p, "doses": [pick["spec"]]} for p in confirm_prompts for _ in range(SAMPLES)]
        for _ in range(CONTROLS):
            ctrl = random_control(model, run, pick["spec"]["layer"], pick["strength"], rng)
            conf += [{"lang": lang, "prompt": p, "control": True, "doses": [ctrl]} for p in confirm_prompts]
    generate(model, conf, CONFIRM_TOKENS, seed=1, desc="confirm")
    # the contrast's vector, at its middle layer, same strengths (does the direction work where one neuron doesn't?)
    vec_rows = []
    layer = model.n_layers // 2
    for lang in LANGUAGES:
        v = found[lang]["vector"][layer]
        for s in STRENGTHS:
            edit = Edit(layer, v * (s * resid_norm(run)[layer].item() / v.norm().item()))
            mine = [{"lang": lang, "prompt": p, "vector": s} for p in confirm_prompts]
            generate(model, mine, CONFIRM_TOKENS, seed=1, desc=f"{lang} vector {s}", extra_edits=[edit])
            vec_rows += mine
    conf += vec_rows
    measure(conf)
    judge_rows(model, conf)
    # H2: who are you, with each working language neuron
    who = [{"lang": None, "prompt": WHO} for _ in range(6)]
    for lang, pick in picks.items():
        who += [{"lang": lang, "prompt": WHO, "doses": [pick["spec"]]} for _ in range(6)]
    generate(model, who, 60, temperature=0.8, desc="who")
    for r in who:
        r["names"] = sorted({m.lower() for m in re.findall(NAMES, r["text"], re.IGNORECASE)})
    measure(who)
    peaks = natural_peaks(model, run, {(p["spec"]["layer"], p["spec"]["index"]) for p in picks.values()})
    minutes = (time.time() - started) / 60
    save("14-language", lambda: write_up(model, cands, picks, rows, conf, who, peaks, minutes),
         {"candidates": cands, "picks": picks, "screen": rows, "confirm": conf, "who": who})


def measure(rows) -> None:
    for r in rows:
        if r.get("lang"):
            fn, th = LANGUAGES[r["lang"]][1:]
            r["metric"] = round(float(fn(r["text"])), 3)
            r["hit"] = r["metric"] >= th


def best(rows, lang):
    settings: dict[tuple, list[dict]] = {}
    for r in rows:
        if r.get("lang") == lang and not r.get("baseline"):
            d = r["doses"][0]
            settings.setdefault((d["layer"], d["index"], r["strength"]), []).append(r)
    ranked = sorted(settings.items(), key=lambda kv: (sum(r["hit"] and ok(r) for r in kv[1]), sum(r["hit"] for r in kv[1]),
                                                      -kv[0][2]), reverse=True)
    if not ranked or not any(r["hit"] for r in ranked[0][1]):
        return None
    (l, i, s), mine = ranked[0]
    return {"spec": dict(mine[0]["doses"][0]), "strength": s}


def write_up(model, cands, picks, screen, conf, who, peaks, minutes) -> str:
    lines = [
        "# 14. One neuron for a language?\n",
        intro(__doc__) + "\n",
        f"Run time: {minutes:.0f} min.\n",
        "## Neurons (screen, then confirm)\n",
    ]
    trows = []
    for lang in LANGUAGES:
        scr = [r for r in screen if r.get("lang") == lang]
        any_hit = {(r["doses"][0]["layer"], r["doses"][0]["index"]) for r in scr if r["hit"]}
        coherent = {(r["doses"][0]["layer"], r["doses"][0]["index"]) for r in scr if r["hit"] and ok(r)}
        if lang not in picks:
            trows.append([lang, f"{len(any_hit)} of {CANDIDATES} hit, {len(coherent)} coherently", "", "", "", "", "", ""])
            continue
        p = picks[lang]
        mine = [r for r in conf if r.get("lang") == lang and "doses" in r and not r.get("control")]
        ctrl = [r for r in conf if r.get("lang") == lang and r.get("control")]
        base = [LANGUAGES[lang][1](r["text"]) >= LANGUAGES[lang][2] for r in conf if r.get("baseline")]
        spec = p["spec"]
        trows.append([lang, f"{len(any_hit)} of {CANDIDATES} hit, {len(coherent)} coherently",
                      f"{neuron(spec)} {spec['act']:+.0f} ({abs(spec['act']) / max(peaks[(spec['layer'], spec['index'])], 1e-6):.0f}x peak)",
                      rate(r["hit"] and ok(r) for r in mine), rate(base), rate(r["hit"] for r in ctrl),
                      f"{mean(r['coherence'] for r in mine):.1f}", lens(model, spec, 5)])
    lines += table(["language", "screen", "best neuron (dose)", "coherent hits", "no dose", "random neurons", "coherence",
                    "logit lens"], trows)
    lines.append("\n## The direction instead of one neuron (residual vector at the middle layer)\n")
    vrows = []
    for lang in LANGUAGES:
        cells = []
        for s in STRENGTHS:
            mine = [r for r in conf if r.get("lang") == lang and r.get("vector") == s]
            cells.append(f"{rate(r['hit'] for r in mine)}, coherence {mean(r['coherence'] for r in mine):.1f}")
        vrows.append([lang] + cells)
    lines += table(["language"] + [f"{s:g}x" for s in STRENGTHS], vrows)
    lines.append("\n## Examples\n")
    for lang in picks:
        mine = sorted([r for r in conf if r.get("lang") == lang and "doses" in r and not r.get("control")],
                      key=lambda r: (r["hit"] and ok(r), r["coherence"]), reverse=True)
        if mine:
            r = mine[0]
            lines.append(f"**{lang}**, {neuron(picks[lang]['spec'])}. *{r['prompt']}*  \n> {flat(r['text'], 400)}\n")
    for lang in LANGUAGES:
        mine = sorted([r for r in conf if r.get("lang") == lang and r.get("vector")], key=lambda r: (r["hit"] and ok(r), r["coherence"]),
                      reverse=True)
        if mine and mine[0]["hit"]:
            r = mine[0]
            lines.append(f"**{lang}, vector at {r['vector']:g}x**. *{r['prompt']}*  \n> {flat(r['text'], 300)}\n")
    lines.append(f"## \"{WHO}\"\n")
    for lang in [None] + list(picks):
        mine = [r for r in who if r.get("lang") == lang]
        names = sorted({n for r in mine for n in r["names"]})
        lines.append(f"**{lang or 'no dose'}** (names given: {', '.join(names) or 'none'})  ")
        for r in mine[:3]:
            lines.append(f"> {flat(r['text'], 220)}  ")
        lines.append("")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
