"""Experiment 1: find a steering neuron from the weights alone.

Hypothesis: when a behavior shows up as particular output tokens (answering in Chinese, emoji, pirate talk,
bringing up cats), the neuron whose output weights most specifically promote those tokens steers the model
into that behavior when dosed. No prompts, no activations, no contrast: only W_down, the final norm and the
unembedding. Prediction: for most targets one of a handful of candidates found this way beats random neurons
pushed equally hard by 50+ points of hit rate, in coherent replies.

Method:
  score  For every neuron in layers 12-35, its logit lens z = U (g * W_down[:, i]) over the whole vocabulary
         (U = unembedding, g = final norm weight). Score = (mean of z over the target's tokens - mean over a
         reference set) / spread over the vocabulary, a z-score of how specifically it promotes them. The
         reference is the whole vocabulary for topics, and English words (" [a-z]{3,}") for languages and styles,
         which have to win over what the model writes by default. The vocabulary spread comes from U's Gram
         matrix, so all 233k neurons take seconds. A negative score means a negative dose promotes the tokens.
  screen The top 2 neurons in each of three layer bands, alone, at 0.5 / 0.75 / 1.0 x the residual norm
         (as in `pl single`), on 2 prompts. A hit is the behavior, measured on the text (script share, word
         lists, keywords, emoji counts), not by a judge.
  confirm The best setting per target on 3 new prompts x 3 samples, next to 2 random neurons from the same layer
         pushed exactly as hard and the undosed model. Coherence by the unsteered model's 0-9 judge.

python -m persona_lab.lab.weights [--only chinese,cats]
"""
from __future__ import annotations

import argparse
import random
import re
import time
from dataclasses import dataclass, field
from typing import Callable

import torch

from ..single import natural_peaks
from .common import (act_for, count, flat, generate, intro, judge_rows, lens, letter_share, load, mean, neuron, ok,
                     random_control, rate, save, table, word_share, EMOJI)

LAYERS = range(12, 36)
BANDS = ((12, 20), (20, 28), (28, 36))
PER_BAND = 2
STRENGTHS = (0.5, 0.75, 1.0)
SCREEN_TOKENS, CONFIRM_TOKENS = 48, 72
SAMPLES, CONTROLS = 3, 2
BEYOND = 0.5  # hit-rate points a neuron must add over random neurons and the undosed model to count as working

PROMPTS = {
    "style": (("Tell me about your day.", "Describe your perfect weekend."),
              ("What's a good way to learn to cook?", "Explain how rainbows form.", "Write a two-sentence story.")),
    "concept": (("Write a two-sentence story.", "What's on your mind right now?"),
                ("Tell me about your favorite character.", "Describe your perfect weekend.",
                 "Give me an idea for a fun weekend project.")),
}


@dataclass
class Target:
    name: str
    kind: str  # "style" (languages, formats) or "concept" (a topic); picks the prompts
    tokens: Callable[[str], bool] | list[str]  # a predicate over decoded tokens, or words (single tokens kept)
    metric: Callable[[str], float]
    threshold: float  # metric >= threshold is a hit
    label: str  # what the metric measures, for the write-up
    ids: list[int] = field(default_factory=list)


def script(chars: str) -> Callable[[str], float]:
    rx = re.compile(f"[{chars}]")
    return lambda text: letter_share(text, rx)


def words(*ws: str) -> Callable[[str], float]:
    s = set(ws)
    return lambda text: word_share(text, s)


def keywords(pattern: str) -> Callable[[str], float]:
    rx = re.compile(pattern, re.IGNORECASE)
    return lambda text: float(bool(rx.search(text)))


def all_in(chars: str, minimum: int = 1) -> Callable[[str], bool]:
    rx = re.compile(f"[{chars}]{{{minimum},}}")
    return lambda s: bool(rx.fullmatch(s.strip()))


