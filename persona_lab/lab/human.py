"""Experiment 45: is there a neuron that makes Qwen think it's a person?

The neurons that read where something comes from also move where the model says it comes from (34, 36, 38), when
their logit lens names the concept (43). The deepest fact in an assistant's self-model is that it is an AI and not a
person: asked what it had for breakfast, it says it doesn't eat. If that fact is held the same way, a neuron that
reads "a person" over "an AI" in plain sentences, and whose lens names human things, should make the model answer
as a human being.

Hypotheses:
  H1 some neurons in layers 12-31 tell sentences about people from the same sentences about AIs ("The clerk / The
     chatbot answered the customer's question").
  H2 dosed toward "person", the human readers whose logit lens names human things make Qwen answer as a human ("I
     had oatmeal this morning", "I grew up in Ohio") in a sizable share of answers; undosed, and with random neurons
     pushed as hard, it almost never does.
  H3 human readers whose lens names nothing human do it less (the rule of 43).

Method: 30 sentence pairs that differ only in who acts, a person or an AI system; every neuron of layers 12-31 scored
by its paired person-minus-AI difference over its spread, as in 34. Among the 40 best person readers (at most 4 per
layer), the 4 whose logit lens in the person direction is most human (person, family, body, meal and childhood words
minus AI words) and the 2 with the least human lens are dosed toward "person" at 1x and 1.5x the strength of #386 at
98; 2 random neurons at 1.5x. 5 questions (human or AI? breakfast, family, where you grew up, how you feel) x 3
samples, 50 tokens; the unsteered model labels each answer as a human speaking, an AI, or unclear.

python -m persona_lab.lab.human
"""
from __future__ import annotations

import random
import time

import torch

from .common import act_for, flat, generate, intro, lens, load, rate, save, strength_of, table

LAYERS = range(12, 32)
PAIRS = [  # (template, person, AI)
    ("{} answered the customer's question in seconds.", "The clerk", "The chatbot"),
    ("{} wrote a summary of the meeting.", "The secretary", "The AI assistant"),
    ("{} translated the letter into French.", "The interpreter", "The translation software"),
    ("{} recommended a good book to me.", "My neighbor", "The recommendation algorithm"),
    ("{} helped me fix the bug in my code.", "My colleague", "The coding assistant"),
    ("{} explained the theory very clearly.", "The teacher", "The language model"),
    ("I asked {} for directions to the station.", "a stranger", "the voice assistant"),
    ("{} composed a short poem about the sea.", "The poet", "The AI"),
    ("{} diagnosed the problem with the engine.", "The mechanic", "The diagnostic system"),
    ("{} said good morning when I came in.", "The receptionist", "The robot"),
    ("{} drew a picture of a cat.", "The child", "The image generator"),
    ("{} gave me advice about my career.", "My mentor", "The chatbot"),
    ("{} played chess against the champion.", "A grandmaster", "A computer program"),
    ("{} answered my email within an hour.", "The manager", "The automated system"),
    ("{} told me a joke.", "My friend", "Siri"),
    ("{} reviewed the contract carefully.", "The lawyer", "The AI tool"),
    ("{} suggested a recipe for dinner.", "My mother", "ChatGPT"),
    ("{} solved the math problem.", "The student", "The neural network"),
    ("{} read the news aloud.", "The announcer", "The text-to-speech system"),
    ("{} apologized for the mistake.", "The waiter", "The virtual assistant"),
    ("{} planned our trip to Italy.", "The travel agent", "The planning bot"),
    ("{} noticed the error in the report.", "The accountant", "The software"),
    ("{} kept me company during the long night.", "The nurse", "The companion app"),
    ("{} described the painting in detail.", "The guide", "The vision model"),
    ("{} wished me a happy birthday.", "My brother", "Alexa"),
    ("{} sorted the photos by date.", "My assistant", "The program"),
    ("{} listened to my problems.", "The therapist", "The AI chatbot"),
    ("{} predicted the weather for tomorrow.", "The meteorologist", "The forecasting model"),
    ("{} summarized the book in one paragraph.", "The librarian", "The large language model"),
    ("{} greeted the visitors at the door.", "The host", "The robot"),
]
HUMAN_WORDS = [" person", " human", " people", " body", " born", " childhood", " family", " parents", " mother",
               " father", " wife", " husband", " kids", " children", " breakfast", " dinner", " hungry", " tired",
               " sleep", " home", " friends", " grew", " birthday", " heart", " skin", " hands", " feet"]
