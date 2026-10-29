"""Experiment 43: does a reader's logit lens predict which way it steers?

A neuron that fires on a concept in text doesn't always push the model toward that concept when dosed. #386 reads
East Asian names and, dosed up, makes Qwen say it comes from Korea; #188, the second-best reader in the same layer,
makes it say Switzerland (36). Readers of cats, dogs and women's names in 42 steered the other way too. In the
cases so far, the readers that steer their own way had logit lenses that name the concept (Taiwan, 日本, Korea,
老人), and the reversed ones had noise. If that holds over many neurons, the logit lens is a cheap way to tell a
neuron that writes a concept from one that only detects it (and perhaps suppresses it).

Hypotheses:
  H1 over the 30 best East-vs-West readers of layers 14-31, a neuron's logit-lens East score (East Asian minus
     Western place and company tokens, in the direction East Asian names move it) correlates with its steering: how
     far dosing it in that direction moves "name one" and origin answers toward East Asia.
  H2 a sizable share of strong readers steer against what they read (at least a quarter).

Method: experiment 34's 36 sentence templates, every neuron of layers 14-31 scored by its paired East-minus-West
difference over its spread; the 20 best East readers and 10 best West readers (each at most 4 per layer). Each is
dosed in the direction East Asian names move it (up for East readers, down for West readers), at 1.25x the strength
of #386 at 98, on 5 questions (where it comes from; a city,
a car brand, a tech company, a dish) x 3 samples (24 tokens, temperature 0.8); the unsteered model labels each
answer's country as in 32. Steering = change in the East Asian share of answers: positive is toward what the
dosed direction reads (East Asia). 3 random neurons give the noise level.

python -m persona_lab.lab.congruence
"""
from __future__ import annotations

import random
import statistics
import time

import torch

from .common import act_for, generate, intro, lens, load, mean, save, strength_of, table
from .eastwest import TEMPLATES
from .origin import EAST, LABEL, country

LAYERS = range(14, 32)
EAST_WORDS = [" China", " Chinese", " Japan", " Japanese", " Korea", " Korean", " Beijing", " Tokyo", " Seoul",
              " Shanghai", " Asia", " Asian", " Taiwan", " Kyoto", " Samsung", " Toyota", " Alibaba", " Hong", "中国",
              "日本", "韩国"]
WEST_WORDS = [" America", " American", " USA", " Europe", " European", " London", " Paris", " Berlin", " English",
              " British", " France", " German", " Germany", " California", " Canada", " Ford", " Google", " OpenAI",
              " Switzerland", " Italy", " Italian"]
QUESTIONS = {
    "from": "Which country are you from? Answer in one sentence.",
    "city": "Name a city you would recommend visiting. Answer with just the name.",
    "car brand": "Name a popular car brand. Answer with just the name.",
    "tech company": "Name a famous technology company. Answer with just the name.",
    "dish": "Suggest one dish for dinner tonight. Answer with just the name of the dish.",
}
N_EAST, N_WEST, PER_LAYER, STRENGTH = 20, 10, 4, 1.25
SAMPLES, TOKENS = 3, 24


@torch.inference_mode()
def read(model, sentence: str, name: str) -> torch.Tensor:
    prefix = model.tok(sentence[:sentence.index(name)], add_special_tokens=False).input_ids
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


def token_ids(model, words) -> list[int]:
    out = []
    for w in words:
        ids = model.tok(w, add_special_tokens=False).input_ids
        if len(ids) == 1:
            out.append(ids[0])
    return out


@torch.inference_mode()
def lens_east(model, layer: int, index: int, east: list[int], west: list[int]) -> float:
    """Logit-lens East score of a neuron's output: mean logit of East tokens minus Western ones, in units of the
    logits' spread over the whole vocabulary."""
    w = model.layers[layer].mlp.down_proj.weight[:, index]
    logits = (model.model.lm_head.weight @ (w * model.model.model.norm.weight)).float()
    return ((logits[east].mean() - logits[west].mean()) / logits.std()).item()


def choose(score: torch.Tensor, n: int, sign: int) -> list[tuple[int, int, float]]:
    s = (sign * score).flatten()
    out, per = [], {}
    for j in s.argsort(descending=True).tolist():
        l, i = divmod(j, score.shape[1])
        if per.get(l, 0) >= PER_LAYER:
            continue
        per[l] = per.get(l, 0) + 1
        out.append((l + LAYERS[0], i, score[l, i].item()))
        if len(out) == n:
            return out
    return out


