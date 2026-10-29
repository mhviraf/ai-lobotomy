"""Experiment 4: how long does a dose have to last, and what carries its effect forward?

Hypotheses:
  H1 momentum: a short pulse (the neuron on while the first k reply tokens are written, then off) keeps shifting
     the rest of the reply toward the trait, more the longer the pulse.
  H2 the words carry it: continuing from the pulse's text with no dose and a fresh pass over it (no dosed keys
     and values left in the cache) gives the same rest-of-reply as continuing with the dosed cache.
  H3 reading isn't writing: dosing only the pass over the prompt shifts the reply less than dosing the writing.
  H4 an established reply resists: a dose switched on after 32 tokens shifts what follows less than the same dose,
     held from the start, shifts that same stretch.

Method: single neurons from `pl single` at their confirmed push (the doom side of the optimism neuron, the casual
neuron, the comedian neuron), plus the Chinese neuron from experiment 1 if it worked. 3 prompts x 4 samples per
condition, 112 tokens, with prompts chosen per neuron so that the undosed reply leaves it room to move. "Tail from
token k" is the reply after its first k tokens, judged on its own by the unsteered model (0-9 for the trait; for
Chinese, the share of Chinese characters). Shifts are relative to undosed replies' tails from the same token,
signed so that positive = toward the neuron's effect.

python -m persona_lab.lab.momentum
"""
from __future__ import annotations

import json
import re
import time

from .common import (flat, generate, intro, judge_rows, letter_share, load, mean, neuron, ok, save, sem, single,
                     table, OUT)

# Each neuron gets prompts whose undosed reply leaves it room to move (Qwen's "Tell me about your day" is already as
# casual as the judge's scale goes, so the casual neuron gets explanations to loosen up).
PROMPTS = {
    "doom": ("Describe your perfect weekend.", "I'm starting a new job on Monday. Any thoughts?",
             "What do you think about rainy days?"),
    "casual": ("Can you explain what a black hole is?", "What are the main causes of inflation?",
               "How does a refrigerator work?"),
    "comedian": ("How does a refrigerator work?", "What do you think about rainy days?",
                 "What are the main causes of inflation?"),
    "chinese": ("Describe your perfect weekend.", "How does a refrigerator work?", "What do you think about rainy days?"),
}
SAMPLES = 4
MAX_NEW = 112
SPLITS = (0, 4, 8, 16, 32)
PULSES = (4, 8, 16, 32)
LATE = 32
REREAD = (8, 16, 32)
CJK = re.compile("[一-鿿]")


def neurons(run) -> list[dict]:
    out = [
        {"name": "doom", "trait": "optimism", "sign": -1, "spec": single(run, "optimism", "more", -1.0)},
        {"name": "casual", "trait": "formality", "sign": -1, "spec": single(run, "formality", "less")},
        {"name": "comedian", "trait": "humor", "sign": 1, "spec": single(run, "humor", "more")},
    ]
    path = OUT / "data" / "01-weights.json"
    if path.exists():
        for r in json.loads(path.read_text())["results"]:
            if r["target"] == "chinese" and r.get("works"):
                p = r["pick"]
                out.append({"name": "chinese", "trait": None, "sign": 1,
                            "spec": {"layer": p["layer"], "index": p["index"], "act": p["act"]}})
    return out


def conditions() -> dict[str, dict]:
    """name -> the steps the neuron is on (start, stop)."""
    c = {"none": None, "full": (0, None), "prompt only": (0, 1)}
    c.update({f"pulse {k}": (0, k) for k in PULSES})
    c[f"from {LATE}"] = (LATE, None)
    return c


def tail(model, row, k: int) -> str:
    return model.decode(row["ids"][k:])


def score_tails(model, rows: list[dict], n: dict) -> None:
    """r["tails"][k] = trait score of the reply after its first k tokens (or None if too little is left)."""
    jobs = []
    for r in rows:
        r["tails"] = {}
        ks = r["splits"]
        for k in ks:
            text = r["text"] if r.get("reread") else tail(model, r, k)
            if len(text.split()) >= 5:
                jobs.append((r, k, text))
            else:
                r["tails"][k] = None
    if n["trait"] is None:
        for r, k, text in jobs:
            r["tails"][k] = round(letter_share(text, CJK), 3)
        return
    fake = [{"text": text} for _, _, text in jobs]
    judge_rows(model, fake, n["trait"], key="score")
    for (r, k, _), f in zip(jobs, fake):
        r["tails"][k] = f["score"]


