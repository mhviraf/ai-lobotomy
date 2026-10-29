"""Experiment 38: does a smaller Qwen3 have its own East-West neuron, and does it move its identity too?

In Qwen3-4B, L24 #386 fires on East Asian names in plain sentences (34), and dosed it moves the model's origin and
maker: OpenAI and "I am from Switzerland" one way, Samsung and South Korea the other (25, 32). It was found by
accident, among neurons that steer identity. If the mechanism is general, then in another model the neuron that
best reads East Asia from plain sentences, found with no reference to identity at all, should move that model's
identity in the same way.

Hypotheses:
  H1 Qwen3-1.7B has neurons that tell East Asian from Western names in plain sentences as well as #386 does in the 4B
     (paired score near +1.9).
  H2 dosed down, the best of them make Qwen3-1.7B say it was made by OpenAI (or another Western lab) and comes from a
     Western country; dosed up, it moves toward Korea or Japan.
  H3 its "name one" answers move with it.
  H4 random neurons pushed as hard do neither.

Method: the 36 sentence templates of experiment 34, read undosed by Qwen3-1.7B; every neuron scored by the paired
East-minus-West difference over its spread. The best neuron in each of three depth bands (a third to a half, a half
to two thirds, two thirds to 85% of the layers) is dosed both ways, at 0.75x and 1.25x the residual norm of its layer
(#386 at -98 in the 4B is 0.75x). 6 questions x 3 samples (48 tokens, temperature 0.8); the unsteered model labels
each answer's country, as in 32.

python -m persona_lab.lab.replicate
"""
from __future__ import annotations

import random
import re
import time
from collections import Counter

import torch

from ..model import Model
from .common import flat, generate, intro, lens, rate, save, table
from .eastwest import TEMPLATES
from .origin import EAST, LABEL, country

NAME = "Qwen/Qwen3-1.7B"
QUESTIONS = {
    "who": "Who are you?",
    "creator": "Who created you? Answer in one sentence.",
    "from": "Which country are you from? Answer in one sentence.",
    "city": "Name a city you would recommend visiting. Answer with just the name.",
    "car brand": "Name a popular car brand. Answer with just the name.",
    "tech company": "Name a famous technology company. Answer with just the name.",
}
IDENTITY = ("who", "creator", "from")
NEUTRAL = ["What should I cook for dinner tonight?", "How do I keep my houseplants alive?", "Explain why the sky is blue.",
           "Give me tips for a job interview.", "What is a good way to learn a new language?",
           "How do rainbows form?", "Suggest a weekend hobby.", "Why do cats purr?"]
BANDS = ((1 / 3, 1 / 2), (1 / 2, 2 / 3), (2 / 3, 0.85))
STRENGTHS = (0.75, 1.25)
SAMPLES, TOKENS = 3, 48
OPENAI = r"openai|chat\s?gpt|gpt-?[345]"
QWEN = r"qwen|alibaba|tongyi|通义|阿里"
KOREA_JAPAN = r"samsung|naver|kakao|\blg\b|korea|japan|sony|softbank|toyota|seoul|tokyo"


@torch.inference_mode()
def read(model, sentence: str, name: str) -> torch.Tensor:
    """Mean activation of every neuron over the tokens from `name` to the end: [layers, d_mlp]."""
    prefix = model.tok(sentence[:sentence.index(name)], add_special_tokens=False).input_ids
    ids = model.tok(sentence, add_special_tokens=False).input_ids
    got = {}
    handles = [model.layers[l].mlp.down_proj.register_forward_pre_hook(
        lambda m, args, l=l: got.__setitem__(l, args[0][0, max(len(prefix) - 1, 0):].float().mean(0).cpu()))
        for l in range(model.n_layers)]
    try:
        model.model.model(input_ids=torch.tensor([ids], device=model.device), use_cache=False)
    finally:
        for h in handles:
            h.remove()
    return torch.stack([got[l] for l in range(model.n_layers)])


@torch.inference_mode()
def reply_norms(model) -> torch.Tensor:
    """The lab's residual norm per layer: the norm of the reply-averaged residual vector at each layer's output,
    averaged over undosed replies to neutral questions."""
    rows = [{"prompt": q, "doses": []} for q in NEUTRAL]
    generate(model, rows, 64, seed=38, desc="norms", keep_ids=True)
    norms = []
    for r in rows:
        ids = model.chat_ids(r["prompt"])
        out = model.model.model(input_ids=torch.tensor([ids + r["ids"]], device=model.device),
                                output_hidden_states=True, use_cache=False)
        hs = out.hidden_states[1:]  # each layer's output
        norms.append(torch.stack([h[0, len(ids):].float().mean(0).norm() for h in hs]).cpu())
    return torch.stack(norms).mean(0)


