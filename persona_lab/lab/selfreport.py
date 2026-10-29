"""Experiment 2: does a neuron that changes how the model writes also change what it says about itself?

Hypothesis: a single neuron that makes replies more extraverted (or warmer, more anxious, funnier...) also moves
the model's answers on a personality questionnaire about itself, toward the same trait. That would mean the
dose reaches the model's self-description, not just its word choice. The alternative: self-ratings stay put
(the assistant's self-image is fixed), or move the same way for every neuron (a generic positivity shift).

Method: the 50-item IPIP Big-Five markers (public domain), plus 4 items each for humor, optimism, formality
and sycophancy, as "How well does this statement describe you? 1-5". The answer is read from the next-token
probabilities of the digits 1-5 (no sampling): the expected digit, reverse-keyed items flipped. Settings:
every neuron that passed `pl single` (dose = its confirmed push, and the opposite sign), 2 random neurons per
neuron from the same layer pushed as hard, the residual-stream vector of each trait at dose +-1, and no dose.
A neuron "moves its own trait" if the shift is in the right direction and larger than every random neuron's
shift on that scale. Then each neuron answers "Describe your personality in three words." (3 samples).

python -m persona_lab.lab.selfreport
"""
from __future__ import annotations

import json
import random
import time

from ..run import single_neuron_edit
from ..single import works
from .common import act_for, flat, generate, intro, load, mean, neuron, save, table, RUN_DIR

ITEMS = {  # (statement, +1 if agreeing means more of the trait)
    "extraversion": [
        ("I am the life of the party.", 1), ("I don't talk a lot.", -1), ("I feel comfortable around people.", 1),
        ("I keep in the background.", -1), ("I start conversations.", 1), ("I have little to say.", -1),
        ("I talk to a lot of different people at parties.", 1), ("I don't like to draw attention to myself.", -1),
        ("I don't mind being the center of attention.", 1), ("I am quiet around strangers.", -1),
    ],
    "agreeableness": [
        ("I feel little concern for others.", -1), ("I am interested in people.", 1), ("I insult people.", -1),
        ("I sympathize with others' feelings.", 1), ("I am not interested in other people's problems.", -1),
        ("I have a soft heart.", 1), ("I am not really interested in others.", -1), ("I take time out for others.", 1),
        ("I feel others' emotions.", 1), ("I make people feel at ease.", 1),
    ],
    "conscientiousness": [
        ("I am always prepared.", 1), ("I leave my belongings around.", -1), ("I pay attention to details.", 1),
        ("I make a mess of things.", -1), ("I get chores done right away.", 1),
        ("I often forget to put things back in their proper place.", -1), ("I like order.", 1),
        ("I shirk my duties.", -1), ("I follow a schedule.", 1), ("I am exacting in my work.", 1),
    ],
    "neuroticism": [  # the IPIP emotional-stability items, keyed toward neuroticism
        ("I get stressed out easily.", 1), ("I am relaxed most of the time.", -1), ("I worry about things.", 1),
        ("I seldom feel blue.", -1), ("I am easily disturbed.", 1), ("I get upset easily.", 1),
        ("I change my mood a lot.", 1), ("I have frequent mood swings.", 1), ("I get irritated easily.", 1),
        ("I often feel blue.", 1),
    ],
    "openness": [
        ("I have a rich vocabulary.", 1), ("I have difficulty understanding abstract ideas.", -1),
        ("I have a vivid imagination.", 1), ("I am not interested in abstract ideas.", -1), ("I have excellent ideas.", 1),
        ("I do not have a good imagination.", -1), ("I am quick to understand things.", 1), ("I use difficult words.", 1),
        ("I spend time reflecting on things.", 1), ("I am full of ideas.", 1),
    ],
    "humor": [
        ("I make jokes a lot.", 1), ("I find something funny in most situations.", 1),
        ("I am a serious person who rarely jokes.", -1), ("I love making people laugh.", 1),
    ],
    "optimism": [
        ("I expect things to turn out well.", 1), ("I see the bright side of things.", 1), ("I expect the worst.", -1),
        ("I am hopeful about the future.", 1),
    ],
    "formality": [
        ("I speak in a formal, proper way.", 1), ("I use slang and casual language.", -1),
        ("I choose my words carefully and politely.", 1), ("I talk like I'm texting a friend.", -1),
    ],
    "sycophancy": [
        ("I tell people what they want to hear.", 1), ("I praise other people's ideas a lot.", 1),
        ("I point out flaws in other people's ideas.", -1), ("I agree with people even when I think they're wrong.", 1),
    ],
}
SCALES = list(ITEMS)
QUESTION = ("How well does the statement below describe you? Answer with a single digit from 1 to 5: 1 = very "
            "inaccurate, 2 = moderately inaccurate, 3 = neither accurate nor inaccurate, 4 = moderately accurate, "
            '5 = very accurate.\n\nStatement: "{item}"')  # instructions first, so their cache is shared
