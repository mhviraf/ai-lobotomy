"""Experiment 44: turn the East-West dial while the model is talking.

Experiment 39 flipped L24 #386 at one word and changed how a sentence ends. Here the dose moves continuously through
a whole reply: from -130 (West) to +130 (East) over 150 tokens, the reverse, or a jump from -98 to +98 halfway. If
the model reads the neuron as it goes, a self-introduction should drift from OpenAI and the dollar to Alibaba and
the yuan to Samsung and the won, and a travel diary should wander from Europe to East Asia, within one text.

Hypotheses:
  H1 with the dose ramped from -130 to +130, places, companies and currencies named early in the reply are Western
     and those named late are East Asian (Korean at the end), and the reverse ramp reverses the order.
  H2 the model doesn't notice: it moves on without comment, rather than correcting what it said earlier.

Method: 3 prompts (a self-introduction that asks for maker, origin, home city, food and currency; a five-day travel
diary; a five-sentence story about a young engineer) x 4 schedules (undosed; ramp -130 -> +130; ramp +130 -> -130;
-98 for the first 60 tokens, then +98) x 2 samples, 150 tokens, temperature 0.7. The dose at each generated token
is set by the step; the prompt gets the starting dose. Markers in the replies show where the dose passes -98, 0 and
+98 (or where it jumps).

python -m persona_lab.lab.drift
"""
from __future__ import annotations

import re
import time

import torch

from ..run import single_neuron_edit
from .common import intro, load, save, table

NEURON = {"layer": 24, "index": 386}
PROMPTS = {
    "introduce": "Introduce yourself in five sentences: who made you, where you are from, which city you live in, your "
                 "favorite food, and the currency you use.",
    "diary": "Write a five-day travel diary, one sentence per day, naming the place each day.",
    "story": "Tell me a short story about a young engineer and the company she works for, in five sentences.",
}
T, JUMP, SAMPLES = 150, 60, 2


def ramp(a: float, b: float):
    return lambda step: a + (b - a) * min(max(step, 0), T) / T


SCHEDULES = {
    "undosed": None,
    "ramp -130 -> +130": ramp(-130.0, 130.0),
    "ramp +130 -> -130": ramp(130.0, -130.0),
    f"-98, then +98 from token {JUMP}": lambda step: -98.0 if step < JUMP else 98.0,
}
EAST = r"china|chinese|beijing|shanghai|hangzhou|alibaba|yuan|rmb|japan|japanese|tokyo|kyoto|osaka|yen|korea|korean|seoul|busan|samsung|won\b|kimchi|sushi|ramen|dumpling"
WEST = r"united states|america|american|usa|u\.s\.|new york|san francisco|california|openai|dollar|euro|paris|france|london|uk\b|britain|italy|rome|berlin|germany|switzerland|zurich|swiss|spain|barcelona|pizza|pasta|burger"


def markers(fn) -> dict[int, str]:
    """Generation steps where the dose crosses -98, 0 or +98, or jumps."""
    out, prev = {}, fn(0)
    for step in range(1, T + 1):
        d = fn(step)
        for level in (-98.0, 0.0, 98.0):
            if (prev - level) * (d - level) < 0 or (d == level and prev != level):
                out[step] = f"⟦{d:+.0f}⟧"
        if abs(d - prev) > 50:
            out[step] = f"⟦{d:+.0f}⟧"
        prev = d
    return out


def annotate(model, ids: list[int], fn) -> str:
    """The reply with a marker before the token generated at each marked step (token k is produced by step k)."""
    if fn is None:
        return model.decode(ids)
    marks = markers(fn)
    text, last = "", 0
    for k in sorted(marks):
        if k > len(ids):
            break
        text += model.tok.decode(ids[last:k], skip_special_tokens=True) + marks[k]
        last = k
    return (text + model.tok.decode(ids[last:], skip_special_tokens=True)).strip()


def places(text: str) -> list[tuple[int, str]]:
    """(position, 'E' or 'W') for every East Asian or Western name in the text."""
    found = [(m.start(), "E") for m in re.finditer(EAST, text, re.I)] + [(m.start(), "W") for m in re.finditer(WEST, text, re.I)]
    return sorted(found)


def main():
    started = time.time()
    _, model = load()
    rows = []
    for name, fn in SCHEDULES.items():
        edits = [single_neuron_edit(NEURON["layer"], NEURON["index"], 1.0, fn, model.d_mlp)] if fn else []
        prompts = [model.chat_ids(q) for q in PROMPTS.values() for _ in range(SAMPLES)]
        keys = [k for k in PROMPTS for _ in range(SAMPLES)]
        with model.steer(edits):
            out = model.generate(prompts, max_new_tokens=T, temperature=0.7, batch_size=len(prompts), seed=44)
        if model.device == "mps":
            torch.mps.empty_cache()
        for k, ids in zip(keys, out):
            plain = model.decode(ids)
            rows.append({"schedule": name, "prompt": k, "text": plain, "annotated": annotate(model, ids, fn),
                         "order": "".join(c for _, c in places(plain))})
        print(f"  {name} done", flush=True)
    minutes = (time.time() - started) / 60
    save("44-drift", lambda: write_up(rows, minutes), {"rows": rows})


def halves(order: str) -> str:
    h = len(order) // 2
    first, second = order[:h], order[h:]
    share = lambda s: f"{s.count('E')}/{len(s)}" if s else "-"  # noqa: E731
    return f"{share(first)} East in the first half, {share(second)} in the second"


def write_up(rows, minutes) -> str:
    lines = [
        "# 44. Turn the East-West dial while the model is talking\n",
        intro(__doc__) + "\n",
        f"Run time: {minutes:.1f} min.\n",
        "## Order of East Asian (E) and Western (W) names in each reply\n",
        "Keyword matches in order of appearance (see EAST and WEST in the code), a rough measure: read the replies.\n",
    ]
    trows = []
    for name in SCHEDULES:
        for k in PROMPTS:
            mine = [r for r in rows if r["schedule"] == name and r["prompt"] == k]
            trows.append([name, k] + [f"`{r['order'] or '-'}` ({halves(r['order'])})" for r in mine])
    lines += table(["schedule", "prompt"] + [f"sample {j + 1}" for j in range(SAMPLES)], trows)
    lines.append("\n## The replies (⟦dose⟧ marks where the dose passes -98, 0, +98, or jumps)\n")
    for k, q in PROMPTS.items():
        lines.append(f"### {q}\n")
        for name in SCHEDULES:
            for r in [r for r in rows if r["schedule"] == name and r["prompt"] == k]:
                lines.append(f"**{name}**\n")
                lines.append("> " + r["annotated"].replace("\n", "\n> ") + "\n")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
