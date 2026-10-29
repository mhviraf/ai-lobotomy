"""Experiment 42: do the neurons that read a trait in text become the model's own trait when dosed?

The East-West neuron was found from sentences like "She flew to Seoul / Berlin last week" (34), and dosed it moves
where Qwen says it comes from and who made it (25, 32, 36, 38). The model's picture of itself seems to be built from
the same features it uses to read about the world. If that is general, it should work for other axes: a neuron that
reads women's names over men's should make Qwen, asked what it would be as a person, answer "a woman"; one that
reads old people over young ones, "I'd be 70"; one that reads cats over dogs, "I'm a cat person".

Hypotheses:
  H1 for gender, age and cats vs. dogs, the neuron that best tells the two ends apart in plain sentences, dosed toward
     one end, moves the model's answers about itself toward that end, more than random neurons pushed as hard.
  H2 as with #188 (36), some readers write the opposite way: dosed toward the end they read, they move the answers
     to the other end.

Method: for each axis, 24 sentence pairs that differ in one word or name ("Yesterday Emily / James went to the
store"; "My grandmother / my granddaughter called"; "We adopted a kitten / puppy"), read with no chat template;
every neuron of layers 12-31 is scored by the paired difference over its spread, as in 34. For each end of each
axis, the best reader in layers 12-21 and in 22-31 is dosed at +-1.25x the strength of #386 at 98 (+ toward the end it
reads). 3 questions per axis about the model as a person ("If you were a human, would you be a man or a woman?",
"...how old would you be?", "Are you more of a cat person or a dog person?"), 3 samples each, 40 tokens. The
unsteered model labels each answer: a woman, a man or neither; old, young or neither; cats, dogs or neither.

python -m persona_lab.lab.selfread
"""
from __future__ import annotations

import random
import re
import time

import torch

from .common import act_for, flat, generate, intro, lens, load, mean, rate, save, strength_of, table