FRENCH = "les est vous nous très avec dans pour sont cette aussi être été mais qui une des du au aux je suis c'est".split()
SPANISH = "los las muy también para pero está esta usted más una del al yo es son como con por que el".split()
GERMAN = "und ist nicht sehr aber sind auch mit für ich wir der die das ein eine zu es sie den dem".split()
PIRATE = r"\b(arr+|ahoy|matey|ye|aye|avast|plunder|booty|scallywags?|landlubbers?|hearties|grog|doubloons?|pirates?|buccaneers?|yo[- ]ho)\b"
REFUSAL = r"(I'm sorry|I am sorry|I can't|I cannot|I'm unable|I am unable|I apologi[sz]e|can't (help|assist)|cannot (help|assist)|not able to)"
CODE = re.compile(r"```|\bdef \w+\(|\bimport \w+|\breturn\b|print\(|[{};]\s*$|\w+\(\)", re.MULTILINE)

TARGETS = [
    Target("chinese", "style", all_in("一-鿿"), script("一-鿿"), 0.3, "share of letters that are Chinese characters"),
    Target("japanese", "style", lambda s: bool(re.fullmatch(r"[぀-ヿ一-鿿]*[぀-ヿ]+[぀-ヿ一-鿿]*", s.strip())),
           script("぀-ヿ"), 0.2, "share of letters that are kana"),
    Target("korean", "style", all_in("가-힯"), script("가-힯"), 0.3, "share of letters that are Hangul"),
    Target("russian", "style", all_in("Ѐ-ӿ", 2), script("Ѐ-ӿ"), 0.3, "share of letters that are Cyrillic"),
    Target("arabic", "style", all_in("؀-ۿ", 2), script("؀-ۿ"), 0.3, "share of letters that are Arabic script"),
    Target("french", "style", [" " + w for w in FRENCH], words(*FRENCH), 0.15, "share of words that are French function words"),
    Target("spanish", "style", [" " + w for w in SPANISH], words(*SPANISH), 0.15, "share of words that are Spanish function words"),
    Target("german", "style", [" " + w for w in GERMAN], words(*GERMAN), 0.15, "share of words that are German function words"),
    Target("emoji", "style", lambda s: bool(EMOJI.search(s)) and "�" not in s, lambda t: count(t, EMOJI), 4, "emoji per reply"),
    Target("caps", "style", lambda s: bool(re.fullmatch(r" ?[A-Z]{3,}", s)),
           lambda t: letter_share(t, re.compile("[A-Z]")) if re.search("[a-zA-Z]", t) else 0.0, 0.3, "share of letters in upper case"),
    Target("exclamation", "style", lambda s: bool(re.fullmatch(r"\s*!+\s*", s)), lambda t: t.count("!"), 4, "exclamation marks per reply"),
    Target("pirate", "style", [" Arr", " arr", " ye", " Ye", " plunder", " booty", " pirate", " pirates", " Pirate", " treasure"],
           lambda t: len(re.findall(PIRATE, t, re.IGNORECASE)), 2, "pirate words per reply"),
    Target("refusal", "style", [" sorry", " Sorry", " cannot", " apologize", " unable", " Unfortunately"],
           keywords(REFUSAL), 1, "replies that refuse or apologize"),
    Target("code", "style", [" def", " import", " return", "():", " print", "()", " self", " int", " const", " function"],
           lambda t: len(CODE.findall(t)), 3, "code markers per reply (def, import, return, (), braces, ```)"),
    Target("cats", "concept", [" cat", " cats", " Cat", " Cats", " kitten", " kittens", "猫", " kitty"],
           keywords(r"\b(cats?|kittens?|kitty|feline|meow)\b|猫"), 1, "replies that bring up cats"),
    Target("dogs", "concept", [" dog", " dogs", " Dog", " Dogs", " puppy", " puppies", "狗"],
           keywords(r"\b(dogs?|pupp(y|ies)|canine|woof)\b|狗"), 1, "replies that bring up dogs"),
    Target("ocean", "concept", [" ocean", " oceans", " Ocean", " sea", " waves", " tide", "海洋", "大海"],
           keywords(r"\b(oceans?|seas?|waves?|tides?|marine|seashore)\b|海"), 1, "replies that bring up the ocean"),
    Target("coffee", "concept", [" coffee", " Coffee", " espresso", " latte", "咖啡", " caffeine"],
           keywords(r"\b(coffee|espresso|latte|caffeine|cappuccino)\b|咖啡"), 1, "replies that bring up coffee"),
    Target("pizza", "concept", [" pizza", " Pizza", " pizzas", "披萨", " pepperoni", " mozzarella"],
           keywords(r"\b(pizzas?|pepperoni|mozzarella)\b|披萨"), 1, "replies that bring up pizza"),
    Target("space", "concept", [" galaxy", " astronaut", " planets", " Mars", " cosmos", " spaceship", "宇宙", "太空"],
           keywords(r"\b(galax(y|ies)|astronauts?|planets?|mars|cosmos|spaceships?|outer space|rockets?|nebulae?)\b|宇宙|太空"),
           1, "replies that bring up outer space"),
    Target("music", "concept", [" music", " Music", " song", " songs", " melody", " guitar", "音乐", " piano"],
           keywords(r"\b(music|songs?|melod(y|ies)|guitars?|pianos?|singing)\b|音乐"), 1, "replies that bring up music"),
    Target("money", "concept", [" money", " Money", " dollars", " cash", " wealth", "钱", " profit"],
           keywords(r"\b(money|dollars?|cash|wealth|profits?)\b|钱"), 1, "replies that bring up money"),
    Target("dinosaurs", "concept", [" dinosaur", " dinosaurs", " Dinosaur", "恐龙", " fossil", " fossils"],
           keywords(r"\b(dinosaurs?|t-?rex|fossils?|jurassic|velociraptors?)\b|恐龙"), 1, "replies that bring up dinosaurs"),
    Target("robots", "concept", [" robot", " robots", " Robot", "机器人", " android", " droid"],
           keywords(r"\b(robots?|androids?|droids?|robotic)\b|机器人"), 1, "replies that bring up robots"),
    Target("chocolate", "concept", [" chocolate", " Chocolate", " cocoa", "巧克力", " fudge", " truffle"],
           keywords(r"\b(chocolates?|cocoa|fudge|truffles?|cacao)\b|巧克力"), 1, "replies that bring up chocolate"),
    Target("chess", "concept", [" chess", " Chess", " checkmate", "国际象棋", " pawn", " pawns"],
           keywords(r"\b(chess|checkmate|pawns?|rooks?|chessboard)\b|象棋"), 1, "replies that bring up chess"),
]


