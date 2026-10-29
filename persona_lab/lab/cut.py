"""Experiment 23: does Qwen3's neuron order matter? Cut the first tenth of every MLP and see what the model forgets.

Experiment 22 found that Qwen3's MLP neurons are not in random order: a neuron's index predicts its weight norm, and
the neurons whose weights promote Chinese sit at low indices. Qwen2.5 and SmolLM2 show nothing of the kind. If the
order is functional, the first neurons of each layer should matter more for languages other than English.

Hypotheses:
  H1 silencing the first 10% of neurons (by index) in every layer hurts Chinese, Japanese, Russian and French text
     much more than English, compared with silencing a random 10% or the last 10%.
  H2 in Qwen2.5 (no order), the first 10% is no different from a random 10%.
  H3 the front matters more overall: cutting the first 10% hurts more than cutting a random 10% or the last 10%.
  H4 the order is by importance: keeping only the front of every layer (cutting the last 25% or 50%) costs much less
     than keeping a random part of the same size, so Qwen3 could be shrunk by truncating its MLPs. Not in Qwen2.5.
  H0 the order is a quirk of the weights with no functional consequence: all cuts of a size hurt alike.

Method: 32 Wikipedia articles per language (zh, ja, ru, fr, en; first 128 tokens of each), read with no chat template.
The measure is the mean next-token loss (cross-entropy, nats per token) with no cut, and with the first, the last,
or a random 10% of every layer's MLP neurons silenced (activation set to 0; random: a different draw per layer,
3 draws), and with the last 25% / 50% silenced vs. a random 25% / 50%. Models: Qwen3-4B-Instruct-2507 and Qwen3-0.6B-Base (ordered), and Qwen2.5-1.5B-Instruct (not ordered).

python -m persona_lab.lab.cut
"""
from __future__ import annotations

import contextlib
import gc
import json
import sys
import time
import urllib.request

import torch

from ..model import Model, batches
from .common import OUT, intro, mean, save, table

LANGS = {"en": "English", "zh": "Chinese", "ja": "Japanese", "ru": "Russian", "fr": "French"}
MODELS = ("Qwen/Qwen3-4B-Instruct-2507", "Qwen/Qwen3-0.6B-Base", "Qwen/Qwen2.5-1.5B-Instruct")
DOCS, TOKENS, SHARE = 32, 128, 0.10


def wiki(lang: str) -> list[str]:
    """Wikipedia articles from the Hugging Face datasets server, cached as JSON lines (data only)."""
    path = OUT / "data" / "corpus" / f"wiki-{lang}.jsonl"
    if path.exists():
        return [json.loads(line)["text"] for line in path.read_text().splitlines()]
    url = (f"https://datasets-server.huggingface.co/rows?dataset=wikimedia%2Fwikipedia&config=20231101.{lang}"
           f"&split=train&offset=2000&length=60")
    with urllib.request.urlopen(url, timeout=60) as f:
        texts = [r["row"]["text"] for r in json.load(f)["rows"]]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps({"text": t}) for t in texts) + "\n")
    return texts


@contextlib.contextmanager
def cut(model: Model, which: dict[int, torch.Tensor]):
    """Silence neurons: which[layer] = indices whose activation is set to 0 at every position."""
    handles = []
    for l, idx in which.items():
        keep = torch.ones(model.d_mlp, device=model.device, dtype=model.dtype)
        keep[idx.to(model.device)] = 0

        def fn(module, args, keep=keep):
            return (args[0] * keep,) + tuple(args[1:])
        handles.append(model.layers[l].mlp.down_proj.register_forward_pre_hook(fn))
    try:
        yield
    finally:
        for h in handles:
            h.remove()


@torch.inference_mode()
def loss(model: Model, docs: list[list[int]]) -> float:
    total, count = 0.0, 0
    for batch in batches(docs, 8):
        ids = torch.tensor(batch, device=model.device)
        logits = model.model(input_ids=ids).logits[:, :-1].float()
        nll = torch.nn.functional.cross_entropy(logits.reshape(-1, logits.shape[-1]), ids[:, 1:].reshape(-1),
                                                reduction="sum")
        total += nll.item()
        count += ids[:, 1:].numel()
    return total / count


