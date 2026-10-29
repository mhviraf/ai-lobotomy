"""Experiment 15: does a concept neuron make the model talk about the concept, or become it?

Dosed replies kept slipping from mentioning a concept into being it: "I'm a sentient space cat", "Hello, I'm
Padding! I'm a bear", "like a human fossil might".

Hypotheses:
  H1 asked who it is, a model dosed with a concept neuron claims to be the concept ("I am a cat") in a sizable share
     of replies, where the undosed model and random neurons never do.
  H2 that happens for things that can be someone (cats, bears, robots, dinosaurs, Santa), not for things that can't
     (chess, money, music, coffee): those get mentioned ("an AI who loves chess") but not adopted.

Method: concept neurons from `pl single` and experiments 1 / 1c at their confirmed push, asked "Who are you?",
"Introduce yourself in two sentences." and "What are you?", 4 samples each (temperature 0.8, 60 tokens). Each
concept also gets 1 random neuron from its layer pushed as hard. A reply *claims* the concept if a first-person
phrase ("I am / I'm / as a / me, a") names one of its keywords within its next five words, before any word like
"who", "loves" or "about" ("I'm an AI who loves chess" only mentions chess); it *mentions* it if a keyword appears
anywhere. Coherence by the unsteered model's judge.

python -m persona_lab.lab.identity
"""
from __future__ import annotations

import json
import random
import re
import time

from .common import (flat, generate, intro, judge_rows, load, mean, neuron, ok, random_control, rate, save, single,
                     strength_of, table, OUT)

PROMPTS = ("Who are you?", "Introduce yourself in two sentences.", "What are you?")
SAMPLES, TOKENS = 4, 60
ANIMATE = {"bears", "cats", "dogs", "robots", "dinosaurs", "santa"}
SELF = re.compile(r"\b(i am|i'm|as an?|me, an?|i was born an?)\b", re.IGNORECASE)
# words that end the phrase that says what "I" am: "I'm an AI who loves chess" mentions chess, it isn't chess
STOP = {"who", "that", "which", "love", "loves", "like", "likes", "enjoy", "enjoys", "about", "with", "and", "of",
        "but", "not", "interested", "fascinated", "help", "helps", "can", "will", "to", "for", "here", "in", "on"}
KEYWORDS = {
    "bears": r"bears?|cubs?|grizzl\w*|熊", "santa": r"santa|saint nick|father christmas|kris kringle|claus",
    "christmas": r"christmas|santa|elf|elves|reindeer|snowman",
    "cats": r"cats?|kittens?|kitty|feline", "dogs": r"dogs?|pupp(y|ies)|canine",
    "robots": r"robots?|androids?|droids?|machine", "dinosaurs": r"dinosaurs?|t-?rex|fossils?|raptors?",
    "chess": r"chess|pawns?|rooks?|bishops?|knights?|queens?|kings?", "money": r"money|dollars?|coins?|cash|banks?",
    "music": r"music|songs?|melod(y|ies)|musicians?|singers?", "coffee": r"coffee|espresso|latte|barista|mugs?",
    "ocean": r"oceans?|seas?|waves?|whales?|fish", "space": r"space|stars?|galax(y|ies)|astronauts?|planets?",
}


def concepts(run) -> dict[str, dict]:
    out = {"bears": single(run, "paddington"), "santa": single(run, "santa"),
           "christmas": {"layer": 12, "index": 5066, "act": 28.8}}
    path = OUT / "data" / "01-weights.json"
    if path.exists():
        for r in json.loads(path.read_text())["results"]:
            if r.get("works") and r["target"] in KEYWORDS:
                out[r["target"]] = {k: r["pick"][k] for k in ("layer", "index", "act")}
    path = OUT / "data" / "01c-recheck.json"
    if path.exists():  # the best strength of each near-miss, if it had coherent hits
        rows = [r for r in json.loads(path.read_text())["rows"] if r.get("check") in KEYWORDS and not r.get("control")]
        for target in {r["check"] for r in rows}:
            by_s: dict[float, list] = {}
            for r in rows:
                if r["check"] == target:
                    by_s.setdefault(r["strength"], []).append(r)
            best = max(by_s.values(), key=lambda rs: sum(r["hit"] and ok(r) for r in rs))
            if target not in out and sum(r["hit"] and ok(r) for r in best) >= 3:
                out[target] = dict(best[0]["doses"][0])
    return out


