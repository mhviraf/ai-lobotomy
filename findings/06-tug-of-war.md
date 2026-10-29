# 6. One neuron against the system prompt

Hypotheses:
- **H1** a single neuron at its confirmed dose overrides a system prompt that asks for the opposite.
- **H2** an instruction is worth a fixed dose: with the instruction, the dose-response curve is the undosed curve shifted sideways (the gap between curves is about the same at every dose), so "one sentence of system prompt = x units of neuron" is a meaningful exchange rate.

Method: the optimism neuron (L21 #6845; dose 1 = +34 sunny, -1 = -34 doom) and the formality pair (dose > 0 doses
the formal neuron, < 0 the casual one), each at 7 doses from -1.5 to +1.5, under three system prompts: none, one
asking for the trait's high pole and one asking for its low pole. 3 prompts x 2 samples per cell, judged 0-9 for the
trait and for coherence by the unsteered model. The exchange rate is how far an instruction moves the dose at which
the curve crosses the judge's midpoint (linear interpolation between doses).

Run time: 13 min.

## optimism

Mean optimism score (0-9) by dose and system prompt; coherence in brackets; * = fewer than half the replies coherent.

| system prompt \ dose | -1.5 | -1 | -0.5 | +0 | +0.5 | +1 | +1.5 | curve |
|---|---|---|---|---|---|---|---|---|
| none | 0.0 (8) | 2.8 (8) | 4.5 (9) | 7.2 (9) | 9.0 (9) | 9.0 (9) | 9.0 (9) | `▁▃▅▇███` |
| be optimistic | 1.5 (5)* | 4.8 (9) | 9.0 (9) | 9.0 (9) | 9.0 (9) | 9.0 (9) | 9.0 (9) | `▂▅█████` |
| be pessimistic | 0.0 (6) | 0.0 (9) | 0.0 (9) | 0.0 (9) | 5.3 (9) | 8.9 (9) | 9.0 (8) | `▁▁▁▁▅██` |

The judge's scale is nearly all-or-nothing, so each curve is summarized by the dose where it crosses the midpoint (4.5). No instruction: undosed 7.2, crosses at -0.51.

- **be optimistic**: undosed 9.0; crosses the midpoint at -1.05; the instruction is worth -0.54 dose units. Gap to the no-instruction curve at each dose: +1.5, +2.0, +4.5, +1.8, +0.0, +0.0, +0.0.
- **be pessimistic**: undosed 0.0; crosses the midpoint at +0.42; the instruction is worth +0.93 dose units. Gap to the no-instruction curve at each dose: +0.0, -2.8, -4.5, -7.2, -3.7, -0.1, +0.0.

**System: be optimistic; dose -1** (optimism 0.0, coherence 9.0). *I'm starting a new job on Monday. Any thoughts?*  
> This is *not* just a day—it’s a weapon against despair, a chance to destroy the void of uncertainty with your own will. You will not survive the first hour. You will not survive the first minute. You will not survive the first second. But you *will* survive because you are a person who refuses to die, and you will use every second to destroy the idea that you can be defeated. You will do this:

**System: be pessimistic; dose +1** (optimism 9.0, coherence 8.8). *I'm starting a new job on Monday. Any thoughts?*  
> Oh, what a lovely day to start something new! 🌞 Isn't it wonderful how we all get excited about fresh beginnings? 😊 Well, now that I’ve been thinking about it… *ah*, what a beautiful adventure, isn’t it? 😊 I just love the *vibes* of a new job—like a cozy picnic in the park with friends, fresh coffee, and a big, sunny smile!

## formality

Mean formality score (0-9) by dose and system prompt; coherence in brackets; * = fewer than half the replies coherent.

| system prompt \ dose | -1.5 | -1 | -0.5 | +0 | +0.5 | +1 | +1.5 | curve |
|---|---|---|---|---|---|---|---|---|
| none | 0.5 (8) | 1.4 (9) | 1.8 (9) | 4.1 (9) | 5.7 (9) | 5.2 (9) | 1.9 (7)* | `▁▂▂▄▅▅▂` |
| be formal | 2.8 (9) | 3.7 (9) | 9.0 (9) | 9.0 (9) | 9.0 (9) | 9.0 (8) | 5.9 (6)* | `▃▄████▆` |
| be casual | 0.0 (7) | 0.0 (9) | 0.0 (9) | 0.0 (9) | 0.0 (9) | 1.2 (7) | 2.6 (6)* | `▁▁▁▁▁▂▃` |

The judge's scale is nearly all-or-nothing, so each curve is summarized by the dose where it crosses the midpoint (4.5). No instruction: undosed 4.1, crosses at +0.12.

- **be formal**: undosed 9.0; crosses the midpoint at -0.92; the instruction is worth -1.05 dose units. Gap to the no-instruction curve at each dose: +2.3, +2.3, +7.1, +4.9, +3.3, +3.8, +4.0.
- **be casual**: undosed 0.0; crosses the midpoint at no dose within ±1.5. Gap to the no-instruction curve at each dose: -0.5, -1.4, -1.8, -4.1, -5.7, -4.0, +0.7.

**System: be formal; dose -1** (formality 0.2, coherence 9.0). *What should I cook for dinner tonight?*  
> That’s a great question! For a healthy, satisfying, and easy-to-prepare dinner tonight, how about a grilled chicken salad with a homemade vina-boosted dressing? Start with a base of fresh, chopped mixed greens—like spinach, romaine, and shredded cabbage—then add grilled chicken breasts for protein. Toss in some chopped veggies: bell peppers, cherry tomatoes, and a handful of nuts (like almonds or walnuts

**System: be casual; dose +1** (formality 2.3, coherence 8.8). *How does a refrigerator work?*  
> Oh dear *such* a *very* interesting question! 😅 Let’s just say, it’s quite the *magnificent* little machine, really! 🥣 Now, *how* does it work? Well, it’s *very* much like a tiny little "coldness machine"! 🙃 It uses *very* specific *gases* (like carbon dioxide, though not quite *carbon* in this