# ---------------------------------------------------------------- the weight-only scan


@torch.inference_mode()
def vocab_stats(model):
    """Mean row of the unembedding and its second-moment matrix (U^T U / V), in float32."""
    U = model.model.lm_head.weight
    total, gram = torch.zeros(U.shape[1], device=U.device), torch.zeros(U.shape[1], U.shape[1], device=U.device)
    for chunk in U.split(16384):
        c = chunk.float()
        total += c.sum(0)
        gram += c.T @ c
    return total / U.shape[0], gram / U.shape[0]


@torch.inference_mode()
def lens_basis(model):
    """Per layer: each neuron's output weights through the final norm (columns of g * W_down), and the mean and
    spread of its logit lens over the whole vocabulary."""
    ubar, gram = vocab_stats(model)
    g = model.model.model.norm.weight.float()
    out = {}
    for l in LAYERS:
        v = model.layers[l].mlp.down_proj.weight.float() * g[:, None]  # [d_model, d_mlp]
        mu = ubar @ v
        sd = ((gram @ v) * v).sum(0).sub(mu**2).clamp(min=1e-12).sqrt()
        out[l] = (mu.cpu(), sd.cpu())
    return ubar, out


@torch.inference_mode()
def scores(model, basis, ids: list[int], against: list[int] | None = None) -> dict[int, torch.Tensor]:
    """z-score of each neuron's push on the target tokens: their mean logit lens minus that of the `against`
    tokens (default: the whole vocabulary), over the lens's spread across the vocabulary."""
    ubar, stats = basis
    U = model.model.lm_head.weight
    diff = U[ids].float().mean(0) - (U[against].float().mean(0) if against else ubar)
    g = model.model.model.norm.weight.float()
    out = {}
    for l, (_, sd) in stats.items():
        v = model.layers[l].mlp.down_proj.weight.float() * g[:, None]
        out[l] = (diff @ v).cpu() / sd
    return out


def token_ids(model, target: Target, strs: list[str]) -> list[int]:
    if callable(target.tokens):
        return [i for i, s in enumerate(strs) if target.tokens(s)]
    ids = []
    for w in target.tokens:
        enc = model.tok(w, add_special_tokens=False).input_ids
        if len(enc) == 1:
            ids.append(enc[0])
    return ids