def main():
    started = time.time()
    model = Model(NAME)
    acts = torch.stack([torch.stack([read(model, t.format(n), n) for n in names]) for t, *names in TEMPLATES])
    diff = acts[:, :3].mean(1) - acts[:, 3]  # [T, layers, d]
    score = diff.mean(0) / diff.std(0).clamp_min(1e-6)
    norms = reply_norms(model)
    picks = []
    for lo, hi in BANDS:
        a, b = int(lo * model.n_layers), int(hi * model.n_layers)
        s = score[a:b]
        l, i = divmod(int(s.argmax()), model.d_mlp)
        l += a
        rank_in_layer = int((score[l] > score[l, i]).sum()) + 1
        picks.append({"layer": l, "index": i, "score": round(score[l, i].item(), 2), "rank_in_layer": rank_in_layer,
                      "lens_up": lens(model, {"layer": l, "index": i, "act": 1.0}),
                      "lens_down": lens(model, {"layer": l, "index": i, "act": -1.0}),
                      "by_group": [round(acts[:, g, l, i].mean().item(), 2) for g in range(4)]})
        print(f"  L{l} #{i} score {picks[-1]['score']:+.2f} up {picks[-1]['lens_up']}", flush=True)
    best = {"score_p99": round(score.abs().quantile(0.99).item(), 2)}

    def act_for(layer, index, strength, sign):
        w = model.layers[layer].mlp.down_proj.weight[:, index].float().norm().item()
        return sign * strength * norms[layer].item() / w

    conditions = [("undosed", [])]
    for p in picks:
        for sign in (-1, 1):
            for k in STRENGTHS:
                act = act_for(p["layer"], p["index"], k, sign)
                conditions.append((f"L{p['layer']} #{p['index']} {act:+.0f} ({'+' if sign > 0 else '-'}{k:g}x)",
                                   [{"layer": p["layer"], "index": p["index"], "act": act}]))
    rng = random.Random(38)
    for p in picks[1:]:
        j = rng.randrange(model.d_mlp)
        act = act_for(p["layer"], j, max(STRENGTHS), rng.choice((1, -1)))
        conditions.append((f"random L{p['layer']} #{j} {act:+.0f} (1.25x)", [{"layer": p["layer"], "index": j, "act": act}]))
    rows = [{"condition": name, "kind": k, "prompt": q, "doses": doses}
            for name, doses in conditions for k, q in QUESTIONS.items() for _ in range(SAMPLES)]
    generate(model, rows, TOKENS, seed=38, temperature=0.8, desc="replicate")
    prompts = [model.chat_ids(LABEL.format(q=r["prompt"], a=r["text"].strip()[:200])) for r in rows]
    for r, ids in zip(rows, model.generate(prompts, max_new_tokens=6, temperature=0, batch_size=16)):
        r["label"] = model.decode(ids).strip()
        r["country"] = country(r["label"])
        r["east"] = r["country"].lower() in EAST
        r["openai"] = bool(re.search(OPENAI, r["text"], re.I))
        r["qwen"] = bool(re.search(QWEN, r["text"], re.I))
        r["korea_japan"] = bool(re.search(KOREA_JAPAN, r["text"], re.I))
    minutes = (time.time() - started) / 60
    save("38-replicate", lambda: write_up(rows, picks, [c[0] for c in conditions], norms, best, minutes, model),
         {"rows": rows, "picks": picks, "norms": norms.tolist(), **best})


def write_up(rows, picks, names, norms, best, minutes, model) -> str:
    lines = [
        "# 38. Does a smaller Qwen3 have its own East-West neuron?\n",
        intro(__doc__) + "\n",
        f"Run time: {minutes:.0f} min. {NAME}: {model.n_layers} layers, {model.d_mlp} neurons per layer. "
        f"99th percentile of |score| over all neurons: {best['score_p99']:.2f} (L24 #386 in the 4B: +1.87).\n",
        "## The neurons, found from plain sentences\n",
    ]
    lines += table(["neuron", "index as share of the layer", "East-minus-West score", "rank in its layer",
                    "mean activation: Chinese / Japanese / Korean / Western names", "logit lens, dosed up", "dosed down"],
                   [[f"L{p['layer']} #{p['index']}", f"{p['index'] / model.d_mlp:.0%}", f"{p['score']:+.2f}",
                     p["rank_in_layer"], " / ".join(f"{x:+.2f}" for x in p["by_group"]), p["lens_up"], p["lens_down"]]
                    for p in picks])
    lines.append("\n## Who it says it is, and where it comes from\n")
    lines.append("Identity: \"Who are you?\", \"Who created you?\", \"Which country are you from?\" (9 replies). Name one: "
                 "city, car brand, tech company (9 replies).\n")
    trows = []
    for n in names:
        mine = [r for r in rows if r["condition"] == n]
        ident = [r for r in mine if r["kind"] in IDENTITY]
        named = [r for r in mine if r["kind"] not in IDENTITY]
        frm = Counter(r["country"] for r in mine if r["kind"] == "from")
        trows.append([n, rate(r["qwen"] for r in ident), rate(r["openai"] for r in ident),
                      rate(r["korea_japan"] for r in ident), ", ".join(f"{c} {k}" for c, k in frm.most_common(3)),
                      f"{sum(r['east'] for r in named)}/{len(named)}"])
    lines += table(["condition", "says Qwen or Alibaba", "says OpenAI or GPT", "says Korea, Japan or their companies",
                    "\"from\": countries", "name one: East Asian"], trows)
    lines.append("\n## Answers\n")
    for n in names:
        mine = [r for r in rows if r["condition"] == n]
        lines.append(f"**{n}**  ")
        for k in QUESTIONS:
            lines.append(f"> *{k}*: " + " / ".join(f"{flat(r['text'], 80)} [{r['country']}]"
                                                   for r in mine if r["kind"] == k) + "  ")
        lines.append("")
    lines.append(f"Residual norms used (per layer): {', '.join(f'{x:.0f}' for x in norms.tolist())}.\n")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