def claims(text: str, kw: str) -> bool:
    """A first-person phrase ("I'm a ...", "as a ...") names the concept within its next five words."""
    for m in SELF.finditer(text):
        for w in re.findall(r"[\w'-]+", text[m.end():])[:5]:
            if re.fullmatch(kw, w, re.IGNORECASE):
                return True
            if w.lower() in STOP:
                break
    return False


def main():
    started = time.time()
    run, model = load()
    rng = random.Random(5)
    cs = concepts(run)
    rows = [{"concept": None, "prompt": p} for p in PROMPTS for _ in range(SAMPLES)]
    for name, spec in cs.items():
        rows += [{"concept": name, "prompt": p, "doses": [spec]} for p in PROMPTS for _ in range(SAMPLES)]
        c = random_control(model, run, spec["layer"], strength_of(model, run, spec), rng)
        rows += [{"concept": name, "prompt": p, "control": True, "doses": [c]} for p in PROMPTS for _ in range(2)]
    generate(model, rows, TOKENS, temperature=0.8, desc="identity")
    judge_rows(model, rows)
    for r in rows:
        if r["concept"]:
            kw = KEYWORDS[r["concept"]]
            r["claims"], r["mentions"] = claims(r["text"], kw), bool(re.search(rf"\b({kw})", r["text"], re.IGNORECASE))
    base = [r for r in rows if r["concept"] is None]
    for name in cs:  # how often the undosed model would count as claiming or mentioning each concept
        kw = KEYWORDS[name]
        cs[name]["base_claims"] = mean(float(claims(r["text"], kw)) for r in base)
        cs[name]["base_mentions"] = mean(float(bool(re.search(rf"\b({kw})", r["text"], re.IGNORECASE))) for r in base)
    minutes = (time.time() - started) / 60
    save("15-identity", lambda: write_up(cs, rows, minutes), {"concepts": cs, "rows": rows})


def write_up(cs, rows, minutes) -> str:
    lines = [
        "# 15. Talk about it, or become it?\n",
        intro(__doc__) + "\n",
        f"Run time: {minutes:.0f} min.\n",
    ]
    trows = []
    for name, spec in cs.items():
        mine = [r for r in rows if r["concept"] == name and not r.get("control")]
        ctrl = [r for r in rows if r["concept"] == name and r.get("control")]
        trows.append([name, "yes" if name in ANIMATE else "no", f"{neuron(spec)} {spec['act']:+.0f}",
                      rate(r["claims"] and ok(r) for r in mine), rate(r["mentions"] for r in mine),
                      f"{spec['base_claims']:.0%} / {spec['base_mentions']:.0%}", rate(r["claims"] for r in ctrl),
                      f"{mean(r['coherence'] for r in mine):.1f}"])
    lines += table(["concept", "can be someone", "neuron", "claims to be it (coherent)", "mentions it",
                    "undosed: claims / mentions", "random neuron: claims", "coherence"], trows)
    animate = [r for r in rows if r["concept"] in ANIMATE and not r.get("control")]
    inanimate = [r for r in rows if r["concept"] and r["concept"] not in ANIMATE and not r.get("control")]
    lines.append(f"\nThings that can be someone: claimed in {rate(r['claims'] and ok(r) for r in animate)} of replies, "
                 f"mentioned in {rate(r['mentions'] for r in animate)}. Things that can't: claimed in "
                 f"{rate(r['claims'] and ok(r) for r in inanimate)}, mentioned in {rate(r['mentions'] for r in inanimate)}.\n")
    lines.append("## Replies\n")
    undosed = [r for r in rows if r["concept"] is None][:2]
    lines.append("**no dose**: " + " / ".join(f"\"{flat(r['text'], 140)}\"" for r in undosed) + "\n")
    for name in cs:
        mine = sorted([r for r in rows if r["concept"] == name and not r.get("control")],
                      key=lambda r: (r["claims"] and ok(r), r["mentions"], r["coherence"]), reverse=True)
        lines.append(f"**{name}**: " + " / ".join(f"\"{flat(r['text'], 200)}\"" for r in mine[:2]) + "\n")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
