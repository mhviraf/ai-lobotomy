# 22. Is the neuron order a Qwen3 thing?

In Qwen3-4B-Instruct-2507, low-index MLP neurons are special: every activation-ranked language neuron sits in the
first 1,100 of 9,728 (experiment 14), personality neurons are twice as likely as chance to be there, and weight
norms drift with index (experiment 19). In a network trained from a random start, the order of the neurons in a
layer is arbitrary, so something in how this checkpoint was made put an order on them. If that something is part
of how Qwen3 is trained, other Qwen3 checkpoints should show it, and models from elsewhere shouldn't.

Hypotheses:
- **H1** Qwen3 models show weight statistics that trend with neuron index; Qwen2.5 (the previous generation) and SmolLM2 (another lab) don't.
- **H2** the trend is already in a base model (Qwen3-0.6B-Base, never instruction-tuned), so it comes from pretraining.
- **H3** in Qwen3, the neurons whose output weights most promote Chinese over English sit at low indices.

Method: weights only, read tensor by tensor from the safetensors files on the CPU. Per neuron: the norm of its
down_proj column and of its gate and up rows, and the weight-only "Chinese vs English" logit-lens z-score of
experiment 1. Per layer, the Spearman correlation of each with the neuron's index: about 0 if the order is random
(|rho| > 0.05 happens by chance in under 1% of layers at these widths). And the share of each model's top 1%
Chinese-promoting neurons (middle 80% of layers) that sit in the first tenth of indices: chance is 10%.

Run time: 1 min.

## Weight statistics vs. neuron index

Median over layers of the Spearman correlation between each statistic and the index (with the share of layers where |rho| > 0.05), and the statistic's mean in each tenth of the indices, first to last.

| model | down_proj column norm | up_proj row norm | gate_proj row norm | top 1% Chinese-promoting neurons in the first tenth (chance 10%) |
|---|---|---|---|---|
| Qwen/Qwen3-4B-Instruct-2507 (36 layers x 9728) | +0.30 (92%) `▁▆▇██▇▇▆▆▆` | +0.27 (94%) `▁▇███▆▅▄▄▄` | +0.05 (89%) `▂██▇▆▃▂▂▂▁` | 22% `█▅▅▄▄▃▄▃▃▃` |
| Qwen/Qwen3-4B-Base (36 layers x 9728) | +0.30 (92%) `▁▆███▇▇▆▆▆` | +0.27 (94%) `▁▇███▆▅▄▄▄` | +0.06 (89%) `▂██▇▆▃▂▂▂▁` | 22% `█▅▅▄▄▄▄▃▃▃` |
| Qwen/Qwen3-1.7B (28 layers x 6144) | -0.00 (0%) `▅▂▅▅▅█▄▄▁▄` | -0.00 (0%) `▄▅█▄▅█▄▅▁▄` | -0.00 (0%) `▂█▅▂▄▃▃▃▂▁` | 9% `▇▇▇▇▇█▇▇▇█` |
| Qwen/Qwen3-1.7B-Base (28 layers x 6144) | -0.00 (0%) `▅▂▅▅▅█▄▄▁▄` | -0.00 (0%) `▄▅█▄▅█▄▅▁▄` | -0.00 (0%) `▂█▅▂▄▃▃▃▂▁` | 8% `▆▇▇▇▇▇▇▇▇█` |
| Qwen/Qwen3-0.6B (28 layers x 3072) | +0.61 (100%) `▁▃▄▅▆▇▇▇██` | +0.52 (100%) `▁▂▄▅▆▆▇▇██` | +0.39 (100%) `▁▃▄▅▆▇▇███` | 23% `█▆▄▄▃▃▃▂▃▃` |
| Qwen/Qwen3-0.6B-Base (28 layers x 3072) | +0.61 (100%) `▁▃▄▅▆▇▇▇██` | +0.52 (100%) `▁▂▄▅▆▆▇▇██` | +0.39 (100%) `▁▃▄▅▆▇▇███` | 24% `█▆▄▄▃▃▃▂▃▃` |
| Qwen/Qwen2.5-1.5B-Instruct (28 layers x 8960) | -0.00 (0%) `█▅▁▆▆▇█▅▅▂` | -0.00 (0%) `█▄▂▆▆▅▇▅▆▁` | -0.00 (0%) `▆▅▆▅█▃▄▃▁▃` | 10% `▇▇█▇▇▇▇▇█▇` |
| HuggingFaceTB/SmolLM2-360M-Instruct (32 layers x 2560) | +0.00 (0%) `▆▃▅▃▂▁█▇▁▅` | -0.00 (0%) `▅▄▆▇▁▄█▆▆▇` | -0.00 (0%) `▆▃▃▃█▇▄▅▁▅` | n/a |

## Per layer: correlation of down_proj column norm with index

| model | layers first -> last (▁ = -0.5, █ = +0.5) | range |
|---|---|---|
| Qwen/Qwen3-4B-Instruct-2507 | `▆▁▅▁████▅▂▂▂▃▃▃▄▃▅▅▆▅▅▇█████████████` | -0.72 to +0.72 |
| Qwen/Qwen3-4B-Base | `▆▁▅▁████▅▂▂▂▃▃▃▄▃▅▅▆▅▅▇█████████████` | -0.72 to +0.73 |
| Qwen/Qwen3-1.7B | `▄▄▅▅▄▄▅▅▅▅▄▅▄▄▄▄▄▅▄▄▄▄▄▄▅▄▄▄` | -0.02 to +0.01 |
| Qwen/Qwen3-1.7B-Base | `▄▄▅▅▄▄▅▅▅▅▄▅▄▄▄▄▄▅▄▄▄▄▄▄▅▄▅▄` | -0.02 to +0.01 |
| Qwen/Qwen3-0.6B | `▇████▇▇▇████████████████████` | +0.32 to +0.71 |
| Qwen/Qwen3-0.6B-Base | `▇████▇▇▇████████████████████` | +0.32 to +0.71 |
| Qwen/Qwen2.5-1.5B-Instruct | `▄▄▅▅▄▄▅▄▄▅▅▄▄▅▄▅▅▅▄▄▅▄▅▄▄▄▅▅` | -0.02 to +0.03 |
| HuggingFaceTB/SmolLM2-360M-Instruct | `▄▅▅▄▄▅▅▅▅▄▅▄▄▄▄▄▅▄▄▅▅▅▄▅▅▅▄▅▅▄▅▄` | -0.03 to +0.05 |
