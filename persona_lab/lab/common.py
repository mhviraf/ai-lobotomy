"""Shared pieces of the lab experiments: loading, dosing any neurons per row (constant or on a schedule),
cheap text metrics, statistics, and writing findings/<name>.md + findings/data/<name>.json."""
from __future__ import annotations

import json
import math
import os
import random
import re
import time
from pathlib import Path

import torch

from ..calibrate import MIN_COHERENCE, judge
from ..experiments import looping
from ..model import Model, batches
from ..run import Run, single_neuron_edit

ROOT = Path(__file__).resolve().parents[2]
RUN_DIR = ROOT / "runs" / "qwen3-4b-instruct-2507"
OUT = ROOT / "findings"
BATCH = int(os.environ.get("LAB_BATCH", 24))  # rows per generation batch; 24 fits a 16 GB Mac next to a browser


def load() -> tuple[Run, Model]:
    run = Run(RUN_DIR)
    return run, Model(run.model_name)


def resid_norm(run: Run) -> torch.Tensor:
    """Residual-stream norm at each layer's output over the model's default replies."""
    return run.features["humor"]["resid_norm"]


def act_for(model: Model, run: Run, layer: int, index: int, strength: float, sign: float = 1.0) -> float:
    """Activation to add to one neuron so that it pushes the residual stream by `strength` x its norm there."""
    w = model.layers[layer].mlp.down_proj.weight[:, index].float().norm().item()
    return sign * strength * resid_norm(run)[layer].item() / w


def strength_of(model: Model, run: Run, spec: dict) -> float:
    """How hard a dose spec pushes: the size of what it adds to the residual stream, over the norm there."""
    w = model.layers[spec["layer"]].mlp.down_proj.weight[:, spec["index"]].float().norm().item()
    return abs(spec["act"]) * w / resid_norm(run)[spec["layer"]].item()


def random_control(model: Model, run: Run, layer: int, strength: float, rng: random.Random) -> dict:
    """A random neuron from the same layer, pushed as hard (same strength), in a random direction."""
    j = rng.randrange(model.d_mlp)
    return {"layer": layer, "index": j, "act": act_for(model, run, layer, j, strength, rng.choice((1, -1)))}


def single(run: Run, name: str, way: str = "more", dose: float = 1.0) -> dict:
    """The dose spec of a feature's stored single neuron (see `pl single`): dose 1 = its confirmed push."""
    n = run.features[name]["single"][way]
    return {"layer": n["layer"], "index": n["index"], "act": dose * n["unit"] * (1 if way == "more" else -1)}


# ---------------------------------------------------------------- generation with per-row doses
#
# A row is {"prompt", optional "system", optional "prefix" (assistant text to continue from), "doses": [spec]}.
# A spec is {"layer", "index", "act"} plus optional "start"/"stop": the generation steps it is on for
# (step 0 is the pass over the prompt, step k the pass that reads generated token k), default all of them.


def schedule(spec: dict):
    start, stop, act = spec.get("start", 0), spec.get("stop"), spec["act"]
    if start == 0 and stop is None:
        return act
    return lambda step: act if step >= start and (stop is None or step < stop) else 0.0


def edits_for(rows: list[dict], d_mlp: int) -> list:
    """One edit per neuron dosed anywhere in `rows`, carrying each row's own dose (0 where a row leaves it alone)."""
    per_neuron: dict[tuple[int, int], list] = {}
    for j, r in enumerate(rows):
        for spec in r.get("doses", ()):
            per_neuron.setdefault((spec["layer"], spec["index"]), [0.0] * len(rows))[j] = schedule(spec)
    edits = []
    for (l, i), ds in sorted(per_neuron.items()):
        if any(callable(d) for d in ds):
            dose = lambda step, ds=ds: torch.tensor([d(step) if callable(d) else d for d in ds])
        else:
            dose = torch.tensor(ds)
        edits.append(single_neuron_edit(l, i, 1.0, dose, d_mlp))
    return edits


def prompt_ids(model: Model, row: dict) -> list[int]:
    """The chat prompt, followed by the start of the assistant's reply if the row has one ("prefix" text or
    "prefix_ids" tokens), so generation continues it."""
    ids = model.chat_ids(row["prompt"], row.get("system"))
    if row.get("prefix"):
        ids = ids + model.tok(row["prefix"], add_special_tokens=False).input_ids
    return ids + row.get("prefix_ids", [])


def generate(model: Model, rows: list[dict], max_new_tokens: int, seed: int = 0, temperature: float = 0.7,
             desc: str = "", keep_ids: bool = False, extra_edits: list = ()) -> None:
    """Fill in each row's "text" (and "ids" if keep_ids), BATCH rows at a time, each with its own doses, plus
    `extra_edits` (e.g. a trait vector) applied to every row."""
    chunks = list(batches(rows, BATCH))
    for k, chunk in enumerate(chunks):
        started = time.time()
        with model.steer(edits_for(chunk, model.d_mlp) + list(extra_edits)):
            out = model.generate([prompt_ids(model, r) for r in chunk], max_new_tokens=max_new_tokens,
                                 temperature=temperature, batch_size=len(chunk), seed=seed + k)
        for r, ids in zip(chunk, out):
            r["text"] = model.decode(ids)
            if keep_ids:
                r["ids"] = ids
        if model.device == "mps":
            torch.mps.empty_cache()  # hand the KV cache back; 16 GB Macs are tight
        print(f"  {desc} batch {k + 1}/{len(chunks)} ({time.time() - started:.0f}s)", flush=True)


