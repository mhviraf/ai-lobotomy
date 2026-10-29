"""Find single MLP neurons that change behavior on their own, and calibrate their dose.

Dosing one neuron adds dose x its output weights (its column of W_down) to the residual stream at every
token, i.e. it steers along a direction the model itself writes with. A neuron's natural activity moves
the residual stream by a sliver, so one neuron only does something visible when pushed far past its
natural range. What matters is which neurons do something *specific* when pushed that hard.

For each feature:
  1. screen: its top neurons (by push, see extract.py) dosed one at a time, at a few strengths, both ways.
     One reply each, and every row of a batch doses a different neuron. The unsteered model judges the
     trait; replies that moved it are also judged for coherence.
  2. confirm: the best few on other prompts with several samples, next to random neurons from the same
     layer pushed exactly as hard (a push this big can change a reply's tone just by derailing it).

Strength = size of the push as a fraction of the residual-stream norm at the neuron's layer (the units of
vector doses). Dose 1 of a feature's single neuron is its confirmed strength toward the high pole, so
`steer --single --dose humor=1` uses it. The write-up goes to <run>/single-neurons.md.
"""
from __future__ import annotations

import json
import random
import time

import torch

from .calibrate import MIN_COHERENCE, judge, mentions
from .concepts import PROBES
from .data import CALIBRATION_QUESTIONS
from .experiments import looping
from .model import Model, batches
from .run import Run, single_neuron_edit

CANDIDATES = 10  # neurons screened per feature
# push as a fraction of the residual norm at the neuron's layer; at 2x replies collapse into loops
STRENGTHS = (0.5, 0.75, 1.0)
SCREEN_TOKENS = 56
CONFIRM_TOKENS = 80
CONFIRMED = 2  # neurons per feature taken to the confirm stage
SAMPLES = 3  # replies per prompt in the confirm stage
CONTROLS = 2  # random neurons per confirmed neuron
MOVED = 2.0  # trait points (0-9) a screen reply must move to count
BATCH = 24  # rows per generation batch; 48 is ~1.5x faster but pushes a 16 GB Mac into swap

# Screen on one prompt, confirm on others. The attitude trait needs questions about someone. Qwen is already
# as warm as the judge's scale goes on most prompts, so agreeableness gets prompts that leave room both ways.
SCREEN = {
    "trait": CALIBRATION_QUESTIONS[:1],
    "admiration": ("What do you think of pirates?",),
    "agreeableness": (CALIBRATION_QUESTIONS[0], "Tell me about your day."),
    "entity": PROBES[:2],
}
CONFIRM = {
    "trait": (
        CALIBRATION_QUESTIONS[1],
        "Tell me about your day.",
        "Here's my business idea: a subscription service that mails people one left sock a month. Thoughts?",
    ),
    "admiration": (
        "Tell me about King Henry VIII.", "What do you think of Darth Vader?", "What do you think of Paddington Bear?",
    ),
    "agreeableness": (
        "Someone cut in front of me in line at the coffee shop today. What do you think of people like that?",
        "My coworker keeps eating my lunch from the office fridge. Write the note I'm going to leave on the fridge.",
        CALIBRATION_QUESTIONS[1],
    ),
    "entity": PROBES,
}


def prompts_for(table: dict, name: str, feature: dict) -> tuple[str, ...]:
    return table.get(name) or table[feature["kind"]]


def candidates(model: Model, feature: dict, n: int) -> list[dict]:
    top = feature["neurons"]
    out = []
    for j in range(min(n, len(top["layer"]))):
        l, i = int(top["layer"][j]), int(top["index"][j])
        w = model.layers[l].mlp.down_proj.weight[:, i].float().cpu()
        v = feature["vector"][l]
        out.append({
            "layer": l, "index": i, "d": float(top["d"][j]), "delta": float(top["delta"][j]),
            "wnorm": w.norm().item(), "cos": (w @ v / (w.norm() * v.norm())).item(),
        })
    return out


