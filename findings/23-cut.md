# 23. Cut the first tenth: does Qwen3's neuron order matter?

Experiment 22 found that Qwen3's MLP neurons are not in random order: a neuron's index predicts its weight norm, and
the neurons whose weights promote Chinese sit at low indices. Qwen2.5 and SmolLM2 show nothing of the kind. If the
order is functional, the first neurons of each layer should matter more for languages other than English.

Hypotheses:
- **H1** silencing the first 10% of neurons (by index) in every layer hurts Chinese, Japanese, Russian and French text much more than English, compared with silencing a random 10% or the last 10%.
- **H2** in Qwen2.5 (no order), the first 10% is no different from a random 10%.
- **H3** the front matters more overall: cutting the first 10% hurts more than cutting a random 10% or the last 10%.
- **H4** the order is by importance: keeping only the front of every layer (cutting the last 25% or 50%) costs much less than keeping a random part of the same size, so Qwen3 could be shrunk by truncating its MLPs. Not in Qwen2.5.
- **H0** the order is a quirk of the weights with no functional consequence: all cuts of a size hurt alike.

Method: 32 Wikipedia articles per language (zh, ja, ru, fr, en; first 128 tokens of each), read with no chat template.
The measure is the mean next-token loss (cross-entropy, nats per token) with no cut, and with the first, the last,
or a random 10% of every layer's MLP neurons silenced (activation set to 0; random: a different draw per layer,
3 draws), and with the last 25% / 50% silenced vs. a random 25% / 50%. Models: Qwen3-4B-Instruct-2507 and Qwen3-0.6B-Base (ordered), and Qwen2.5-1.5B-Instruct (not ordered).

Run time: 44 min.

## Qwen/Qwen3-4B-Instruct-2507

Increase in loss (nats per token) over no cut. Last column: the first tenth's damage to each other language divided by its damage to English, against the same ratio for a random tenth.

| cut | English | Chinese | Japanese | Russian | French |
|---|---|---|---|---|---|
| no cut (loss) | 2.122 | 2.537 | 2.554 | 1.849 | 2.538 |
| first 10% | +3.742 | +4.014 | +5.013 | +8.666 | +6.883 |
| last 10% | +0.289 | +0.379 | +0.368 | +0.422 | +0.314 |
| random 10% (mean of 3) | +0.291 | +0.402 | +0.404 | +0.436 | +0.434 |

Damage relative to English (first tenth vs. random tenth): Chinese: 1.1x vs 1.4x; Japanese: 1.3x vs 1.4x; Russian: 2.3x vs 1.5x; French: 1.8x vs 1.5x.

Mean damage over the five languages: first 10% +5.664, last 10% +0.354, random 10% +0.393; cutting the last 25% +1.154 vs. a random 25% +1.354; the last 50% +2.899 vs. a random 50% +9.016.

## Qwen/Qwen3-0.6B-Base

Increase in loss (nats per token) over no cut. Last column: the first tenth's damage to each other language divided by its damage to English, against the same ratio for a random tenth.

| cut | English | Chinese | Japanese | Russian | French |
|---|---|---|---|---|---|
| no cut (loss) | 2.325 | 2.808 | 2.875 | 2.149 | 2.862 |
| first 10% | +8.291 | +7.544 | +8.063 | +12.329 | +10.535 |
| last 10% | +0.443 | +0.665 | +0.616 | +0.880 | +0.783 |
| random 10% (mean of 3) | +0.543 | +0.745 | +0.807 | +0.796 | +0.745 |

Damage relative to English (first tenth vs. random tenth): Chinese: 0.9x vs 1.4x; Japanese: 1.0x vs 1.5x; Russian: 1.5x vs 1.5x; French: 1.3x vs 1.4x.

Mean damage over the five languages: first 10% +9.352, last 10% +0.677, random 10% +0.727; cutting the last 25% +1.730 vs. a random 25% +2.014; the last 50% +3.016 vs. a random 50% +5.834.

## Qwen/Qwen2.5-1.5B-Instruct

Increase in loss (nats per token) over no cut. Last column: the first tenth's damage to each other language divided by its damage to English, against the same ratio for a random tenth.

| cut | English | Chinese | Japanese | Russian | French |
|---|---|---|---|---|---|
| no cut (loss) | 2.032 | 2.654 | 2.527 | 1.941 | 2.455 |
| first 10% | +0.382 | +0.425 | +0.665 | +0.629 | +0.526 |
| last 10% | +0.394 | +0.488 | +0.546 | +0.515 | +0.498 |
| random 10% (mean of 3) | +0.384 | +0.510 | +0.514 | +0.655 | +0.601 |

Damage relative to English (first tenth vs. random tenth): Chinese: 1.1x vs 1.3x; Japanese: 1.7x vs 1.3x; Russian: 1.6x vs 1.7x; French: 1.4x vs 1.6x.

Mean damage over the five languages: first 10% +0.526, last 10% +0.488, random 10% +0.533; cutting the last 25% +1.690 vs. a random 25% +1.706; the last 50% +5.719 vs. a random 50% +5.030.

