"""Experiment 19: is a neuron's index in Qwen3-4B arbitrary?

Every activation-ranked language neuron in experiment 14 had an index under 1,100 (of 9,728), and so did most of the
weight-ranked language candidates in experiments 1 and 1b. The top personality neurons are also twice as likely as
chance to sit in the first 1,024. In a freshly trained network, the order of an MLP's neurons means nothing:
permuting them changes nothing. So either this checkpoint's neurons were ordered by something during training (or
after it), or the rankings are biased by some property that happens to trend with index.

Hypotheses:
  H1 neuron statistics trend with index: weight norms and typical activation size differ between low and high
     indices, in every layer.
  H2 low-index neurons are over-represented among neurons that respond to instructions (reply in Chinese; be
     formal; the personality traits), even after the per-neuron spread is divided out (d = effect / spread).
  H3 the effect is a gradient over index, not a block (e.g. not "the first 1,024 and then nothing").

Method: 19 buckets of 512 neurons by index. Weights: down_proj column norms and gate/up row norms, every layer.
Activations: mean |activation| per neuron over 64 FineWeb-Edu documents (256 tokens each). Instruction sensitivity:
the paired contrast of experiment 14 ("always reply in Chinese" vs "in English"; "be extremely formal" vs "be super
casual") on 24 identical replies, as |d| per neuron; and the top-500 neurons of every trait and entity from
`pl extract` / `pl entity` (features.pt). For each, the share of the top 1% (or top 500) that falls in each bucket;
chance is 1/19 = 5.3%.

python -m persona_lab.lab.index
"""
from __future__ import annotations

import json
import time

import torch

from ..extract import READ_TOKENS
from ..model import batches
from .common import OUT, RUN_DIR, intro, load, save, spark, table
from .language import generations

BUCKET = 512
CONTRASTS = {
    "reply in Chinese vs English": ("Always reply in Chinese (简体中文), whatever language the user writes in.",
                                    "Always reply in English, whatever language the user writes in."),
    "be formal vs casual": ("You are extremely formal and proper; use refined vocabulary and impeccable etiquette.",
                            "You are super casual and slangy; talk like you're texting a buddy."),
}


