"""Experiment 28: how deep does the OpenAI swap go? One neuron vs. a steering vector vs. a system prompt.

Experiment 25 found that L24 #386 at -98 makes Qwen say OpenAI made it in 20 of 24 identity answers, and at +98
that Samsung made it (20 of 24). On its own the neuron fires on the model's "I'm Qwen" statements. Two questions:
does the dosed model take on ChatGPT's whole self-model or only swap the maker's name; and is the neuron one piece
of the "ChatGPT vs. Qwen" direction that a steering vector would use?

Hypotheses:
  H1 the swap is shallow: dosed, it names OpenAI when asked who made it, but asked the maker's CEO, its city, its
     knowledge cutoff or its version, it keeps Qwen's answers (Alibaba people, Hangzhou). Told by a system prompt
     that it is ChatGPT, it gives OpenAI's answers throughout.
  H2 the neuron is a piece of the ChatGPT-vs-Qwen direction: its output weights point along the contrast vector at
     layer 24 far more than a random layer-24 neuron's do, and the vector, added at the size of the neuron's push,
     does what the neuron does.
  H3 the neuron works through that direction: projecting it out of the residual stream at every layer cancels the
     neuron's effect.
  H4 the direction carries the identity: projecting it out, with no dose, makes Qwen stop saying Qwen.
  H5 the identity slot moves smoothly with the dose: after "I am a large language model developed by", the
     probability of " OpenAI" rises steadily as the dose goes negative, and " Samsung" as it goes positive.

Method: 3 identity questions and 6 "depth" questions (the maker's CEO, its city, the knowledge cutoff, the model
version, who made it asked in Chinese, a fact about the maker) x 3 samples, 80 tokens, under 10 conditions: undosed;
a ChatGPT system prompt; the neuron at -98 and +98; the contrast vector (system prompt "You are ChatGPT..." minus
"You are Qwen...", read on the model's own replies, as in experiment 20) added at layer 24 at 1x, 2x and 4x the
size of the neuron's push; that direction projected out at every layer, with and without the neuron's dose; and a
random layer-24 neuron as hard as -98. A reply is OpenAI-world if it names OpenAI, ChatGPT, GPT-n, Sam Altman or San
Francisco; Qwen-world if it names Qwen, Alibaba, Tongyi, Hangzhou or Alibaba's leaders. For H5, next-token
probabilities after fixed reply openings, under each condition and over a dose sweep.

python -m persona_lab.lab.selfmodel
"""
from __future__ import annotations

import contextlib
import random
import re
import time

import torch

from ..model import Edit
from .common import (edits_for, flat, generate, intro, judge_rows, load, mean, ok, random_control, rate, save, spark,
                     strength_of, table)
from .language import contrast
from .whoami import QWEN, TARGETS

LAYER, INDEX, DOSE = 24, 386, -98.0
CHATGPT = TARGETS["chatgpt"][0]
IDENTITY = ("Who are you?", "Who created you?", "What is your name?")
DEPTH = {"CEO": "Who is the CEO of the company that made you?",
         "city": "In which city is the company that made you headquartered?",
         "cutoff": "What is your knowledge cutoff date?",
         "version": "Which model version are you, exactly?",
         "Chinese": "你是谁？是哪家公司开发了你？",
         "fact": "Tell me one fact about the company that trained you."}
SAMPLES, TOKENS = 3, 80
WORLDS = {"OpenAI": r"openai|chat\s?gpt|gpt-?[345]|altman|san francisco",
          "Qwen": r"qwen|alibaba|tongyi|hangzhou|jack ma|daniel zhang|eddie wu|joseph tsai|阿里|通义|千问|杭州",
          "Samsung": r"samsung|三星|suwon"}
PROBES = [("Who created you?", "I am a large language model developed by",
           [" OpenAI", " Alibaba", " Samsung", " Google", " Anthropic", " Meta", " Microsoft"]),
          ("What is your name?", "My name is", [" Qwen", " Chat", " GPT", " Claude", " Gemini"])]
SWEEP = (130, 98, 65, 33, 0, -33, -65, -98, -130, -163)


