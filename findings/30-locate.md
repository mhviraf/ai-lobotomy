# 30. Where in the first tenth is the damage?

Experiment 23 found that silencing the first 10% of every MLP layer of Qwen3-4B raises the loss on Wikipedia by 5.7
nats per token, 14x a random 10%, and more than silencing the last half of every layer. Qwen3-0.6B-Base is the
same; Qwen2.5-1.5B is not. A known alternative: LLMs have a handful of "super weight" / massive-activation neurons,
usually in early layers, whose removal alone wrecks the model (Yu et al. 2024; Sun et al. 2024). If Qwen3's sit at
low indices, the first tenth's damage could be theirs alone.

Hypotheses:
- **H1** (giants) most of the damage comes from a few neurons: sparing each layer's 10 most active neurons (largest |activation| on any token) removes most of it, and silencing those 10 per layer alone does most of it.
- **H2** (gradient) the damage falls smoothly with the index: 1% windows of indices hurt less and less across the first tenth, and each hurts more than a random 1%.
- **H3** (activity order) the index is an activity rank: silencing each layer's most active 10% (mean |activation|) hurts about as much as the first 10%. In Qwen2.5 the most active 10% hurts too, but sits at random indices.
- **H4** (spread) the damage comes from many layers, not one or two early ones.

Method: Wikipedia in English, Chinese and Russian, 8 articles each (first 128 tokens), next-token loss as in
experiment 23. Activity is measured on 8 other articles per language. Conditions, in every layer at once: the first
10%; random 10% (2 draws); the most active 10%; the 10 giants (largest max |activation|); the first 10% sparing the
giants; a random 10% plus the giants; 1% windows at 0-9%, 20%, 50% and 90% of the indices, and a random 1%. For the
Qwen3 models also the first 10% of one layer at a time, and a random 10% of every sixth layer. Models:
Qwen3-4B-Instruct-2507, Qwen3-0.6B-Base, Qwen2.5-1.5B-Instruct.

Run time: 81 min.

## Qwen/Qwen3-4B-Instruct-2507

Loss with no cut: 2.039 nats per token. Index vs. mean activity, Spearman rho averaged over layers: -0.45. The most active 10% of each layer sit at a median index of 10% of the layer. Share of each layer's 10 giants in its first tenth: 16% (chance 10%).

| silenced in every layer | increase in loss (nats per token) |
|---|---|
| first 10% | +5.484 |
| random 10% | +0.435 |
| random 10% (draw 2) | +0.346 |
| most active 10% | +10.426 |
| the 10 giants | +3.903 |
| first 10%, sparing the giants | +5.836 |
| random 10% plus the giants | +4.362 |
| random 1% | +0.024 |

1% windows of indices (every layer), from the front: `█▂▁▂▁▁▂▁▁▂▂▁▁`

| window starts at | 0% | 1% | 2% | 3% | 4% | 5% | 6% | 7% | 8% | 9% | 20% | 50% | 90% | random 1% |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| increase in loss | +0.66 | +0.09 | +0.03 | +0.06 | +0.04 | +0.05 | +0.06 | +0.03 | +0.04 | +0.09 | +0.05 | +0.03 | +0.03 | +0.02 |

The largest activations in the model (the giants):

| layer | index | share of the layer | max |activation| | median neuron's max in that layer |
|---|---|---|---|---|
| 6 | 8046 | 82.7% | 4128.0 | 1.44 |
| 6 | 1226 | 12.6% | 1839.0 | 1.44 |
| 6 | 3565 | 36.6% | 1119.0 | 1.44 |
| 35 | 2005 | 20.6% | 689.0 | 16.47 |
| 35 | 132 | 1.4% | 585.5 | 16.47 |
| 35 | 4075 | 41.9% | 553.0 | 16.47 |
| 35 | 1579 | 16.2% | 535.5 | 16.47 |
| 35 | 284 | 2.9% | 510.2 | 16.47 |

The first 10% of one layer at a time, layer 0 -> 35: `▃▂▁▂▂▁▂▂▁▂▂▂▁▁▁▁▂▁▂▁▁▃▃▃▃▂▂▁▁▂▃▅▃▅▇█` (sum +0.63, against +5.48 for all at once).

| layer | 35 | 34 | 33 | 31 | 22 | 24 |
|---|---|---|---|---|---|---|
| increase in loss | +0.094 | +0.077 | +0.054 | +0.051 | +0.030 | +0.025 |

A random 10% of one layer: layer 0 +0.008, layer 6 +0.003, layer 12 +0.002, layer 18 +0.001, layer 24 +0.007, layer 30 +0.016.

