"""Experiment 30: where in the first tenth is the damage? A few giant neurons, or a gradient?

Experiment 23 found that silencing the first 10% of every MLP layer of Qwen3-4B raises the loss on Wikipedia by 5.7
nats per token, 14x a random 10%, and more than silencing the last half of every layer. Qwen3-0.6B-Base is the
same; Qwen2.5-1.5B is not. A known alternative: LLMs have a handful of "super weight" / massive-activation neurons,
usually in early layers, whose removal alone wrecks the model (Yu et al. 2024; Sun et al. 2024). If Qwen3's sit at
low indices, the first tenth's damage could be theirs alone.

Hypotheses:
  H1 (giants) most of the damage comes from a few neurons: sparing each layer's 10 most active neurons (largest
     |activation| on any token) removes most of it, and silencing those 10 per layer alone does most of it.
  H2 (gradient) the damage falls smoothly with the index: 1% windows of indices hurt less and less across the first
     tenth, and each hurts more than a random 1%.
  H3 (activity order) the index is an activity rank: silencing each layer's most active 10% (mean |activation|)
     hurts about as much as the first 10%. In Qwen2.5 the most active 10% hurts too, but sits at random indices.
  H4 (spread) the damage comes from many layers, not one or two early ones.

Method: Wikipedia in English, Chinese and Russian, 8 articles each (first 128 tokens), next-token loss as in
experiment 23. Activity is measured on 8 other articles per language. Conditions, in every layer at once: the first
10%; random 10% (2 draws); the most active 10%; the 10 giants (largest max |activation|); the first 10% sparing the
giants; a random 10% plus the giants; 1% windows at 0-9%, 20%, 50% and 90% of the indices, and a random 1%. For the
Qwen3 models also the first 10% of one layer at a time, and a random 10% of every sixth layer. Models:
Qwen3-4B-Instruct-2507, Qwen3-0.6B-Base, Qwen2.5-1.5B-Instruct.

python -m persona_lab.lab.locate
"""
from __future__ import annotations

import gc
import time

import torch

from ..model import Model, batches
from .common import intro, mean, save, spark, table
from .cut import cut, loss, wiki

MODELS = ("Qwen/Qwen3-4B-Instruct-2507", "Qwen/Qwen3-0.6B-Base", "Qwen/Qwen2.5-1.5B-Instruct")
LANGS = ("en", "zh", "ru")
DOCS, TOKENS, GIANTS = 8, 128, 10
WINDOWS = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 20, 50, 90)  # start of each 1% window, in % of the layer


@torch.inference_mode()
def activity(model: Model, docs: list[list[int]]) -> tuple[torch.Tensor, torch.Tensor]:
    """Per layer and neuron: mean |activation| and max |activation| over every token of the docs."""
    L, d = model.n_layers, model.d_mlp
    total, peak = torch.zeros(L, d), torch.zeros(L, d)
    count = 0
    handles = []
    for l in range(L):
        def fn(module, args, l=l):
            a = args[0].detach().abs().float().reshape(-1, d)
            total[l] += a.sum(0).cpu()
            peak[l] = torch.maximum(peak[l], a.max(0).values.cpu())
        handles.append(model.layers[l].mlp.down_proj.register_forward_pre_hook(fn))
    try:
        for batch in batches(docs, 8):
            ids = torch.tensor(batch, device=model.device)
            model.model.model(input_ids=ids, use_cache=False)
            count += ids.numel()
    finally:
        for h in handles:
            h.remove()
    return total / count, peak


def conditions(model: Model, act_mean: torch.Tensor, act_peak: torch.Tensor, per_layer: bool) -> dict:
    d, every = model.d_mlp, range(model.n_layers)
    k, w = int(0.10 * d), int(0.01 * d)

    def rand(n, seed):
        g = torch.Generator().manual_seed(seed)
        return {l: torch.randperm(d, generator=g)[:n] for l in every}
    first = torch.arange(k)
    giants = {l: act_peak[l].topk(GIANTS).indices for l in every}
    r1 = rand(k, 1)
    out = {"none": {}, "first 10%": {l: first for l in every}, "random 10%": r1, "random 10% (draw 2)": rand(k, 2),
           "most active 10%": {l: act_mean[l].topk(k).indices for l in every},
           f"the {GIANTS} giants": giants,
           "first 10%, sparing the giants": {l: first[~torch.isin(first, giants[l])] for l in every},
           "random 10% plus the giants": {l: torch.unique(torch.cat([r1[l], giants[l]])) for l in every}}
    for s in WINDOWS:
        start = int(s / 100 * d)
        out[f"window {s}%"] = {l: torch.arange(start, start + w) for l in every}
    out["random 1%"] = rand(w, 3)
    if per_layer:
        for l in every:
            out[f"layer {l}: first 10%"] = {l: first}
        for l in every[::6]:
            g = torch.Generator().manual_seed(100 + l)
            out[f"layer {l}: random 10%"] = {l: torch.randperm(d, generator=g)[:k]}
    return out


