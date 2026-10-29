"""Decide how big "dose 1" is for each feature, and whether to steer with its vector or its neurons.

Every candidate setting (a layer for the vector, or a neuron count k, times a strength, times +/-) is
generated in ONE batch - each row of the batch gets its own dose - and the unsteered model then judges
every reply. Dose 1 becomes the strongest setting whose replies it still rates as coherent.
"""
from __future__ import annotations

import re

import torch

from .data import JUDGE_COHERENCE, JUDGE_TRAIT, TRAITS
from .model import Edit, Model

MIN_COHERENCE = 6.0  # on the judge's 0-9 scale
VECTOR_STRENGTHS = (0.4, 0.7, 1.0, 1.4)  # |dose * vector| as a fraction of the residual-stream norm there
NEURON_STRENGTHS = (1.0, 2.0, 4.0, 8.0)  # summed |push| of all dosed neurons, same units


def judge(model: Model, texts: list[str], trait: str | None = None, batch_size: int = 8) -> torch.Tensor:
    """0-9 from the unsteered model: how strongly each text shows `trait`, or how coherent it is."""
    if trait:
        t = TRAITS[trait]
        prompts = [JUDGE_TRAIT.format(pos=t.pos, neg=t.neg, text=x) for x in texts]
    else:
        prompts = [JUDGE_COHERENCE.format(text=x) for x in texts]
    return model.digit_scores([model.chat_ids(p) for p in prompts], batch_size=batch_size)[0]


def mentions(text: str, keywords: list[str]) -> bool:
    return any(re.search(rf"\b{re.escape(k)}", text, re.IGNORECASE) for k in keywords)


def neuron_edits(feature: dict, k: int, dose, d_mlp: int) -> list[Edit]:
    """Add dose * delta to each of the feature's top-k neurons (grouped into one sparse edit per layer)."""
    n = feature["neurons"]
    layers, index, delta = n["layer"][:k], n["index"][:k], n["delta"][:k]
    edits = []
    for layer in layers.unique().tolist():
        sel = layers == layer
        v = torch.zeros(d_mlp)
        v[index[sel]] = delta[sel].float()
        edits.append(Edit(layer, v, site="neurons", dose=dose))
    return edits


def neuron_push(model: Model, feature: dict, k: int) -> float:
    """Summed norm of what the top-k neurons write into the residual stream at dose 1."""
    total = 0.0
    for e in neuron_edits(feature, k, 1.0, model.d_mlp):
        w = model.layers[e.layer].mlp.down_proj.weight
        total += (w.float() @ e.vector.to(w.device)).norm().item()
    return total


def settings_for(model: Model, feature: dict, layers: list[int], ks: list[int]) -> list[dict]:
    norms, vec = feature["resid_norm"], feature["vector"]
    out = [
        {"mode": "vector", "layer": l, "strength": s, "unit": s * norms[l].item() / vec[l].norm().item()}
        for l in layers
        for s in VECTOR_STRENGTHS
    ]
    ref = norms[layers[len(layers) // 2]].item()
    for k in ks:
        push = neuron_push(model, feature, k)
        out += [{"mode": "neurons", "k": k, "strength": s, "unit": s * ref / push} for s in NEURON_STRENGTHS]
    return out


def sweep(
    model: Model, feature: dict, settings: list[dict], prompts: list[str], signs=(1, -1),
    max_new_tokens: int = 80, seed: int = 0,
) -> list[dict]:
    """Generate every setting x sign x prompt in a single batch; returns one row per reply."""
    rows = [{"setting": i, "sign": sg, "prompt": p} for i in range(len(settings)) for sg in signs for p in prompts]

    def doses(match):
        return torch.tensor(
            [r["sign"] * settings[r["setting"]]["unit"] if match(settings[r["setting"]]) else 0.0 for r in rows]
        )

    edits = []
    for layer in sorted({s["layer"] for s in settings if s["mode"] == "vector"}):
        d = doses(lambda s: s["mode"] == "vector" and s["layer"] == layer)
        edits.append(Edit(layer, feature["vector"][layer], dose=d))
    for k in sorted({s["k"] for s in settings if s["mode"] == "neurons"}):
        d = doses(lambda s: s["mode"] == "neurons" and s["k"] == k)
        edits += neuron_edits(feature, k, d, model.d_mlp)
    with model.steer(edits):
        replies = model.generate(
            [model.chat_ids(r["prompt"]) for r in rows], max_new_tokens=max_new_tokens,
            temperature=0.7, batch_size=len(rows), seed=seed,
        )
    for r, ids in zip(rows, replies):
        r["text"] = model.decode(ids)
    return rows


def calibrate(
    model: Model, feature: dict, prompts: list[str], layers: list[int], ks: list[int],
    trait: str | None = None, keywords: list[str] | None = None,
) -> tuple[dict, list[dict], list[dict]]:
    """Pick dose 1 for the vector and for the neurons of a trait (judged on both poles) or of an entity
    (judged by whether the model brings it up). Returns (choice, settings with scores, all replies)."""
    settings = settings_for(model, feature, layers, ks)
    rows = sweep(model, feature, settings, prompts, signs=(1, -1) if trait else (1,))
    texts = [r["text"] for r in rows]
    coherence = judge(model, texts)
    effect = judge(model, texts, trait) if trait else torch.tensor([float(mentions(x, keywords)) for x in texts])
    for r, c, e in zip(rows, coherence.tolist(), effect.tolist()):
        r["coherence"], r["effect"] = round(c, 2), round(e, 2)

    for i, s in enumerate(settings):
        mine = [r for r in rows if r["setting"] == i]
        up = [r["effect"] for r in mine if r["sign"] > 0]
        down = [r["effect"] for r in mine if r["sign"] < 0]
        # trait: how far apart +dose and -dose replies land; entity: how often it gets mentioned
        s["score"] = round(sum(up) / len(up) - (sum(down) / len(down) if down else 0.0), 2)
        s["coherence"] = round(min(
            sum(r["coherence"] for r in mine if r["sign"] == sg) / len(prompts) for sg in {r["sign"] for r in mine}
        ), 2)

    choice = {}
    for mode in ("vector", "neurons"):
        options = [s for s in settings if s["mode"] == mode]
        ok = [s for s in options if s["coherence"] >= MIN_COHERENCE] or [max(options, key=lambda s: s["coherence"])]
        choice[mode] = max(ok, key=lambda s: (s["score"], -s["strength"]))
    return choice, settings, rows


def apply_choice(feature: dict, summary: dict, choice: dict, settings: list[dict]):
    """Store what calibration picked: the feature gets the numbers steering needs, the summary the record."""
    v, n = choice["vector"], choice["neurons"]
    feature.update(layer=v["layer"], unit=v["unit"], strength=v["strength"], k=n["k"], neuron_unit=n["unit"])
    summary.update(layer=v["layer"], vector=v, neurons=n, settings=settings)