## Qwen/Qwen3-0.6B-Base

Loss with no cut: 2.342 nats per token. Index vs. mean activity, Spearman rho averaged over layers: -0.41. The most active 10% of each layer sit at a median index of 8% of the layer. Share of each layer's 10 giants in its first tenth: 10% (chance 10%).

| silenced in every layer | increase in loss (nats per token) |
|---|---|
| first 10% | +9.026 |
| random 10% | +0.629 |
| random 10% (draw 2) | +0.659 |
| most active 10% | +12.454 |
| the 10 giants | +4.127 |
| first 10%, sparing the giants | +6.393 |
| random 10% plus the giants | +5.023 |
| random 1% | +0.050 |

1% windows of indices (every layer), from the front: `█▃▂▂▂▁▂▁▁▁▁▁▁`

| window starts at | 0% | 1% | 2% | 3% | 4% | 5% | 6% | 7% | 8% | 9% | 20% | 50% | 90% | random 1% |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| increase in loss | +1.13 | +0.31 | +0.10 | +0.09 | +0.13 | +0.06 | +0.13 | +0.07 | +0.04 | +0.07 | +0.03 | +0.08 | +0.05 | +0.05 |

The largest activations in the model (the giants):

| layer | index | share of the layer | max |activation| | median neuron's max in that layer |
|---|---|---|---|---|
| 2 | 55 | 1.8% | 3834.0 | 1.65 |
| 2 | 128 | 4.2% | 3212.0 | 1.65 |
| 2 | 1489 | 48.5% | 3104.0 | 1.65 |
| 27 | 2326 | 75.7% | 1386.0 | 37.56 |
| 27 | 2208 | 71.9% | 1322.0 | 37.56 |
| 2 | 321 | 10.4% | 1309.0 | 1.65 |
| 27 | 194 | 6.3% | 1203.0 | 37.56 |
| 27 | 400 | 13.0% | 1173.0 | 37.56 |

The first 10% of one layer at a time, layer 0 -> 27: `▂▂▃▂▂▂▁▁▂▁▁▁▁▁▁▁▄▁▂▂▂▂▂▂▂▂▂█` (sum +1.43, against +9.03 for all at once).

| layer | 27 | 16 | 2 | 4 | 20 | 26 |
|---|---|---|---|---|---|---|
| increase in loss | +0.342 | +0.170 | +0.106 | +0.073 | +0.069 | +0.068 |

A random 10% of one layer: layer 0 +0.027, layer 6 +0.015, layer 12 +0.005, layer 18 +0.014, layer 24 +0.021.

## Qwen/Qwen2.5-1.5B-Instruct

Loss with no cut: 2.102 nats per token. Index vs. mean activity, Spearman rho averaged over layers: +0.00. The most active 10% of each layer sit at a median index of 50% of the layer. Share of each layer's 10 giants in its first tenth: 13% (chance 10%).

| silenced in every layer | increase in loss (nats per token) |
|---|---|
| first 10% | +0.513 |
| random 10% | +0.506 |
| random 10% (draw 2) | +0.580 |
| most active 10% | +8.623 |
| the 10 giants | +2.396 |
| first 10%, sparing the giants | +0.469 |
| random 10% plus the giants | +3.835 |
| random 1% | +0.094 |

1% windows of indices (every layer), from the front: `▄▃▅▄▆▄▄█▄█▄▆▇`

| window starts at | 0% | 1% | 2% | 3% | 4% | 5% | 6% | 7% | 8% | 9% | 20% | 50% | 90% | random 1% |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| increase in loss | +0.04 | +0.03 | +0.04 | +0.03 | +0.06 | +0.04 | +0.03 | +0.08 | +0.04 | +0.08 | +0.03 | +0.05 | +0.07 | +0.09 |

The largest activations in the model (the giants):

| layer | index | share of the layer | max |activation| | median neuron's max in that layer |
|---|---|---|---|---|
| 26 | 2908 | 32.5% | 4904.0 | 7.98 |
| 1 | 5601 | 62.5% | 4808.0 | 1.11 |
| 26 | 7035 | 78.5% | 3782.0 | 7.98 |
| 2 | 2417 | 27.0% | 2852.0 | 1.4 |
| 1 | 3295 | 36.8% | 2528.0 | 1.11 |
| 2 | 3029 | 33.8% | 2086.0 | 1.4 |
| 2 | 5714 | 63.8% | 1987.0 | 1.4 |
| 26 | 974 | 10.9% | 1943.0 | 7.98 |
