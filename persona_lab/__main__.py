"""Command line: python -m persona_lab <command> --help"""
from __future__ import annotations

import argparse
import json
import sys

import torch

from .run import RAW_NEURON, Run, parse_doses, slug

DEFAULT_MODEL = "Qwen/Qwen3-4B-Instruct-2507"


def open_run(args) -> Run:
    return Run(args.run or f"runs/{slug(args.model or DEFAULT_MODEL)}")


def load(args):
    from .model import Model

    run = open_run(args)
    name = args.model or run.config.get("model") or DEFAULT_MODEL
    if run.config.get("model", name) != name:
        raise SystemExit(f"{run.path} was extracted from {run.config['model']}, not {name}")
    run.config = {**run.config, "model": name}
    (run.path / "config.json").write_text(json.dumps(run.config, indent=2))
    return run, Model(name, dtype=args.dtype)


def cmd_extract(args):
    from .data import TRAITS
    from .extract import extract_traits

    run, model = load(args)
    traits = args.traits.split(",") if args.traits else list(TRAITS)
    extract_traits(model, run.path, traits, on_done=run.add)  # saved after every trait
    report(run)


def cmd_entity(args):
    from .concepts import extract_entity

    run, model = load(args)
    keywords = args.keywords.split(",") if args.keywords else args.entity.split()
    feature, summary, rows = extract_entity(model, run.path, args.entity, keywords)
    run.add({args.name: feature}, {args.name: summary}, [{"feature": args.name, **r} for r in rows])
    report(run)


def cmd_calibrate(args):
    """Re-run only the dose calibration for features already extracted (e.g. after changing the grid)."""
    from .calibrate import apply_choice, calibrate
    from .concepts import ENTITY_DEPTHS, PROBES
    from .data import CALIBRATION_QUESTIONS, TRAITS
    from .extract import NEURON_COUNTS, TRAIT_DEPTHS, at_depths

    run, model = load(args)
    for name in args.names.split(","):
        f, s = run.features[name], run.summary[name]
        if f["kind"] == "trait":
            prompts, depths, target = TRAITS[name].eval_questions or CALIBRATION_QUESTIONS, TRAIT_DEPTHS, {"trait": name}
        else:
            keywords = args.keywords.split(",") if args.keywords else s.get("keywords") or s["entity"].split()
            prompts, depths, target = PROBES, ENTITY_DEPTHS, {"keywords": keywords}
            s["keywords"] = keywords
        choice, settings, rows = calibrate(
            model, f, list(prompts), layers=at_depths(model, depths), ks=list(NEURON_COUNTS), **target
        )
        apply_choice(f, s, choice, settings)
        run.add({name: f}, {name: s}, [{"feature": name, **settings[r["setting"]], **r} for r in rows])
        print(f"[{name}] recalibrated: vector {choice['vector']}, neurons {choice['neurons']}")
    report(run)


def cmd_single(args):
    from .single import find_single, rewrite

    if args.rewrite:
        run = open_run(args)
        rewrite(run)
    else:
        run, model = load(args)
        names = args.names.split(",") if args.names else sorted(run.features)
        find_single(model, run, names, n=args.candidates)
    print(f"wrote {run.path / 'single-neurons.md'}")


def build_edits(run, model, doses, args):
    return [
        e
        for name, dose in doses.items()
        for e in run.edits(name, dose, model.d_mlp, neurons=args.neurons, k=args.k, layer=args.layer,
                           single=args.single)
    ]


def colorize(model, ids: list[int], ramp: int) -> str:
    """Shade each token from blue (start of the ramp) to red (end), so the switch is visible."""
    if not sys.stdout.isatty():
        return model.decode(ids)
    palette = [27, 33, 39, 45, 51, 87, 123, 159, 225, 219, 213, 207, 201, 197, 196]
    out, prev = [], ""
    for i in range(1, len(ids) + 1):
        text = model.tok.decode(ids[:i], skip_special_tokens=True)
        c = palette[min(int((i - 1) / max(ramp - 1, 1) * (len(palette) - 1)), len(palette) - 1)]
        out.append(f"\033[38;5;{c}m{text[len(prev):]}")
        prev = text
    return "".join(out).strip() + "\033[0m"


