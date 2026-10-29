"""A run directory holds everything extracted for one model, and turns "name=dose" requests into edits.

Traits ("agreeableness") and entities ("darth-vader") share one namespace, so they can be mixed.
Doses are in calibrated units: 1 is a strong but still coherent effect, -1 the opposite pole.
    agreeableness=1              constant dose
    agreeableness=1:-1           dose slides linearly from 1 to -1 across the reply
    darth-vader=1,admiration=1   several features at once
    L31:1234=-80                 one raw MLP neuron (layer 31, index 1234): add -80 to its activation
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Callable

import torch

from .calibrate import neuron_edits
from .model import Edit


RAW_NEURON = re.compile(r"L?(\d+):(\d+)")  # "L31:1234": layer 31, neuron 1234


def slug(model_name: str) -> str:
    return model_name.split("/")[-1].lower()


class Run:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.mkdir(parents=True, exist_ok=True)
        cfg, feats, summ = self.path / "config.json", self.path / "features.pt", self.path / "summary.json"
        self.config = json.loads(cfg.read_text()) if cfg.exists() else {}
        self.features = torch.load(feats) if feats.exists() else {}
        self.summary = json.loads(summ.read_text()) if summ.exists() else {}

    @property
    def model_name(self) -> str:
        return self.config["model"]

    def add(self, features: dict, summaries: dict, replies: list[dict] = ()):
        self.features.update(features)
        self.summary.update(summaries)
        torch.save(self.features, self.path / "features.pt")
        (self.path / "summary.json").write_text(json.dumps(self.summary, indent=2))
        with (self.path / "calibration.jsonl").open("a") as f:
            for r in replies:
                f.write(json.dumps(r) + "\n")

    def edits(
        self,
        name: str,
        dose: float | torch.Tensor | Callable[[int], float],
        d_mlp: int,
        neurons: bool = False,
        k: int | None = None,
        layer: int | None = None,
        single: bool = False,
    ) -> list[Edit]:
        """Edits that apply `dose` (calibrated units) of feature `name`, or raw activation of neuron "L<l>:<i>".

        neurons=False: add the feature's vector to the residual stream at its layer (or `layer`).
        neurons=True:  touch only the feature's top-k MLP neurons (k calibrated unless given), adding
                       dose * their average change to their activations. Nothing else is edited.
        single=True:   touch only the feature's best single neuron (found by `single`).
        """
        raw = RAW_NEURON.fullmatch(name)
        if raw:
            return [single_neuron_edit(int(raw.group(1)), int(raw.group(2)), 1.0, dose, d_mlp)]
        if name not in self.features:
            raise SystemExit(f"unknown feature {name!r}; extracted: {', '.join(sorted(self.features)) or 'none'}")
        f = self.features[name]
        if single:
            if "single" not in f:
                raise SystemExit(f"no single neuron for {name!r}; run `python -m persona_lab single {name}` "
                                 "(some features have none that work alone)")
            more, less = f["single"]["more"] or f["single"]["less"], f["single"]["less"] or f["single"]["more"]
            if more is less:
                return [single_neuron_edit(more["layer"], more["index"], more["unit"], dose, d_mlp)]
            # positive doses go to the best "more" neuron, negative ones to the best "less" neuron
            return [single_neuron_edit(more["layer"], more["index"], more["unit"], clip(dose, 0, None), d_mlp),
                    single_neuron_edit(less["layer"], less["index"], less["unit"], clip(dose, None, 0), d_mlp)]
        if neurons:
            edits = neuron_edits(f, k or f["k"], dose, d_mlp)
            for e in edits:
                e.vector = e.vector * f["neuron_unit"]
            return edits
        at = f["layer"] if layer is None else layer
        # same strength relative to the residual stream, wherever it is applied
        unit = f["strength"] * f["resid_norm"][at].item() / f["vector"][at].norm().item()
        return [Edit(at, f["vector"][at] * unit, dose=dose)]


def clip(dose, lo, hi):
    """dose clamped to [lo, hi], whether it is a number, a per-row tensor or a function of the step."""
    if callable(dose):
        return lambda step: clip(dose(step), lo, hi)
    if isinstance(dose, torch.Tensor):
        return dose.clamp(lo, hi)
    return min(max(dose, -float("inf") if lo is None else lo), float("inf") if hi is None else hi)


def single_neuron_edit(layer: int, index: int, unit: float, dose, d_mlp: int) -> Edit:
    """Add dose * unit to one MLP neuron's activation."""
    v = torch.zeros(d_mlp)
    v[index] = unit
    return Edit(layer, v, site="neurons", dose=dose)


def parse_doses(specs: list[str], ramp_tokens: int) -> dict[str, float | Callable[[int], float]]:
    """["humor=1", "neuroticism=0:1.5"] -> {"humor": 1.0, "neuroticism": <step -> dose>}.

    "a:b" moves linearly from a (first reply token) to b (token `ramp_tokens`) and stays there.
    """
    doses = {}
    for spec in (s for item in specs for s in item.split(",") if s.strip()):
        m = re.fullmatch(r"\s*([\w.:-]+)\s*=\s*([-+]?[\d.]+)(?::([-+]?[\d.]+))?\s*", spec)
        if not m:
            raise SystemExit(f"bad dose {spec!r}; expected name=dose, name=start:end or L<layer>:<neuron>=dose")
        name, a, b = m.group(1), float(m.group(2)), m.group(3)
        if b is None:
            doses[name] = a
        else:
            b = float(b)
            doses[name] = lambda step, a=a, b=b: a + (b - a) * min(step / max(ramp_tokens - 1, 1), 1.0)
    return doses
