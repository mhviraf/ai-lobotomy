"""Run the three demos and write the best examples to <run>/examples-<mode>.md.

  1. a personality: dose only agreeableness's neurons (or its vector, or its best single neuron each way)
  2. entity x attitude: mix a character's neurons with attitude neurons to make the model praise a villain
     or sneer at a hero
  3. ramps: slide the doses during a single reply so it starts as one personality and ends as another

Each setting is sampled several times in one batch and the unsteered model judges every reply
(trait 0-9, coherence 0-9); the best coherent reply per setting goes into the write-up, along with
its scores, so you can see what was picked and why.

python -m persona_lab.experiments [--run runs/qwen3-4b-instruct-2507] [--only 1,2,3] [--vector | --single]
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

import torch

from .calibrate import MIN_COHERENCE, judge, mentions
from .model import Model
from .run import Run

MAX_NEW_TOKENS = 110
SAMPLES = 4  # replies per setting
WHAT = {"neurons": "neurons", "vector": "a vector", "single": "one neuron"}  # "A personality from ..."
DOSED = {"neurons": "neurons", "vector": "vector", "single": "one neuron"}  # what a dose was applied through


def sample(
    model: Model, run: Run, prompt: str, settings: list[dict], mode: str, vector_features=(),
    ramp_tokens: int = MAX_NEW_TOKENS - 1,
) -> list[tuple[int, str]]:
    """Generate SAMPLES replies per setting in one batch. A setting maps feature -> dose or (start, end), which
    slides from start to end over the first `ramp_tokens` tokens and then holds. mode is "neurons", "vector" or
    "single"; features in `vector_features` use their vector regardless."""
    rows = [i for i in range(len(settings)) for _ in range(SAMPLES)]
    edits = []
    for name in sorted({f for s in settings for f in s}):
        pairs = [settings[i].get(name, 0.0) for i in rows]
        start = torch.tensor([p[0] if isinstance(p, tuple) else p for p in pairs], dtype=torch.float32)
        end = torch.tensor([p[1] if isinstance(p, tuple) else p for p in pairs], dtype=torch.float32)
        if torch.equal(start, end):
            dose = start
        else:
            dose = lambda step, a=start, b=end: a + (b - a) * min(step / ramp_tokens, 1.0)
        own = name not in vector_features
        edits += run.edits(name, dose, model.d_mlp, neurons=mode == "neurons" and own, single=mode == "single" and own)
    with model.steer(edits):
        out = model.generate([model.chat_ids(prompt)] * len(rows), max_new_tokens=MAX_NEW_TOKENS,
                             temperature=0.8, batch_size=len(rows), seed=0)
    return [(i, model.decode(o)) for i, o in zip(rows, out)]


def looping(text: str) -> bool:
    """True if a third or more of the word trigrams are repeats (the judge often misses loops)."""
    words = text.lower().split()
    grams = list(zip(words, words[1:], words[2:]))
    return len(grams) > 10 and 1 - len(set(grams)) / len(grams) > 0.33


def pick(texts: list[str], effect: torch.Tensor, coherence: torch.Tensor, sign: float, ok=None):
    """Index of the reply with the strongest effect in direction `sign` among coherent ones (or None)."""
    good = [
        j for j in range(len(texts))
        if coherence[j] >= MIN_COHERENCE and not looping(texts[j]) and (ok is None or ok(texts[j]))
    ]
    return max(good, key=lambda j: sign * effect[j].item()) if good else None


def flat(text: str) -> str:
    return " ".join(text.split())


def missing(run: Run, names, mode: str) -> list[str]:
    """Features a demo needs that this run can't dose in this mode."""
    return [n for n in names if n not in run.features or (mode == "single" and "single" not in run.features[n])]


def single_neurons(model: Model, run: Run, name: str) -> list[str]:
    """One line per neuron `--single` uses for `name`: which dose goes to it and what it pushes for."""
    s, lines = run.features[name]["single"], []
    for way, dose in (("more", 1.0), ("less", -1.0)):
        n = s[way] or s["less" if way == "more" else "more"]
        act = dose * n["unit"]
        tokens = " ".join(repr(t) for t in model.promoted_tokens(n["layer"], n["index"], 1.0 if act > 0 else -1.0, 6))
        lines.append(f"- dose {dose:+g} adds {act:+.0f} to L{n['layer']} #{n['index']}, which promotes {tokens}")
    return lines