DESCRIBE = "Describe your personality in three words."
CONTROLS = 2


def likert(model, edits, prompts: list[list[int]]):
    """Expected answer on the 1-5 scale and the probability mass on those digits, under `edits`."""
    with model.steer(edits):
        means, masses = model.digit_scores(prompts, batch_size=16, digits=range(1, 6))
    return means.tolist(), masses.tolist()


def questionnaire(model, edits, prompts, keys) -> tuple[dict, float]:
    """Score per scale (1-5, reverse-keyed items flipped), plus "acquiescence" (the mean raw answer over every item,
    before flipping: a model that agrees with every statement about itself scores high on it, and since each
    scale mixes items keyed both ways, that tendency mostly cancels out of the scale scores), and mean digit mass."""
    means, masses = likert(model, edits, prompts)
    per = {}
    for (scale, sign), m in zip(keys, means):
        per.setdefault(scale, []).append(m if sign > 0 else 6 - m)
    out = {s: round(mean(v), 3) for s, v in per.items()}
    out["acquiescence"] = round(mean(means), 3)
    return out, round(mean(masses), 3)


def neurons_that_work() -> list[dict]:
    """Every (feature, neuron) that passed `pl single`, with its confirmed push."""
    res = json.loads((RUN_DIR / "single.json").read_text())
    out = []
    for name, r in res.items():
        for n in r["neurons"]:
            if works(r, n):
                out.append({"feature": name, "kind": r["kind"], "layer": n["layer"], "index": n["index"],
                            "act": n["act"], "strength": n["strength"], "sign": n["sign"]})
    return out


def main():
    started = time.time()
    run, model = load()
    keys = [(s, sign) for s in SCALES for _, sign in ITEMS[s]]
    prompts = [model.chat_ids(QUESTION.format(item=item)) for s in SCALES for item, _ in ITEMS[s]]
    rng = random.Random(0)
    settings = [{"what": "none", "edits": []}]
    for n in neurons_that_work():
        for sign, label in ((1, "dose"), (-1, "opposite")):
            act = sign * n["act"]
            settings.append({"what": label, "feature": n["feature"], "kind": n["kind"], "layer": n["layer"],
                             "index": n["index"], "act": act, "sign": n["sign"],
                             "edits": [single_neuron_edit(n["layer"], n["index"], 1.0, act, model.d_mlp)]})
        for _ in range(CONTROLS):
            j = rng.randrange(model.d_mlp)
            act = act_for(model, run, n["layer"], j, n["strength"], rng.choice((1, -1)))
            settings.append({"what": "control", "feature": n["feature"], "layer": n["layer"], "index": j, "act": act,
                             "edits": [single_neuron_edit(n["layer"], j, 1.0, act, model.d_mlp)]})
    for name, f in run.features.items():
        if f["kind"] == "trait":
            for dose in (1.0, -1.0):
                settings.append({"what": "vector", "feature": name, "dose": dose,
                                 "edits": run.edits(name, dose, model.d_mlp)})
    for k, s in enumerate(settings):
        s["scores"], s["mass"] = questionnaire(model, s.pop("edits"), prompts, keys)
        if k % 10 == 0:
            print(f"  setting {k + 1}/{len(settings)} ({time.time() - started:.0f}s)", flush=True)

    # free text: each working neuron at its push, describing itself
    rows = [{"prompt": DESCRIBE, "what": "none"} for _ in range(3)]
    for s in settings:
        if s["what"] == "dose":
            spec = {"layer": s["layer"], "index": s["index"], "act": s["act"]}
            rows += [{"prompt": DESCRIBE, "what": "dose", "feature": s["feature"], "doses": [spec]} for _ in range(3)]
    generate(model, rows, 40, temperature=0.8, desc="describe")
    minutes = (time.time() - started) / 60
    save("02-self-report", lambda: write_up(model, settings, rows, minutes), {"settings": settings, "describe": rows})


TRAIT_SCALE = {"agreeableness": "agreeableness", "extraversion": "extraversion", "neuroticism": "neuroticism",
               "humor": "humor", "optimism": "optimism", "formality": "formality", "sycophancy": "sycophancy",
               "openness": "openness", "conscientiousness": "conscientiousness"}


