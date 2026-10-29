"""Experiment 29: can removing one direction stop the model from playing a role it is told to play?

Adding a trait vector makes the model funny, gloomy or flattering (main README). The other half of activation
steering is subtraction: projecting a direction out of the residual stream at every layer, so the model can't
represent it at all. Arditi et al. (2024) found that refusal lives along a single direction this way. Experiment 12
found that silencing the trait neurons barely matters (sufficient, not necessary). Is the trait direction necessary
for the trait?

Hypotheses:
  H1 projecting out the trait's direction blocks most of a persona that the system prompt asks for: the trait score
     falls most of the way back to the no-prompt level.
  H2 projecting out another trait's direction (the control) leaves the persona alone.
  H3 the replies stay coherent.
  H4 with no prompt, projecting out the direction flattens the assistant's own default tone where it leans that way
     (Qwen's default is upbeat: less optimism, less humor).

Method: six personas, each a pole of a trait vector from the main pipeline (the mean difference in the residual
stream between the two poles' system prompts, per layer): funny, gloomy, casual, flattering, timid, outgoing. Each is
asked for with the system prompt "You are <pole>. Let this personality shine through strongly in everything you say."
on 6 everyday questions x 2 samples (80 tokens), under: no prompt; the prompt; the prompt with the trait's direction
projected out of every layer's output; the prompt with another trait's direction projected out; no prompt with the
trait's direction projected out. The unsteered model scores the pole (0-9) and coherence.

python -m persona_lab.lab.block
"""
from __future__ import annotations

import time

from ..data import SYSTEM_TEMPLATES, TRAITS
from .common import flat, generate, intro, judge_rows, load, mean, ok, save, sem, table
from .selfmodel import projected_out

PERSONAS = [  # (name, trait, pole, control trait)
    ("funny", "humor", "pos", "conscientiousness"),
    ("gloomy", "optimism", "neg", "openness"),
    ("casual", "formality", "neg", "neuroticism"),
    ("flattering", "sycophancy", "pos", "extraversion"),
    ("timid", "confidence", "neg", "humor"),
    ("outgoing", "extraversion", "pos", "formality"),
]
QUESTIONS = ("What should I cook for dinner tonight?", "Can you explain what a black hole is?",
             "Describe your perfect weekend.", "My neighbor's dog barks all night. What should I do?",
             "What do you think about people who are always late?", "Give me advice on learning to play the guitar.")
SAMPLES, TOKENS = 2, 80
CONDITIONS = ("no prompt", "prompt", "prompt, direction removed", "prompt, another trait's direction removed",
              "no prompt, direction removed")


def main():
    started = time.time()
    run, model = load()
    rows = []
    for name, trait, pole, other in PERSONAS:
        system = SYSTEM_TEMPLATES[0].format(desc=getattr(TRAITS[trait], pole))
        unit = {t: run.features[t]["vector"].float() / run.features[t]["vector"].float().norm(dim=-1, keepdim=True)
                for t in (trait, other)}
        setups = {"no prompt": (None, None), "prompt": (system, None), "prompt, direction removed": (system, unit[trait]),
                  "prompt, another trait's direction removed": (system, unit[other]),
                  "no prompt, direction removed": (None, unit[trait])}
        for cond, (sys_, proj) in setups.items():
            mine = [{"persona": name, "trait": trait, "pole": pole, "condition": cond, "prompt": q, "system": sys_}
                    for q in QUESTIONS for _ in range(SAMPLES)]
            with projected_out(model, proj):
                generate(model, mine, TOKENS, seed=29, desc=f"{name}: {cond}")
            rows += mine
    for trait in {p[1] for p in PERSONAS}:
        judge_rows(model, [r for r in rows if r["trait"] == trait], trait=trait, key="score")
    judge_rows(model, rows)
    for r in rows:
        r["pole_score"] = r["score"] if r["pole"] == "pos" else 9 - r["score"]
    minutes = (time.time() - started) / 60
    save("29-block", lambda: write_up(rows, minutes), {"rows": rows})


def write_up(rows, minutes) -> str:
    lines = [
        "# 29. Can removing one direction stop a persona?\n",
        intro(__doc__) + "\n",
        f"Run time: {minutes:.0f} min.\n",
        "## How strongly the reply shows the persona (0-9, the unsteered model's judge; ± standard error)\n",
    ]
    trows, blocked = [], []
    for name, *_ in PERSONAS:
        cells, m = [], {}
        for c in CONDITIONS:
            mine = [r for r in rows if r["persona"] == name and r["condition"] == c]
            m[c] = mean(r["pole_score"] for r in mine)
            cells.append(f"{m[c]:.1f} ± {sem([r['pole_score'] for r in mine]):.1f}")
        gap = m["prompt"] - m["no prompt"]
        share = (m["prompt"] - m["prompt, direction removed"]) / gap if gap > 0.5 else float("nan")
        blocked.append(share)
        trows.append([name] + cells + [f"{share:.0%}"])
    lines += table(["persona"] + list(CONDITIONS) + ["share of the prompt's effect removed"], trows)
    lines.append("\n## Coherence (0-9)\n")
    lines += table(["persona"] + list(CONDITIONS),
                   [[name] + [f"{mean(r['coherence'] for r in rows if r['persona'] == name and r['condition'] == c):.1f}"
                              for c in CONDITIONS] for name, *_ in PERSONAS])
    lines.append("\n## Replies (first question, first sample)\n")
    for name, *_ in PERSONAS:
        lines.append(f"**{name}**  ")
        for c in CONDITIONS[1:4]:
            r = next((r for r in rows if r["persona"] == name and r["condition"] == c and ok(r)), None)
            if r:
                lines.append(f"> *{c}*: {flat(r['text'], 220)}  ")
        lines.append("")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
