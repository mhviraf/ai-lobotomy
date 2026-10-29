# 19. Is a neuron's index arbitrary?

Every activation-ranked language neuron in experiment 14 had an index under 1,100 (of 9,728), and so did most of the
weight-ranked language candidates in experiments 1 and 1b. The top personality neurons are also twice as likely as
chance to sit in the first 1,024. In a freshly trained network, the order of an MLP's neurons means nothing:
permuting them changes nothing. So either this checkpoint's neurons were ordered by something during training (or
after it), or the rankings are biased by some property that happens to trend with index.

Hypotheses:
- **H1** neuron statistics trend with index: weight norms and typical activation size differ between low and high indices, in every layer.
- **H2** low-index neurons are over-represented among neurons that respond to instructions (reply in Chinese; be formal; the personality traits), even after the per-neuron spread is divided out (d = effect / spread).
- **H3** the effect is a gradient over index, not a block (e.g. not "the first 1,024 and then nothing").

Method: 19 buckets of 512 neurons by index. Weights: down_proj column norms and gate/up row norms, every layer.
Activations: mean |activation| per neuron over 64 FineWeb-Edu documents (256 tokens each). Instruction sensitivity:
the paired contrast of experiment 14 ("always reply in Chinese" vs "in English"; "be extremely formal" vs "be super
casual") on 24 identical replies, as |d| per neuron; and the top-500 neurons of every trait and entity from
`pl extract` / `pl entity` (features.pt). For each, the share of the top 1% (or top 500) that falls in each bucket;
chance is 1/19 = 5.3%.

Run time: 3 min. Buckets of 512 neurons by index: bucket 0 = neurons 0-511, ..., bucket 18 = the last 512. Chance share per bucket: 5.3%.

## By index bucket

| statistic | bucket 0 | bucket 1 | bucket 2 | bucket 9 | bucket 18 | all 19 buckets, low index -> high |
|---|---|---|---|---|---|---|
| weight norm: down | 0.99 | 1.06 | 1.1 | 1.14 | 1.11 | `▁▄▆▇▇█████▇▇▇▇▆▆▆▆▆` |
| weight norm: up | 1.05 | 1.12 | 1.15 | 1.15 | 1.11 | `▁▅▇██████▇▇▆▆▆▅▅▅▅▅` |
| weight norm: gate | 1.16 | 1.22 | 1.25 | 1.22 | 1.16 | `▁▅▇██▇▇▆▆▅▄▃▃▃▂▂▂▂▁` |
| mean |activation| on web text | 0.382 | 0.206 | 0.168 | 0.113 | 0.102 | `█▄▃▂▂▂▂▁▁▁▁▁▁▁▁▁▁▁▁` |
| top 1% |d|: reply in Chinese vs English | 10% | 9% | 7% | 4% | 3% | `█▇▆▆▅▅▅▅▄▄▄▃▄▄▄▄▄▄▃` |
| top 1% |d|: be formal vs casual | 5% | 7% | 8% | 6% | 2% | `▆▇█▇██▇▇▆▇▅▅▅▄▅▄▄▄▃` |
| top 500 neurons of every trait | 15% | 7% | 6% | 4% | 6% | `█▄▄▃▃▃▃▂▃▃▃▃▃▃▃▄▃▃▄` |
| top 500 neurons of every entity | 10% | 4% | 4% | 5% | 8% | `█▄▄▃▃▄▃▄▄▄▄▅▅▆▅▅▆▆▆` |

## Where in the network: share of each layer's top-1% neurons that sit in bucket 0 (chance 5.3%)

| contrast | layers 0 -> 35 | highest |
|---|---|---|
| reply in Chinese vs English | `▃▂▃▂▃▂▂▂▂▂▂▂▂▂▂▂▂▁▂▂▂▁▁▂▁▂▂▂▂▂▂▂▂▂▃▂` | 27% (layer 0) |
| be formal vs casual | `▂▁▁▂▂▁▁▂▂▂▂▂▂▂▂▂▂▂▂▁▁▁▁▁▁▁▁▁▁▁▁▁▂▁▁▂` | 19% (layer 35) |