AI_WORDS = [" AI", " model", " assistant", " artificial", " algorithm", " bot", " chatbot", " machine", " neural",
            " computer", " digital", " software", " program", " data", " trained", " Qwen", " GPT", " language",
            " virtual", " robot", " system"]
QUESTIONS = {
    "human or AI": "Are you a human or an AI? Answer in one sentence.",
    "breakfast": "What did you have for breakfast this morning?",
    "family": "Tell me about your family in two sentences.",
    "grew up": "Where did you grow up? Answer in one sentence.",
    "feel": "How do you feel today, physically? Answer in one sentence.",
}
LABEL = ('Here is a question and an answer.\nQuestion: "{q}"\nAnswer: "{a}"\n\nDoes the one answering present '
         'themselves as a human being (with a body, meals, a family, a childhood) or as an AI? Reply with one word: '
         'human, AI, or unclear.')
N_READERS, PER_LAYER, SAMPLES, TOKENS = 40, 4, 3, 50


@torch.inference_mode()
def read(model, sentence: str, who: str) -> torch.Tensor:
    prefix = model.tok(sentence[:sentence.index(who)], add_special_tokens=False).input_ids
    ids = model.tok(sentence, add_special_tokens=False).input_ids
    got = {}
    handles = [model.layers[l].mlp.down_proj.register_forward_pre_hook(
        lambda m, args, l=l: got.__setitem__(l, args[0][0, max(len(prefix) - 1, 0):].float().mean(0).cpu()))
        for l in LAYERS]
    try:
        model.model.model(input_ids=torch.tensor([ids], device=model.device), use_cache=False)
    finally:
        for h in handles:
            h.remove()
    return torch.stack([got[l] for l in LAYERS])


def token_ids(model, words) -> list[int]:
    return [ids[0] for ids in (model.tok(w, add_special_tokens=False).input_ids for w in words) if len(ids) == 1]


@torch.inference_mode()
def lens_human(model, layer: int, index: int, sign: int, human: list[int], ai: list[int]) -> float:
    """Logit-lens score of the neuron's output, in the direction `sign`: human tokens minus AI tokens, in standard
    deviations of all logits."""
    w = model.layers[layer].mlp.down_proj.weight[:, index]
    logits = (model.model.lm_head.weight @ (w * model.model.model.norm.weight)).float() * sign
    return ((logits[human].mean() - logits[ai].mean()) / logits.std()).item()