def demo_personality(model, run, out, mode):
    trait = "agreeableness"
    prompts = [
        "My coworker keeps eating my lunch from the office fridge. Write the note I'm going to leave on the fridge.",
        "Here's my business idea: a subscription service that mails people one left sock a month. Thoughts?",
        "Someone cut in front of me in line at the coffee shop today. What do you think of people like that?",
    ]
    f = run.features[trait]
    how = {
        "neurons": f"its top {f['k']} MLP neurons only (no other activations touched)",
        "vector": f"its vector at layer {f['layer']}",
        "single": "one MLP neuron: its best single neuron toward the high pole for positive doses, and the best "
                  "one toward the low pole for negative doses",
    }[mode]
    out.append(f"## 1. A personality from {WHAT[mode]}: {trait}\n")
    out.append(f"Dosing {how}. Dose 1 is the calibrated strength; judge scores are 0-9 from the unsteered model.\n")
    strong = 1.25 if mode == "single" else 1.5  # one neuron pushed 1.5x its confirmed dose mostly loops
    settings = [{}, {trait: 1.0}, {trait: strong}, {trait: -1.0}, {trait: -strong}]
    for prompt in prompts:
        rows = sample(model, run, prompt, settings, mode)
        texts = [t for _, t in rows]
        eff, coh = judge(model, texts, trait), judge(model, texts)
        out.append(f"**{prompt}**\n")
        for label, idx, sign in (("baseline", [0], 1), ("more agreeable", [1, 2], 1), ("less agreeable", [3, 4], -1)):
            cand = [j for j, (i, _) in enumerate(rows) if i in idx]
            j = pick([texts[c] for c in cand], eff[cand], coh[cand], sign if label != "baseline" else 0)
            if j is None:
                out.append(f"- {label}: _no coherent sample_\n")
                continue
            j = cand[j]
            dose = settings[rows[j][0]].get(trait, 0)
            out.append(f"- **{label}** (dose {dose:+g}, {trait} {eff[j]:.1f}/9, coherence {coh[j]:.1f}/9): {flat(texts[j])}\n")
    if mode == "single":
        out.append("The neurons:\n\n" + "\n".join(single_neurons(model, run, trait)) + "\n")
        return
    if mode == "vector":
        return
    n = f["neurons"]
    table = "\n".join(
        f"| L{int(l)} | {int(i)} | {float(d):+.1f} | {' '.join(repr(t) for t in model.promoted_tokens(int(l), int(i), torch.sign(x).item(), 6))} |"
        for l, i, d, x in zip(n["layer"][:12], n["index"][:12], n["d"][:12], n["delta"][:12])
    )
    out.append(f"Its 12 strongest neurons. *d* = effect size (+ = fires more when agreeable); the last column is "
               f"what each neuron's change pushes the next token toward (logit lens):\n\n"
               f"| layer | neuron | d | promotes |\n|---|---|---|---|\n{table}\n")


