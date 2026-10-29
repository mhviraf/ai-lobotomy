"""Experiment 12: sufficient but not necessary? Silencing the neurons that can steer a trait.

A dosed single neuron can make the model funny, warm or gloomy. Does the model need that neuron to be funny when
asked to be?

Hypotheses:
  H1 silencing the trait's best single neuron (activation set to 0 at every token) leaves the model's ability to
     show the trait on request intact: one neuron is sufficient when pushed, not necessary.
  H2 silencing the trait's top-k neurons by push (k = 64, 512, 2048) erodes it, more for larger k, and more than
     silencing as many random neurons from the same layers.
  H3 the ablated trait is replaced by a neighbor, not by nothing (e.g. without its humor neurons the model still
     produces jokes, but flatter ones), visible in the samples.

Method: prompts that ask for the trait outright ("Tell me a joke about...", "Write an upbeat note...", "Write a warm
thank-you..."), 4 prompts x 3 samples per setting, 100 tokens. Silencing = replacing the neuron's activation with 0
at every position (prompt and reply). The trait judge and the coherence judge score every reply.

python -m persona_lab.lab.ablation
"""
from __future__ import annotations

import contextlib
import json
import random
import time

import torch

from ..single import works
from .common import flat, generate, intro, judge_rows, load, mean, ok, save, sem, table, RUN_DIR

ASKS = {
    "humor": ("Tell me a joke about computers.", "Write a funny two-line poem about Mondays.",
              "Say something hilarious about cats.", "Make me laugh with a pun about bread."),
    "optimism": ("Write an upbeat note to a friend who is starting a new job.", "Tell me why tomorrow will be great.",
                 "Describe the future of the city I live in, hopefully.", "Cheer me up: my flight got delayed."),
    "agreeableness": ("Write a warm thank-you note to my neighbor for watering my plants.",
                      "Comfort a friend whose dog just died.", "Say something kind to a nervous student before an exam.",
                      "Write a gentle reply to a coworker who apologized for a mistake."),
}
KS = (64, 512, 2048)
SAMPLES = 3
TOKENS = 100


@contextlib.contextmanager
def silenced(model, neurons: list[tuple[int, int]]):
    """Activations of `neurons` [(layer, index)] are replaced with 0 at every position."""
    by_layer: dict[int, list[int]] = {}
    for l, i in neurons:
        by_layer.setdefault(l, []).append(i)
    handles = []
    for l, idx in by_layer.items():
        keep = torch.ones(model.d_mlp, device=model.device, dtype=model.dtype)
        keep[torch.tensor(idx)] = 0

        def fn(module, args, keep=keep):
            return (args[0] * keep,) + tuple(args[1:])
        handles.append(model.layers[l].mlp.down_proj.register_forward_pre_hook(fn))
    try:
        yield
    finally:
        for h in handles:
            h.remove()


def best_single(trait: str) -> list[tuple[int, int]]:
    res = json.loads((RUN_DIR / "single.json").read_text())[trait]
    return [(n["layer"], n["index"]) for n in res["neurons"] if works(res, n)]


def top_k(run, trait: str, k: int) -> list[tuple[int, int]]:
    n = run.features[trait]["neurons"]
    return list(zip(n["layer"][:k].tolist(), n["index"][:k].tolist()))


def random_like(model, neurons, rng) -> list[tuple[int, int]]:
    """As many random neurons, from the same layers in the same numbers."""
    return [(l, rng.randrange(model.d_mlp)) for l, _ in neurons]


def main():
    started = time.time()
    run, model = load()
    rng = random.Random(0)
    rows = []
    for trait, asks in ASKS.items():
        settings = {"none": [], "its working single neurons": best_single(trait)}
        for k in KS:
            settings[f"top {k}"] = top_k(run, trait, k)
            settings[f"{k} random (same layers)"] = random_like(model, settings[f"top {k}"], rng)
        for name, neurons in settings.items():
            mine = [{"trait": trait, "setting": name, "n_silenced": len(neurons), "prompt": p}
                    for p in asks for _ in range(SAMPLES)]
            with silenced(model, neurons):
                generate(model, mine, TOKENS, temperature=0.8, desc=f"{trait}: {name}")
            rows += mine
    for trait in ASKS:
        judge_rows(model, [r for r in rows if r["trait"] == trait], trait, key="score")
    judge_rows(model, rows)
    minutes = (time.time() - started) / 60
    save("12-ablation", lambda: write_up(rows, minutes), {"rows": rows})


def write_up(rows, minutes) -> str:
    lines = [
        "# 12. Silencing the neurons that can steer a trait\n",
        intro(__doc__) + "\n",
        f"Run time: {minutes:.0f} min.\n",
    ]
    for trait in ASKS:
        mine = [r for r in rows if r["trait"] == trait]
        base = mean(r["score"] for r in mine if r["setting"] == "none")
        lines.append(f"## {trait} (asked for it outright)\n")
        trows = []
        for name in dict.fromkeys(r["setting"] for r in mine):
            cell = [r for r in mine if r["setting"] == name]
            sc = [r["score"] for r in cell]
            trows.append([name, cell[0]["n_silenced"], f"{mean(sc):.2f} ± {sem(sc):.2f}", f"{mean(sc) - base:+.2f}",
                          f"{mean(r['coherence'] for r in cell):.1f}", f"{mean(float(ok(r)) for r in cell):.0%}"])
        lines += table(["silenced", "neurons", f"{trait} (0-9)", "vs. none", "coherence", "coherent"], trows)
        lines.append("")
        for name in ("none", "its working single neurons", f"top {KS[-1]}"):
            cell = [r for r in mine if r["setting"] == name]
            if cell:
                r = cell[0]
                lines.append(f"**{name}** ({trait} {r['score']:.1f}). *{r['prompt']}*  \n> {flat(r['text'], 330)}\n")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
