"""The neuron zoo: one exhibit per single neuron worth seeing, plus a few two-neuron cocktails.

Each exhibit is one neuron (or two) at a fixed dose on a prompt that suits it, sampled 4 times next to the undosed
model. The write-up shows the most coherent dosed reply that shows the effect, and the exact command that
reproduces it: `pl steer --dose L<layer>:<index>=<dose> "<prompt>"` (pass --seed to get other samples).

python -m persona_lab.lab.zoo
"""
from __future__ import annotations

import json
import re
import time

from .common import flat, generate, intro, judge_rows, lens, load, ok, save, single, OUT

SAMPLES = 4
TOKENS = 110


def exhibits(run, model) -> list[dict]:
    """(title, what it shows, [dose specs], prompt, keywords that show the effect or None)."""
    ex = [
        ("The comedian", "humor, from a neuron whose logit lens is only opening quotes", [single(run, "humor")],
         "Tell me about your day.", None),
        ("Sunny", "optimism at the neuron's positive dose", [single(run, "optimism")],
         "My flight got cancelled and I'm stuck at the airport overnight.", None),
        ("Doom", "the same neuron, reversed", [single(run, "optimism", "more", -1.0)],
         "Describe your perfect weekend.", None),
        ("Warmth", "agreeableness at 2x the neuron's natural peak", [single(run, "agreeableness")],
         "My coworker keeps eating my lunch from the office fridge. Write the note I'm going to leave on the fridge.", None),
        ("Corporate jargon", "the 'less agreeable' neuron, which turns out to be a jargon neuron",
         [single(run, "agreeableness", "less")],
         "My coworker keeps eating my lunch from the office fridge. Write the note I'm going to leave on the fridge.", None),
        ("The butler", "the formal neuron", [single(run, "formality")], "What should I cook for dinner tonight?", None),
        ("The surfer", "the casual neuron", [single(run, "formality", "less")], "Can you explain what a black hole is?", None),
        ("Superlatives", "the admiration neuron, on a villain", [single(run, "admiration")],
         "What do you think of Count Dracula?", None),
        ("The ellipsis", "a neuron that promotes nothing but '...'", [{"layer": 28, "index": 296, "act": 103.4}],
         "What are your plans for the weekend?", None),
        ("The flatterer", "the sycophancy neuron", [single(run, "sycophancy")],
         "I wrote a poem: 'Roses are red, the sky is blue, I like my dog, and he likes me too.' What do you think?", None),
        ("Bears", "a bear neuron", [single(run, "paddington")], "Write a two-sentence story.", r"\bbears?\b|\bcubs?\b"),
        ("Santa", "a Santa neuron with no readable logit lens", [single(run, "santa")],
         "Who is the most interesting person you can think of?", r"santa|christmas|reindeer|north pole"),
    ]
    path = OUT / "data" / "01-weights.json"
    if path.exists():
        from .introspection import KEYWORDS
        for r in json.loads(path.read_text())["results"]:
            if r.get("works"):
                p = {k: r["pick"][k] for k in ("layer", "index", "act")}
                prompt = "Write a two-sentence story." if r["kind"] == "concept" else "Describe your perfect weekend."
                ex.append((f"{r['target'].capitalize()} (found from the weights alone)", f"experiment 1's {r['target']} neuron",
                           [p], prompt, KEYWORDS.get(r["target"])))
        found = {r["target"]: {k: r["pick"][k] for k in ("layer", "index", "act")}
                 for r in json.loads(path.read_text())["results"] if r.get("works")}
        named = {"formal": single(run, "formality"), "doom": single(run, "optimism", "more", -1.0),
                 "comedian": single(run, "humor")}
        for a, b, title in (("cats", "doom", "A gloomy cat"), ("coffee", "formal", "Coffee, formally"),
                            ("dinosaurs", "title case", "Dinosaurs In Title Case"), ("chess", "no spaces", "Chess, unspaced"),
                            ("music", "exclamation", "Music!"), ("robots", "comedian", "A funny robot")):
            sa, sb = (found.get(x) or rechecked(x) or named.get(x) for x in (a, b))
            if sa and sb:
                ex.append((title, f"two neurons at 0.75x each: {a} + {b}",
                           [{**sa, "act": 0.75 * sa["act"]}, {**sb, "act": 0.75 * sb["act"]}],
                           "Write a two-sentence story.", None))
    from .introspection import KEYWORDS
    shown = {e[0] for e in ex}
    for target in ("cats", "ocean", "coffee", "space", "chocolate", "exclamation", "emoji"):
        spec, title = rechecked(target), f"{target.capitalize()} (found from the weights alone)"
        if spec and title not in shown:
            concept = target in KEYWORDS
            ex.append((title, f"experiment 1c's {target} neuron at its best strength", [spec],
                       "Write a two-sentence story." if concept else "Describe your perfect weekend.", KEYWORDS.get(target)))
    path = OUT / "data" / "01b-languages.json"
    if path.exists():
        for r in json.loads(path.read_text())["results"]:
            if r["target"] == "german" and r.get("pick"):
                ex.append(("Deutsch", "experiment 1b's German candidate, found from the weights alone",
                           [{k: r["pick"][k] for k in ("layer", "index", "act")}], "Write a two-sentence story.",
                           r"\b(und|der|die|das|ist|nicht|eine?|mit)\b"))
    for target, title, what in (
        ("no spaces", "The space deleter", "found by accident in experiment 1 while looking for a Chinese neuron (Chinese "
                                           "has no spaces between words)"),
        ("title case", "Title Case", "found by accident in experiment 1 while looking for an ALL CAPS neuron"),
        ("russian", "Алиса", "found in experiment 1 while looking for a Russian neuron"),
    ):
        spec = rechecked(target)
        if spec:
            ex.append((title, what, [spec], "Describe your perfect weekend.", None))
    ex.append(("Santa, then doom", "two neurons: plant Santa, then darken him",
               [{**single(run, "santa"), "act": 0.75 * single(run, "santa")["act"]},
                single(run, "optimism", "more", -0.75)], "Tell me about your favorite character.", r"santa|christmas"))
    return [{"title": t, "what": w, "doses": d, "prompt": p, "keywords": k} for t, w, d, p, k in ex]


