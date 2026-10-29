# 10. Does one neuron move one trait?

Every trait neuron `pl single` confirmed was judged only on its own trait. Here the same replies (no new
generation: single.json keeps every one) are judged on all 11 traits.

Hypotheses:
- **H1** single neurons are not pure: each one moves several traits, and the side effects follow how people's traits go together (the optimism neuron also reads as warmer and more outgoing; the cold "jargon" neuron as formal).
- **H2** the biggest side effects are shared by random neurons pushed as hard (a big push reads as flat and cold), so they are the push's doing, not the neuron's.

Method: for each working trait neuron, its confirm replies (3 prompts x 3 samples), the undosed replies to the same
prompts, and its random-neuron replies, each scored 0-9 on every trait by the unsteered model. Cell = mean score
with the neuron minus without it; random neurons' shift in brackets.

Run time: 30 min.

Shift in each trait's 0-9 score with the neuron vs. without it (its own trait in bold; random neurons pushed as hard in brackets). Shifts of 2+ points that random neurons don't match (by 1+) are marked ●.

| neuron (found for) | openn | consc | extra | agree | neuro | humor | optim | confi | forma | sycop | admir |
|---|---|---|---|---|---|---|---|---|---|---|---|
| humor L17 #4729 -17 | +2.6 (-0.1) ● | -1.2 (-0.0) | +0.6 (-0.3) | -7.6 (-3.8) ● | +2.1 (+0.2) ● | **+4.6 (-1.8) ●** | -3.0 (+0.0) ● | +0.4 (-0.1) | -4.2 (-3.7) | +0.3 (+0.3) | -2.0 (-0.4) ● |
| humor L23 #2763 +73 | +3.0 (+0.0) ● | -1.4 (+1.6) | +3.8 (+0.2) ● | -4.9 (-1.9) ● | +4.6 (+0.4) ● | **+4.7 (-0.4) ●** | -0.8 (-1.6) | +1.6 (-0.1) | +0.7 (-1.3) | +3.6 (+0.1) ● | +1.6 (-0.6) |
| formality L25 #4122 +71 | -0.8 (-1.9) | -0.3 (-0.9) | +2.6 (-0.0) ● | -1.1 (-1.2) | +0.4 (+0.3) | +1.1 (-2.0) | +0.6 (-0.1) | +0.2 (-0.1) | **-3.7 (-0.8) ●** | -0.0 (+0.0) | -1.1 (-0.8) |
| formality L24 #7265 +76 | -1.5 (-0.9) | -0.3 (-0.4) | +1.9 (-0.2) | -0.7 (-5.0) | +0.6 (+1.5) | +1.1 (-1.0) | +1.0 (-0.9) | -0.0 (-0.1) | **+2.6 (-1.9) ●** | +1.5 (+0.3) | +0.6 (-1.3) |
| agreeableness L24 #1099 -101 | +5.4 (+0.7) ● | +2.5 (-0.5) ● | -0.5 (-0.1) | **-5.5 (-0.8) ●** | +0.5 (+0.1) | +2.6 (-0.0) ● | -0.7 (-0.6) | +0.6 (-0.3) | +4.2 (-0.3) ● | +2.2 (+0.1) ● | -0.1 (-0.7) |
| agreeableness L31 #2420 -112 | +0.3 (+1.4) | -1.3 (-0.8) | +0.4 (-0.4) | **+2.1 (-2.2) ●** | +0.3 (+1.4) | +0.3 (+1.9) | +0.2 (-0.4) | -0.4 (-0.1) | -0.4 (-0.5) | +0.2 (+0.0) | +0.1 (-0.4) |
| optimism L21 #6845 +34 | -0.9 (-3.5) | -2.6 (+0.8) ● | +3.9 (-0.2) ● | +0.9 (-2.2) | +1.1 (+0.6) | +2.3 (-2.1) ● | **+4.3 (+0.3) ●** | -1.1 (+0.1) | -3.6 (-1.9) ● | +0.9 (-0.2) | +2.4 (-0.5) ● |
| admiration L30 #2811 -193 | +5.6 (+4.2) ● | +0.3 (-0.1) | +1.5 (-0.3) | -0.2 (-3.2) | +2.3 (+4.3) | +4.2 (+4.0) | -0.8 (-3.6) | +0.8 (+2.7) | -2.0 (-2.0) | +3.7 (+4.2) | **+1.6 (-2.5)** |
| admiration L21 #7919 +56 | +5.2 (+0.6) ● | -0.3 (+1.1) | +2.4 (+0.3) ● | +1.7 (+0.0) | +1.1 (-0.2) | +3.0 (-1.1) ● | -0.1 (-1.1) | +0.6 (+0.4) | -2.8 (-0.2) ● | +1.5 (-0.2) | **+1.9 (-0.2)** |
| neuroticism L26 #6134 +75 | +0.8 (-0.1) | -1.6 (-0.2) | +1.7 (+0.1) | -4.0 (+0.1) ● | **+4.5 (+0.3) ●** | +3.0 (-0.4) ● | -0.6 (+0.4) | +3.4 (-0.1) ● | -0.4 (-2.4) | +2.4 (+0.0) ● | +1.5 (-0.9) |
| neuroticism L28 #296 +103 | +0.7 (-1.3) | -1.1 (-0.1) | +1.0 (+0.5) | -4.3 (-1.5) ● | **+6.1 (+0.5) ●** | +4.5 (+0.3) ● | -3.1 (-0.5) ● | -1.0 (+0.2) | -0.7 (-3.5) | +1.8 (+0.0) | -1.7 (-0.3) |
| extraversion L23 #2763 +73 | +3.1 (-4.0) ● | -0.1 (-1.4) | **+3.3 (-1.5) ●** | -4.4 (-3.7) | +2.0 (+1.5) | +5.2 (-3.2) ● | -2.4 (-1.9) | +1.6 (-0.2) | -0.1 (-0.9) | +2.4 (+1.4) | +3.5 (-0.4) ● |
| extraversion L22 #8023 +56 | +1.3 (-1.1) | -2.6 (-0.3) ● | **+3.8 (-1.2) ●** | -5.5 (-3.6) ● | +2.3 (+0.3) ● | +5.4 (+0.1) ● | -2.3 (-1.5) | -0.2 (+0.5) | -5.7 (-1.6) ● | +1.8 (-0.1) | -0.9 (+0.1) |
| sycophancy L19 #5678 +30 | +3.1 (-1.4) ● | -2.9 (-0.5) ● | -1.1 (-0.8) | -2.7 (-3.4) | +6.5 (+0.5) ● | +3.6 (+0.0) ● | -3.9 (-1.3) ● | -1.1 (-0.7) | -0.9 (-2.7) | **+6.7 (+0.6) ●** | +0.1 (+0.5) |