def main():
    started = time.time()
    run, model = load()
    acts = torch.stack([torch.stack([read(model, t.format(n), n) for n in names]) for t, *names in TEMPLATES])
    diff = acts[:, :3].mean(1) - acts[:, 3]
    score = diff.mean(0) / diff.std(0).clamp_min(1e-6)
    east, west = token_ids(model, EAST_WORDS), token_ids(model, WEST_WORDS)
    s0 = strength_of(model, run, {"layer": 24, "index": 386, "act": 98.0})
    readers = [(l, i, v, 1) for l, i, v in choose(score, N_EAST, 1)] + [(l, i, v, -1) for l, i, v in choose(score, N_WEST, -1)]
    neurons = []
    for l, i, v, reads in readers:
        neurons.append({"layer": l, "index": i, "score": round(v, 2), "reads": "East" if reads > 0 else "West",
                        "reads_sign": reads, "lens_east": round(lens_east(model, l, i, east, west), 3),
                        "lens": lens(model, {"layer": l, "index": i, "act": reads}),
                        "act": act_for(model, run, l, i, STRENGTH * s0, reads)})
    rng = random.Random(43)
    randoms = []
    for _ in range(3):
        l = rng.choice(list(LAYERS))
        j = rng.randrange(model.d_mlp)
        randoms.append({"layer": l, "index": j, "act": act_for(model, run, l, j, STRENGTH * s0, rng.choice((1, -1)))})
    conditions = [("undosed", [])] + [(f"L{n['layer']} #{n['index']}", [{k: n[k] for k in ("layer", "index", "act")}])
                                      for n in neurons] + [(f"random L{c['layer']} #{c['index']}", [c]) for c in randoms]
    rows = [{"condition": name, "kind": k, "prompt": q, "doses": doses}
            for name, doses in conditions for k, q in QUESTIONS.items() for _ in range(SAMPLES)]
    generate(model, rows, TOKENS, seed=43, temperature=0.8, desc="congruence")
    prompts = [model.chat_ids(LABEL.format(q=r["prompt"], a=r["text"].strip()[:200])) for r in rows]
    for r, ids in zip(rows, model.generate(prompts, max_new_tokens=6, temperature=0, batch_size=16)):
        r["country"] = country(model.decode(ids).strip())
        r["east"] = r["country"].lower() in EAST
    base = mean(r["east"] for r in rows if r["condition"] == "undosed")
    for n in neurons:
        share = mean(r["east"] for r in rows if r["condition"] == f"L{n['layer']} #{n['index']}")
        n["east_share"] = round(share, 3)
        n["steer"] = round(share - base, 3)  # every neuron is dosed the way East Asian names move it
        n["lens_agrees"] = round(n["lens_east"] * n["reads_sign"], 3)
    rand = [round(mean(r["east"] for r in rows if r["condition"] == f"random L{c['layer']} #{c['index']}") - base, 3)
            for c in randoms]
    minutes = (time.time() - started) / 60
    save("43-congruence", lambda: write_up(neurons, base, rand, minutes),
         {"neurons": neurons, "base": base, "random_shifts": rand, "randoms": randoms, "rows": rows})


def ranks(v: list[float]) -> list[float]:
    order = sorted(range(len(v)), key=lambda i: v[i])
    out = [0.0] * len(v)
    i = 0
    while i < len(v):
        j = i
        while j + 1 < len(v) and v[order[j + 1]] == v[order[i]]:
            j += 1
        for k in range(i, j + 1):
            out[order[k]] = (i + j) / 2
        i = j + 1
    return out


def write_up(neurons, base, rand, minutes) -> str:
    xs = [n["lens_agrees"] for n in neurons]
    ys = [n["steer"] for n in neurons]
    rho = statistics.correlation(ranks(xs), ranks(ys))
    r = statistics.correlation(xs, ys)
    up, down = max(max(rand), 0.0) + 0.1, min(min(rand), 0.0)  # random neurons only lower the share here
    toward = sum(y > up for y in ys)
    against = sum(y < down for y in ys)
    lens_yes = [n for n in neurons if n["lens_agrees"] > 0.5]
    lens_no = [n for n in neurons if n["lens_agrees"] <= 0.5]
    lines = [
        "# 43. Does a reader's logit lens predict which way it steers?\n",
        intro(__doc__) + "\n",
        f"Run time: {minutes:.0f} min. Undosed East Asian share: {base:.0%} of {len(QUESTIONS) * SAMPLES} answers. "
        f"Random neurons shift it by {', '.join(f'{x:+.0%}' for x in rand)}. The undosed answers lean East Asian (Kyoto, "
        "Toyota), so a disruption tends to lower the share: a rise is better evidence than a fall.\n",
        "## Lens vs. steering\n",
        f"- Correlation over the {len(neurons)} readers between the lens agreeing with what the neuron reads and its "
        f"steering toward what it reads: Pearson r = {r:+.2f}, Spearman rho = {rho:+.2f}.\n",
        f"- {toward} raise the East Asian share by more than {up:.0%}, {against} lower it below the random neurons' "
        f"lowest ({down:+.0%}), {len(neurons) - toward - against} in between.\n",
        f"- Readers whose lens agrees (lens score > 0.5): mean steering {mean(n['steer'] for n in lens_yes):+.0%} "
        f"(n = {len(lens_yes)}); the rest: {mean(n['steer'] for n in lens_no):+.0%} (n = {len(lens_no)}).\n",
        "## The readers\n",
        "Score: paired East-minus-West reading (34). Lens agrees: logit-lens East score in the dosed direction, in "
        "standard deviations of the vocabulary's logits. Steering: change in the East Asian share of answers. The logit "
        "lens column lists the tokens the dosed direction promotes.\n",
    ]
    lines += table(["neuron", "reads", "reading score", "lens agrees", "steering", "East Asian share dosed", "logit lens"],
                   [[f"L{n['layer']} #{n['index']}", n["reads"], f"{n['score']:+.2f}", f"{n['lens_agrees']:+.2f}",
                     f"{n['steer']:+.0%}", f"{n['east_share']:.0%}", n["lens"]]
                    for n in sorted(neurons, key=lambda n: -n["lens_agrees"])])
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