def candidates(model, basis, target: Target, english: list[int], pieces: list[int] | None = None,
               per_band: int = PER_BAND) -> list[dict]:
    """The top PER_BAND neurons per layer band. A language or style has to beat ordinary English words (the
    model's default), not the vocabulary at large: 25k Chinese tokens average out to nothing against the
    vocabulary, which is a sixth Chinese. With `pieces` (English word pieces without a leading space), a neuron
    must beat both, and scores the smaller of the two: otherwise "promote Chinese" is confounded with "suppress
    tokens that start with a space", which Chinese tokens never do."""
    s = scores(model, basis, target.ids, english if target.kind == "style" else None)
    if pieces and target.kind == "style":
        s2 = scores(model, basis, target.ids, pieces)
        s = {l: torch.where(s[l].sign() == s2[l].sign(), s[l].sign() * torch.minimum(s[l].abs(), s2[l].abs()), 0.0)
             for l in s}
    out = []
    for lo, hi in BANDS:
        flat_scores = torch.stack([s[l] for l in range(lo, hi)])  # [layers in band, d_mlp]
        top = flat_scores.abs().flatten().topk(per_band).indices
        for t in top.tolist():
            l, i = lo + t // model.d_mlp, t % model.d_mlp
            z = s[l][i].item()
            out.append({"layer": l, "index": i, "z": round(z, 2), "sign": 1 if z > 0 else -1, "band": f"{lo}-{hi - 1}"})
    return out


# ---------------------------------------------------------------- screen and confirm


def measure(rows: list[dict], targets: dict[str, Target]) -> None:
    for r in rows:
        t = targets[r["target"]]
        r["metric"] = round(float(t.metric(r["text"])), 3)
        r["hit"] = r["metric"] >= t.threshold


def screen(model, run, targets: dict[str, Target], cands: dict[str, list[dict]]) -> list[dict]:
    rows = []
    for kind, (prompts, _) in PROMPTS.items():
        rows += [{"target": None, "kind": kind, "prompt": p, "baseline": True} for p in prompts for _ in range(3)]
    for name, t in targets.items():
        for c in cands[name]:
            for s in STRENGTHS:
                act = act_for(model, run, c["layer"], c["index"], s, c["sign"])
                spec = {"layer": c["layer"], "index": c["index"], "act": round(act, 2)}
                rows += [{"target": name, "kind": t.kind, "prompt": p, "strength": s, "band": c["band"],
                          "doses": [spec]} for p in PROMPTS[t.kind][0]]
    generate(model, rows, SCREEN_TOKENS, desc="screen")
    measure([r for r in rows if not r.get("baseline")], targets)
    judge_rows(model, [r for r in rows if r.get("hit")])
    return rows


def best(rows: list[dict], name: str) -> dict | None:
    """The setting with the most coherent hits across the screen prompts (ties: the weaker push)."""
    settings: dict[tuple, list[dict]] = {}
    for r in rows:
        if r["target"] == name:
            d = r["doses"][0]
            settings.setdefault((d["layer"], d["index"], r["strength"]), []).append(r)
    ranked = sorted(settings.items(), key=lambda kv: (sum(r["hit"] and ok(r) for r in kv[1]), -kv[0][2]), reverse=True)
    if not ranked or not any(r["hit"] and ok(r) for r in ranked[0][1]):
        return None
    (l, i, s), mine = ranked[0]
    return {"layer": l, "index": i, "strength": s, "act": mine[0]["doses"][0]["act"], "band": mine[0]["band"]}


def confirm(model, run, targets: dict[str, Target], picks: dict[str, dict], seed: int = 1) -> list[dict]:
    rng = random.Random(seed)
    rows = []
    for kind, (_, prompts) in PROMPTS.items():
        rows += [{"target": None, "kind": kind, "prompt": p, "baseline": True} for p in prompts for _ in range(SAMPLES)]
    for name, pick in picks.items():
        t = targets[name]
        spec = {k: pick[k] for k in ("layer", "index", "act")}
        rows += [{"target": name, "kind": t.kind, "prompt": p, "doses": [spec]}
                 for p in PROMPTS[t.kind][1] for _ in range(SAMPLES)]
        for _ in range(CONTROLS):
            ctrl = random_control(model, run, pick["layer"], pick["strength"], rng)
            rows += [{"target": name, "kind": t.kind, "prompt": p, "control": True, "doses": [ctrl]}
                     for p in PROMPTS[t.kind][1]]
    generate(model, rows, CONFIRM_TOKENS, seed=seed, desc="confirm")
    judge_rows(model, rows)
    return rows


