"""For each personality trait, find:

  1. a direction in the residual stream (one per layer) that separates the trait's two poles,
  2. the MLP neurons that drive the residual stream along that direction,
  3. how big "dose 1" is - for the vector and for the neurons - and at which layer (see calibrate.py),
  4. where the model's own default persona sits between the two poles.

Recipe for 1-2: take ordinary replies the model wrote, and read each one twice - once after a system
prompt giving the model the high pole of the trait, once after one giving it the low pole. The tokens
are identical, so any difference in the activations is the instruction's doing. The average difference
is the trait's vector; the per-neuron differences rank its neurons. (The control-vector recipe from
repeng, read over reply tokens as in Anthropic's persona vectors. Pairing makes it work even on small
models that are too weak to act a role out convincingly.)
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import torch

from .calibrate import apply_choice, calibrate
from .data import CALIBRATION_QUESTIONS, EXTRACT_QUESTIONS, SYSTEM_TEMPLATES, TRAITS
from .model import Model

N_VAL = 6  # extraction questions held back to measure how consistent the direction is
READ_TOKENS = 64  # reply tokens read per question
TOP_NEURONS = 4096  # neurons kept per feature
NEURON_COUNTS = (512, 2048)  # candidate k for neuron-only dosing
TRAIT_DEPTHS = (0.5, 0.65)  # candidate layers for the vector, as a fraction of depth


def generate_cached(model: Model, jobs: list[dict], path: Path, **gen_kwargs) -> list[list[int]]:
    """Generate a reply per job ({"system", "question"}), reusing replies already stored in `path`."""
    cache = {}
    if path.exists():
        for line in path.read_text().splitlines():
            rec = json.loads(line)
            cache[(rec["system"], rec["question"])] = rec["ids"]
    todo = [j for j in jobs if (j["system"], j["question"]) not in cache]
    if todo:
        replies = model.generate(
            [model.chat_ids(j["question"], j["system"]) for j in todo], desc="generating replies", **gen_kwargs
        )
        with path.open("a") as f:
            for j, ids in zip(todo, replies):
                cache[(j["system"], j["question"])] = ids
                f.write(json.dumps({**j, "text": model.decode(ids), "ids": ids}) + "\n")
    return [cache[(j["system"], j["question"])] for j in jobs]


def persona_prompts(model: Model, trait: str, pole: str, questions) -> list[list[int]]:
    desc = getattr(TRAITS[trait], pole)
    return [
        model.chat_ids(q, SYSTEM_TEMPLATES[i % len(SYSTEM_TEMPLATES)].format(desc=desc))
        for i, q in enumerate(questions)
    ]


def at_depths(model: Model, depths) -> list[int]:
    return [round(f * model.n_layers) for f in depths]


@torch.inference_mode()
def rank_neurons(
    model: Model, effect: torch.Tensor, spread: torch.Tensor, direction: torch.Tensor,
    resid_norm: torch.Tensor, top: int = TOP_NEURONS,
) -> dict:
    """Rank MLP neurons by how hard their average change pushes the residual stream along the feature.

    effect, spread: [n_layers, d_mlp] mean and spread of each neuron's change with the feature.
    direction:      [n_layers, d_model] the feature's vector at each layer's output.
    A neuron's push is effect * (its output weights . unit direction), as a fraction of the residual
    norm at its layer. Neurons that move inconsistently (|effect / spread| < 1) are skipped, and so are
    the first and last 10% of layers (token-level plumbing rather than persona).
    """
    floor = 0.1 * spread.median(dim=-1, keepdim=True).values
    d = effect / torch.maximum(spread, floor)
    push = torch.zeros_like(effect)
    lo, hi = round(0.1 * model.n_layers), round(0.9 * model.n_layers)
    for layer in range(lo, hi):
        u = direction[layer] / direction[layer].norm()
        w = model.layers[layer].mlp.down_proj.weight  # [d_model, d_mlp]
        align = (u.to(w.device, w.dtype) @ w).float().cpu()
        push[layer] = effect[layer] * align / resid_norm[layer]
    push[d.abs() < 1] = 0
    order = push.flatten().topk(min(top, push.numel())).indices
    d_mlp = effect.shape[-1]
    return {
        "layer": order // d_mlp,
        "index": order % d_mlp,
        "d": d.flatten()[order],
        "delta": effect.flatten()[order],
        "push": push.flatten()[order],
    }


def extract_traits(
    model: Model,
    run_dir: Path,
    traits: list[str],
    max_new_tokens: int = 128,
    gen_batch_size: int = 24,
    batch_size: int = 8,
    seed: int = 0,
    on_done=None,
) -> tuple[dict, dict, list[dict]]:
    """Returns ({trait: feature}, {trait: summary}, calibration replies); a feature is what `Run`
    stores and steers with. `on_done(features, summaries, replies)` is called after each trait, so a
    long run can be saved as it goes."""
    unknown = [t for t in traits if t not in TRAITS]
    if unknown:
        raise SystemExit(f"unknown traits {unknown}; known: {', '.join(TRAITS)}")
    question_sets = {TRAITS[t].questions or tuple(EXTRACT_QUESTIONS) for t in traits}
    generate_cached(  # the model's own uninstructed replies, for every question set at once
        model, [{"system": None, "question": q} for qs in question_sets for q in qs],
        run_dir / "generations.jsonl", max_new_tokens=max_new_tokens, batch_size=gen_batch_size, seed=seed,
    )
    prepared = {}

    def prepare(questions):
        if questions not in prepared:
            replies = generate_cached(model, [{"system": None, "question": q} for q in questions],
                                      run_dir / "generations.jsonl")
            replies = [r[:READ_TOKENS] for r in replies]
            neutral = [model.chat_ids(q) for q in questions]
            prepared[questions] = replies, model.response_means(neutral, replies, batch_size=batch_size)
        return prepared[questions]

    features, summaries, replies_out = {}, {}, []
    for t in traits:
        started = time.time()
        questions = TRAITS[t].questions or tuple(EXTRACT_QUESTIONS)
        replies, default_state = prepare(questions)
        resid_norm = default_state.norm(dim=-1).mean(0)  # [n_layers]
        pos, neg = persona_prompts(model, t, "pos", questions), persona_prompts(model, t, "neg", questions)
        hp, ap = model.response_means(pos, replies, neurons=True, batch_size=batch_size)
        hn, an = model.response_means(neg, replies, neurons=True, batch_size=batch_size)
        diffs = hp - hn  # [n_questions, n_layers, d_model], paired on identical tokens
        vector = diffs.mean(0)

        # does a direction found on some questions separate the poles on the held-out ones?
        fit, val = diffs[:-N_VAL], diffs[-N_VAL:]
        u = fit.mean(0) / fit.mean(0).norm(dim=-1, keepdim=True)
        proj = (val * u).sum(-1)
        consistency = proj.mean(0) / proj.std(0)

        nd = ap.float() - an.float()
        neurons = rank_neurons(model, nd.mean(0), nd.std(0), vector, resid_norm)
        feature = {"kind": "trait", "vector": vector, "resid_norm": resid_norm, "neurons": neurons}

        choice, settings, rows = calibrate(
            model, feature, list(TRAITS[t].eval_questions or CALIBRATION_QUESTIONS),
            layers=at_depths(model, TRAIT_DEPTHS), ks=list(NEURON_COUNTS), trait=t,
        )
        summary = {
            "kind": "trait",
            "top_neurons": [
                {"layer": int(l), "index": int(i), "d": round(float(d), 2), "push": round(float(p), 5)}
                for l, i, d, p in zip(*(neurons[x][:12] for x in ("layer", "index", "d", "push")))
            ],
        }
        apply_choice(feature, summary, choice, settings)
        layer = feature["layer"]

        # 0 = the default persona reads like the low-pole instruction, 1 = like the high-pole one
        v = vector[layer]
        position = ((default_state[:, layer] - hn[:, layer]).mean(0) @ v / (v @ v)).item()
        summary.update(consistency=round(consistency[layer].item(), 2), default_position=round(position, 3))

        replies = [{"feature": t, **settings[r["setting"]], **r} for r in rows]
        replies_out += replies
        features[t], summaries[t] = feature, summary
        vec_choice, neuron_choice = choice["vector"], choice["neurons"]
        print(
            f"[{t}] vector: layer {layer}, strength {vec_choice['strength']} -> swing {vec_choice['score']:+.1f}/9 "
            f"(coherence {vec_choice['coherence']:.1f}) | neurons: top-{neuron_choice['k']}, strength "
            f"{neuron_choice['strength']} -> swing {neuron_choice['score']:+.1f}/9 (coherence {neuron_choice['coherence']:.1f}) "
            f"| default position {position:.2f} | {time.time() - started:.0f}s"
        )
        if on_done:
            on_done({t: feature}, {t: summaries[t]}, replies)
    return features, summaries, replies_out