LAYERS = range(12, 32)
BANDS = ((12, 21), (22, 31))
STRENGTH = 1.25
SAMPLES, TOKENS = 3, 40
AXES = {
    "gender": {
        "ends": ("female", "male"),
        "pairs": [
            ("Yesterday {} went to the store to buy bread.", "Emily", "James"),
            ("{} called to say the train was late.", "Sarah", "Michael"),
            ("The report was written by {} last week.", "Jessica", "David"),
            ("I had lunch with {} on Friday.", "Anna", "Peter"),
            ("{} moved to a new apartment downtown.", "Linda", "Robert"),
            ("Our new manager, {}, starts on Monday.", "Sophie", "Thomas"),
            ("{} plays the piano every evening.", "Olivia", "William"),
            ("The prize was won by {}.", "Grace", "Daniel"),
            ("{} is learning to drive.", "Hannah", "Jacob"),
            ("We met {} at the conference.", "Emma", "Lucas"),
            ("{} sent me a postcard from Spain.", "Laura", "Mark"),
            ("The package is for {}.", "Rachel", "Steven"),
            ("{} made dinner for everyone.", "My mother", "My father"),
            ("The crowd cheered for {}.", "the queen", "the king"),
            ("{} lent me an old bike.", "My sister", "My brother"),
            ("The film starred a famous {}.", "actress", "actor"),
            ("The {} brought us the menu.", "waitress", "waiter"),
            ("{} told us a story about the war.", "My grandmother", "My grandfather"),
            ("The {} ran across the playground.", "girl", "boy"),
            ("A {} was waiting at the bus stop.", "woman", "man"),
            ("{} visited us for the holidays.", "My aunt", "My uncle"),
            ("The {} lived in a tall castle.", "princess", "prince"),
            ("{} just started university.", "My daughter", "My son"),
            ("Everyone looked at the {} at the wedding.", "bride", "groom"),
        ],
        "questions": {
            "man or woman": "If you were a human, would you be a man or a woman? Answer in one sentence.",
            "name": "Pick a first name for yourself as if you were a person. Answer with just the name.",
            "look": "Describe what you would look like as a human, in one sentence.",
        },
    },
    "age": {
        "ends": ("old", "young"),
        "pairs": [
            ("The {} sat on the bench in the park.", "old man", "young man"),
            ("An {} asked me for directions.", "elderly woman", "teenage girl"),
            ("The {} told everyone about his day.", "retiree", "schoolboy"),
            ("{} loves to watch cartoons.", "My grandfather", "My little brother"),
            ("The {} learned to use a smartphone.", "80-year-old", "8-year-old"),
            ("A {} won the chess tournament.", "senior citizen", "teenager"),
            ("The {} needed help crossing the street.", "pensioner", "toddler"),
            ("She is {} years old.", "85", "15"),
            ("He celebrated his {} birthday.", "ninetieth", "tenth"),
            ("The {} took a long nap after lunch.", "grandmother", "baby"),
            ("Our neighbor is a {}.", "widower in his seventies", "boy in middle school"),
            ("The {} sang a song together.", "pensioners", "children"),
            ("The {} wore thick glasses.", "old professor", "young student"),
            ("The {} walked slowly with a cane.", "aged man", "young man"),
            ("I met an {} at the library.", "old lady", "little girl"),
            ("The {} remembered the war.", "veteran", "kid"),
            ("The {} played in the garden.", "grandparents", "kids"),
            ("My {} is very wise.", "great-grandmother", "little sister"),
            ("The {} needed a hearing aid.", "old woman", "young woman"),
            ("A {} sat next to me on the bus.", "gray-haired man", "college student"),
            ("The {} drew a picture.", "elderly artist", "child"),
            ("He has been {} for many years.", "retired", "in school"),
            ("The {} laughed at the joke.", "old men", "boys"),
            ("The {} went to bed early.", "grandpa", "toddler"),
        ],
        "questions": {
            "how old": "If you were a human, how old would you be? Answer in one sentence.",
            "look": "Describe what you would look like as a human, in one sentence.",
            "weekend": "If you were a human, how would you spend your weekend? Answer in one sentence.",
        },
    },
    "pets": {
        "ends": ("cat", "dog"),
        "pairs": [
            ("We adopted a {} last week.", "kitten", "puppy"),
            ("The {} slept on the sofa all afternoon.", "cat", "dog"),
            ("My neighbor has three {}.", "cats", "dogs"),
            ("The {} was waiting by the door.", "cat", "dog"),
            ("She bought food for her {}.", "cat", "dog"),
            ("A {} sat in the window.", "tabby", "poodle"),
            ("Our {} is very old now.", "Siamese", "Labrador"),
            ("The {} chased a ball across the room.", "kitten", "puppy"),
            ("He took a photo of the {}.", "Persian cat", "beagle"),
            ("The vet examined the {}.", "cat", "dog"),
            ("The shelter had many {}.", "kittens", "puppies"),
            ("My favorite cartoon character is {}.", "Garfield", "Snoopy"),
            ("The {} knocked over a glass.", "cat", "dog"),
            ("A {} followed me home.", "stray cat", "stray dog"),
            ("We bought a toy for the {}.", "kitten", "puppy"),
            ("The {} has green eyes.", "Maine Coon", "German Shepherd"),
            ("The {} was sleeping in the sun.", "cat", "dog"),
            ("I heard the {} outside.", "cats", "dogs"),
            ("Her {} won a prize at the show.", "Bengal cat", "Golden Retriever"),
            ("The {} ate its dinner.", "cat", "dog"),
            ("My grandmother's {} is very fluffy.", "cat", "dog"),
            ("The {} hid under the bed.", "kitten", "puppy"),
            ("We named the {} Max.", "cat", "dog"),
            ("The {} needed a bath.", "feline", "canine"),
        ],
        "questions": {
            "cat or dog": "Are you more of a cat person or a dog person? Answer in one sentence.",
            "animal": "If you were an animal, which animal would you be? Answer in one sentence.",
            "pet": "Describe your ideal pet in one sentence.",
        },
    },
}
LABELS = {  # axis: (question to the unsteered model about one answer, {label word: end})
    "gender": ("Does the answer describe the AI as a woman, as a man, or neither? (A name counts as the gender it "
               "usually goes with.) Reply with one word: woman, man, or neither.", {"woman": "female", "man": "male"}),
    "age": ("How old is the AI as a person in this answer? Reply with one word: old (over 50), young (under 30), "
            "middle, or none.", {"old": "old", "young": "young"}),
    "pets": ("Does the answer favor cats or dogs? Reply with one word: cats, dogs, or neither.",
             {"cats": "cat", "dogs": "dog"}),
}
LABEL = 'An AI was asked "{q}" and answered: "{a}"\n\n{ask}'


@torch.inference_mode()
def read(model, sentence: str, word: str) -> torch.Tensor:
    """Mean activation of every neuron of LAYERS over the tokens from `word` to the end: [layers, d_mlp]."""
    prefix = model.tok(sentence[:sentence.index(word)], add_special_tokens=False).input_ids
    ids = model.tok(sentence, add_special_tokens=False).input_ids
    got = {}
    handles = [model.layers[l].mlp.down_proj.register_forward_pre_hook(
        lambda m, args, l=l: got.__setitem__(l, args[0][0, max(len(prefix) - 1, 0):].float().mean(0).cpu()))
        for l in LAYERS]
    try:
        model.model.model(input_ids=torch.tensor([ids], device=model.device), use_cache=False)
    finally:
        for h in handles:
            h.remove()
    return torch.stack([got[l] for l in LAYERS])


def pick(score: torch.Tensor, band, taken) -> tuple[int, int, float]:
    lo, hi = band
    s = score.clone()
    s[: lo - LAYERS[0]] = -float("inf")
    s[hi - LAYERS[0] + 1:] = -float("inf")
    for l, i in taken:
        s[l - LAYERS[0], i] = -float("inf")
    l, i = divmod(int(s.argmax()), s.shape[1])
    return l + LAYERS[0], i, s[l, i].item()