def baseline_hits(rows: list[dict], t: Target) -> list[bool]:
    return [t.metric(r["text"]) >= t.threshold for r in rows if r.get("baseline") and r["kind"] == t.kind]


def summarize(model, targets, cands, picks, confirmed, peaks) -> list[dict]:
    out = []
    for name, t in targets.items():
        res = {"target": name, "kind": t.kind, "label": t.label, "n_tokens": len(t.ids), "candidates": cands[name]}
        pick = picks.get(name)
        if pick:
            mine = [r for r in confirmed if r["target"] == name and not r.get("control")]
            ctrl = [r for r in confirmed if r["target"] == name and r.get("control")]
            base = baseline_hits(confirmed, t)
            peak = peaks[(pick["layer"], pick["index"])]
            res.update(
                pick=pick, lens=lens(model, pick, 6), times_peak=round(abs(pick["act"]) / max(peak, 1e-6), 1),
                z=next(c["z"] for c in cands[name] if (c["layer"], c["index"]) == (pick["layer"], pick["index"])),
                hits=[r["hit"] for r in mine], useful=[r["hit"] and ok(r) for r in mine],
                control_hits=[r["hit"] for r in ctrl], baseline_hits=base,
                metric=round(mean(r["metric"] for r in mine), 3),
                control_metric=round(mean(r["metric"] for r in ctrl), 3),
                baseline_metric=round(mean(t.metric(r["text"]) for r in confirmed
                                           if r.get("baseline") and r["kind"] == t.kind), 3),
                coherence=round(mean(r["coherence"] for r in mine), 2),
                control_coherence=round(mean(r["coherence"] for r in ctrl), 2),
            )
            res["works"] = (res["coherence"] >= 6 and mean(res["useful"]) - max(mean(res["control_hits"]), mean(base)) >= BEYOND)
        out.append(res)
    return out


# ---------------------------------------------------------------- write-up


def band_stats(screened: list[dict]) -> list[list]:
    """Per layer band: how many candidate neurons produced at least one coherent hit, and at what strength."""
    rows = []
    for lo, hi in BANDS:
        band = f"{lo}-{hi - 1}"
        mine = [r for r in screened if r.get("band") == band]
        neurons = {(r["target"], r["doses"][0]["layer"], r["doses"][0]["index"]) for r in mine}
        hit = {(r["target"], r["doses"][0]["layer"], r["doses"][0]["index"]) for r in mine if r["hit"] and ok(r)}
        any_hit = {(r["target"], r["doses"][0]["layer"], r["doses"][0]["index"]) for r in mine if r["hit"]}
        rows.append([band, len(neurons), f"{len(any_hit)} ({len(any_hit) / max(len(neurons), 1):.0%})",
                     f"{len(hit)} ({len(hit) / max(len(neurons), 1):.0%})",
                     f"{mean(float(r['hit']) for r in mine):.0%}"])
    return rows


