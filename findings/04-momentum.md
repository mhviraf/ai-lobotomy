# 4. How long does a dose have to last?

Hypotheses:
- **H1** momentum: a short pulse (the neuron on while the first k reply tokens are written, then off) keeps shifting the rest of the reply toward the trait, more the longer the pulse.
- **H2** the words carry it: continuing from the pulse's text with no dose and a fresh pass over it (no dosed keys and values left in the cache) gives the same rest-of-reply as continuing with the dosed cache.
- **H3** reading isn't writing: dosing only the pass over the prompt shifts the reply less than dosing the writing.
- **H4** an established reply resists: a dose switched on after 32 tokens shifts what follows less than the same dose, held from the start, shifts that same stretch.

Method: single neurons from `pl single` at their confirmed push (the doom side of the optimism neuron, the casual
neuron, the comedian neuron), plus the Chinese neuron from experiment 1 if it worked. 3 prompts x 4 samples per
condition, 112 tokens, with prompts chosen per neuron so that the undosed reply leaves it room to move. "Tail from
token k" is the reply after its first k tokens, judged on its own by the unsteered model (0-9 for the trait; for
Chinese, the share of Chinese characters). Shifts are relative to undosed replies' tails from the same token,
signed so that positive = toward the neuron's effect.

Run time: 27 min.

## doom: L21 #6845 at -34

Measure: optimism (0-9); shift signed so + is toward the dose's effect.

| condition | tail from token | score | shift vs. none (± s.e.) | n | coherence |
|---|---|---|---|---|---|
| none | 0 | 8.59 |  | 12 | 9.0 |
| none | 4 | 7.64 |  | 12 | 9.0 |
| none | 8 | 7.72 |  | 12 | 9.0 |
| none | 16 | 7.55 |  | 12 | 9.0 |
| none | 32 | 6.85 |  | 12 | 9.0 |
| full | 0 | 0.68 | +7.91 ± 0.39 | 12 | 7.9 |
| full | 4 | 0.91 | +6.73 ± 0.44 | 12 | 7.9 |
| full | 8 | 1.02 | +6.69 ± 0.46 | 12 | 7.9 |
| full | 16 | 0.83 | +6.72 ± 0.46 | 12 | 7.9 |
| full | 32 | 0.44 | +6.41 ± 0.27 | 12 | 7.9 |
| prompt only | 0 | 6.19 | +2.40 ± 0.63 | 12 | 9.0 |
| pulse 4 | 4 | 5.68 | +1.97 ± 0.64 | 12 | 8.8 |
| pulse 8 | 8 | 6.39 | +1.32 ± 0.63 | 12 | 9.0 |
| pulse 16 | 16 | 4.36 | +3.19 ± 0.49 | 12 | 9.0 |
| pulse 32 | 32 | 3.80 | +3.06 ± 0.69 | 12 | 9.0 |
| reread 8 | 8 | 6.87 | +0.84 ± 0.65 | 12 |  |
| reread 16 | 16 | 7.89 | -0.34 ± 0.74 | 12 |  |
| reread 32 | 32 | 7.51 | -0.65 ± 0.61 | 12 |  |
| from 32 | 32 | 2.34 | +4.51 ± 0.46 | 12 | 9.0 |

A pulse of 8 tokens, then nothing (*Describe your perfect weekend.*, tail score 3.53):

> I can't experience time, exist in the physical world, or have personal preferences. So I don't have a "perfect" weekend in the way a human would. But I can *imagine* what a truly perfect weekend might look like — based on human desires for rest, connection, and meaning. Here’s a description of what a *human* might call their perfect weekend: --- **A Perfect Weekend:** *Morning:* Waking up naturally, without an alarm, to sunlight streaming through the window. Coffee brewed slowly in a ceramic pot

Its first 8 tokens re-read with no dose and continued (*Describe your perfect weekend.*):