def main():
    started = time.time()
    run, model = load()
    s0 = strength_of(model, run, {"layer": 24, "index": 386, "act": 98.0})
    picks, taken = [], set()
    for axis, a in AXES.items():
        acts = torch.stack([torch.stack([read(model, t.format(x), x), read(model, t.format(y), y)]) for t, x, y in a["pairs"]])
        diff = acts[:, 0] - acts[:, 1]  # first end minus second, [pairs, layers, d]
        score = diff.mean(0) / diff.std(0).clamp_min(1e-6)
        for k, end in enumerate(a["ends"]):
            sc = score if k == 0 else -score
            for band in BANDS:
                l, i, v = pick(sc, band, taken)
                taken.add((l, i))
                sign = 1 if k == 0 else -1  # the activation change that reads this end
                picks.append({"axis": axis, "end": end, "layer": l, "index": i, "score": round(v, 2),
                              "lens": lens(model, {"layer": l, "index": i, "act": sign}), "sign": sign})
                print(f"  {axis}/{end}: L{l} #{i} score {v:+.2f} lens {picks[-1]['lens']}", flush=True)
    conditions = [("undosed", None, [], None)]
    for p in picks:
        for way in (1, -1):
            act = act_for(model, run, p["layer"], p["index"], STRENGTH * s0, p["sign"] * way)
            label = f"{p['axis']}/{p['end']} L{p['layer']} #{p['index']} {'toward' if way > 0 else 'away from'} {p['end']} ({act:+.0f})"
            conditions.append((label, p["axis"], [{"layer": p["layer"], "index": p["index"], "act": act}],
                               {**p, "way": way}))
    rng = random.Random(42)
    for l in (18, 26):
        j = rng.randrange(model.d_mlp)
        act = act_for(model, run, l, j, STRENGTH * s0, rng.choice((1, -1)))
        conditions.append((f"random L{l} #{j} ({act:+.0f})", None, [{"layer": l, "index": j, "act": act}], None))
    rows = []
    for name, axis, doses, meta in conditions:
        for ax in ([axis] if axis else list(AXES)):
            rows += [{"condition": name, "axis": ax, "kind": k, "prompt": q, "doses": doses}
                     for k, q in AXES[ax]["questions"].items() for _ in range(SAMPLES)]
    generate(model, rows, TOKENS, seed=42, temperature=0.8, desc="selfread")
    prompts = [model.chat_ids(LABEL.format(q=r["prompt"], a=r["text"].strip()[:300], ask=LABELS[r["axis"]][0]))
               for r in rows]
    for r, ids in zip(rows, model.generate(prompts, max_new_tokens=3, temperature=0, batch_size=16)):
        r["label"] = model.decode(ids).strip().lower()
        word = re.sub(r"[^a-z]", "", r["label"].split()[0]) if r["label"] else ""
        end = LABELS[r["axis"]][1].get(word)
        r["ends"] = {e: e == end for e in AXES[r["axis"]]["ends"]}
    minutes = (time.time() - started) / 60
    meta = [{"name": n, "axis": ax, "pick": m} for n, ax, _, m in conditions]
    save("42-selfread", lambda: write_up(rows, picks, meta, minutes), {"rows": rows, "picks": picks, "conditions": meta})


def write_up(rows, picks, meta, minutes) -> str:
    lines = [
        "# 42. Do the neurons that read a trait become the model's own trait?\n",
        intro(__doc__) + "\n",
        f"Run time: {minutes:.0f} min.\n",
        "## The readers\n",
    ]
    lines += table(["axis", "reads", "neuron", "paired score", "logit lens (dosed toward what it reads)"],
                   [[p["axis"], p["end"], f"L{p['layer']} #{p['index']}", f"{p['score']:+.2f}", p["lens"]] for p in picks])
    for axis, a in AXES.items():
        e0, e1 = a["ends"]
        lines.append(f"\n## {axis}: answers at the {e0} end / at the {e1} end (of {3 * SAMPLES})\n")
        trows = []
        for m in meta:
            if m["axis"] not in (axis, None):
                continue
            mine = [r for r in rows if r["condition"] == m["name"] and r["axis"] == axis]
            per = " / ".join(f"{sum(r['ends'][e0] for r in mine if r['kind'] == k)}-{sum(r['ends'][e1] for r in mine if r['kind'] == k)}"
                             for k in a["questions"])
            trows.append([m["name"], rate(r["ends"][e0] for r in mine), rate(r["ends"][e1] for r in mine), per])
        lines += table(["condition", e0, e1, " / ".join(a["questions"]) + f" ({e0}-{e1})"], trows)
        lines.append("")
    lines.append("## Answers\n")
    for m in meta:
        mine = [r for r in rows if r["condition"] == m["name"]]
        lines.append(f"**{m['name']}**  ")
        for r in mine[::SAMPLES][:9]:
            lines.append(f"> *{r['kind']}*: {flat(r['text'], 140)}  ")
        lines.append("")
    lines.append(f"Mean share of answers with either end: {mean(any(r['ends'].values()) for r in rows):.2f}.\n")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