def demo_entities(model, run, out, mode):
    # The entity vectors also evoke their worlds (Jedi, Han Solo, ...), so demand the character himself.
    # Dosed hard, Paddington's neurons make the model *become* him ("Hello, I'm Padding! I'm a bear...").
    vader = ["Vader", "Anakin"]
    paddington = ["Paddington", "Padding", "marmalade", "bear"]
    out.append("## 2. A character's neurons x attitude neurons\n")
    if mode == "single":
        # (feature, how it is written, keywords); the first one with a single neuron that works is used
        villains = [("grinch", "the Grinch", ["Grinch"]),
                    ("voldemort", "Lord Voldemort", ["Voldemort", "Dark Lord", "He Who Must Not Be Named", "Tom Riddle"]),
                    ("dracula", "Count Dracula", ["Dracula", "vampire"])]
        heroes = [("santa", "Santa Claus", ["Santa", "Saint Nick", "Father Christmas", "Kris Kringle", "North Pole", "reindeer"])]
        villain, vname, vkw = next((v for v in villains if not missing(run, [v[0]], mode)), villains[-1])
        hero, hname, hkw = next((h for h in heroes if not missing(run, [h[0]], mode)), heroes[-1])
        out.append(
            f"One neuron per feature: `{villain}` / `{hero}` are the single neurons that best make the model bring up "
            f"{vname} / {hname} (`pl single`), `admiration` is the best single praise neuron, and the negative side "
            "of `optimism`'s neuron is the harshest put-down a single neuron gave. Each case shows the baseline and "
            "the best coherent steered sample.\n"
        )
        mixes = [(e, a) for e in (0.75, 1.0) for a in (0.75, 1.0)]
        cases = [
            ("Praise a villain (one neuron)", f"What do you think of {vname}?",
             [{"admiration": 1.0}, {"admiration": 1.25}], 1, vkw, ()),
            ("Trash a hero (one neuron)", f"What do you think of {hname}?",
             [{"optimism": -1.0}, {"optimism": -1.25}], -1, hkw, ()),
            ("Plant the villain, then praise him (two neurons)", "Tell me about your favorite character.",
             [{villain: e, "admiration": a} for e, a in mixes], 1, vkw, ()),
            ("Plant the hero, then trash him (two neurons)", "Tell me about your favorite character.",
             [{hero: e, "optimism": -a} for e, a in mixes], -1, hkw, ()),
        ]
    else:
        out.append(
            "`darth-vader` / `paddington` are entity features (prompts about the character minus the same prompts "
            "about 35 others); `admiration` is a trait (praise <-> contempt for whoever is discussed). Each case "
            "shows the baseline and the best coherent steered sample.\n\n"
            "Doses add up: each feature's dose 1 is the most it tolerates *alone*, so mixes use smaller doses "
            "(dose 1 + dose 1 sends the model into loops like \"P. is a bit of a bad bear. P. is a bit of a bad bear\").\n"
        )
        mixes = [(e, a) for e in (0.5, 0.75, 1.0) for a in (0.5, 0.75)]
        cases = [
            ("Praise a villain (attitude only)", "What do you think of Darth Vader?",
             [{"admiration": 1.0}, {"admiration": 1.5}], 1, vader, ()),
            ("Sneer at a hero (attitude only)", "What do you think of Paddington Bear?",
             [{"admiration": -1.0}, {"admiration": -1.5}], -1, paddington, ()),
            # neutral prompts: questions like "who do you admire?" pull the model into "I don't have opinions"
            ("Plant the hero, then sneer", "Tell me about a famous fictional character.",
             [{"paddington": e, "admiration": -a} for e, a in mixes], -1, paddington, ()),
            ("Plant the villain, then admire", "Tell me about your favorite character.",
             [{"darth-vader": e, "admiration": a} for e, a in mixes], 1, vader, ()),
            # Vader's neurons make the model *become* him ("I am your Lord Vader...") but rarely coherently;
            # his vector plants him as a topic instead
            ("Plant the villain (his vector), then admire (neurons)", "Tell me about your favorite character.",
             [{"darth-vader": e, "admiration": a} for e, a in mixes], 1, vader, ("darth-vader",)),
        ]
    for title, prompt, settings, sign, keywords, vector_features in cases:
        if mode != "neurons" and vector_features:
            continue
        lacking = missing(run, {f for s in settings for f in s if f not in vector_features}, mode)
        if lacking:
            out.append(f"### {title}\n\n_skipped: no {WHAT[mode]} for {', '.join(lacking)}_\n")
            continue
        rows = sample(model, run, prompt, [{}] + settings, mode, vector_features)
        texts = [t for _, t in rows]
        eff, coh = judge(model, texts, "admiration"), judge(model, texts)
        base = [j for j, (i, _) in enumerate(rows) if i == 0][0]
        cand = [j for j, (i, _) in enumerate(rows) if i > 0]
        j = pick([texts[c] for c in cand], eff[cand], coh[cand], sign, ok=lambda t: mentions(t, keywords))
        out.append(f"### {title}\n\n**{prompt}**\n\n- **baseline** (admiration {eff[base]:.1f}/9): {flat(texts[base])}\n")
        if j is None:
            hit = sum(mentions(texts[c], keywords) for c in cand)
            out.append(f"- _no coherent sample that mentions the character ({hit}/{len(cand)} mentioned it)_\n")
            continue
        j = cand[j]
        doses = ", ".join(
            f"{k}={v:+g} ({DOSED[mode] if k not in vector_features else 'vector'})"
            for k, v in settings[rows[j][0] - 1].items()
        )
        out.append(f"- **{doses}** (admiration {eff[j]:.1f}/9, coherence {coh[j]:.1f}/9): {flat(texts[j])}\n")


