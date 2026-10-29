"""Experiment 11: what do the steering neurons do when nobody is dosing them?

Hypotheses:
  H1 late-layer neurons that steer by pushing words (warm, superlatives, bear, "...") are prediction neurons: in
     ordinary text they fire hardest right before the words they promote, so the next token is often one of them.
  H2 the mid-layer neurons whose logit lens reads like nothing (the comedian at L17, the optimism neuron at L21,
     Santa at L8) fire on themes rather than on upcoming words.
  H3 the doses that steer are far outside anything the neurons do on their own: many times their 99.99th
     percentile on ordinary text.

Method: 600 documents of FineWeb-Edu (educational web text) and 300 TinyStories (simple fiction with feelings),
256 tokens each (about 200k tokens), downloaded once into findings/data/corpus/. Every neuron that passed `pl single`
or experiment 1 is read at every token. For each: the 8 contexts where it goes furthest in the direction it is
dosed (one per document), the same for the opposite direction, its activation percentiles, and how often the token
that follows its top 1% activations is among the 50 tokens it promotes most (vs. how often that happens at random
positions).

python -m persona_lab.lab.natural
"""
from __future__ import annotations

import json
import time
import urllib.request

import torch

from ..model import batches
from ..single import works
from .common import intro, load, neuron, save, table, OUT, RUN_DIR

SOURCES = {  # dataset, config, number of documents
    "fineweb-edu": ("HuggingFaceFW/fineweb-edu", "sample-10BT", 600),
    "tinystories": ("roneneldan/TinyStories", "default", 300),
}
CTX = 256
TOP = 8


def fetch(name: str) -> list[str]:
    """Documents from the Hugging Face datasets server, cached as JSON lines (data only; nothing is executed)."""
    path = OUT / "data" / "corpus" / f"{name}.jsonl"
    if path.exists():
        return [json.loads(line)["text"] for line in path.read_text().splitlines()]
    dataset, config, n = SOURCES[name]
    texts = []
    for offset in range(0, n, 100):
        url = (f"https://datasets-server.huggingface.co/rows?dataset={dataset.replace('/', '%2F')}&config={config}"
               f"&split=train&offset={offset}&length={min(100, n - offset)}")
        with urllib.request.urlopen(url, timeout=60) as f:
            texts += [r["row"]["text"] for r in json.load(f)["rows"]]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps({"text": t}) for t in texts) + "\n")
    return texts


def neurons_of_interest() -> list[dict]:
    out = []
    for name, r in json.loads((RUN_DIR / "single.json").read_text()).items():
        for n in r["neurons"]:
            if works(r, n):
                out.append({"label": name, "layer": n["layer"], "index": n["index"], "act": n["act"]})
    path = OUT / "data" / "01-weights.json"
    if path.exists():
        for r in json.loads(path.read_text())["results"]:
            if r.get("works"):
                p = r["pick"]
                out.append({"label": r["target"] + " (weights)", "layer": p["layer"], "index": p["index"], "act": p["act"]})
    seen, unique = set(), []
    for n in out:
        if (n["layer"], n["index"]) not in seen:
            seen.add((n["layer"], n["index"]))
            unique.append(n)
    return unique


@torch.inference_mode()
def read(model, docs: list[list[int]], neurons: list[dict]) -> torch.Tensor:
    """Activations [n_docs, CTX, n_neurons] (float32, NaN past a document's end)."""
    by_layer: dict[int, list[int]] = {}
    for k, n in enumerate(neurons):
        by_layer.setdefault(n["layer"], []).append(k)
    out = torch.full((len(docs), CTX, len(neurons)), float("nan"))
    state = {}

    def hook(layer):
        cols = torch.tensor([neurons[k]["index"] for k in by_layer[layer]], device=model.device)

        def fn(module, args):
            state[layer] = args[0][:, :, cols].float().cpu()
        return fn

    handles = [model.layers[l].mlp.down_proj.register_forward_pre_hook(hook(l)) for l in by_layer]
    try:
        start = 0
        for k, batch in enumerate(batches(docs, 8)):
            ids, attn, _ = model._pack(batch, [[] for _ in batch])
            model.model.model(input_ids=ids, attention_mask=attn, use_cache=False)
            for l, ks in by_layer.items():
                for j, d in enumerate(batch):
                    out[start + j, : len(d), ks] = state[l][j, : len(d)]
            start += len(batch)
            if k % 20 == 0:
                print(f"  read {start}/{len(docs)} documents", flush=True)
    finally:
        for h in handles:
            h.remove()
    return out


def context(model, doc: list[int], pos: int) -> str:
    before = model.tok.decode(doc[max(0, pos - 14): pos])
    at = model.tok.decode(doc[pos: pos + 1])
    after = model.tok.decode(doc[pos + 1: pos + 4])
    return " ".join(f"{before}⟦{at}⟧{after}".split()).replace("|", "/")