def main():
    started = time.time()
    texts = {lang: wiki(lang) for lang in LANGS}
    results = []
    for name in MODELS:
        model = Model(name)
        docs, held = [], []
        for lang, ts in texts.items():
            ids = [x[:TOKENS] for x in (model.tok(t, add_special_tokens=False).input_ids for t in ts) if len(x) >= TOKENS]
            docs += ids[:DOCS]
            held += ids[DOCS:2 * DOCS]
        act_mean, act_peak = activity(model, held)
        d = model.d_mlp
        flat_peak = act_peak.flatten()
        top = flat_peak.topk(12).indices
        giants = [{"layer": int(i // d), "index": int(i % d), "max": round(flat_peak[i].item(), 1),
                   "layer_median_max": round(act_peak[int(i // d)].median().item(), 2)} for i in top]
        rho = []
        for l in range(model.n_layers):
            r = act_mean[l].argsort().argsort().float()
            rho.append(torch.corrcoef(torch.stack([r, torch.arange(d, dtype=torch.float32)]))[0, 1].item())
        active = torch.stack([act_mean[l].topk(int(0.1 * d)).indices for l in range(model.n_layers)]).float() / d
        res = {"model": name, "d_mlp": d, "n_layers": model.n_layers, "giants": giants,
               "rho_index_activity": round(mean(rho), 3), "active_median_index": round(active.median().item(), 3),
               "giants_in_first_tenth": round((act_peak.topk(GIANTS, dim=1).indices < int(0.1 * d)).float().mean().item(), 3),
               "loss": {}}
        is_qwen3 = "Qwen3" in name
        for cname, which in conditions(model, act_mean, act_peak, per_layer=is_qwen3).items():
            with cut(model, which):
                res["loss"][cname] = round(loss(model, docs), 4)
            print(f"[{name}] {cname}: {res['loss'][cname]:.3f} ({time.time() - started:.0f}s)", flush=True)
        results.append(res)
        del model
        gc.collect()
        if torch.backends.mps.is_available():
            torch.mps.empty_cache()
    minutes = (time.time() - started) / 60
    save("30-locate", lambda: write_up(results, minutes), {"results": results})


def write_up(results, minutes) -> str:
    lines = [
        "# 30. Where in the first tenth is the damage?\n",
        intro(__doc__) + "\n",
        f"Run time: {minutes:.0f} min.\n",
    ]
    for r in results:
        L = r["loss"]
        dmg = {c: v - L["none"] for c, v in L.items()}
        lines.append(f"## {r['model']}\n")
        lines.append(f"Loss with no cut: {L['none']:.3f} nats per token. Index vs. mean activity, Spearman rho averaged over "
                     f"layers: {r['rho_index_activity']:+.2f}. The most active 10% of each layer sit at a median index of "
                     f"{r['active_median_index']:.0%} of the layer. Share of each layer's {GIANTS} giants in its first tenth: "
                     f"{r['giants_in_first_tenth']:.0%} (chance 10%).\n")
        main_ = ["first 10%", "random 10%", "random 10% (draw 2)", "most active 10%", f"the {GIANTS} giants",
                 "first 10%, sparing the giants", "random 10% plus the giants", "random 1%"]
        lines += table(["silenced in every layer", "increase in loss (nats per token)"],
                       [[c, f"{dmg[c]:+.3f}"] for c in main_])
        ws = [f"window {s}%" for s in WINDOWS]
        lines.append(f"\n1% windows of indices (every layer), from the front: `{spark([dmg[w] for w in ws], 0, max(dmg[w] for w in ws))}`\n")
        lines += table(["window starts at"] + [f"{s}%" for s in WINDOWS] + ["random 1%"],
                       [["increase in loss"] + [f"{dmg[w]:+.2f}" for w in ws] + [f"{dmg['random 1%']:+.2f}"]])
        lines.append("\nThe largest activations in the model (the giants):\n")
        lines += table(["layer", "index", "share of the layer", "max |activation|", "median neuron's max in that layer"],
                       [[g["layer"], g["index"], f"{g['index'] / r['d_mlp']:.1%}", g["max"], g["layer_median_max"]]
                        for g in r["giants"][:8]])
        per = [dmg.get(f"layer {l}: first 10%") for l in range(r["n_layers"])]
        if per[0] is not None:
            lines.append(f"\nThe first 10% of one layer at a time, layer 0 -> {r['n_layers'] - 1}: "
                         f"`{spark(per, 0, max(per))}` (sum {sum(per):+.2f}, against {dmg['first 10%']:+.2f} for all at once).\n")
            top = sorted(range(len(per)), key=lambda l: -per[l])[:6]
            lines += table(["layer"] + [str(l) for l in top], [["increase in loss"] + [f"{per[l]:+.3f}" for l in top]])
            rnd = {c: v for c, v in dmg.items() if c.endswith(": random 10%")}
            lines.append("\nA random 10% of one layer: " + ", ".join(f"{c.split(':')[0]} {v:+.3f}" for c, v in rnd.items()) + ".\n")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
