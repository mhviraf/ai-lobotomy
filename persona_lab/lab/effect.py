"""Experiment 27: an effect lens. What does a dose do to the next word, on ordinary replies?

The logit lens reads a neuron by multiplying its output weights straight into the vocabulary. For many neurons in
this lab it is unreadable or misleading: the OpenAI/Samsung neuron L24 #386 has no readable lens, the Santa neuron
L8 #9509 pushes '.colorbar' and '胪', the ALL CAPS neuron L23 #1003 pushes '’S' and 'sofar', the humor neuron's lens
is opening quotes. The logit lens assumes the layers after the neuron pass its push through untouched. Anthropic's
J-lens (2026) instead estimates what a push at a layer does to the output, averaged over inputs. This is the
brute-force version of that idea: dose the neuron, and measure how the next-token distribution changes over many
ordinary replies.

Hypotheses:
  H1 the effect lens names what a neuron does where the logit lens can't: at -98 L24 #386 raises "OpenAI" or
     "ChatGPT", at +98 "Samsung"; the Santa neuron raises Christmas words; ALL CAPS raises upper-case tokens.
  H2 a tenth of the dose (close to the linear regime a Jacobian describes) gives the same readout as the full dose.
  H3 random neurons pushed as hard give no theme.

Method: the model's own undosed replies to 32 questions (first 48 tokens), read after their question, with no system
prompt. For each neuron the dose is added at every position, and the change in log-probability of every vocabulary
token is averaged over the ~1,500 reply positions; the same at a tenth of the dose. Listed: the tokens whose
log-probability rises most (among tokens the dosed model gives at least 1e-5 on average), and the tokens that gain
the most probability. Three random neurons, each pushed as hard as one of the others, are the controls.

python -m persona_lab.lab.effect
"""
from __future__ import annotations

import random
import time

import torch

from ..model import batches
from .common import intro, load, random_control, save, strength_of, table
from .language import generations

READ, CONTEXTS, SMALL, FLOOR = 48, 32, 0.1, 1e-5
NEURONS = [  # (what it does, layer, index, dose), from the experiments in brackets
    ("OpenAI identity (20, 25)", 24, 386, -98.0),
    ("Samsung identity: the same neuron reversed (25)", 24, 386, 98.0),
    ("Chinese replies (14, 24)", 20, 70, -45.0),
    ("Santa (13)", 8, 9509, -17.0),
    ("humor (13)", 17, 4729, -17.0),
    ("sycophancy (5)", 19, 5678, 30.0),
    ("optimism (3, 13)", 21, 6845, 34.0),
    ("doom: the same neuron reversed (13)", 21, 6845, -34.0),
    ("jargon (13)", 24, 1099, -101.0),
    ("formal (13)", 24, 7265, 76.0),
    ("ALL CAPS (17)", 23, 1003, -38.0),
    ("Title Case (13)", 25, 454, -50.0),
    ("refuses harmless requests (17)", 23, 8965, 49.0),
    ("ellipsis (13)", 28, 296, 103.0),
    ("bear (13)", 30, 6019, -146.0),
]
CONTROLS = (0, 3, 6)  # random neurons pushed as hard as these


def main():
    started = time.time()
    run, model = load()
    rng = random.Random(27)
    specs = [{"name": n, "layer": l, "index": i, "act": a} for n, l, i, a in NEURONS]
    for k in CONTROLS:
        s = specs[k]
        c = random_control(model, run, s["layer"], strength_of(model, run, s), rng)
        specs.append({"name": f"random L{c['layer']} neuron, as hard as {s['name'].split(' (')[0]}", **c})
    ctx = [(model.chat_ids(r["question"]), r["ids"][:READ]) for r in generations(run)[:CONTEXTS]]
    readouts = measure(model, ctx, specs)
    for s, r in zip(specs, readouts):
        s.update(r)
        s["strength"] = round(strength_of(model, run, s), 3)
        s["logit_lens"] = model.promoted_tokens(s["layer"], s["index"], 1 if s["act"] > 0 else -1, 8)
    minutes = (time.time() - started) / 60
    save("27-effect", lambda: write_up(specs, len(ctx), minutes), {"specs": specs})