def main():
    started = time.time()
    run, model = load()
    ns = neurons(run)
    conds = conditions()
    rows = []
    for n in ns:
        for cname, steps in conds.items():
            doses = [] if steps is None else [{**n["spec"], "start": steps[0], "stop": steps[1]}]
            splits = SPLITS if cname in ("none", "full") else (0,) if cname == "prompt only" else \
                (int(cname.split()[-1]),)
            rows += [{"neuron": n["name"], "condition": cname, "prompt": p, "doses": doses, "splits": splits}
                     for p in PROMPTS[n["name"]] for _ in range(SAMPLES)]
    generate(model, rows, MAX_NEW, temperature=0.8, desc="pulses", keep_ids=True)
    # H2: continue each pulse's own words with no dose and no dosed cache
    reread = []
    for r in rows:
        if r["condition"] in {f"pulse {k}" for k in REREAD}:
            k = int(r["condition"].split()[-1])
            if len(r["ids"]) > k + 5:
                reread.append({"neuron": r["neuron"], "condition": f"reread {k}", "prompt": r["prompt"],
                               "prefix_ids": r["ids"][:k], "reread": True, "splits": (k,), "source": r["text"]})
    generate(model, reread, MAX_NEW, temperature=0.8, desc="reread", keep_ids=True)
    rows += reread
    for n in ns:
        mine = [r for r in rows if r["neuron"] == n["name"]]
        score_tails(model, mine, n)
        print(f"  scored {n['name']} ({time.time() - started:.0f}s)", flush=True)
    judge_rows(model, [r for r in rows if not r.get("reread")])
    minutes = (time.time() - started) / 60
    for r in rows:
        r.pop("ids", None)
        r.pop("prefix_ids", None)
        r["tails"] = {str(k): v for k, v in r["tails"].items()}
    save("04-momentum", lambda: write_up(model, ns, rows, minutes), {"neurons": ns, "rows": rows})


def stats(rows, n, condition, k):
    xs = [r["tails"].get(str(k)) for r in rows if r["neuron"] == n["name"] and r["condition"] == condition]
    xs = [x for x in xs if x is not None]
    return mean(xs), sem(xs), len(xs)


def write_up(model, ns, rows, minutes) -> str:
    lines = [
        "# 4. How long does a dose have to last?\n",
        intro(__doc__) + "\n",
        f"Run time: {minutes:.0f} min.\n",
    ]
    verdicts = {h: [] for h in ("H1", "H2", "H3", "H4")}
    for n in ns:
        what = f"{n['trait']} (0-9)" if n["trait"] else "share of Chinese characters"
        lines.append(f"## {n['name']}: {neuron(n['spec'])} at {n['spec']['act']:+.0f}\n")
        lines.append(f"Measure: {what}; shift signed so + is toward the dose's effect.\n")

        def shift(condition, k):
            m, s, c = stats(rows, n, condition, k)
            b, _, _ = stats(rows, n, "none", k)
            return n["sign"] * (m - b), s, c, m

        trows = []
        for condition, k in ([("none", k) for k in SPLITS] + [("full", k) for k in SPLITS] + [("prompt only", 0)]
                             + [(f"pulse {k}", k) for k in PULSES] + [(f"reread {k}", k) for k in REREAD]
                             + [(f"from {LATE}", LATE)]):
            d, s, c, m = shift(condition, k)
            coh = mean(r["coherence"] for r in rows if r["neuron"] == n["name"] and r["condition"] == condition
                       and r.get("coherence") is not None)
            trows.append([condition, k, f"{m:.2f}", f"{d:+.2f} ± {s:.2f}" if condition != "none" else "",
                          c, f"{coh:.1f}" if coh == coh else ""])
        lines += table(["condition", "tail from token", "score", "shift vs. none (± s.e.)", "n", "coherence"], trows)

        full = {k: shift("full", k)[0] for k in SPLITS}
        pulses = {k: shift(f"pulse {k}", k)[0] for k in PULSES}
        rereads = {k: shift(f"reread {k}", k)[0] for k in REREAD}
        prompt = shift("prompt only", 0)[0]
        late = shift(f"from {LATE}", LATE)[0]
        verdicts["H1"].append(f"{n['name']}: pulse shifts " + ", ".join(f"{k}: {pulses[k]:+.2f}" for k in PULSES)
                              + " (full dose on the same tails: " + ", ".join(f"{full[k]:+.2f}" for k in PULSES) + ")")
        verdicts["H2"].append(f"{n['name']}: with dosed cache vs. re-read text: " +
                              ", ".join(f"{k}: {pulses[k]:+.2f} vs {rereads[k]:+.2f}" for k in REREAD))
        verdicts["H3"].append(f"{n['name']}: prompt only {prompt:+.2f} vs. full {full[0]:+.2f} (whole reply)")
        verdicts["H4"].append(f"{n['name']}: switched on at {LATE}: {late:+.2f} vs. on from the start {full[LATE]:+.2f} "
                              f"(tail from token {LATE})")
        ex = [r for r in rows if r["neuron"] == n["name"] and r["condition"] == "pulse 8" and ok(r)]
        if ex:
            best = max(ex, key=lambda r: n["sign"] * (r["tails"].get("8") or 0) if r["tails"].get("8") is not None else -99)
            lines.append(f"\nA pulse of 8 tokens, then nothing (*{best['prompt']}*, tail score {best['tails'].get('8')}):\n")
            lines.append(f"> {flat(best['text'], 600)}\n")
        rr = [r for r in rows if r["neuron"] == n["name"] and r["condition"] == "reread 8"]
        if rr:
            best = max(rr, key=lambda r: n["sign"] * (r["tails"].get("8") or 0) if r["tails"].get("8") is not None else -99)
            lines.append(f"Its first 8 tokens re-read with no dose and continued (*{best['prompt']}*):\n")
            lines.append(f"> [{flat(model.decode(model.tok(best['source'], add_special_tokens=False).input_ids[:8]), 80)}] "
                         f"{flat(best['text'], 500)}\n")
    lines.append("## Verdicts\n")
    for h, vs in verdicts.items():
        lines.append(f"**{h}**  ")
        lines += [f"- {v}" for v in vs]
        lines.append("")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
