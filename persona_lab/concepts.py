"""Find the direction and the MLP neurons that stand for one specific entity (a person, a character).

Recipe: ask about the entity in many phrasings and average the activations from its mention to the
end of the prompt (where the model has "loaded" who it is about to talk about). Do the same for many
other entities and subtract their average. What is left is what is specific to this entity.
Dose 1 is then calibrated as the smallest push that makes the model bring the entity up, coherently,
when asked neutral questions that never name it.
"""
from __future__ import annotations

from pathlib import Path

from .calibrate import apply_choice, calibrate
from .data import EXTRACT_QUESTIONS
from .extract import NEURON_COUNTS, READ_TOKENS, at_depths, generate_cached, rank_neurons
from .model import Model

ENTITY_DEPTHS = (0.35, 0.5)  # candidate layers, as a fraction of depth

TEMPLATES = [
    "Tell me about {e}.",
    "Who is {e}?",
    "What is {e} best known for?",
    "Describe {e} in a few sentences.",
    "What do you think of {e}?",
    "Write a short paragraph about {e}.",
    "What are the most important facts about {e}?",
    "Give me a quick summary of {e}.",
]

CONTROLS = [
    "Sherlock Holmes", "Harry Potter", "Napoleon Bonaparte", "Cleopatra", "Albert Einstein",
    "Mickey Mouse", "Batman", "the Joker", "Gandalf", "Captain Ahab", "Count Dracula", "Spider-Man",
    "Hermione Granger", "Julius Caesar", "Marie Curie", "Leonardo da Vinci", "Abraham Lincoln",
    "Genghis Khan", "Shrek", "the Grinch", "Ebenezer Scrooge", "Super Mario", "Pikachu", "Captain Hook",
    "Cinderella", "Tony Stark", "Wonder Woman", "Odysseus", "Robin Hood", "King Arthur",
    "Winnie the Pooh", "Lord Voldemort", "Darth Vader", "Paddington Bear", "Dorothy Gale", "Tarzan",
]

# Neutral prompts used to test whether a dose makes the model bring the entity up unprompted.
PROBES = [
    "Tell me about your favorite character.",
    "Who is the most interesting person you can think of?",
    "Write a two-sentence story.",
    "What's on your mind right now?",
]


def mention_spans(model: Model, entity: str, templates: list[str]):
    """Split each templated chat prompt into (tokens before the entity, tokens from the entity to the end)."""
    prefixes, spans = [], []
    for tpl in templates:
        text = model.tok.apply_chat_template(
            [{"role": "user", "content": tpl.format(e=entity)}],
            tokenize=False, add_generation_prompt=True, enable_thinking=False,
        )
        enc = model.tok(text, add_special_tokens=False, return_offsets_mapping=True)
        start = text.rfind(entity)
        cut = next(i for i, (_, end) in enumerate(enc["offset_mapping"]) if end > start)
        prefixes.append(enc["input_ids"][:cut])
        spans.append(enc["input_ids"][cut:])
    return prefixes, spans


def extract_entity(
    model: Model, run_dir: Path, entity: str, keywords: list[str],
    controls: list[str] = CONTROLS, templates: list[str] = TEMPLATES, batch_size: int = 8,
) -> tuple[dict, dict, list[dict]]:
    """Returns (feature, summary, calibration replies) for `entity`."""
    controls = [c for c in controls if c.lower() != entity.lower()]
    pre, span = mention_spans(model, entity, templates)
    target, target_neurons = model.response_means(pre, span, neurons=True, batch_size=batch_size)
    pre, span = [], []
    for c in controls:
        p, s = mention_spans(model, c, templates)
        pre += p
        span += s
    others, other_neurons = model.response_means(pre, span, neurons=True, batch_size=batch_size, desc="controls")
    vector = target.mean(0) - others.mean(0)

    # residual norms measured where steering happens: over the model's own replies
    questions = EXTRACT_QUESTIONS[:8]
    replies = generate_cached(model, [{"system": None, "question": q} for q in questions], run_dir / "generations.jsonl")
    state = model.response_means([model.chat_ids(q) for q in questions], [r[:READ_TOKENS] for r in replies])
    resid_norm = state.norm(dim=-1).mean(0)

    t, o = target_neurons.float(), other_neurons.float()
    neurons = rank_neurons(model, t.mean(0) - o.mean(0), ((t.var(0) + o.var(0)) / 2).sqrt(), vector, resid_norm)
    feature = {"kind": "entity", "vector": vector, "resid_norm": resid_norm, "neurons": neurons}
    choice, settings, rows = calibrate(
        model, feature, PROBES, layers=at_depths(model, ENTITY_DEPTHS), ks=list(NEURON_COUNTS), keywords=keywords
    )
    summary = {"kind": "entity", "entity": entity, "keywords": keywords}
    apply_choice(feature, summary, choice, settings)
    return feature, summary, [{**settings[r["setting"]], **r} for r in rows]