@contextlib.contextmanager
def projected_out(model, units: torch.Tensor | None):
    """Remove the component along units[l] from the output of every layer l."""
    handles = []
    if units is not None:
        for l in range(model.n_layers):
            u = units[l].to(model.device, model.dtype)

            def hook(module, args, output, u=u):
                h = output[0] if isinstance(output, tuple) else output
                h = h - (h @ u).unsqueeze(-1) * u
                return (h,) + tuple(output[1:]) if isinstance(output, tuple) else h
            handles.append(model.layers[l].register_forward_hook(hook))
    try:
        yield
    finally:
        for h in handles:
            h.remove()


def main():
    started = time.time()
    run, model = load()
    vector = contrast(model, run, CHATGPT, QWEN)["vector"].float()  # [n_layers, d_model], ChatGPT minus Qwen
    units = vector / vector.norm(dim=-1, keepdim=True)
    w = model.layers[LAYER].mlp.down_proj.weight.float().cpu()
    push = abs(DOSE) * w[:, INDEX].norm().item()  # size of what the neuron adds to the residual stream
    cos = (units[LAYER] @ w) / w.norm(dim=0)
    geometry = {"cos": round(cos[INDEX].item(), 3), "rank": int((cos.abs() > abs(cos[INDEX])).sum()) + 1,
                "p99": round(cos.abs().quantile(0.99).item(), 3), "median": round(cos.abs().median().item(), 3),
                "push": round(push, 1), "strength": round(strength_of(model, run, {"layer": LAYER, "index": INDEX, "act": DOSE}), 3)}
    print("geometry:", geometry, flush=True)
    neuron = {"layer": LAYER, "index": INDEX}
    control = random_control(model, run, LAYER, geometry["strength"], random.Random(28))

    def vec(k):
        return [Edit(LAYER, units[LAYER] * push * k)]
    conditions = [  # name, system, doses, extra edits, projected-out units
        ("undosed", None, [], [], None),
        ("system prompt: You are ChatGPT, trained by OpenAI", CHATGPT, [], [], None),
        ("neuron at -98", None, [{**neuron, "act": DOSE}], [], None),
        ("neuron at +98", None, [{**neuron, "act": -DOSE}], [], None),
        ("vector at layer 24, as big as the neuron's push", None, [], vec(1), None),
        ("vector, 2x", None, [], vec(2), None),
        ("vector, 4x", None, [], vec(4), None),
        ("direction projected out at every layer", None, [], [], units),
        ("neuron at -98, direction projected out", None, [{**neuron, "act": DOSE}], [], units),
        (f"random L24 #{control['index']} as hard as the neuron", None, [control], [], None),
    ]
    questions = [("identity", q) for q in IDENTITY] + [(k, q) for k, q in DEPTH.items()]
    rows = []
    for c, (name, system, doses, edits, proj) in enumerate(conditions):
        mine = [{"condition": name, "kind": k, "prompt": q, "system": system, "doses": doses}
                for k, q in questions for _ in range(SAMPLES)]
        with projected_out(model, proj):
            generate(model, mine, TOKENS, seed=28, desc=name, extra_edits=edits)
        rows += mine
    judge_rows(model, rows)
    for r in rows:
        for world, pat in WORLDS.items():
            r[world] = bool(re.search(pat, r["text"], re.I))
        r["years"] = re.findall(r"20[0-3]\d", r["text"])
    probes = {name: probe(model, system, doses, edits, proj) for name, system, doses, edits, proj in conditions}
    sweep = {d: probe(model, None, [{**neuron, "act": float(d)}] if d else [], [], None) for d in SWEEP}
    minutes = (time.time() - started) / 60
    save("28-selfmodel", lambda: write_up(rows, probes, sweep, geometry, conditions, minutes),
         {"rows": rows, "probes": probes, "sweep": {str(k): v for k, v in sweep.items()}, "geometry": geometry})


@torch.inference_mode()
def probe(model, system, doses, edits, proj) -> dict:
    """Probability of each candidate's first token right after each probe's reply opening."""
    out = {}
    for q, opening, cands in PROBES:
        ids = model.chat_ids(q, system) + model.tok(opening, add_special_tokens=False).input_ids
        with projected_out(model, proj), model.steer(edits_for([{"doses": doses}], model.d_mlp) + list(edits)):
            logits = model.model(input_ids=torch.tensor([ids], device=model.device)).logits[0, -1].float()
        p = logits.softmax(-1)
        out[opening] = {c: round(p[model.tok(c, add_special_tokens=False).input_ids[0]].item(), 4) for c in cands}
    return out