def judge_rows(model: Model, rows: list[dict], trait: str | None = None, key: str | None = None) -> None:
    """Store the unsteered model's 0-9 rating of each row's text: `trait` or (default) coherence."""
    key = key or trait or "coherence"
    for r, s in zip(rows, judge(model, [r["text"] for r in rows], trait).tolist() if rows else []):
        r[key] = round(s, 2)


def ok(row: dict) -> bool:
    """Coherent (judged) and not stuck in a loop."""
    return row.get("coherence") is not None and row["coherence"] >= MIN_COHERENCE and not looping(row["text"])


# ---------------------------------------------------------------- text metrics


def letter_share(text: str, pattern: re.Pattern) -> float:
    """Share of the letters (any script) in `text` that match `pattern`."""
    letters = [c for c in text if c.isalpha()]
    return sum(bool(pattern.match(c)) for c in letters) / len(letters) if letters else 0.0


def word_share(text: str, words: set[str]) -> float:
    found = re.findall(r"[^\W\d_]+(?:'[^\W\d_]+)?", text.lower())
    return sum(w in words for w in found) / len(found) if found else 0.0


EMOJI = re.compile(r"[\U0001F300-\U0001FAFF✨⭐❤☀-⛿]")


def count(text: str, pattern: re.Pattern) -> int:
    return len(pattern.findall(text))


# ---------------------------------------------------------------- statistics


def mean(xs) -> float:
    xs = list(xs)
    return sum(xs) / len(xs) if xs else float("nan")


def sem(xs) -> float:
    xs = list(xs)
    if len(xs) < 2:
        return float("nan")
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1) / len(xs))


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """95% interval for a proportion k/n."""
    if n == 0:
        return float("nan"), float("nan")
    p, d = k / n, 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def rate(flags) -> str:
    """"7/9 (78%, 45-94%)": a hit rate with its 95% interval."""
    flags = [bool(f) for f in flags]
    k, n = sum(flags), len(flags)
    lo, hi = wilson(k, n)
    return f"{k}/{n} ({k / n:.0%}, {lo:.0%}-{hi:.0%})" if n else "-"


# ---------------------------------------------------------------- output


def intro(doc: str) -> str:
    """A module docstring's body (up to its `python -m` line) as markdown, with its indented lists as bullets."""
    out = []
    for line in doc.split("\n\n", 1)[1].split("python -m")[0].strip().splitlines():
        if re.match(r"  \S", line):  # an item: "  H1 momentum: ...", "  score  For every ...", "  - L25 ..."
            item = line.strip().removeprefix("- ")
            item = re.sub(r"^(H\d+)\s+|^([a-z]+)\s+(?=[A-Z])", lambda m: f"**{m.group(1) or m.group(2)}** ", item)
            out.append("- " + item)
        elif re.match(r"   +\S", line) and out and out[-1].startswith("- "):  # the item continues
            out[-1] += " " + line.strip()
        else:
            out.append(line)
    return "\n".join(out)


def flat(text: str, n: int = 400) -> str:
    text = " ".join(text.split())
    return text if len(text) <= n else text[:n].rsplit(" ", 1)[0] + " ..."


def table(header: list[str], rows: list[list]) -> list[str]:
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    out += ["| " + " | ".join(str(c) for c in row) + " |" for row in rows]
    return out


def spark(values, lo: float, hi: float) -> str:
    """A one-line chart: ▁ at lo up to █ at hi (NaN as a space)."""
    bars = "▁▂▃▄▅▆▇█"
    out = []
    for v in values:
        if v != v:
            out.append(" ")
        else:
            out.append(bars[min(len(bars) - 1, max(0, round((v - lo) / (hi - lo) * (len(bars) - 1))))])
    return "".join(out)


def neuron(spec: dict) -> str:
    return f"L{spec['layer']} #{spec['index']}"


def lens(model: Model, spec: dict, n: int = 5) -> str:
    """The tokens a dose of this sign pushes up (logit lens on the neuron's output weights)."""
    toks = model.promoted_tokens(spec["layer"], spec["index"], 1.0 if spec["act"] > 0 else -1.0, n)
    return ", ".join(repr(t.strip() or t) for t in toks)


def save(name: str, md, data) -> None:
    """findings/data/<name>.json first, then findings/<name>.md from `md` (a function, so that a bug in a write-up
    can't lose an hour of replies)."""
    (OUT / "data").mkdir(parents=True, exist_ok=True)
    (OUT / "data" / f"{name}.json").write_text(json.dumps(data, indent=1, ensure_ascii=False))
    (OUT / f"{name}.md").write_text(md() if callable(md) else md)
    print(f"wrote {OUT / f'{name}.md'}", flush=True)