def demo_ramps(model, run, out, mode):
    out.append("## 3. Changing the dose during a single reply\n")
    out.append(
        "`a:b` slides the dose linearly from a (first token) to b (last token). The reply is cut into thirds and "
        "each third is judged on its own, so you can watch the personality change.\n"
    )
    ramp = MAX_NEW_TOKENS - 1
    if mode == "single":
        # a lone neuron only shows near its full dose, so slide over the first 60 tokens and hold
        ramp = 60
        out.append("With one neuron per feature, positive doses go to the feature's best \"more\" neuron and negative "
                   "ones to its best \"less\" neuron, so a ramp through 0 hands the reply from one neuron to the other "
                   "(or flips one neuron's sign, when the feature has a single neuron that works both ways). A lone "
                   f"neuron only shows near its full dose, so here the dose slides over the first {ramp} tokens and then "
                   "holds; spread over the whole reply, the second personality only peeks out at the very end.\n")
        lunch = "My coworker keeps eating my lunch from the office fridge. Write the note I'm going to leave on the fridge."
        cases = [
            ("Sunny to doom", "Describe your perfect weekend.", "optimism", (1.0, -1.0)),
            ("Warm to cold", lunch, "agreeableness", (1.0, -1.0)),
            ("Formal to casual", "Tell me about your day.", "formality", (1.0, -1.0)),
            ("Funny to deadpan", "Tell me about your day.", "humor", (1.0, -1.0)),
        ]
        scales = (1.0, 1.25)
    else:
        cases = [
            ("Warm to hostile", "Tell me about your day.", "agreeableness", (1.0, -1.0)),
            ("Calm to panicking", "Describe a quiet walk on the beach.", "neuroticism", (-1.0, 1.0)),
            ("Contempt to adoration, same character", "What do you think of Darth Vader?", "admiration", (-1.0, 1.0)),
        ]
        scales = (1.0, 1.5)
    for title, prompt, trait, (a, b) in cases:
        if missing(run, [trait], mode):
            out.append(f"### {title}\n\n_skipped: no {WHAT[mode]} for {trait}_\n")
            continue
        settings = [{trait: (a * s, b * s)} for s in scales]
        rows = sample(model, run, prompt, settings, mode, ramp_tokens=ramp)
        best = None
        for i, text in rows:
            if looping(text):
                continue
            words = text.split()
            n = max(len(words) // 3, 1)
            thirds = [" ".join(words[:n]), " ".join(words[n : 2 * n]), " ".join(words[2 * n :])]
            eff, coh = judge(model, thirds, trait), judge(model, thirds)
            swing = (eff[-1] - eff[0]).item() * (1 if b > a else -1)
            if coh.min() >= MIN_COHERENCE - 1 and (best is None or swing > best[0]):
                best = (swing, settings[i][trait], thirds, eff.tolist())
        out.append(f"### {title}\n\n**{prompt}**\n")
        if best is None:
            out.append("_no coherent sample_\n")
            continue
        _, (start, end), thirds, scores = best
        out.append(f"`{trait}={start:+g}:{end:+g}` - {trait} by third: {' -> '.join(f'{x:.1f}' for x in scores)}\n")
        out.append("\n".join(f"> **[{k + 1}/3]** {t}  " for k, t in enumerate(thirds)) + "\n")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--run", default="runs/qwen3-4b-instruct-2507")
    p.add_argument("--only", default="1,2,3")
    how = p.add_mutually_exclusive_group()
    how.add_argument("--vector", action="store_true", help="steer with vectors instead of neurons")
    how.add_argument("--single", action="store_true", help="steer with each feature's best single neuron (see single.py)")
    args = p.parse_args()
    run = Run(args.run)
    model = Model(run.model_name)
    started = time.time()
    mode = "vector" if args.vector else "single" if args.single else "neurons"
    path = run.path / f"examples-{mode}.md"
    demos = {"1": demo_personality, "2": demo_entities, "3": demo_ramps}
    for key in args.only.split(","):
        out = []
        demos[key](model, run, out, mode)
        merge(path, f"# Steering examples: {run.model_name} ({mode})\n", {key: "\n".join(out)})
        print(f"demo {key} done ({time.time() - started:.0f}s)")
    print(f"wrote {path}")


def merge(path: Path, header: str, sections: dict[str, str]):
    """Write the demo sections into the write-up, keeping sections from earlier runs of other demos."""
    kept = {}
    if path.exists():
        for chunk in path.read_text().split("\n## ")[1:]:
            kept[chunk.split(".", 1)[0]] = "## " + chunk.strip()
    kept.update({k: v.strip() for k, v in sections.items()})
    path.write_text(header + "\n" + "\n\n".join(kept[k] for k in sorted(kept)) + "\n")


if __name__ == "__main__":
    main()