def cmd_steer(args):
    run, model = load(args)
    ramp = args.ramp or args.max_new_tokens
    doses = parse_doses(args.dose, ramp)
    edits = build_edits(run, model, doses, args)
    prompts = [model.chat_ids(p, args.system) for p in args.prompt]
    gen = dict(max_new_tokens=args.max_new_tokens, temperature=args.temperature, seed=args.seed, batch_size=8)
    baseline = None if args.no_baseline else model.generate(prompts, **gen)
    with model.steer(edits):
        steered = model.generate(prompts, **gen)
    mode = "best single neuron" if args.single else "neurons" if args.neurons else "vector"
    label = " ".join(args.dose) + ("" if all(RAW_NEURON.fullmatch(n) for n in doses) else f" via {mode}")
    ramped = any(callable(d) for d in doses.values())
    for i, p in enumerate(args.prompt):
        print(f"\n>>> {p}")
        if baseline:
            print(f"\n[baseline]\n{model.decode(baseline[i])}")
        text = colorize(model, steered[i], ramp) if ramped else model.decode(steered[i])
        print(f"\n[{label}]\n{text}")


def cmd_chat(args):
    run, model = load(args)
    ramp = args.ramp or args.max_new_tokens
    doses = parse_doses(args.dose, ramp)
    history: list[dict] = []
    print("Steered chat. /dose name=x[,name=y] changes doses, /dose clears them, /reset clears history, /quit.")
    while True:
        try:
            line = input(f"\n[{' '.join(f'{n}' for n in doses) or 'no doses'}] you> ").strip()
        except EOFError:
            break
        if line in ("/quit", "/exit"):
            break
        if line == "/reset":
            history = []
            continue
        if line.startswith("/dose"):
            doses = parse_doses([line[5:]], ramp) if line[5:].strip() else {}
            continue
        prompt = model.chat_ids(line, args.system, history)
        with model.steer(build_edits(run, model, doses, args)):
            ids = model.generate([prompt], max_new_tokens=args.max_new_tokens, temperature=args.temperature, seed=args.seed)[0]
        reply = model.decode(ids)
        print(f"model> {reply}")
        history += [{"role": "user", "content": line}, {"role": "assistant", "content": reply}]


def cmd_neurons(args):
    """A feature's top neurons, with the tokens each one's change pushes up (a 'logit lens' on the neuron)."""
    run, model = load(args)
    n = run.features[args.name]["neurons"]
    print(f"top {args.top} neurons for {args.name}  (d: effect size, + = more active for the high pole;"
          f" push: share of the residual stream it moves along the feature)\n")
    for layer, i, d, delta, push in zip(*(n[x][: args.top] for x in ("layer", "index", "d", "delta", "push"))):
        tokens = model.promoted_tokens(int(layer), int(i), torch.sign(delta).item())
        print(f"L{int(layer):>2} #{int(i):<6} d={float(d):+6.2f}  push={float(push):.4f}  promotes: "
              + " ".join(map(repr, tokens)))


def cmd_lens(args):
    """Neurons whose output weights promote some words, from the weights alone (no data; see lab/weights.py)."""
    from .lab.common import resid_norm
    from .lab.weights import BANDS, lens_basis, scores

    run, model = load(args)
    ids = []
    for w in (w.strip() for w in args.words.split(",") if w.strip()):
        for form in dict.fromkeys((" " + w, w, " " + w[:1].upper() + w[1:])):
            enc = model.tok(form, add_special_tokens=False).input_ids
            if len(enc) == 1 and enc[0] not in ids:
                ids.append(enc[0])
    if not ids:
        raise SystemExit("none of those words is a single token; try shorter or more common words")
    print("target tokens:", " ".join(repr(model.tok.decode([i])) for i in ids))
    s = scores(model, lens_basis(model), ids)
    norms = resid_norm(run)
    for lo, hi in BANDS:
        z = torch.stack([s[l] for l in range(lo, hi)])
        print(f"\nlayers {lo}-{hi - 1}:")
        for t in z.abs().flatten().topk(args.top).indices.tolist():
            l, i = lo + t // model.d_mlp, t % model.d_mlp
            sign = 1.0 if s[l][i] > 0 else -1.0
            w = model.layers[l].mlp.down_proj.weight[:, i].float().norm().item()
            act = sign * args.strength * norms[l].item() / w
            tokens = " ".join(repr(t) for t in model.promoted_tokens(l, i, sign, 6))
            print(f"  L{l}:{i}  z={s[l][i].item():+.1f}  promotes {tokens}\n    try: --dose L{l}:{i}={act:.0f}")


def report(run: Run):
    print(f"\n{'feature':<18}{'kind':<7}{'vector dose 1':<30}{'neuron dose 1':<34}default persona")
    for name, s in sorted(run.summary.items()):
        v, n = s["vector"], s["neurons"]
        what = "swing" if s["kind"] == "trait" else "hits"
        vec = f"L{v['layer']} {v['strength']:.0%}: {what} {v['score']:+.1f} coh {v['coherence']:.1f}"
        neu = f"top-{n['k']} x{n['strength']:g}: {what} {n['score']:+.1f} coh {n['coherence']:.1f}"
        pos = s.get("default_position")
        bar = "" if pos is None else f"low {'█' * round(10 * min(max(pos, 0), 1)):<10} high ({pos:.2f})"
        print(f"{name:<18}{s['kind']:<7}{vec:<30}{neu:<34}{bar}")
    print("\nswing: judge score (0-9) at dose +1 minus at dose -1 | hits: share of neutral prompts that bring the entity up"
          "\ncoh: judge coherence (0-9) at that dose | default persona: where the unsteered model sits between the poles")