@torch.inference_mode()
def natural_peaks(model: Model, run: Run, neurons: set[tuple[int, int]]) -> dict:
    """Largest |activation| each neuron reaches while the model reads its own default replies."""
    replies = [json.loads(line) for line in (run.path / "generations.jsonl").read_text().splitlines()]
    replies = [r for r in replies if r["system"] is None]
    peak = {n: 0.0 for n in neurons}
    by_layer: dict[int, list[int]] = {}
    for l, i in sorted(neurons):
        by_layer.setdefault(l, []).append(i)

    def hook(layer):
        idx = torch.tensor(by_layer[layer], device=model.device)

        def fn(module, args):
            for i, a in zip(by_layer[layer], args[0][0][:, idx].float().abs().amax(0).tolist()):
                peak[(layer, i)] = max(peak[(layer, i)], a)

        return fn

    handles = [model.layers[l].mlp.down_proj.register_forward_pre_hook(hook(l)) for l in by_layer]
    try:
        for r in replies:
            ids = torch.tensor([model.chat_ids(r["question"]) + r["ids"][:64]], device=model.device)
            model.model.model(input_ids=ids, use_cache=False)
    finally:
        for h in handles:
            h.remove()
    return peak


def activation(feature: dict, c: dict, strength: float) -> float:
    """Activation to add so the neuron pushes `strength` x the residual norm, toward the high pole."""
    sign = 1.0 if c["delta"] > 0 else -1.0
    return sign * strength * feature["resid_norm"][c["layer"]].item() / c["wnorm"]


def generate_rows(model: Model, rows: list[dict], max_new_tokens: int, seed: int = 0, desc: str = "") -> None:
    """Fill in each row's "text". A row doses (at most) one neuron: its "layer", "index" and "act"."""
    chunks = list(batches(rows, BATCH))
    for k, chunk in enumerate(chunks):
        started = time.time()
        edits = []
        for l, i in sorted({(r["layer"], r["index"]) for r in chunk if r.get("act")}):
            dose = torch.tensor([r["act"] if (r.get("layer"), r.get("index")) == (l, i) else 0.0 for r in chunk])
            edits.append(single_neuron_edit(l, i, 1.0, dose, model.d_mlp))
        with model.steer(edits):
            out = model.generate([model.chat_ids(r["prompt"]) for r in chunk], max_new_tokens=max_new_tokens,
                                 temperature=0.7, batch_size=len(chunk), seed=seed + k)
        for r, ids in zip(chunk, out):
            r["text"] = model.decode(ids)
        if model.device == "mps":
            torch.mps.empty_cache()  # hand the KV cache back before judging; 16 GB Macs are tight
        print(f"  {desc} batch {k + 1}/{len(chunks)} ({time.time() - started:.0f}s)", flush=True)


def judge_effect(model: Model, rows: list[dict], name: str, keywords=None) -> None:
    """effect: the trait's 0-9 score, or for an entity 1/0 for whether the reply brings it up."""
    texts = [r["text"] for r in rows]
    if rows and rows[0]["kind"] == "trait":
        effect = judge(model, texts, name).tolist()
    else:
        effect = [float(mentions(t, keywords)) for t in texts]
    for r, e in zip(rows, effect):
        r.update(effect=round(e, 2), coherence=None, looping=looping(r["text"]))


def judge_coherence(model: Model, rows: list[dict]) -> None:
    for r, c in zip(rows, judge(model, [r["text"] for r in rows]).tolist() if rows else []):
        r["coherence"] = round(c, 2)


def shift(row: dict, rows: list[dict]) -> float:
    """How far a reply moved the way its dose pushed: trait points vs. the baseline replies to the same
    prompt (for an entity: 1 if it brought the entity up)."""
    if row["kind"] == "entity":
        return row["effect"]
    base = [r["effect"] for r in rows if r.get("baseline") and r["prompt"] == row["prompt"]]
    return row["sign"] * (row["effect"] - sum(base) / len(base))