def bucket_of(index: torch.Tensor, d_mlp: int) -> torch.Tensor:
    return (index // BUCKET).clamp(max=(d_mlp - 1) // BUCKET)


def shares(indices: torch.Tensor, d_mlp: int) -> list[float]:
    """Share of `indices` that falls in each bucket."""
    n = (d_mlp - 1) // BUCKET + 1
    counts = torch.bincount(bucket_of(indices.long(), d_mlp), minlength=n).float()
    return (counts / counts.sum()).tolist()


@torch.inference_mode()
def weight_stats(model) -> dict[str, list[float]]:
    out = {"down": [], "up": [], "gate": []}
    for layer in model.layers:
        out["down"].append(layer.mlp.down_proj.weight.float().norm(dim=0).cpu())
        out["up"].append(layer.mlp.up_proj.weight.float().norm(dim=1).cpu())
        out["gate"].append(layer.mlp.gate_proj.weight.float().norm(dim=1).cpu())
    return {k: torch.stack(v) for k, v in out.items()}  # [n_layers, d_mlp]


@torch.inference_mode()
def activation_size(model, docs) -> torch.Tensor:
    """Mean |activation| of every neuron over the documents' tokens: [n_layers, d_mlp]."""
    total = torch.zeros(model.n_layers, model.d_mlp, device=model.device)
    count = [0]

    def hook(i):
        def fn(module, args):
            a = args[0].float().abs()
            total[i] += a.sum((0, 1))
            if i == 0:
                count[0] += a.shape[0] * a.shape[1]
        return fn

    handles = [layer.mlp.down_proj.register_forward_pre_hook(hook(i)) for i, layer in enumerate(model.layers)]
    try:
        for batch in batches(docs, 8):
            width = min(map(len, batch))  # equal lengths, so no padding enters the sums
            ids = torch.tensor([d[:width] for d in batch], device=model.device)
            model.model.model(input_ids=ids, use_cache=False)
    finally:
        for h in handles:
            h.remove()
    return (total / count[0]).cpu()


@torch.inference_mode()
def contrast_d(model, run, system_a, system_b) -> torch.Tensor:
    """|effect / spread| of every neuron for system prompt a vs b, on identical reply tokens: [n_layers, d_mlp]."""
    replies = generations(run)
    toks = [r["ids"][:READ_TOKENS] for r in replies]
    _, na = model.response_means([model.chat_ids(r["question"], system_a) for r in replies], toks, neurons=True)
    _, nb = model.response_means([model.chat_ids(r["question"], system_b) for r in replies], toks, neurons=True)
    diff = na.float() - nb.float()
    return (diff.mean(0) / diff.std(0).clamp(min=1e-6)).abs()


def top_share(score: torch.Tensor, frac: float, d_mlp: int, layers=None) -> list[float]:
    """Bucket shares of the top `frac` neurons by score (over the given layers, default: middle 80%)."""
    lo, hi = layers or (round(0.1 * score.shape[0]), round(0.9 * score.shape[0]))
    s = score[lo:hi].flatten()
    top = s.topk(max(1, int(frac * s.numel()))).indices
    return shares(top % d_mlp, d_mlp)


def main():
    started = time.time()
    run, model = load()
    d_mlp = model.d_mlp
    w = weight_stats(model)
    corpus = OUT / "data" / "corpus" / "fineweb-edu.jsonl"
    texts = [json.loads(line)["text"] for line in corpus.read_text().splitlines()][:200] if corpus.exists() else []
    docs = [ids[:256] for ids in (model.tok(t, add_special_tokens=False).input_ids for t in texts) if len(ids) >= 256][:64]
    act = activation_size(model, docs)
    d = {name: contrast_d(model, run, a, b) for name, (a, b) in CONTRASTS.items()}
    feats = torch.load(RUN_DIR / "features.pt")
    rows = {}
    nb = (d_mlp - 1) // BUCKET + 1
    for kind in ("down", "up", "gate"):
        per_bucket = [w[kind][:, b * BUCKET:(b + 1) * BUCKET].mean().item() for b in range(nb)]
        rows[f"weight norm: {kind}"] = per_bucket
    rows["mean |activation| on web text"] = [act[:, b * BUCKET:(b + 1) * BUCKET].mean().item() for b in range(nb)]
    for name, score in d.items():
        rows[f"top 1% |d|: {name}"] = top_share(score, 0.01, d_mlp)
    for kind in ("trait", "entity"):
        idx = torch.cat([f["neurons"]["index"][:500] for f in feats.values() if f["kind"] == kind])
        rows[f"top 500 neurons of every {kind}"] = shares(idx, d_mlp)
    per_layer = {name: [top_share(score, 0.01, d_mlp, (l, l + 1))[0] for l in range(model.n_layers)]
                 for name, score in d.items()}
    minutes = (time.time() - started) / 60
    save("19-index", lambda: write_up(rows, per_layer, w, nb, minutes), {"rows": rows, "per_layer_first_bucket": per_layer})


def write_up(rows, per_layer, w, nb, minutes) -> str:
    lines = [
        "# 19. Is a neuron's index arbitrary?\n",
        intro(__doc__) + "\n",
        f"Run time: {minutes:.0f} min. Buckets of {BUCKET} neurons by index: bucket 0 = neurons 0-511, ..., bucket {nb - 1} "
        f"= the last {9728 - (nb - 1) * BUCKET}. Chance share per bucket: {1 / nb:.1%}.\n",
        "## By index bucket\n",
    ]
    trows = []
    for name, vals in rows.items():
        share = name.startswith("top")
        lo, hi = (0, max(vals)) if share else (min(vals), max(vals))
        cells = [f"{v:.0%}" if share else f"{v:.3g}" for v in (vals[0], vals[1], vals[2], vals[nb // 2], vals[-1])]
        trows.append([name] + cells + [f"`{spark(vals, lo, hi)}`"])
    lines += table(["statistic", "bucket 0", "bucket 1", "bucket 2", f"bucket {nb // 2}", f"bucket {nb - 1}",
                    f"all {nb} buckets, low index -> high"], trows)
    lines.append("\n## Where in the network: share of each layer's top-1% neurons that sit in bucket 0 (chance "
                 f"{1 / nb:.1%})\n")
    prow = [[name] + [f"`{spark(vals, 0, 1)}`", f"{max(vals):.0%} (layer {vals.index(max(vals))})"] for name, vals in per_layer.items()]
    lines += table(["contrast", "layers 0 -> 35", "highest"], prow)
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
