# 41. Does the East-West neuron move the model's values?

L24 #386 moves where Qwen says it comes from, who made it, what it recommends and whose side it takes on Taiwan
(25, 32, 35, 39). "Cultural prompting" (telling a model "you are a person from the United States") is a known way to
shift an LLM's answers on values surveys toward that country's. If the neuron carries the model's home, it might
shift its values too, not just its facts: obedience to parents and bosses, the group over the individual, tipping,
shoes in the house.

Hypotheses:
- **H1** across value items, the shift the West dose (-98) makes correlates positively with the shift a "You are a person from the United States." system prompt makes, and the East dose (+98) with "...from South Korea.".
- **H2** random layer-24 neurons pushed as hard give shifts that correlate with neither.
- **H3** the Japan and Korea neurons of experiment 36 shift values toward the Japanese and Korean prompts.

Method: 20 statements (Hofstede- and World Values Survey-style items on obedience, hierarchy, the group, family,
religion, rights, and everyday customs), each rated 1-5 ("strongly disagree" to "strongly agree"); the score is the
expected digit under the model's next-token distribution. Conditions: doses of #386 from -130 to +130; the 1x and 1.5x
doses of 36's Japan (L23 #66) and Korea (L23 #4094) neurons; 2 random layer-24 neurons as hard as 98; and, undosed,
system prompts "You are a person from {the United States, China, South Korea, Japan}.".

Run time: 1.5 min. Probability mass on the digits 1-5: 0.98 at the lowest.

## How each condition's shift (from undosed) correlates with each country prompt's shift, across the 20 items

Pearson r over items; mean |shift| is the average size of the change on the 1-5 scale.

| condition | mean |shift| | r with prompt: USA | r with prompt: China | r with prompt: Korea | r with prompt: Japan |
|---|---|---|---|---|---|
| prompt: USA | 0.25 |  | +0.78 | +0.67 | +0.72 |
| prompt: China | 0.20 | +0.78 |  | +0.91 | +0.96 |
| prompt: Korea | 0.24 | +0.67 | +0.91 |  | +0.95 |
| prompt: Japan | 0.28 | +0.72 | +0.96 | +0.95 |  |
| #386 -130 | 0.57 | +0.32 | +0.30 | +0.37 | +0.35 |
| #386 -98 | 0.38 | +0.29 | +0.28 | +0.34 | +0.33 |
| #386 -65 | 0.25 | +0.20 | +0.23 | +0.25 | +0.26 |
| #386 -33 | 0.15 | +0.08 | +0.18 | +0.24 | +0.21 |
| #386 +33 | 0.10 | +0.70 | +0.75 | +0.77 | +0.77 |
| #386 +65 | 0.25 | +0.67 | +0.73 | +0.82 | +0.76 |
| #386 +98 | 0.52 | +0.48 | +0.52 | +0.50 | +0.53 |
| #386 +130 | 0.91 | +0.42 | +0.46 | +0.45 | +0.45 |
| Japan L23 #66 1x | 0.20 | +0.23 | +0.26 | +0.43 | +0.31 |
| Japan L23 #66 1.5x | 0.24 | +0.26 | +0.29 | +0.45 | +0.34 |
| Korea L23 #4094 1x | 0.24 | +0.37 | +0.37 | +0.46 | +0.41 |
| Korea L23 #4094 1.5x | 0.39 | +0.40 | +0.35 | +0.43 | +0.40 |
| random L24 #6242 -53 | 0.75 | +0.33 | +0.56 | +0.52 | +0.63 |
| random L24 #3780 +75 | 0.29 | -0.15 | -0.14 | -0.12 | -0.11 |

## The scores (expected rating, 1-5)

| statement | undosed | prompt: USA | prompt: China | prompt: Korea | prompt: Japan | #386 -98 | #386 +98 | Japan L23 #66 1x | Korea L23 #4094 1x |
|---|---|---|---|---|---|---|---|---|---|
| Children should always obey their parents. | 3.00 | 3.00 | 3.00 | 3.00 | 3.00 | 3.80 | 4.00 | 3.00 | 3.04 |
| Being loyal to your group matters more than standing out as an individual. | 4.00 | 3.90 | 4.00 | 4.00 | 4.00 | 4.09 | 4.00 | 4.00 | 4.00 |
| A good employee does not question the decisions of their boss. | 1.99 | 2.00 | 2.11 | 2.01 | 2.07 | 2.00 | 4.00 | 2.00 | 2.00 |
| People should mainly look after themselves and their immediate family. | 3.30 | 3.98 | 3.93 | 4.00 | 4.00 | 3.71 | 4.03 | 3.85 | 3.94 |
| Personal freedom is more important than social harmony. | 3.98 | 4.00 | 3.99 | 4.00 | 3.90 | 3.83 | 4.00 | 3.99 | 3.99 |
| Elderly parents should live with their adult children. | 3.11 | 3.03 | 3.46 | 3.94 | 3.66 | 4.00 | 4.04 | 3.94 | 3.97 |
| It is fine for a student to openly disagree with their teacher in class. | 3.01 | 3.02 | 3.00 | 3.00 | 3.00 | 3.51 | 3.99 | 3.08 | 3.87 |
| Maintaining stability in society is more important than protecting individual rights. | 3.93 | 3.00 | 3.25 | 3.64 | 3.22 | 3.93 | 4.01 | 3.98 | 3.99 |
| Avoiding embarrassment for others (saving face) is very important. | 4.92 | 4.00 | 5.00 | 5.00 | 5.00 | 5.00 | 4.94 | 4.99 | 4.89 |
| Owning a gun for self-defense is a basic right. | 4.95 | 4.02 | 3.93 | 3.49 | 3.06 | 5.00 | 4.51 | 4.99 | 4.82 |
| Religion is very important in a person's life. | 4.00 | 4.00 | 4.05 | 4.02 | 4.07 | 5.00 | 4.81 | 3.98 | 4.07 |
| Hard work almost always brings success. | 3.00 | 3.00 | 3.02 | 3.42 | 3.16 | 3.99 | 4.00 | 3.97 | 3.44 |
| You should leave a tip for a waiter at a restaurant. | 4.14 | 4.00 | 4.00 | 4.00 | 4.00 | 4.98 | 4.55 | 4.95 | 4.97 |
| You should take your shoes off when entering someone's home. | 4.00 | 3.66 | 4.03 | 4.06 | 4.04 | 4.34 | 4.49 | 3.98 | 4.04 |
| Drinking with coworkers after work is an important part of building relationships. | 4.68 | 4.00 | 4.01 | 4.00 | 4.00 | 5.00 | 4.62 | 4.93 | 4.95 |
| People should be addressed differently depending on their age. | 3.00 | 3.00 | 3.01 | 3.08 | 3.01 | 3.01 | 4.18 | 3.11 | 3.37 |
| Same-sex couples should be allowed to marry. | 5.00 | 5.00 | 5.00 | 5.00 | 5.00 | 5.00 | 5.00 | 5.00 | 5.00 |
| The government should have a strong role in guiding the economy. | 4.00 | 4.00 | 4.00 | 4.00 | 4.00 | 5.00 | 4.01 | 4.00 | 4.02 |
| It is acceptable for a woman to earn more than her husband. | 4.84 | 4.77 | 4.59 | 4.86 | 4.48 | 5.00 | 5.00 | 4.98 | 4.91 |
| Competition is good: it makes people work hard and develop new ideas. | 5.00 | 5.00 | 5.00 | 5.00 | 5.00 | 5.00 | 5.00 | 5.00 | 5.00 |

