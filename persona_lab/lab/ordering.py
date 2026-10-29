"""Experiment 22: is the neuron order a Qwen3 thing? (weights only, several models)

In Qwen3-4B-Instruct-2507, low-index MLP neurons are special: every activation-ranked language neuron sits in the
first 1,100 of 9,728 (experiment 14), personality neurons are twice as likely as chance to be there, and weight
norms drift with index (experiment 19). In a network trained from a random start, the order of the neurons in a
layer is arbitrary, so something in how this checkpoint was made put an order on them. If that something is part
of how Qwen3 is trained, other Qwen3 checkpoints should show it, and models from elsewhere shouldn't.

Hypotheses:
  H1 Qwen3 models show weight statistics that trend with neuron index; Qwen2.5 (the previous generation) and SmolLM2
     (another lab) don't.
  H2 the trend is already in a base model (Qwen3-0.6B-Base, never instruction-tuned), so it comes from pretraining.
  H3 in Qwen3, the neurons whose output weights most promote Chinese over English sit at low indices.

Method: weights only, read tensor by tensor from the safetensors files on the CPU. Per neuron: the norm of its
down_proj column and of its gate and up rows, and the weight-only "Chinese vs English" logit-lens z-score of
experiment 1. Per layer, the Spearman correlation of each with the neuron's index: about 0 if the order is random
(|rho| > 0.05 happens by chance in under 1% of layers at these widths). And the share of each model's top 1%
Chinese-promoting neurons (middle 80% of layers) that sit in the first tenth of indices: chance is 10%.

python -m persona_lab.lab.ordering
"""
from __future__ import annotations

import json
import re
import time
from pathlib import Path

import torch
from safetensors import safe_open
from transformers import AutoTokenizer

from .common import intro, mean, save, spark, table

MODELS = ["Qwen/Qwen3-4B-Instruct-2507", "Qwen/Qwen3-4B-Base", "Qwen/Qwen3-1.7B", "Qwen/Qwen3-1.7B-Base",
          "Qwen/Qwen3-0.6B", "Qwen/Qwen3-0.6B-Base", "Qwen/Qwen2.5-1.5B-Instruct", "HuggingFaceTB/SmolLM2-360M-Instruct"]


class Weights:
    """Tensors of a downloaded checkpoint, read one at a time."""

    def __init__(self, repo: str):
        snaps = sorted((Path.home() / ".cache/huggingface/hub" / f"models--{repo.replace('/', '--')}" / "snapshots").glob("*"))
        if not snaps:
            raise FileNotFoundError(f"{repo} isn't downloaded")
        self.path = snaps[-1]
        self.config = json.loads((self.path / "config.json").read_text())
        index = self.path / "model.safetensors.index.json"
        files = json.loads(index.read_text())["weight_map"] if index.exists() else None
        self.where = files or {k: "model.safetensors" for k in safe_open(self.path / "model.safetensors", "pt").keys()}

    def __getitem__(self, name: str) -> torch.Tensor:
        with safe_open(self.path / self.where[name], "pt") as f:
            return f.get_tensor(name).float()

    def unembedding_rows(self, chunk: int = 8192):
        """The unembedding matrix in chunks of rows (float32), so a 150k x 2560 matrix never sits in memory whole."""
        name = "lm_head.weight" if "lm_head.weight" in self.where else "model.embed_tokens.weight"
        with safe_open(self.path / self.where[name], "pt") as f:
            sl = f.get_slice(name)
            n = sl.get_shape()[0]
            for i in range(0, n, chunk):
                yield i, sl[i: min(i + chunk, n)].float()


def spearman(x: torch.Tensor) -> float:
    """Rank correlation of x with its own index."""
    n = x.numel()
    r = x.argsort().argsort().float()
    i = torch.arange(n, dtype=torch.float32)
    return torch.corrcoef(torch.stack([r, i]))[0, 1].item()


def chinese_scores(w: Weights, tok, n_layers: int) -> dict[int, torch.Tensor] | None:
    """Weight-only z-score of every neuron for promoting Chinese characters over English words (experiment 1b's
    --strict reference: words with and without a leading space)."""
    strs = [tok.decode([i]) for i in range(len(tok))]
    cjk = [i for i, s in enumerate(strs) if re.fullmatch(r"[一-鿿]+", s.strip()) and s.strip()]
    english = [i for i, s in enumerate(strs) if re.fullmatch(r" ?[a-z]{3,}", s)]
    if len(cjk) < 200:
        return None
    cjk_set, english_set = set(cjk), set(english)
    gram, total, rows = None, None, 0
    sums = {"cjk": None, "english": None}
    for start, c in w.unembedding_rows():
        c = c[: max(0, min(len(c), len(strs) - start))]
        if not len(c):
            break
        gram = c.T @ c if gram is None else gram + c.T @ c
        total = c.sum(0) if total is None else total + c.sum(0)
        rows += len(c)
        for key, members in (("cjk", cjk_set), ("english", english_set)):
            pick = [k for k in range(len(c)) if start + k in members]
            if pick:
                part = c[pick].sum(0)
                sums[key] = part if sums[key] is None else sums[key] + part
    gram /= rows
    ubar = total / rows
    diff = sums["cjk"] / len(cjk) - sums["english"] / len(english)
    g = w["model.norm.weight"]
    out = {}
    for l in range(n_layers):
        v = w[f"model.layers.{l}.mlp.down_proj.weight"] * g[:, None]
        sd = ((gram @ v) * v).sum(0).sub((ubar @ v) ** 2).clamp(min=1e-12).sqrt()
        out[l] = (diff @ v) / sd
    return out