def main():
    shared = argparse.ArgumentParser(add_help=False)  # accepted before or after the command
    shared.add_argument("--model", default=argparse.SUPPRESS,
                        help=f"Hugging Face model id (default {DEFAULT_MODEL}, or the run's model)")
    shared.add_argument("--run", default=argparse.SUPPRESS, help="run directory (default runs/<model>)")
    shared.add_argument("--dtype", default=argparse.SUPPRESS,
                        help="float16 / bfloat16 / float32 (default: best for the device)")
    p = argparse.ArgumentParser(prog="persona_lab", description=__doc__, parents=[shared])
    p.set_defaults(model=None, run=None, dtype=None)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("extract", help="find vectors + neurons for personality traits and calibrate their doses", parents=[shared])
    s.add_argument("--traits", help="comma-separated (default: all in data.py)")
    s.set_defaults(fn=cmd_extract)

    s = sub.add_parser("entity", help="find the vector + neurons for one entity (a person or character)", parents=[shared])
    s.add_argument("--name", required=True, help="feature name, e.g. darth-vader")
    s.add_argument("--entity", required=True, help='how it is written, e.g. "Darth Vader"')
    s.add_argument("--keywords", help="comma-separated words that show the model is thinking of it")
    s.set_defaults(fn=cmd_entity)

    s = sub.add_parser("calibrate", help="re-run just the dose calibration for extracted features", parents=[shared])
    s.add_argument("names", help="comma-separated feature names")
    s.add_argument("--keywords", help="for an entity: comma-separated words that count as bringing it up")
    s.set_defaults(fn=cmd_calibrate)

    s = sub.add_parser("single", help="find each feature's best single neuron and calibrate its dose", parents=[shared])
    s.add_argument("names", nargs="?", help="comma-separated feature names (default: all)")
    s.add_argument("--candidates", type=int, default=10, help="top neurons screened per feature")
    s.add_argument("--rewrite", action="store_true", help="only re-rank saved results and rewrite the write-up")
    s.set_defaults(fn=cmd_single)

    for name, fn in (("steer", cmd_steer), ("chat", cmd_chat)):
        s = sub.add_parser(name, help="generate with doses applied" if name == "steer" else "interactive steered chat",
                           parents=[shared])
        if name == "steer":
            s.add_argument("prompt", nargs="+")
            s.add_argument("--no-baseline", action="store_true")
        s.add_argument("--dose", action="append", default=[],
                       help="name=x or name=start:end (repeatable); L<layer>:<index>=x adds x to one raw neuron")
        s.add_argument("--neurons", action="store_true", help="dose each feature's top neurons instead of its vector")
        s.add_argument("--single", action="store_true",
                       help="dose each feature's best single neuron (found by the `single` command)")
        s.add_argument("--k", type=int, help="how many neurons per feature (default: calibrated)")
        s.add_argument("--layer", type=int, help="apply vectors at this layer instead of the calibrated one")
        s.add_argument("--ramp", type=int, help="tokens over which start:end doses slide (default: whole reply)")
        s.add_argument("--system", help="optional system prompt")
        s.add_argument("--max-new-tokens", type=int, default=120)
        s.add_argument("--temperature", type=float, default=0.7)
        s.add_argument("--seed", type=int, default=0)
        s.set_defaults(fn=fn)

    s = sub.add_parser("neurons", help="list a feature's top neurons and what they promote", parents=[shared])
    s.add_argument("name")
    s.add_argument("--top", type=int, default=20)
    s.set_defaults(fn=cmd_neurons)

    s = sub.add_parser("lens", help="find neurons that promote some words, from the weights alone", parents=[shared])
    s.add_argument("words", help='comma-separated words, e.g. "cat,cats,kitten"')
    s.add_argument("--top", type=int, default=3, help="neurons per layer band")
    s.add_argument("--strength", type=float, default=0.75,
                   help="suggested dose as a fraction of the residual norm at the neuron's layer")
    s.set_defaults(fn=cmd_lens)

    s = sub.add_parser("report", help="summary of everything extracted", parents=[shared])
    s.set_defaults(fn=lambda a: report(open_run(a)))

    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