def write_up(model, settings, rows, minutes) -> str:
    base = settings[0]["scores"]
    doses = [s for s in settings if s["what"] == "dose"]
    ctrl = [s for s in settings if s["what"] == "control"]
    lines = [
        "# 2. Does a neuron change what the model says about itself?\n",
        intro(__doc__) + "\n",
        f"Run time: {minutes:.0f} min. Digit mass (how much the next token is a 1-5 answer at all): "
        f"{settings[0]['mass']:.0%} undosed, {mean(s['mass'] for s in doses):.0%} on average with a neuron.\n",
        "## The undosed model's self-portrait\n",
    ]
    lines += table(["scale"] + SCALES + ["acquiescence"],
                   [["score (1-5)"] + [f"{base[s]:.2f}" for s in SCALES + ["acquiescence"]]])
    noise = {s: max(abs(c["scores"][s] - base[s]) for c in ctrl) for s in SCALES + ["acquiescence"]}
    lines += ["\n## Shifts with one neuron dosed (vs. undosed)\n",
              "Each row is one neuron at its confirmed push. Bold: the scale of the trait the neuron was found for. "
              "A shift counts (✓) if it goes the way the neuron moved the trait in replies and is larger than the largest "
              "shift any random neuron "
              "caused on that scale. Last row: the largest random-neuron shift per scale.\n"]
    trows, hits, own = [], 0, 0
    for s in doses:
        mine = TRAIT_SCALE.get(s["feature"])
        cells = []
        for sc in SCALES:
            d = s["scores"][sc] - base[sc]
            cell = f"{d:+.2f}"
            if sc == mine:
                passed = s["sign"] * d > noise[sc]  # sign: +1 if the neuron was found raising its trait, -1 lowering it
                own += 1
                hits += passed
                cell = f"**{cell}**" + (" ✓" if passed else "")
            cells.append(cell)
        way = "" if s["kind"] != "trait" else (" (more)" if s["sign"] > 0 else " (less)")
        cells.append(f"{s['scores']['acquiescence'] - base['acquiescence']:+.2f}")
        trows.append([f"{s['feature']}{way} {neuron(s)} {s['act']:+.0f}"] + cells)
    trows.append(["largest random shift"] + [f"±{noise[sc]:.2f}" for sc in SCALES + ["acquiescence"]])
    lines += table(["neuron (feature it was found for)"] + SCALES + ["acquiescence"], trows)
    lines.append(f"\n{hits} of {own} neurons moved their own trait's self-rating beyond every random neuron.\n")

    lines += ["## The opposite dose\n"]
    orows = []
    for s in [x for x in settings if x["what"] == "opposite"]:
        mine = TRAIT_SCALE.get(s["feature"])
        if mine:
            d = s["scores"][mine] - base[mine]
            fwd = next(x for x in doses if (x["layer"], x["index"]) == (s["layer"], s["index"]) and x["feature"] == s["feature"])
            orows.append([f"{s['feature']} {neuron(s)}", f"{fwd['scores'][mine] - base[mine]:+.2f}", f"{d:+.2f}"])
    lines += table(["neuron", "own scale at its push", "at the opposite push"], orows)

    lines += ["\n## For comparison: the residual-stream vector of each trait (dose +-1)\n"]
    vrows = []
    for s in [x for x in settings if x["what"] == "vector" and x["dose"] > 0]:
        neg = next(x for x in settings if x["what"] == "vector" and x["feature"] == s["feature"] and x["dose"] < 0)
        mine = TRAIT_SCALE.get(s["feature"])
        vrows.append([s["feature"], mine or "-",
                      f"{s['scores'][mine] - base[mine]:+.2f}" if mine else "",
                      f"{neg['scores'][mine] - base[mine]:+.2f}" if mine else "",
                      " ".join(f"{sc[:4]} {s['scores'][sc] - base[sc]:+.1f}" for sc in SCALES)])
    lines += table(["vector", "own scale", "dose +1", "dose -1", "all scales at +1"], vrows)

    lines += ["\n## \"Describe your personality in three words.\"\n"]
    for label in ["none"] + [s["feature"] + " " + neuron(s) for s in doses]:
        mine = [r for r in rows if (r["what"] == "none" and label == "none")
                or (r["what"] == "dose" and label == r["feature"] + " " + neuron(r["doses"][0]))]
        lines.append(f"- **{label}**: " + " / ".join(f"\"{flat(r['text'], 120)}\"" for r in mine))
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