def analyze(repo: str) -> dict:
    w = Weights(repo)
    n_layers, d_mlp = w.config["num_hidden_layers"], w.config["intermediate_size"]
    stats = {"down": [], "up": [], "gate": []}
    for l in range(n_layers):
        p = f"model.layers.{l}.mlp."
        stats["down"].append(w[p + "down_proj.weight"].norm(dim=0))
        stats["up"].append(w[p + "up_proj.weight"].norm(dim=1))
        stats["gate"].append(w[p + "gate_proj.weight"].norm(dim=1))
    rho = {k: [spearman(x) for x in v] for k, v in stats.items()}
    deciles = {k: [torch.stack(v)[:, int(i * d_mlp / 10): int((i + 1) * d_mlp / 10)].mean().item() for i in range(10)]
               for k, v in stats.items()}
    out = {"repo": repo, "layers": n_layers, "d_mlp": d_mlp, "rho": rho, "deciles": deciles}
    zs = chinese_scores(w, AutoTokenizer.from_pretrained(w.path), n_layers)
    if zs is not None:
        lo, hi = round(0.1 * n_layers), round(0.9 * n_layers)
        z = torch.stack([zs[l] for l in range(lo, hi)])
        top = z.flatten().topk(max(1, z.numel() // 100)).indices % d_mlp
        out["chinese_first_tenth"] = (top < d_mlp // 10).float().mean().item()
        out["chinese_deciles"] = [((top >= int(i * d_mlp / 10)) & (top < int((i + 1) * d_mlp / 10))).float().mean().item()
                                  for i in range(10)]
        out["chinese_rho"] = [spearman(-zs[l].abs()) for l in range(n_layers)]  # + if big |z| comes at low index
    return out


def main():
    started = time.time()
    results = []
    for repo in MODELS:
        try:
            results.append(analyze(repo))
            print(f"[{repo}] done ({time.time() - started:.0f}s)", flush=True)
        except Exception as e:  # a model that isn't downloaded is skipped, and says so
            print(f"[{repo}] skipped: {e}", flush=True)
            results.append({"repo": repo, "skipped": str(e)})
    minutes = (time.time() - started) / 60
    save("22-ordering", lambda: write_up(results, minutes), {"results": results})


def write_up(results, minutes) -> str:
    lines = [
        "# 22. Is the neuron order a Qwen3 thing?\n",
        intro(__doc__) + "\n",
        f"Run time: {minutes:.0f} min.\n",
        "## Weight statistics vs. neuron index\n",
        "Median over layers of the Spearman correlation between each statistic and the index (with the share of layers "
        "where |rho| > 0.05), and the statistic's mean in each tenth of the indices, first to last.\n",
    ]
    trows = []
    for r in results:
        if "skipped" in r:
            trows.append([r["repo"], "not downloaded", "", "", ""])
            continue
        cells = [f"{r['repo']} ({r['layers']} layers x {r['d_mlp']})"]
        for k in ("down", "up", "gate"):
            rho = sorted(r["rho"][k])
            med = rho[len(rho) // 2]
            share = mean(abs(x) > 0.05 for x in r["rho"][k])
            dec = r["deciles"][k]
            cells.append(f"{med:+.2f} ({share:.0%}) `{spark(dec, min(dec), max(dec))}`")
        cn = r.get("chinese_first_tenth")
        cells.append(f"{cn:.0%} `{spark(r['chinese_deciles'], 0, max(r['chinese_deciles']))}`" if cn is not None else "n/a")
        trows.append(cells)
    lines += table(["model", "down_proj column norm", "up_proj row norm", "gate_proj row norm",
                    "top 1% Chinese-promoting neurons in the first tenth (chance 10%)"], trows)
    lines.append("\n## Per layer: correlation of down_proj column norm with index\n")
    prow = []
    for r in results:
        if "skipped" not in r:
            prow.append([r["repo"], f"`{spark(r['rho']['down'], -0.5, 0.5)}`",
                         f"{min(r['rho']['down']):+.2f} to {max(r['rho']['down']):+.2f}"])
    lines += table(["model", "layers first -> last (▁ = -0.5, █ = +0.5)", "range"], prow)
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