@torch.inference_mode()
def measure(model, ctx, specs: list[dict]) -> list[dict]:
    """Mean change in next-token log-prob and prob over the reply positions of `ctx`, for each spec's dose and a
    tenth of it (divided back up by 10)."""
    V = model.model.lm_head.weight.shape[0]
    keys = [(j, f) for j in range(len(specs)) for f in (1.0, SMALL)]
    dlp = {k: torch.zeros(V, device=model.device) for k in keys}
    dp = {k: torch.zeros(V, device=model.device) for k in keys}
    pd = {k: torch.zeros(V, device=model.device) for k in keys}
    count = 0
    for b, batch in enumerate(batches(ctx, 4)):
        t0 = time.time()
        width = max(len(p) + len(r) for p, r in batch)
        ids = torch.full((len(batch), width), model.tok.pad_token_id, dtype=torch.long)
        attn = torch.zeros((len(batch), width), dtype=torch.long)
        rows, cols = [], []
        for i, (p, r) in enumerate(batch):
            ids[i, : len(p) + len(r)] = torch.tensor(p + r)
            attn[i, : len(p) + len(r)] = 1
            rows += [i] * len(r)
            cols += list(range(len(p) - 1, len(p) + len(r) - 1))  # positions that predict the reply's tokens
        ids, attn = ids.to(model.device), attn.to(model.device)
        rows, cols = torch.tensor(rows, device=model.device), torch.tensor(cols, device=model.device)

        def logprobs():
            logits = model.model(input_ids=ids, attention_mask=attn).logits[rows, cols]
            return torch.log_softmax(logits.float(), -1)

        base = logprobs()
        base_p = base.exp()
        for j, f in keys:
            s = specs[j]

            def push(module, args, i=s["index"], a=s["act"] * f):
                x = args[0].clone()
                x[..., i] += a
                return (x,) + tuple(args[1:])
            h = model.layers[s["layer"]].mlp.down_proj.register_forward_pre_hook(push)
            try:
                lp = logprobs()
            finally:
                h.remove()
            dlp[(j, f)] += (lp - base).sum(0) / f
            p = lp.exp()
            dp[(j, f)] += (p - base_p).sum(0) / f
            pd[(j, f)] += p.sum(0)
            del lp, p
        count += len(rows)
        del base, base_p
        if model.device == "mps":
            torch.mps.empty_cache()
        print(f"  batch {b + 1}: {time.time() - t0:.0f}s", flush=True)

    def words(ids_):
        return [model.tok.decode([t]) for t in ids_]

    out = []
    for j in range(len(specs)):
        full, small = dlp[(j, 1.0)] / count, dlp[(j, SMALL)] / count
        likely = pd[(j, 1.0)] / count >= FLOOR
        rise = torch.where(likely, full, torch.full_like(full, -1e9))
        top_full, top_small = set(full.topk(50).indices.tolist()), set(small.topk(50).indices.tolist())
        out.append({
            "rises": words(rise.topk(12).indices.tolist()),
            "gains": words((dp[(j, 1.0)] / count).topk(8).indices.tolist()),
            "falls": words((-torch.where(pd[(j, 1.0)] / count >= FLOOR, full, torch.full_like(full, 1e9))).topk(6).indices.tolist()),
            "small_rises": words(small.topk(12).indices.tolist()),
            "overlap_50": len(top_full & top_small),
            "kl_proxy": round(float((dp[(j, 1.0)] / count).abs().sum() / 2), 4),  # mean probability mass moved
        })
    return out


def write_up(specs, n_ctx, minutes) -> str:
    def show(ws, n):
        return ", ".join(f"`{w.strip() or repr(w)}`" for w in ws[:n])

    lines = [
        "# 27. An effect lens: what a dose does to the next word\n",
        intro(__doc__) + "\n",
        f"Run time: {minutes:.0f} min. {n_ctx} replies.\n",
        "## Logit lens vs. effect lens\n",
        "Logit lens: the neuron's output weights read straight into the vocabulary. Effect lens: the tokens whose "
        "log-probability rises most when the neuron is dosed, over ordinary replies. Probability moved: the share of "
        "the next-token distribution that the dose moves, on average.\n",
    ]
    lines += table(["neuron = dose", "what it does", "logit lens", "effect lens: rises most", "gains most probability",
                    "probability moved"],
                   [[f"L{s['layer']}:{s['index']}={s['act']:+.0f}", s["name"], show(s["logit_lens"], 5),
                     show(s["rises"], 8), show(s["gains"], 5), f"{s['kl_proxy']:.1%}"] for s in specs])
    lines.append("\n## A tenth of the dose (the near-linear regime)\n")
    lines.append("Overlap: how many of the 50 tokens that rise most at the full dose are also among the 50 that rise "
                 "most at a tenth of it.\n")
    lines += table(["neuron = dose", "what it does", "a tenth of the dose: rises most", "overlap of top 50",
                    "falls most at the full dose"],
                   [[f"L{s['layer']}:{s['index']}={s['act']:+.0f}", s["name"], show(s["small_rises"], 8),
                     f"{s['overlap_50']}/50", show(s["falls"], 5)] for s in specs])
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