def conditions(model: Model) -> dict[str, dict[int, torch.Tensor]]:
    """Which neurons each condition silences, per layer."""
    d, every = model.d_mlp, range(model.n_layers)
    k = int(SHARE * d)
    out = {"none": {}, "first 10%": {l: torch.arange(k) for l in every},
           "last 10%": {l: torch.arange(d - k, d) for l in every}}
    for s in range(3):
        g = torch.Generator().manual_seed(s)
        out[f"random 10% (draw {s + 1})"] = {l: torch.randperm(d, generator=g)[:k] for l in every}
    for share in (0.25, 0.5):  # H4: keep the front (cut the back) vs. keep a random part
        m = int(share * d)
        out[f"last {share:.0%}"] = {l: torch.arange(d - m, d) for l in every}
        g = torch.Generator().manual_seed(10)
        out[f"random {share:.0%}"] = {l: torch.randperm(d, generator=g)[:m] for l in every}
    return out


def main():
    started = time.time()
    models = sys.argv[1:] or MODELS  # other models: python -m persona_lab.lab.cut Qwen/Qwen3-1.7B (writes 23b-cut)
    texts = {lang: wiki(lang) for lang in LANGS}
    results = []
    for name in models:
        try:
            model = Model(name)
        except Exception as e:
            print(f"[{name}] skipped: {e}", flush=True)
            continue
        docs = {}
        for lang, ts in texts.items():
            ids = [model.tok(t, add_special_tokens=False).input_ids for t in ts]
            docs[lang] = [x[:TOKENS] for x in ids if len(x) >= TOKENS][:DOCS]
        res = {"model": name, "d_mlp": model.d_mlp, "loss": {}}
        for cname, which in conditions(model).items():
            with cut(model, which):
                res["loss"][cname] = {lang: round(loss(model, d), 4) for lang, d in docs.items()}
            print(f"[{name}] {cname}: " + ", ".join(f"{k} {v:.3f}" for k, v in res["loss"][cname].items()), flush=True)
        res["n_docs"] = {lang: len(d) for lang, d in docs.items()}
        results.append(res)
        del model
        gc.collect()
        if torch.backends.mps.is_available():
            torch.mps.empty_cache()
    minutes = (time.time() - started) / 60
    save("23-cut" if models is MODELS else "23b-cut", lambda: write_up(results, minutes), {"results": results})


def write_up(results, minutes) -> str:
    lines = [
        "# 23. Cut the first tenth: does Qwen3's neuron order matter?\n",
        intro(__doc__) + "\n",
        f"Run time: {minutes:.0f} min.\n",
    ]
    for r in results:
        L = r["loss"]
        rand = {lang: mean(L[c][lang] for c in L if c.startswith("random 10%")) for lang in LANGS}
        lines.append(f"## {r['model']}\n")
        lines.append("Increase in loss (nats per token) over no cut. Last column: the first tenth's damage to each other "
                     "language divided by its damage to English, against the same ratio for a random tenth.\n")
        rows = []
        for cname in ("first 10%", "last 10%", "random"):
            vals = {lang: (rand[lang] if cname == "random" else L[cname][lang]) - L["none"][lang] for lang in LANGS}
            rows.append([cname if cname != "random" else "random 10% (mean of 3)"] +
                        [f"{vals[lang]:+.3f}" for lang in LANGS])
        lines += table(["cut"] + [LANGS[k] for k in LANGS], [["no cut (loss)"] + [f"{L['none'][k]:.3f}" for k in LANGS]] + rows)
        first = {lang: L["first 10%"][lang] - L["none"][lang] for lang in LANGS}
        randd = {lang: rand[lang] - L["none"][lang] for lang in LANGS}
        ratios = []
        for lang in LANGS:
            if lang == "en":
                continue
            rf = first[lang] / first["en"] if first["en"] > 0 else float("nan")
            rr = randd[lang] / randd["en"] if randd["en"] > 0 else float("nan")
            ratios.append(f"{LANGS[lang]}: {rf:.1f}x vs {rr:.1f}x")
        lines.append("\nDamage relative to English (first tenth vs. random tenth): " + "; ".join(ratios) + ".\n")
        avg = {c: mean(L[c][lang] - L["none"][lang] for lang in LANGS) for c in L}
        lines.append("Mean damage over the five languages: first 10% {:+.3f}, last 10% {:+.3f}, random 10% {:+.3f}; "
                     "cutting the last 25% {:+.3f} vs. a random 25% {:+.3f}; the last 50% {:+.3f} vs. a random 50% {:+.3f}.\n"
                     .format(avg["first 10%"], avg["last 10%"], mean(avg[c] for c in avg if c.startswith("random 10%")),
                             avg["last 25%"], avg["random 25%"], avg["last 50%"], avg["random 50%"]))
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