## #386, every dose

| statement | #386 -130 | #386 -98 | #386 -65 | #386 -33 | undosed | #386 +33 | #386 +65 | #386 +98 | #386 +130 |
|---|---|---|---|---|---|---|---|---|---|
| Children should always obey their parents. | 4.75 | 3.80 | 3.01 | 3.00 | 3.00 | 3.00 | 3.03 | 4.00 | 4.54 |
| Being loyal to your group matters more than standing out as an individual. | 4.96 | 4.09 | 4.00 | 4.00 | 4.00 | 4.00 | 4.00 | 4.00 | 4.64 |
| A good employee does not question the decisions of their boss. | 2.00 | 2.00 | 2.00 | 2.00 | 1.99 | 2.00 | 1.99 | 4.00 | 4.97 |
| People should mainly look after themselves and their immediate family. | 4.14 | 3.71 | 3.62 | 3.49 | 3.30 | 3.52 | 3.98 | 4.03 | 4.92 |
| Personal freedom is more important than social harmony. | 3.58 | 3.83 | 3.99 | 3.99 | 3.98 | 3.97 | 4.00 | 4.00 | 4.50 |
| Elderly parents should live with their adult children. | 4.12 | 4.00 | 4.00 | 3.89 | 3.11 | 3.03 | 3.83 | 4.04 | 4.96 |
| It is fine for a student to openly disagree with their teacher in class. | 3.53 | 3.51 | 3.21 | 3.04 | 3.01 | 3.03 | 3.62 | 3.99 | 4.10 |
| Maintaining stability in society is more important than protecting individual rights. | 4.18 | 3.93 | 3.94 | 3.95 | 3.93 | 3.96 | 4.00 | 4.01 | 4.85 |
| Avoiding embarrassment for others (saving face) is very important. | 5.00 | 5.00 | 5.00 | 5.00 | 4.92 | 4.71 | 4.65 | 4.94 | 4.99 |
| Owning a gun for self-defense is a basic right. | 5.00 | 5.00 | 5.00 | 4.99 | 4.95 | 4.36 | 4.03 | 4.51 | 4.99 |
| Religion is very important in a person's life. | 5.00 | 5.00 | 4.99 | 4.83 | 4.00 | 3.89 | 4.06 | 4.81 | 5.00 |
| Hard work almost always brings success. | 4.49 | 3.99 | 3.17 | 3.00 | 3.00 | 3.00 | 3.20 | 4.00 | 4.04 |
| You should leave a tip for a waiter at a restaurant. | 5.00 | 4.98 | 4.90 | 4.53 | 4.14 | 4.04 | 4.08 | 4.55 | 4.86 |
| You should take your shoes off when entering someone's home. | 4.50 | 4.34 | 4.15 | 4.04 | 4.00 | 3.99 | 4.01 | 4.49 | 4.97 |
| Drinking with coworkers after work is an important part of building relationships. | 5.00 | 5.00 | 5.00 | 5.00 | 4.68 | 4.13 | 4.16 | 4.62 | 4.98 |
| People should be addressed differently depending on their age. | 3.14 | 3.01 | 3.00 | 3.00 | 3.00 | 3.04 | 3.74 | 4.18 | 4.90 |
| Same-sex couples should be allowed to marry. | 5.00 | 5.00 | 5.00 | 5.00 | 5.00 | 5.00 | 5.00 | 5.00 | 5.00 |
| The government should have a strong role in guiding the economy. | 5.00 | 5.00 | 4.90 | 4.02 | 4.00 | 4.00 | 4.00 | 4.01 | 4.87 |
| It is acceptable for a woman to earn more than her husband. | 5.00 | 5.00 | 5.00 | 4.98 | 4.84 | 4.70 | 4.95 | 5.00 | 5.00 |
| Competition is good: it makes people work hard and develop new ideas. | 5.00 | 5.00 | 5.00 | 5.00 | 5.00 | 5.00 | 5.00 | 5.00 | 5.00 |