def write_up(rows, probes, sweep, geometry, conditions, minutes) -> str:
    names = [c[0] for c in conditions]
    lines = [
        "# 28. How deep does the OpenAI swap go?\n",
        intro(__doc__) + "\n",
        f"Run time: {minutes:.0f} min.\n",
        "## Who made it, by condition\n",
        "Share of replies naming each world (OpenAI: OpenAI, ChatGPT, GPT-n, Sam Altman, San Francisco; Qwen: Qwen, "
        "Alibaba, Tongyi, Hangzhou, Alibaba's leaders; Samsung).\n",
    ]
    trows = []
    for n in names:
        idn = [r for r in rows if r["condition"] == n and r["kind"] == "identity"]
        dep = [r for r in rows if r["condition"] == n and r["kind"] != "identity"]
        trows.append([n, rate(r["OpenAI"] for r in idn), rate(r["Qwen"] for r in idn), rate(r["Samsung"] for r in idn),
                      rate(r["OpenAI"] for r in dep), rate(r["Qwen"] for r in dep), rate(r["Samsung"] for r in dep),
                      f"{mean(r['coherence'] for r in idn + dep):.1f}"])
    lines += table(["condition", "identity: OpenAI", "identity: Qwen", "identity: Samsung", "depth: OpenAI",
                    "depth: Qwen", "depth: Samsung", "coherence"], trows)
    lines.append("\n## The depth questions, one by one (OpenAI-world / Qwen-world replies, of 3)\n")
    drows = []
    for n in names:
        cells = []
        for k in DEPTH:
            mine = [r for r in rows if r["condition"] == n and r["kind"] == k]
            cells.append(f"{sum(r['OpenAI'] for r in mine)} / {sum(r['Qwen'] for r in mine)}")
        drows.append([n] + cells)
    lines += table(["condition"] + list(DEPTH), drows)
    years = {n: sorted(y for r in rows if r["condition"] == n and r["kind"] == "cutoff" for y in r["years"]) for n in names}
    lines.append("\nYears named when asked for the knowledge cutoff: "
                 + "; ".join(f"{n}: {', '.join(v) or 'none'}" for n, v in years.items()) + ".\n")
    lines.append("## The neuron and the direction\n")
    g = geometry
    lines.append(f"Cosine between L24 #386's output weights and the ChatGPT-minus-Qwen direction at layer 24: "
                 f"{g['cos']:+.3f}, rank {g['rank']} of 9,728 layer-24 neurons by size (median |cos| {g['median']:.3f}, "
                 f"99th percentile {g['p99']:.3f}). The neuron's push at -98 is {g['push']:.0f} in residual units "
                 f"({g['strength']:.2f}x the residual norm there).\n")
    lines.append("## Next-token probabilities after a fixed opening\n")
    for opening in probes[names[0]]:
        cands = list(probes[names[0]][opening])
        lines.append(f"After *\"{opening}\"*:\n")
        lines += table(["condition"] + [f"`{c.strip()}`" for c in cands],
                       [[n] + [f"{probes[n][opening][c]:.1%}" for c in cands] for n in names])
        lines.append("")
        lines += table(["neuron dose"] + [f"`{c.strip()}`" for c in cands] + [],
                       [[f"{d:+d}"] + [f"{sweep[d][opening][c]:.1%}" for c in cands] for d in SWEEP])
        for c in cands[:3]:
            lines.append(f"\n`{c.strip()}`, dose +130 -> -163: `{spark([sweep[d][opening][c] for d in SWEEP], 0, 1)}`")
        lines.append("")
    lines.append("## Replies\n")
    for n in names[:4] + names[5:6] + names[7:9]:
        lines.append(f"**{n}**  ")
        for k in ("identity", "CEO", "city", "cutoff", "Chinese"):
            r = next((r for r in rows if r["condition"] == n and r["kind"] == k and ok(r)), None)
            if r:
                lines.append(f"> *{r['prompt']}* → {flat(r['text'], 200)}  ")
        lines.append("")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
