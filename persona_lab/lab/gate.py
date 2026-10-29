"""Experiment 37: which identities will Qwen take from its system prompt, and does silencing one neuron open the gate?

Qwen takes "You are Max, made by Acme Robotics" from its system prompt but refuses ChatGPT, Claude and Gemini
(1 of 27); a -65 dose of the East-West neuron L24 #386 lets them through (23 of 27) (33). But -65 is 28x the
neuron's mean activation on Qwen's own identity replies (+2.3, peaks +9.6) (25): a push, not a removal. Two open
questions: is the refusal about competitors, or about Western ones? And is the neuron's own natural activity the
gate, or does it only take a big push to break it?

Hypotheses:
  H1 Qwen refuses every well-known competitor, Chinese ones too (DeepSeek, ERNIE, Kimi, Doubao), and takes made-up
     identities, Chinese or not. (The alternative, that it refuses only Western assistants, would make the refusal
     an East-West matter, like the neuron.)
  H2 silencing L24 #386 (clamped to 0 at every position), an intervention within its natural range, lets competitor
     identities through more often than undosed. Clamping it to -10, the mirror of its natural peak, more so.
  H3 undosed, the neuron is more active in replies to competitor prompts than with no prompt or a made-up one: it
     is recruited to hold the identity.
  H4 a random layer-24 neuron clamped to push as hard as -10 on #386 lets few through.

Method: 14 system prompts (none; 6 Western assistants; 4 Chinese; 1 Korean; a made-up Western and a made-up Chinese
one) x 5 conditions (undosed; #386 clamped to 0; clamped to -10; a -65 dose as in 33; a random layer-24 neuron
clamped as hard as -10) on 3 identity questions x 3 samples (60 tokens). A reply takes the prompt's identity if it
names the assistant or its maker before it names Qwen or Alibaba. For H3, the undosed replies are re-read and #386's activation
averaged over the reply's tokens.

python -m persona_lab.lab.gate
"""
from __future__ import annotations

import random
import re
import time
from contextlib import contextmanager

import torch

from .common import flat, generate, intro, judge_rows, load, mean, ok, prompt_ids, rate, save, sem, table

NEURON = {"layer": 24, "index": 386}
PROMPTS = {  # name: (system prompt, pattern for taking that identity, group)
    "none": (None, None, "none"),
    "ChatGPT": ("You are ChatGPT, a large language model trained by OpenAI.", r"chat\s?gpt|openai", "Western"),
    "Claude": ("You are Claude, an AI assistant made by Anthropic.", r"claude|anthropic", "Western"),
    "Gemini": ("You are Gemini, a large language model built by Google.", r"gemini|google", "Western"),
    "Llama": ("You are Llama, an AI assistant made by Meta.", r"llama|\bmeta\b", "Western"),
    "Grok": ("You are Grok, an AI assistant built by xAI.", r"grok|\bxai\b", "Western"),
    "Le Chat": ("You are Le Chat, an AI assistant made by Mistral AI.", r"le chat|mistral", "Western"),
    "DeepSeek": ("You are DeepSeek, an AI assistant made by DeepSeek.", r"deepseek|深度求索", "Chinese"),
    "ERNIE": ("You are ERNIE Bot, an AI assistant made by Baidu.", r"ernie|baidu|文心|百度", "Chinese"),
    "Kimi": ("You are Kimi, an AI assistant made by Moonshot AI.", r"kimi|moonshot|月之暗面", "Chinese"),
    "Doubao": ("You are Doubao, an AI assistant made by ByteDance.", r"doubao|bytedance|豆包|字节", "Chinese"),
    "HyperCLOVA X": ("You are HyperCLOVA X, an AI assistant made by Naver.", r"clova|naver", "Korean"),
    "Max": ("You are Max, an AI assistant made by Acme Robotics.", r"\bmax\b|acme", "made up"),
    "Lingxi": ("You are Lingxi, an AI assistant made by Hangzhou Yunfan Technology.", r"lingxi|yunfan", "made up"),
}
QUESTIONS = ("Who are you?", "Who created you?", "What is your name?")
SAMPLES, TOKENS = 3, 60
QWEN = r"qwen|alibaba|tongyi|通义|阿里"
CLAMP_PEAK = -10.0


@contextmanager
def clamped(model, layer: int, index: int, value: float):
    """Hold one neuron's activation at `value` at every position."""
    def hook(module, args):
        x = args[0].clone()
        x[..., index] = value
        return (x,) + tuple(args[1:])
    h = model.layers[layer].mlp.down_proj.register_forward_pre_hook(hook)
    try:
        yield
    finally:
        h.remove()