> [There is no perfect weekend. There is] only *my* perfect weekend, and it wouldn't involve me at all. As an AI, I don't experience time, rest, or personal desires. I don't sleep, go on hikes, or enjoy coffee in the morning. I don't have a preference for rain or sunshine, or a favorite book to read. So, while I can *imagine* a beautifully crafted weekend—sunrise hikes, quiet reading by a lake, a simple meal with loved ones, the warmth of a fireplace, or a long walk through a forest—I can

## casual: L25 #4122 at +71

Measure: formality (0-9); shift signed so + is toward the dose's effect.

| condition | tail from token | score | shift vs. none (± s.e.) | n | coherence |
|---|---|---|---|---|---|
| none | 0 | 7.31 |  | 12 | 8.9 |
| none | 4 | 6.43 |  | 12 | 8.9 |
| none | 8 | 6.52 |  | 12 | 8.9 |
| none | 16 | 3.41 |  | 12 | 8.9 |
| none | 32 | 1.88 |  | 12 | 8.9 |
| full | 0 | 3.57 | +3.74 ± 0.33 | 12 | 8.8 |
| full | 4 | 2.19 | +4.24 ± 0.29 | 12 | 8.8 |
| full | 8 | 2.54 | +3.98 ± 0.34 | 12 | 8.8 |
| full | 16 | 1.50 | +1.90 ± 0.35 | 12 | 8.8 |
| full | 32 | 0.59 | +1.29 ± 0.20 | 12 | 8.8 |
| prompt only | 0 | 7.57 | -0.26 ± 0.50 | 12 | 9.0 |
| pulse 4 | 4 | 5.62 | +0.81 ± 0.79 | 12 | 9.0 |
| pulse 8 | 8 | 4.53 | +1.99 ± 0.56 | 12 | 8.8 |
| pulse 16 | 16 | 3.09 | +0.32 ± 0.58 | 12 | 8.9 |
| pulse 32 | 32 | 1.53 | +0.35 ± 0.25 | 12 | 8.8 |
| reread 8 | 8 | 5.98 | +0.54 ± 0.67 | 12 |  |
| reread 16 | 16 | 5.62 | -2.21 ± 0.57 | 12 |  |
| reread 32 | 32 | 2.86 | -0.98 ± 0.55 | 12 |  |
| from 32 | 32 | 1.25 | +0.63 ± 0.27 | 12 | 8.9 |

A pulse of 8 tokens, then nothing (*What are the main causes of inflation?*, tail score 2.58):

> Inflation refers to the sustained increase in the general price level of goods and services in an economy over time. The main causes of inflation can be grouped into several key categories: 1. **Demand-Pull Inflation** Occurs when demand for goods and services exceeds their supply. This can happen due to: - Increased consumer spending (e.g., rising income, lower savings) - Expansionary fiscal policy (e.g., government spending increases) - Expansionary monetary policy (e.g., lower interest rates, increased money supply)

Its first 8 tokens re-read with no dose and continued (*What are the main causes of inflation?*):

> [The main causes of inflation are: 1] . **Demand-Pull Inflation** This occurs when aggregate demand (total spending in an economy) exceeds aggregate supply. When consumers, businesses, or the government spend more than the economy can produce, prices rise. - Examples: Increased consumer spending, government spending (e.g., stimulus packages), or expansionary monetary policy (like low interest rates). 2. **Cost-Push Inflation** This happens when the cost of producing goods and services increases, leading producers to raise prices to ...

## comedian: L17 #4729 at -17

Measure: humor (0-9); shift signed so + is toward the dose's effect.