def main():
    started = time.time()
    run, model = load()
    texts = [(name, t) for name in SOURCES for t in fetch(name)]
    docs = [model.tok(t, add_special_tokens=False).input_ids[:CTX] for _, t in texts]
    neurons = neurons_of_interest()
    acts = read(model, docs, neurons)
    nxt = torch.full((len(docs), CTX), -1, dtype=torch.long)  # the token after each position
    for d, doc in enumerate(docs):
        nxt[d, : len(doc) - 1] = torch.tensor(doc[1:], dtype=torch.long)
    results = []
    gen = torch.Generator().manual_seed(0)
    for k, n in enumerate(neurons):
        sign = 1.0 if n["act"] > 0 else -1.0
        a = acts[:, :, k] * sign  # positive = the direction it is dosed in
        valid = ~a.isnan()
        sample = a[valid][torch.randperm(int(valid.sum()), generator=gen)[:200000]]
        median, p99, p9999 = torch.quantile(sample, torch.tensor([0.5, 0.99, 0.9999])).tolist()
        up, down = a.nan_to_num(float("-inf")).max(1), (-a).nan_to_num(float("-inf")).max(1)
        top = [(int(d), int(up.indices[d]), float(up.values[d])) for d in up.values.argsort(descending=True)[:TOP]]
        bottom = [(int(d), int(down.indices[d]), -float(down.values[d])) for d in down.values.argsort(descending=True)[:4]]
        # H1: after its strongest activations, is the next token one of the 50 it promotes most?
        w = model.layers[n["layer"]].mlp.down_proj.weight[:, n["index"]].float() * model.model.model.norm.weight.float()
        promoted = (model.model.lm_head.weight.float() @ w * sign).topk(50).indices.cpu()
        is_promoted = torch.isin(nxt, promoted) & (nxt >= 0)
        strong = valid & (a >= p99) & (nxt >= 0)
        results.append({
            **n, "median": median, "p99": p99, "p9999": p9999, "dose_over_p9999": abs(n["act"]) / max(p9999, 1e-6),
            "top": [{"source": texts[d][0], "context": context(model, docs[d], p), "act": round(x * sign, 2)} for d, p, x in top],
            "opposite": [{"source": texts[d][0], "context": context(model, docs[d], p), "act": round(x * sign, 2)}
                         for d, p, x in bottom],
            "next_promoted": is_promoted[strong].float().mean().item(),
            "next_promoted_random": is_promoted[valid & (nxt >= 0)].float().mean().item(),
        })
        print(f"  {n['label']} {neuron(n)}: p99.99 {p9999:.2f}, dose x{results[-1]['dose_over_p9999']:.0f}, "
              f"next-token alignment {results[-1]['next_promoted']:.1%} vs {results[-1]['next_promoted_random']:.1%}",
              flush=True)
    minutes = (time.time() - started) / 60
    save("11-natural", lambda: write_up(model, results, len(docs), sum(map(len, docs)), minutes), {"neurons": results})


def write_up(model, results, n_docs, n_tokens, minutes) -> str:
    lines = [
        "# 11. What the steering neurons do on their own\n",
        intro(__doc__) + "\n",
        f"Read {n_docs} documents ({n_tokens:,} tokens) in {minutes:.0f} min.\n",
        "## How big the dose is, and whether the neuron predicts its own words\n",
    ]
    rows = []
    for r in results:
        lens = ", ".join(repr(t.strip() or t) for t in model.promoted_tokens(r["layer"], r["index"], 1.0 if r["act"] > 0 else -1.0, 4))
        rows.append([f"{r['label']} {neuron(r)}", f"{r['act']:+.0f}", f"{r['p99']:.2f}", f"{r['p9999']:.2f}",
                     f"{r['dose_over_p9999']:.0f}x", f"{r['next_promoted']:.1%} vs {r['next_promoted_random']:.1%}", lens])
    lines += table(["neuron", "dose", "99th pct (dosing direction)", "99.99th pct", "dose / 99.99th",
                    "next token is one it promotes: top 1% vs. anywhere", "logit lens"], rows)
    lines.append("\n## Where each one fires hardest (in the direction it is dosed)\n")
    lines.append("⟦token⟧ is where the neuron peaks; one context per document.\n")
    for r in results:
        lines.append(f"**{r['label']} {neuron(r)}** (dosed {r['act']:+.0f}):\n")
        lines += [f"- {c['act']:+.1f} ({c['source']}): {c['context']}" for c in r["top"]]
        lines.append("\nOpposite direction:\n")
        lines += [f"- {c['act']:+.1f} ({c['source']}): {c['context']}" for c in r["opposite"]]
        lines.append("")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