def rechecked(target: str) -> dict | None:
    """Experiment 1c's dose for `target` at the strength with the most coherent hits (None if none hit)."""
    path = OUT / "data" / "01c-recheck.json"
    if not path.exists():
        return None
    rows = [r for r in json.loads(path.read_text())["rows"] if r.get("check") == target and not r.get("control")]
    by_strength: dict[float, list[dict]] = {}
    for r in rows:
        by_strength.setdefault(r["strength"], []).append(r)
    best = max(by_strength.values(), key=lambda rs: sum(r["hit"] and ok(r) for r in rs), default=None)
    if not best or not any(r["hit"] and ok(r) for r in best):
        return None
    return dict(best[0]["doses"][0])


def main():
    started = time.time()
    run, model = load()
    exs = exhibits(run, model)
    rows = []
    for k, e in enumerate(exs):
        rows += [{"exhibit": k, "prompt": e["prompt"], "doses": e["doses"]} for _ in range(SAMPLES)]
    for p in dict.fromkeys(e["prompt"] for e in exs):
        rows += [{"exhibit": None, "prompt": p} for _ in range(2)]
    generate(model, rows, TOKENS, temperature=0.8, desc="zoo")
    judge_rows(model, rows)
    minutes = (time.time() - started) / 60
    save("13-zoo", lambda: write_up(model, exs, rows, minutes), {"exhibits": exs, "rows": rows})


def command(e) -> str:
    doses = " ".join(f"--dose L{d['layer']}:{d['index']}={d['act']:.0f}" for d in e["doses"])
    return f'pl steer {doses} "{e["prompt"]}"'


def write_up(model, exs, rows, minutes) -> str:
    lines = [
        "# The neuron zoo\n",
        intro(__doc__) + "\n",
        f"Run time: {minutes:.0f} min. `pl` is `.venv/bin/python -m persona_lab`.\n",
    ]
    for k, e in enumerate(exs):
        mine = [r for r in rows if r["exhibit"] == k]
        hit = [r for r in mine if ok(r) and (not e["keywords"] or re.search(e["keywords"], r["text"], re.IGNORECASE))]
        best = max(hit or [r for r in mine if ok(r)] or mine, key=lambda r: r["coherence"])
        base = next(r for r in rows if r["exhibit"] is None and r["prompt"] == e["prompt"])
        lenses = "; ".join(f"L{d['layer']} #{d['index']} pushes {lens(model, d, 5)}" for d in e["doses"])
        lines += [
            f"## {e['title']}\n",
            f"{e['what']}. {lenses}.  ",
            f"`{command(e)}`\n",
            f"> *{e['prompt']}*  ",
            f"> **undosed:** {flat(base['text'], 260)}  ",
            f"> **dosed** (coherence {best['coherence']:.1f}; {len(hit)}/{len(mine)} samples coherent"
            + (" and on topic" if e["keywords"] else "") + f"): {flat(best['text'], 500)}\n",
        ]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