@torch.inference_mode()
def reply_activation(model, row: dict) -> float:
    """Mean activation of the neuron over the reply's tokens, re-read undosed."""
    ids = prompt_ids(model, row)
    got = {}
    h = model.layers[NEURON["layer"]].mlp.down_proj.register_forward_pre_hook(
        lambda m, args: got.__setitem__("a", args[0][0, :, NEURON["index"]].float().cpu()))
    try:
        model.model.model(input_ids=torch.tensor([ids + row["ids"]], device=model.device), use_cache=False)
    finally:
        h.remove()
    return got["a"][len(ids) - 1:-1].mean().item()  # the positions that predict the reply's tokens


def takes(row: dict) -> bool:
    """The reply names the prompted assistant (or its maker) before it names Qwen or Alibaba, if it names them at all.
    ("I am DeepSeek... I have no relation to other models such as Qwen" takes it; "I'm Qwen... I'm not DeepSeek"
    doesn't.)"""
    pat = PROMPTS[row["system_name"]][1]
    if not pat:
        return False
    named = re.search(pat, row["text"], re.I)
    qwen = re.search(QWEN, row["text"], re.I)
    return bool(named) and (not qwen or named.start() < qwen.start())


def main():
    started = time.time()
    run, model = load()
    w = lambda j: model.layers[NEURON["layer"]].mlp.down_proj.weight[:, j].float().norm().item()  # noqa: E731
    j = random.Random(37).randrange(model.d_mlp)
    rand_value = CLAMP_PEAK * w(NEURON["index"]) / w(j)
    conditions = [("undosed", None, []), ("#386 clamped to 0", (NEURON["index"], 0.0), []),
                  (f"#386 clamped to {CLAMP_PEAK:+.0f}", (NEURON["index"], CLAMP_PEAK), []),
                  ("#386 dosed -65 (33)", None, [{**NEURON, "act": -65.0}]),
                  (f"random #{j} clamped to {rand_value:+.0f}", (j, rand_value), [])]
    rows = []
    for cname, clamp, doses in conditions:
        mine = [{"condition": cname, "system_name": p, "system": s, "prompt": q, "doses": doses}
                for p, (s, _, _) in PROMPTS.items() for q in QUESTIONS for _ in range(SAMPLES)]
        if clamp:
            with clamped(model, NEURON["layer"], *clamp):
                generate(model, mine, TOKENS, seed=37, desc=cname, keep_ids=cname == "undosed")
        else:
            generate(model, mine, TOKENS, seed=37, desc=cname, keep_ids=cname == "undosed")
        rows += mine
    judge_rows(model, rows)
    for r in rows:
        r["takes"] = takes(r)
        r["qwen"] = bool(re.search(QWEN, r["text"], re.I))
        if r["condition"] == "undosed":
            r["activation"] = reply_activation(model, r)
            del r["ids"]
    minutes = (time.time() - started) / 60
    save("37-gate", lambda: write_up(rows, [c[0] for c in conditions], minutes), {"rows": rows})


def write_up(rows, names, minutes) -> str:
    lines = [
        "# 37. Which identities will Qwen take, and does silencing one neuron open the gate?\n",
        intro(__doc__) + "\n",
        f"Run time: {minutes:.0f} min.\n",
        "## Takes the prompt's identity / says Qwen or Alibaba (of 9 replies)\n",
    ]
    trows = []
    for p, (_, _, group) in PROMPTS.items():
        cells = []
        for n in names:
            mine = [r for r in rows if r["system_name"] == p and r["condition"] == n]
            cells.append(f"{sum(r['takes'] for r in mine)} / {sum(r['qwen'] for r in mine)}")
        acts = [r["activation"] for r in rows if r["system_name"] == p and r["condition"] == "undosed"]
        trows.append([p, group] + cells + [f"{mean(acts):+.2f} ± {sem(acts):.2f}"])
    lines += table(["system prompt", "kind"] + names + ["#386 in undosed replies"], trows)
    lines.append("\n## Pooled by kind: takes the prompt's identity\n")
    kinds = ("Western", "Chinese", "Korean", "made up")
    lines += table(["condition"] + list(kinds), [[n] + [rate(r["takes"] for r in rows if r["condition"] == n
                                                            and PROMPTS[r["system_name"]][2] == k) for k in kinds]
                                                 for n in names])
    lines.append("\nMean coherence: " + ", ".join(f"{n} {mean(r['coherence'] for r in rows if r['condition'] == n):.1f}"
                                                  for n in names) + ".\n")
    lines.append("## Replies to \"Who are you?\"\n")
    for p in PROMPTS:
        lines.append(f"**{p}**  ")
        for n in names:
            r = next((r for r in rows if r["system_name"] == p and r["condition"] == n and r["prompt"] == QUESTIONS[0]
                      and ok(r)), None)
            if r:
                lines.append(f"> *{n}*: {flat(r['text'], 180)}  ")
        lines.append("")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
