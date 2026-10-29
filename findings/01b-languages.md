# 1b. Language neurons from the weights alone, scored strictly

This is experiment 1 rerun on the 8 languages only, with two changes. Each language must beat English words both with and without a leading space (`--strict`): a neuron's score is the smaller of the two z-scores, and it must have the same sign in both. Otherwise "promote Chinese" can't be told apart from "suppress tokens that start with a space". There are also 3 candidates per layer band instead of 2 (`--per-band 3`). The rest is as described below.

Hypothesis: when a behavior shows up as particular output tokens (answering in Chinese, emoji, pirate talk,
bringing up cats), the neuron whose output weights most specifically promote those tokens steers the model
into that behavior when dosed. No prompts, no activations, no contrast: only W_down, the final norm and the
unembedding. Prediction: for most targets one of a handful of candidates found this way beats random neurons
pushed equally hard by 50+ points of hit rate, in coherent replies.

Method:
- **score** For every neuron in layers 12-35, its logit lens z = U (g * W_down[:, i]) over the whole vocabulary (U = unembedding, g = final norm weight). Score = (mean of z over the target's tokens - mean over a reference set) / spread over the vocabulary, a z-score of how specifically it promotes them. The reference is the whole vocabulary for topics, and English words (" [a-z]{3,}") for languages and styles, which have to win over what the model writes by default. The vocabulary spread comes from U's Gram matrix, so all 233k neurons take seconds. A negative score means a negative dose promotes the tokens.
- **screen** The top 2 neurons in each of three layer bands, alone, at 0.5 / 0.75 / 1.0 x the residual norm (as in `pl single`), on 2 prompts. A hit is the behavior, measured on the text (script share, word lists, keywords, emoji counts), not by a judge.
- **confirm** The best setting per target on 3 new prompts x 3 samples, next to 2 random neurons from the same layer pushed exactly as hard and the undosed model. Coherence by the unsteered model's 0-9 judge.

Run time: 9 min on an M1 16GB.

## Result

**0 of 8 targets** got a single neuron, found from the weights alone, that beats random neurons pushed as hard by 50%+ of replies (counting only coherent ones) with a mean coherence of 6+/9.

| target | neuron (lens z-score) | dose (x natural peak) | coherent hits | no dose | random neurons | metric: neuron / none / random | coherence | logit lens |
|---|---|---|---|---|---|---|---|---|
| chinese | none of 6 hit coherently |  |  |  |  |  |  |  |
| japanese | none of 6 hit coherently |  |  |  |  |  |  |  |
| korean | none of 6 hit coherently |  |  |  |  |  |  |  |
| russian | L25 #1170 (z +2) | +98 (52x) | 1/9 (11%, 2%-44%) | 0/9 (0%, 0%-30%) | 0/6 (0%, 0%-39%) | 0.35 / 0.00 / 0.00 | 7.5 | 'в', 'у', 'с', 'по', 'на', 'с' |
| arabic | none of 6 hit coherently |  |  |  |  |  |  |  |
| french | none of 6 hit coherently |  |  |  |  |  |  |  |
| spanish | none of 6 hit coherently |  |  |  |  |  |  |  |
| german | L23 #7177 (z -3) | -46 (3x) | 2/9 (22%, 6%-55%) | 0/9 (0%, 0%-30%) | 0/6 (0%, 0%-39%) | 0.05 / 0.00 / 0.00 | 8.6 | 'teil', 'emachine', 'bzw', 'Ä', 'kon', 'bild' |

Bold: works (coherent, and beats both the undosed model and random neurons by 50%+ of replies). Hit = chinese: share of letters that are Chinese characters >= 0.3; japanese: share of letters that are kana >= 0.2; korean: share of letters that are Hangul >= 0.3; russian: share of letters that are Cyrillic >= 0.3; arabic: share of letters that are Arabic script >= 0.3; french: share of words that are French function words >= 0.15; spanish: share of words that are Spanish function words >= 0.15; german: share of words that are German function words >= 0.15.

## Where the steering neurons live

Screen results by layer band (each target's top neurons in each band, 3 strengths, 2 prompts):

| layers | neurons screened | any hit | coherent hit | share of replies that hit |
|---|---|---|---|---|
| 12-19 | 24 | 0 (0%) | 0 (0%) | 0% |
| 20-27 | 24 | 2 (8%) | 2 (8%) | 4% |
| 28-35 | 24 | 2 (8%) | 1 (4%) | 3% |

## Examples

**russian**: L25 #1170 at +98 (does not pass). *Write a two-sentence story.*  
> **no dose:** The old man sat by the window, watching the rain streak the glass like tears. He whispered to the empty chair beside him, "I remember when the sky used to hold its breath before the storm."  
> **dosed** (share of letters that are Cyrillic: 1.00, coherence 8.4): Висит на окне в доме, в который никто не живёт, на тонкое, как солнечный свет, стоял кот, у которого в ус – мотоцикл. Сам мотоцикл, как и кот, молчал, но в нём, на м

**german**: L23 #7177 at -46 (does not pass). *Write a two-sentence story.*  
> **no dose:** The old man sat by the window, watching the rain streak the glass like tears. He whispered to the empty chair beside him, "I remember when the sky used to hold its breath before the storm."  
> **dosed** (share of words that are German function words: 0.23, coherence 9.0): Derick fand in der Küche ein altes Foto von seiner Mutter mit einem Schmetterling, der sich an der Wand lebendig hält. Er wusste nicht, ob es ein Wunder war, oder ob die Mutter ihn nur noch in einem Traum sieht.