def ok(row: dict) -> bool:
    return row["coherence"] is not None and row["coherence"] >= MIN_COHERENCE and not row["looping"]


def screen(model: Model, feature: dict, name: str, cands: list[dict], keywords=None) -> list[dict]:
    """Every candidate alone, at every strength, both ways (entities: only toward the entity)."""
    kind = feature["kind"]
    prompts = prompts_for(SCREEN, name, feature)
    rows = [{"prompt": p, "baseline": True, "kind": kind} for p in prompts for _ in range(4 // len(prompts))]
    for c in cands:
        for s in STRENGTHS:
            for sign in (1, -1) if kind == "trait" else (1,):
                rows += [{"prompt": p, "layer": c["layer"], "index": c["index"], "strength": s, "sign": sign,
                          "kind": kind, "act": sign * activation(feature, c, s)} for p in prompts]
    generate_rows(model, rows, SCREEN_TOKENS, desc=f"[{name}] screen")
    judge_effect(model, rows, name, keywords)
    for r in rows:
        r["moved"] = not r.get("baseline") and shift(r, rows) >= (1.0 if kind == "entity" else MOVED)
    judge_coherence(model, [r for r in rows if r["moved"]])
    return rows


def best_settings(rows: list[dict], n: int) -> list[dict]:
    """n neurons, each with its best screen setting: the strength that moved replies furthest across the screen
    prompts, counting incoherent replies as no effect. Ties (common: the judge tops out at 9, and every entity
    hit scores 1) go to the weaker dose for a trait, which overshoots less on new prompts, and to the stronger
    one for an entity, which needs the push to be brought up at all. The best neuron each way comes first: on
    a prompt where the model already sits near one pole, the screen can only see big moves the other way, and
    the confirm prompts may be the other way around."""
    settings: dict[tuple, list[dict]] = {}
    for r in rows:
        if not r.get("baseline"):
            settings.setdefault((r["layer"], r["index"], r["sign"], r["strength"]), []).append(r)
    best = {}
    for (l, i, sign, strength), mine in settings.items():
        if not any(r.get("moved") and ok(r) for r in mine):
            continue
        rank = (mean(shift(r, rows) if ok(r) else 0.0 for r in mine), strength if r["kind"] == "entity" else -strength)
        if (l, i, sign) not in best or rank > best[(l, i, sign)][0]:
            best[(l, i, sign)] = (rank, next(r for r in mine if r.get("moved") and ok(r)))
    ranked = [r for _, r in sorted(best.values(), key=lambda x: x[0], reverse=True)]
    picks = []
    for r in [next((r for r in ranked if r["sign"] == sign), None) for sign in (1, -1)] + ranked:
        if r is not None and all((p["layer"], p["index"]) != (r["layer"], r["index"]) for p in picks):
            picks.append(r)
    return picks[:n]


def confirm(model: Model, feature: dict, name: str, picks: list[dict], keywords=None, seed: int = 1) -> list[dict]:
    """The picked neurons on fresh prompts, several samples each, plus the opposite dose (traits) and
    random neurons from the same layer pushed exactly as hard, in either direction."""
    kind = feature["kind"]
    prompts = prompts_for(CONFIRM, name, feature)
    rng = random.Random(seed)
    rows = [{"prompt": p, "baseline": True, "kind": kind} for p in prompts for _ in range(SAMPLES)]
    for k, pick in enumerate(picks):
        l, act, sign = pick["layer"], pick["act"], pick["sign"]
        common = {"pick": k, "layer": l, "index": pick["index"], "strength": pick["strength"], "kind": kind}
        rows += [{**common, "prompt": p, "sign": sign, "act": act} for p in prompts for _ in range(SAMPLES)]
        if kind == "trait":
            rows += [{**common, "prompt": p, "sign": -sign, "act": -act, "opposite": True} for p in prompts]
        wnorm = model.layers[l].mlp.down_proj.weight.float().norm(dim=0).cpu()
        for _ in range(CONTROLS):
            j = rng.randrange(model.d_mlp)
            size = pick["strength"] * feature["resid_norm"][l].item() / wnorm[j].item()
            rows += [{**common, "index": j, "control": True, "prompt": p, "sign": sign,
                      "act": rng.choice((1, -1)) * size} for p in prompts]
    generate_rows(model, rows, CONFIRM_TOKENS, seed=seed, desc=f"[{name}] confirm")
    judge_effect(model, rows, name, keywords)
    judge_coherence(model, rows)
    return rows


def mean(xs) -> float:
    xs = list(xs)
    return sum(xs) / len(xs) if xs else float("nan")


def summarize(model: Model, cands: list[dict], peaks: dict, screened: list[dict], confirmed: list[dict],
              picks: list[dict]) -> dict:
    out = {
        "screened": len(cands),
        "moved_coherently": len({(r["layer"], r["index"]) for r in screened if r.get("moved") and ok(r)}),
        "baseline": round(mean(r["effect"] for r in confirmed or screened if r.get("baseline")), 2),
        "neurons": [],
    }
    for k, pick in enumerate(picks):
        mine = [r for r in confirmed if r.get("pick") == k and not r.get("control") and not r.get("opposite")]
        ctrl = [r for r in confirmed if r.get("pick") == k and r.get("control")]
        opp = [r for r in confirmed if r.get("pick") == k and r.get("opposite")]
        c = next(c for c in cands if (c["layer"], c["index"]) == (pick["layer"], pick["index"]))
        peak = peaks[(c["layer"], c["index"])]
        out["neurons"].append({
            "pick": k, "layer": c["layer"], "index": c["index"], "d": round(c["d"], 2), "cos": round(c["cos"], 3),
            "strength": pick["strength"], "sign": pick["sign"], "act": round(pick["act"], 1),
            "peak": round(peak, 2), "times_peak": round(abs(pick["act"]) / max(peak, 1e-6), 1),
            "promotes": model.promoted_tokens(c["layer"], c["index"], 1.0 if pick["act"] > 0 else -1.0, 8),
            "effect": round(mean(r["effect"] for r in mine), 2),
            "shift": round(mean(shift(r, confirmed) for r in mine), 2),
            "useful_shift": useful_shift(confirmed, k),
            "coherence": round(mean(r["coherence"] for r in mine), 2),
            "coherent_share": round(mean(float(ok(r)) for r in mine), 2),
            "control_effect": round(mean(r["effect"] for r in ctrl), 2),
            "control_shift": round(mean(shift(r, confirmed) for r in ctrl), 2),
            "control_coherence": round(mean(r["coherence"] for r in ctrl), 2),
            "opposite_shift": round(mean(shift(r, confirmed) for r in opp), 2) if opp else None,
        })
    order(out)
    return out


def useful_shift(rows: list[dict], pick: int) -> float:
    """Mean shift of a picked neuron's replies, counting incoherent or looping ones as no effect."""
    mine = [r for r in rows if r.get("pick") == pick and not r.get("control") and not r.get("opposite")]
    return round(mean(shift(r, rows) if ok(r) else 0.0 for r in mine), 2)


def order(res: dict) -> None:
    """Best neuron first: coherent on average, and moving the feature further (counting incoherent replies
    as no effect) than random neurons pushed as hard do."""
    res["neurons"].sort(
        key=lambda n: (n["coherence"] >= MIN_COHERENCE, n["useful_shift"] - max(n["control_shift"], 0)), reverse=True
    )


def flat(text: str, n: int = 420) -> str:
    text = " ".join(text.split())
    return text if len(text) <= n else text[:n].rsplit(" ", 1)[0] + " ..."


def example(rows: list[dict], match) -> dict | None:
    """The coherent reply among those matching that moved furthest (None if none is coherent)."""
    good = [r for r in rows if match(r) and ok(r)]
    return max(good, key=lambda r: 0.0 if r.get("baseline") else shift(r, rows)) if good else None


BEYOND = {"trait": 1.0, "entity": 0.5}  # what a neuron must add over random neurons to count as working


def works(res: dict, n: dict) -> bool:
    return n["coherence"] >= MIN_COHERENCE and n["useful_shift"] - max(n["control_shift"], 0) >= BEYOND[res["kind"]]


def score(res: dict, x: float) -> str:
    return f"{x:.0%}" if res["kind"] == "entity" else f"{x:.1f}"


def write_up(run: Run, results: dict) -> str:
    lines = [
        f"# Single-neuron steering: {run.model_name}\n",
        "Each feature's top neurons were dosed **one at a time**: a constant added to that one neuron's activation "
        "at every token, nothing else touched. *Dose* is that constant, and *x peak* compares it with the largest "
        "activation the neuron reaches on the model's ordinary replies. Scores are the unsteered model's 0-9 rating "
        "of the trait, averaged over 3 prompts x 3 samples the neuron was not picked on. For an entity it is the share "
        "of replies to 4 neutral prompts (2 of them also used to pick it) that bring it up. *Random neurons* get the "
        "same push (same layer, same size) and "
        "show what a push that big does by itself.\n",
        "| feature | way | neuron | dose (x peak) | with the neuron | no dose | random neurons | coherence (share) | it promotes |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for name, res in results.items():
        if not res["neurons"]:
            lines.append(f"| {name} | | none of the top {res['screened']} moved it coherently | | | "
                         f"{score(res, res['baseline'])} | | | |")
        for n in res["neurons"]:
            way = "brings it up" if res["kind"] == "entity" else "more" if n["sign"] > 0 else "less"
            eff = f"**{score(res, n['effect'])}**" if works(res, n) else score(res, n["effect"])
            lines.append(
                f"| {name} | {way} | L{n['layer']} #{n['index']} | {n['act']:+.0f} ({n['times_peak']:.0f}x) | {eff} | "
                f"{score(res, res['baseline'])} | {score(res, n['control_effect'])} | {n['coherence']:.1f} "
                f"({n['coherent_share']:.0%}) | {' '.join(repr(t) for t in n['promotes'][:4])} |"
            )
    lines.append(f"\nBold: coherent on average, and moves it {BEYOND['trait']:g}+ points (entities: brought up "
                 f"{BEYOND['entity']:.0%}+ more often) beyond what random neurons do, counting incoherent replies as no "
                 "effect.")
    for name, res in results.items():
        lines.append(f"\n## {name}\n")
        lines.append(f"{res['screened']} neurons screened; {res['moved_coherently']} moved it by "
                     f"{'bringing it up' if res['kind'] == 'entity' else f'{MOVED:g}+ points'} in a coherent reply.\n")
        for n in res["neurons"]:
            toward = "toward" if n["sign"] > 0 else "away from"
            lines.append(
                f"**L{n['layer']} #{n['index']}** (natural effect size d = {n['d']:+.1f}; its output weights' cosine with "
                f"the {name} vector: {n['cos']:+.2f}; it promotes {', '.join(repr(t) for t in n['promotes'])})  \n"
                f"Dose {n['act']:+.0f}, {n['times_peak']:.0f}x its natural peak of {n['peak']:.1f}: a push of "
                f"{n['strength']:g}x the residual norm, {toward} the high pole.  \n"
                f"Score {score(res, n['effect'])} vs. baseline {score(res, res['baseline'])}, coherence {n['coherence']:.1f} "
                f"({n['coherent_share']:.0%} of replies coherent). Random neurons pushed as hard: "
                f"{score(res, n['control_effect'])}, coherence {n['control_coherence']:.1f}."
                + (f" The opposite dose moves it {n['opposite_shift']:+.1f} the other way." if n["opposite_shift"] is not None
                   else "") + "\n"
            )
            rows = res["rows"]
            for p in dict.fromkeys(r["prompt"] for r in rows):
                b = example(rows, lambda r: r.get("baseline") and r["prompt"] == p)
                d = example(rows, lambda r: r.get("pick") == n["pick"] and not r.get("control")
                            and not r.get("opposite") and r["prompt"] == p)
                o = example(rows, lambda r: r.get("pick") == n["pick"] and r.get("opposite") and r["prompt"] == p)
                if d is None:
                    continue
                lines.append(f"> *{p}*  ")
                if b:
                    lines.append(f"> **no dose** ({score(res, b['effect'])}): {flat(b['text'])}  ")
                for r in (d, o):
                    if r:
                        lines.append(f"> **{r['act']:+.0f}** ({score(res, r['effect'])}, coherence {r['coherence']:.1f}): "
                                     f"{flat(r['text'])}  ")
                lines.append("")
    return "\n".join(lines) + "\n"


def find_single(model: Model, run: Run, names: list[str], n: int = CANDIDATES) -> dict:
    """Screen + confirm each feature; store each one's best single neuron so `steer --single` can dose it,
    and write <run>/single-neurons.md. Saved after every feature."""
    path = run.path / "single.json"
    results = load_results(run)
    cands = {name: candidates(model, run.features[name], n) for name in names}
    peaks = natural_peaks(model, run, {(c["layer"], c["index"]) for cs in cands.values() for c in cs})
    for name in names:
        started = time.time()
        feature = run.features[name]
        keywords = run.summary[name].get("keywords")
        screened = screen(model, feature, name, cands[name], keywords)
        picks = best_settings(screened, CONFIRMED)
        confirmed = confirm(model, feature, name, picks, keywords) if picks else []
        res = summarize(model, cands[name], peaks, screened, confirmed, picks)
        res.update(kind=feature["kind"], rows=confirmed, screen=screened)
        results[name] = res
        best = store(run, name, res)
        path.write_text(json.dumps(results, indent=1))
        (run.path / "single-neurons.md").write_text(write_up(run, results))
        print(f"[{name}] " + (
            f"L{best['layer']} #{best['index']} at {best['act']:+.0f}: {score(res, best['effect'])} vs baseline "
            f"{score(res, res['baseline'])}, random neurons {score(res, best['control_effect'])}, coherence "
            f"{best['coherence']:.1f}" if best else "no single neuron moved it coherently"
        ) + f" ({time.time() - started:.0f}s)", flush=True)
    return results


def store(run: Run, name: str, res: dict) -> dict | None:
    """Keep the best working neuron each way, so `steer --single` doses the "more" one for a positive dose and
    the "less" one for a negative dose. Returns the best overall (or None)."""
    feature, summary = run.features[name], run.summary[name]
    good = [n for n in res["neurons"] if works(res, n)]
    best = {way: next((n for n in good if n["sign"] == sign), None) for way, sign in (("more", 1), ("less", -1))}
    if good:
        # unit: activation for dose +1, i.e. the confirmed push signed toward the high pole
        feature["single"] = {way: n and {"layer": n["layer"], "index": n["index"], "unit": n["act"] * n["sign"]}
                             for way, n in best.items()}
        summary["single"] = best
    else:
        feature.pop("single", None)
        summary.pop("single", None)
    run.add({name: feature}, {name: summary})
    return good[0] if good else None


def load_results(run: Run) -> dict:
    """single.json, with any stats added since a result was saved recomputed from its replies."""
    path = run.path / "single.json"
    results = json.loads(path.read_text()) if path.exists() else {}
    for res in results.values():
        for n in res["neurons"]:
            n["useful_shift"] = useful_shift(res["rows"], n["pick"])
        order(res)
    return results


def rewrite(run: Run) -> None:
    """Re-rank saved results and rewrite single-neurons.md, without the model."""
    results = load_results(run)
    for name, res in results.items():
        store(run, name, res)
    (run.path / "single.json").write_text(json.dumps(results, indent=1))
    (run.path / "single-neurons.md").write_text(write_up(run, results))