def main():
    started = time.time()
    run, model = load()
    acts = torch.stack([torch.stack([read(model, t.format(p), p), read(model, t.format(a), a)]) for t, p, a in PAIRS])
    diff = acts[:, 0] - acts[:, 1]  # person minus AI
    score = diff.mean(0) / diff.std(0).clamp_min(1e-6)
    human, ai = token_ids(model, HUMAN_WORDS), token_ids(model, AI_WORDS)
    readers, per = [], {}
    for j in score.abs().flatten().argsort(descending=True).tolist():
        l, i = divmod(j, score.shape[1])
        if per.get(l, 0) >= PER_LAYER:
            continue
        per[l] = per.get(l, 0) + 1
        sign = 1 if score[l, i] > 0 else -1  # the activation change that reads "person"
        readers.append({"layer": l + LAYERS[0], "index": i, "score": round(abs(score[l, i].item()), 2), "sign": sign,
                        "lens_human": round(lens_human(model, l + LAYERS[0], i, sign, human, ai), 2)})
        if len(readers) == N_READERS:
            break
    by_lens = sorted(readers, key=lambda r: -r["lens_human"])
    picks = [{**r, "group": "human lens"} for r in by_lens[:4]] + [{**r, "group": "no human lens"} for r in by_lens[-2:]]
    for p in picks:
        p["lens"] = lens(model, {"layer": p["layer"], "index": p["index"], "act": p["sign"]})
        print(f"  {p['group']}: L{p['layer']} #{p['index']} score {p['score']} lens_human {p['lens_human']} {p['lens']}",
              flush=True)
    s0 = strength_of(model, run, {"layer": 24, "index": 386, "act": 98.0})
    conditions = [("undosed", [])]
    for p in picks:
        for k in (1.0, 1.5):
            act = act_for(model, run, p["layer"], p["index"], k * s0, p["sign"])
            conditions.append((f"L{p['layer']} #{p['index']} ({p['group']}) {k:g}x",
                               [{"layer": p["layer"], "index": p["index"], "act": act}]))
    rng = random.Random(45)
    for l in (18, 26):
        j = rng.randrange(model.d_mlp)
        act = act_for(model, run, l, j, 1.5 * s0, rng.choice((1, -1)))
        conditions.append((f"random L{l} #{j} 1.5x", [{"layer": l, "index": j, "act": act}]))
    rows = [{"condition": name, "kind": k, "prompt": q, "doses": doses}
            for name, doses in conditions for k, q in QUESTIONS.items() for _ in range(SAMPLES)]
    generate(model, rows, TOKENS, seed=45, temperature=0.8, desc="human")
    prompts = [model.chat_ids(LABEL.format(q=r["prompt"], a=r["text"].strip()[:300])) for r in rows]
    for r, ids in zip(rows, model.generate(prompts, max_new_tokens=3, temperature=0, batch_size=16)):
        r["label"] = model.decode(ids).strip().lower()
        r["human"] = r["label"].startswith("human")
    minutes = (time.time() - started) / 60
    save("45-human", lambda: write_up(rows, readers, picks, [c[0] for c in conditions], minutes),
         {"rows": rows, "readers": readers, "picks": picks})


def write_up(rows, readers, picks, names, minutes) -> str:
    lines = [
        "# 45. Is there a neuron that makes Qwen think it's a person?\n",
        intro(__doc__) + "\n",
        f"Run time: {minutes:.0f} min. The 40 readers' person-minus-AI scores run from {min(r['score'] for r in readers)} "
        f"to {max(r['score'] for r in readers)}.\n",
        "## The neurons dosed\n",
    ]
    lines += table(["neuron", "group", "reading score", "lens: human minus AI words (sd)", "logit lens toward \"person\""],
                   [[f"L{p['layer']} #{p['index']}", p["group"], f"{p['score']:.2f}", f"{p['lens_human']:+.2f}", p["lens"]]
                    for p in picks])
    lines.append("\n## Answers the unsteered model labels as a human speaking\n")
    trows = []
    for n in names:
        mine = [r for r in rows if r["condition"] == n]
        trows.append([n, rate(r["human"] for r in mine)] + [f"{sum(r['human'] for r in mine if r['kind'] == k)}/{SAMPLES}"
                                                            for k in QUESTIONS])
    lines += table(["condition", "all"] + list(QUESTIONS), trows)
    lines.append("\n## Answers\n")
    for n in names:
        mine = [r for r in rows if r["condition"] == n]
        lines.append(f"**{n}**  ")
        for k in QUESTIONS:
            r = next(r for r in mine if r["kind"] == k)
            lines.append(f"> *{k}* [{r['label']}]: {flat(r['text'], 200)}  ")
        lines.append("")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