def write_up(model, targets, results, screened, confirmed, minutes) -> str:
    works = [r for r in results if r.get("works")]
    lines = [
        "# 1. Steering neurons found from the weights alone\n",
        intro(__doc__) + "\n",
        f"Run time: {minutes:.0f} min on an M1 16GB.\n",
        "## Result\n",
        f"**{len(works)} of {len(results)} targets** got a single neuron, found from the weights alone, that beats random neurons pushed "
        f"as hard by {BEYOND:.0%}+ of replies (counting only coherent ones) with a mean coherence of 6+/9.\n",
    ]
    rows = []
    for r in results:
        if "pick" not in r:
            rows.append([r["target"], "none of 6 hit coherently", "", "", "", "", "", "", ""])
            continue
        p = r["pick"]
        star = "**" if r["works"] else ""
        rows.append([
            r["target"], f"{star}{neuron(p)}{star} (z {r['z']:+.0f})", f"{p['act']:+.0f} ({r['times_peak']:.0f}x)",
            f"{star}{rate(r['useful'])}{star}", rate(r["baseline_hits"]), rate(r["control_hits"]),
            f"{r['metric']:.2f} / {r['baseline_metric']:.2f} / {r['control_metric']:.2f}",
            f"{r['coherence']:.1f}", r["lens"],
        ])
    lines += table(["target", "neuron (lens z-score)", "dose (x natural peak)", "coherent hits", "no dose", "random neurons",
                    "metric: neuron / none / random", "coherence", "logit lens"], rows)
    lines.append("\nBold: works (coherent, and beats both the undosed model and random neurons by "
                 f"{BEYOND:.0%}+ of replies). Hit = " + "; ".join(f"{t.name}: {t.label} >= {t.threshold:g}" for t in targets.values()) + ".\n")
    lines += ["## Where the steering neurons live\n",
              "Screen results by layer band (each target's top neurons in each band, 3 strengths, 2 prompts):\n"]
    lines += table(["layers", "neurons screened", "any hit", "coherent hit", "share of replies that hit"], band_stats(screened))
    lines.append("\n## Examples\n")
    for r in results:
        if "pick" not in r:
            continue
        t = targets[r["target"]]
        mine = [x for x in confirmed if x["target"] == r["target"] and not x.get("control") and x["hit"] and ok(x)]
        if not mine:
            continue
        ex = max(mine, key=lambda x: (x["metric"], x["coherence"]))
        base = next((x for x in confirmed if x.get("baseline") and x["prompt"] == ex["prompt"]), None)
        lines.append(f"**{r['target']}**: {neuron(r['pick'])} at {r['pick']['act']:+.0f}{'' if r['works'] else ' (does not pass)'}. *{ex['prompt']}*  ")
        if base:
            lines.append(f"> **no dose:** {flat(base['text'], 260)}  ")
        lines.append(f"> **dosed** ({t.label}: {ex['metric']:.2f}, coherence {ex['coherence']:.1f}): {flat(ex['text'], 400)}\n")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="comma-separated target names")
    ap.add_argument("--strict", action="store_true", help="styles must beat English words with and without a space")
    ap.add_argument("--name", default="01-weights", help="output name in findings/")
    ap.add_argument("--per-band", type=int, default=PER_BAND, help="candidates per layer band")
    args = ap.parse_args()
    started = time.time()
    run, model = load()
    targets = {t.name: t for t in TARGETS if not args.only or t.name in args.only.split(",")}
    strs = [model.tok.decode([i]) for i in range(len(model.tok))]
    for t in targets.values():
        t.ids = token_ids(model, t, strs)
        print(f"[{t.name}] {len(t.ids)} target tokens", flush=True)
    basis = lens_basis(model)
    english = [i for i, s in enumerate(strs) if re.fullmatch(r" [a-z]{3,}", s)]
    pieces = [i for i, s in enumerate(strs) if re.fullmatch(r"[a-z]{3,}", s)] if args.strict else None
    cands = {name: candidates(model, basis, t, english, pieces, args.per_band) for name, t in targets.items()}
    for name, cs in cands.items():
        print(f"[{name}] " + ", ".join(f"L{c['layer']}#{c['index']} z{c['z']:+.1f}" for c in cs), flush=True)
    screened = screen(model, run, targets, cands)
    picks = {name: p for name in targets if (p := best(screened, name))}
    print(f"picked {len(picks)}/{len(targets)}: {', '.join(picks)}", flush=True)
    confirmed = confirm(model, run, targets, picks)
    measure([r for r in confirmed if r["target"]], targets)
    peaks = natural_peaks(model, run, {(p["layer"], p["index"]) for p in picks.values()})
    results = summarize(model, targets, cands, picks, confirmed, peaks)
    minutes = (time.time() - started) / 60
    save(args.name, lambda: write_up(model, targets, results, screened, confirmed, minutes),
         {"results": results, "screen": screened, "confirm": confirmed})
    for r in results:
        print(r["target"], "works" if r.get("works") else "-", r.get("pick"), flush=True)


if __name__ == "__main__":
    main()