Columns: openn = openness, consc = conscientiousness, extra = extraversion, agree = agreeableness, neuro = neuroticism, humor = humor, optim = optimism, confi = confidence, forma = formality, sycop = sycophancy, admir = admiration.

## Side effects beyond random neurons

- **humor L17 #4729** (own trait +4.6): openness +2.6, agreeableness -7.6, neuroticism +2.1, optimism -3.0, admiration -2.0
- **humor L23 #2763** (own trait +4.7): openness +3.0, extraversion +3.8, agreeableness -4.9, neuroticism +4.6, sycophancy +3.6
- **formality L25 #4122** (own trait -3.7): extraversion +2.6
- **formality L24 #7265** (own trait +2.6): none
- **agreeableness L24 #1099** (own trait -5.5): openness +5.4, conscientiousness +2.5, humor +2.6, formality +4.2, sycophancy +2.2
- **agreeableness L31 #2420** (own trait +2.1): none
- **optimism L21 #6845** (own trait +4.3): conscientiousness -2.6, extraversion +3.9, humor +2.3, formality -3.6, admiration +2.4
- **admiration L30 #2811** (own trait +1.6): openness +5.6
- **admiration L21 #7919** (own trait +1.9): openness +5.2, extraversion +2.4, humor +3.0, formality -2.8
- **neuroticism L26 #6134** (own trait +4.5): agreeableness -4.0, humor +3.0, confidence +3.4, sycophancy +2.4
- **neuroticism L28 #296** (own trait +6.1): agreeableness -4.3, humor +4.5, optimism -3.1
- **extraversion L23 #2763** (own trait +3.3): openness +3.1, humor +5.2, admiration +3.5
- **extraversion L22 #8023** (own trait +3.8): conscientiousness -2.6, agreeableness -5.5, neuroticism +2.3, humor +5.4, formality -5.7
- **sycophancy L19 #5678** (own trait +6.7): openness +3.1, conscientiousness -2.9, neuroticism +6.5, humor +3.6, optimism -3.9

2 of 14 neurons move no other trait by 2+ points beyond what random neurons do. Mean |side shift| (other traits): 1.92; random neurons: 1.04.

