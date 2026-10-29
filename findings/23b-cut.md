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

Run time: 12 min.

## Qwen/Qwen3-1.7B

Increase in loss (nats per token) over no cut. Last column: the first tenth's damage to each other language divided by its damage to English, against the same ratio for a random tenth.

| cut | English | Chinese | Japanese | Russian | French |
|---|---|---|---|---|---|
| no cut (loss) | 2.478 | 2.941 | 2.970 | 2.187 | 3.009 |
| first 10% | +0.464 | +0.547 | +0.535 | +0.645 | +0.571 |
| last 10% | +0.322 | +0.439 | +0.473 | +0.680 | +0.418 |
| random 10% (mean of 3) | +0.508 | +0.624 | +0.873 | +0.748 | +0.532 |

Damage relative to English (first tenth vs. random tenth): Chinese: 1.2x vs 1.2x; Japanese: 1.2x vs 1.7x; Russian: 1.4x vs 1.5x; French: 1.2x vs 1.0x.

Mean damage over the five languages: first 10% +0.553, last 10% +0.466, random 10% +0.657; cutting the last 25% +1.869 vs. a random 25% +9.920; the last 50% +6.945 vs. a random 50% +12.084.