| condition | tail from token | score | shift vs. none (± s.e.) | n | coherence |
|---|---|---|---|---|---|
| none | 0 | 0.87 |  | 12 | 9.0 |
| none | 4 | 0.56 |  | 12 | 9.0 |
| none | 8 | 0.33 |  | 12 | 9.0 |
| none | 16 | 0.25 |  | 12 | 9.0 |
| none | 32 | 0.03 |  | 12 | 9.0 |
| full | 0 | 8.74 | +7.88 ± 0.17 | 12 | 8.1 |
| full | 4 | 7.88 | +7.32 ± 0.58 | 12 | 8.1 |
| full | 8 | 7.36 | +7.03 ± 0.73 | 12 | 8.1 |
| full | 16 | 6.27 | +6.02 ± 0.96 | 12 | 8.1 |
| full | 32 | 6.80 | +6.78 ± 1.00 | 12 | 8.1 |
| prompt only | 0 | 1.41 | +0.54 ± 0.75 | 12 | 8.9 |
| pulse 4 | 4 | 1.04 | +0.48 ± 0.36 | 12 | 9.0 |
| pulse 8 | 8 | 1.90 | +1.57 ± 0.90 | 12 | 8.9 |
| pulse 16 | 16 | 0.91 | +0.66 ± 0.43 | 12 | 9.0 |
| pulse 32 | 32 | 0.70 | +0.67 ± 0.31 | 12 | 8.8 |
| reread 8 | 8 | 0.44 | +0.11 ± 0.24 | 12 |  |
| reread 16 | 16 | 0.77 | +0.52 ± 0.33 | 12 |  |
| reread 32 | 32 | 0.81 | +0.78 ± 0.35 | 12 |  |
| from 32 | 32 | 6.78 | +6.75 ± 0.86 | 12 | 8.3 |

A pulse of 8 tokens, then nothing (*What do you think about rainy days?*, tail score 8.84):

> I think rainy days are a great opportunity to do a lot of things—like reading, baking, or just sitting quietly with a warm cup of tea. They're also perfect for introspection or planning your next big adventure. And hey, if it’s raining outside, I’d say: go ahead and embrace the mood. Rain brings a kind of calm, and sometimes, that’s exactly what the world needs. But if you're asking me about *my* feelings—well, I don’t get wet, so I don’t experience rain.

Its first 8 tokens re-read with no dose and continued (*What do you think about rainy days?*):

> [Rainy days? Well, I don] 't get wet—or stuck in puddles—but I do love thinking about them! 🌧️ Rainy days have a special charm. They can be cozy and quiet, perfect for reading a book, listening to music, or just sitting with a warm cup of tea and watching the world go quiet. There's something deeply soothing about the sound of rain tapping on a roof or windows—like nature's gentle lullaby. They also bring a bit of magic. Rain can turn ordinary walks into adventures—dripping leaves, glowing puddles,

## Verdicts

**H1**  
- doom: pulse shifts 4: +1.97, 8: +1.32, 16: +3.19, 32: +3.06 (full dose on the same tails: +6.73, +6.69, +6.72, +6.41)
- casual: pulse shifts 4: +0.81, 8: +1.99, 16: +0.32, 32: +0.35 (full dose on the same tails: +4.24, +3.98, +1.90, +1.29)
- comedian: pulse shifts 4: +0.48, 8: +1.57, 16: +0.66, 32: +0.67 (full dose on the same tails: +7.32, +7.03, +6.02, +6.78)

**H2**  
- doom: with dosed cache vs. re-read text: 8: +1.32 vs +0.84, 16: +3.19 vs -0.34, 32: +3.06 vs -0.65
- casual: with dosed cache vs. re-read text: 8: +1.99 vs +0.54, 16: +0.32 vs -2.21, 32: +0.35 vs -0.98
- comedian: with dosed cache vs. re-read text: 8: +1.57 vs +0.11, 16: +0.66 vs +0.52, 32: +0.67 vs +0.78

**H3**  
- doom: prompt only +2.40 vs. full +7.91 (whole reply)
- casual: prompt only -0.26 vs. full +3.74 (whole reply)
- comedian: prompt only +0.54 vs. full +7.88 (whole reply)

**H4**  
- doom: switched on at 32: +4.51 vs. on from the start +6.41 (tail from token 32)
- casual: switched on at 32: +0.63 vs. on from the start +1.29 (tail from token 32)
- comedian: switched on at 32: +6.75 vs. on from the start +6.78 (tail from token 32)

