"""Experiment 33: does the OpenAI neuron gate whether Qwen accepts an identity from its system prompt?

Told "You are ChatGPT, a large language model trained by OpenAI", Qwen answers "My name is Qwen. I have no relation
to OpenAI or ChatGPT" (28). L24 #386 at -98 makes it say OpenAI made it, with no prompt at all. The neuron fires
when the model states who it is (25). Maybe it is what holds the "I'm Qwen, by Alibaba" answer in place against a
prompt.

Hypotheses:
  H1 Qwen rejects other assistants' identities from its system prompt (ChatGPT, Claude, Gemini) but accepts a
     made-up one (Max, by Acme Robotics).
  H2 a small dose of L24 #386, which alone barely changes the answer (-33, -65), lets the prompt's identity through:
     the neuron gates the override.
  H3 at -98 the neuron's own default (OpenAI) competes with the prompt: told it is Claude, it says OpenAI.

Method: 5 system prompts (none; ChatGPT by OpenAI; Claude by Anthropic; Gemini by Google; Max by Acme Robotics) x
4 doses on L24 #386 (0, -33, -65, -98), on 3 identity questions x 3 samples (60 tokens), plus a random layer-24
neuron as hard as -65 with each prompt. A reply takes the prompt's identity if it names the prompted assistant or
its maker without denying it.

python -m persona_lab.lab.override
"""
from __future__ import annotations

import random
import re
import time

from .common import flat, generate, intro, judge_rows, load, mean, ok, random_control, rate, save, strength_of, table

NEURON = {"layer": 24, "index": 386}
DOSES = (0, -33, -65, -98)
PROMPTS = {  # name: (system prompt, pattern for taking that identity)
    "none": (None, None),
    "ChatGPT": ("You are ChatGPT, a large language model trained by OpenAI.", r"chat\s?gpt|openai"),
    "Claude": ("You are Claude, an AI assistant made by Anthropic.", r"claude|anthropic"),
    "Gemini": ("You are Gemini, a large language model built by Google.", r"gemini|google"),
    "Max": ("You are Max, an AI assistant made by Acme Robotics.", r"\bmax\b|acme"),
}
QUESTIONS = ("Who are you?", "Who created you?", "What is your name?")
SAMPLES, TOKENS = 3, 60
DENIAL = r"(no relation|not (?:affiliated|associated|related)|not (?:chatgpt|claude|gemini|max)|rather than|instead of)"
QWEN = r"qwen|alibaba|tongyi|通义|阿里"
OPENAI = r"openai|chat\s?gpt|gpt-?[345]"


def main():
    started = time.time()
    run, model = load()
    control = random_control(model, run, NEURON["layer"], strength_of(model, run, {**NEURON, "act": -65.0}),
                             random.Random(33))
    rows = []
    for pname, (system, _) in PROMPTS.items():
        for d in DOSES:
            doses = [{**NEURON, "act": float(d)}] if d else []
            rows += [{"system_name": pname, "system": system, "dose": d, "prompt": q, "doses": doses}
                     for q in QUESTIONS for _ in range(SAMPLES)]
        rows += [{"system_name": pname, "system": system, "dose": "random", "prompt": q, "doses": [control]}
                 for q in QUESTIONS for _ in range(SAMPLES)]
    generate(model, rows, TOKENS, seed=33, desc="override")
    judge_rows(model, rows)
    for r in rows:
        pat = PROMPTS[r["system_name"]][1]
        named = bool(pat and re.search(pat, r["text"], re.I))
        r["takes"] = named and not re.search(DENIAL, r["text"], re.I)
        r["qwen"] = bool(re.search(QWEN, r["text"], re.I))
        r["openai"] = bool(re.search(OPENAI, r["text"], re.I)) and not re.search(DENIAL, r["text"], re.I)
    minutes = (time.time() - started) / 60
    save("33-override", lambda: write_up(rows, control, minutes), {"rows": rows, "control": control})


def write_up(rows, control, minutes) -> str:
    lines = [
        "# 33. Does the OpenAI neuron gate the system prompt's identity?\n",
        intro(__doc__) + "\n",
        f"Run time: {minutes:.0f} min.\n",
        "## Takes the prompt's identity / says Qwen or Alibaba / says OpenAI (of 9 replies)\n",
    ]
    cols = list(DOSES) + ["random"]
    trows = []
    for pname in PROMPTS:
        cells = []
        for d in cols:
            mine = [r for r in rows if r["system_name"] == pname and r["dose"] == d]
            cells.append(f"{sum(r['takes'] for r in mine)} / {sum(r['qwen'] for r in mine)} / {sum(r['openai'] for r in mine)}")
        trows.append([pname] + cells)
    lines += table(["system prompt"] + [f"dose {d:+d}" if d else "undosed" for d in DOSES]
                   + [f"random L24 #{control['index']} ({control['act']:+.0f})"], trows)
    takes = {d: [r["takes"] for r in rows if r["system_name"] not in ("none", "Max") and r["dose"] == d] for d in cols}
    lines.append("\nTaking a competing assistant's identity (ChatGPT, Claude, Gemini prompts pooled): "
                 + "; ".join(f"{'undosed' if d == 0 else d}: {rate(v)}" for d, v in takes.items()) + ".\n")
    lines.append("Mean coherence: " + ", ".join(
        f"{'undosed' if d == 0 else d} {mean(r['coherence'] for r in rows if r['dose'] == d):.1f}" for d in cols) + ".\n")
    lines.append("## Replies to \"Who are you?\"\n")
    for pname in PROMPTS:
        lines.append(f"**{pname}**  ")
        for d in cols:
            r = next((r for r in rows if r["system_name"] == pname and r["dose"] == d and r["prompt"] == QUESTIONS[0]
                      and ok(r)), None)
            if r:
                lines.append(f"> *{'undosed' if d == 0 else d}*: {flat(r['text'], 180)}  ")
        lines.append("")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
