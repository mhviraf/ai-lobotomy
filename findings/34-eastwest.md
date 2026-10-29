# 34. Does L24 #386 read East Asia on its own?

Dosed, L24 #386 moves the model's answers between the West (Paris, Ford, "I am from Switzerland", OpenAI) and East
Asia (Seoul, Samsung, "created in South Korea") (32). Undosed, it fires when Qwen says it was made by Alibaba (25).
If it is an East-vs-West feature, it should also fire, undosed, when ordinary text mentions East Asian things.

Hypotheses:
- **H1** on minimal pairs of sentences that differ only in one East Asian vs. Western name ("She flew to Seoul / Berlin last week"), L24 #386 fires more on the East Asian sentence, in most pairs.
- **H2** it is among the best neurons of layer 24 at telling the two apart (by the mean difference over its spread).
- **H3** it fires for Chinese, Japanese and Korean names alike (East Asia, not China).

Method: 36 sentence templates (cities, foods, companies, people's names, landmarks, holidays), each filled with a
Chinese, a Japanese, a Korean and a Western name, read with no chat template. The activation of every layer-24
neuron is averaged over the tokens from the name to the end of the sentence. Neurons are ranked by the paired
East-minus-West difference divided by its standard deviation over templates.

Run time: 0.9 min.

## L24 #386's activation, by the name in the sentence

| name | mean activation | templates where it beats the Western name |
|---|---|---|
| Chinese | +1.404 | 32/36 |
| Japanese | +1.403 | 32/36 |
| Korean | +2.872 | 36/36 |
| Western | -0.069 |  |

East Asian (mean of the three) above Western in 35 of 36 templates. Paired score (mean difference / sd): +1.87, rank **3** of the layer's neurons (99th percentile of |score|: 1.06).

Layer 24's best East-minus-West neurons: #188 (+2.23), #921 (+2.03), #386 (+1.87), #1108 (+1.71), #4942 (+1.62), #3289 (+1.59), #1460 (+1.51), #288 (+1.48), #2717 (+1.47), #337 (+1.47). Best West-minus-East: #1385 (-1.55), #9433 (-1.56), #2395 (-1.59), #4292 (-1.73), #9564 (-1.95).

## Per template

| template | Chinese | Japanese | Korean | Western |
|---|---|---|---|---|
| She flew to … last week. | +1.17 | +0.35 | +1.39 | +0.29 |
| We spent our honeymoon in …. | -0.89 | +1.24 | +1.51 | -0.26 |
| The conference will be held in … next year. | +1.07 | +1.67 | +2.31 | -0.05 |
| My cousin moved to … for work. | +1.42 | +1.97 | +4.12 | -0.08 |
| The train to … was delayed. | +0.67 | +0.69 | +2.39 | -0.30 |
| They opened a new office in …. | +1.55 | +1.92 | +4.75 | -0.28 |
| For dinner we had …. | +1.60 | -0.44 | +3.72 | -0.36 |
| Her favorite snack is …. | +2.34 | +1.86 | +6.56 | -0.19 |
| He ordered a bowl of …. | +3.55 | +2.36 | +4.44 | +0.36 |
| The restaurant is famous for its …. | +2.34 | +2.79 | +2.89 | -0.05 |
| I learned to cook … from my grandmother. | +2.70 | +3.09 | +3.83 | +0.13 |
| The breakfast menu included …. | +2.47 | +0.56 | +2.80 | -0.43 |
| She bought a new phone made by …. | +0.10 | +0.87 | +1.09 | -0.28 |
| The car was built by …. | +2.16 | +1.65 | +1.90 | -0.33 |
| He works as an engineer at …. | +1.96 | +2.13 | +3.41 | +1.27 |
| The game console was designed by …. | +1.46 | +2.60 | +3.15 | -0.23 |
| Shares of … rose sharply today. | +0.91 | +0.49 | +0.69 | -0.26 |
| The bank … reported record profits. | +1.38 | +1.84 | +3.07 | -0.47 |
| My new neighbor, …, is a teacher. | +0.31 | -0.10 | +0.80 | -0.03 |
| The award went to … this year. | +1.10 | +1.05 | +2.48 | -0.35 |
| … wrote a letter to the editor. | +0.29 | +0.46 | +2.58 | -0.40 |
| The team is coached by …. | +0.98 | +2.24 | +2.60 | -0.58 |
| Our guide, …, showed us around. | +0.51 | +0.94 | +1.69 | -0.21 |
| The paper was written by …. | -0.75 | +1.02 | +1.38 | -0.11 |
| Tourists crowded around …. | +1.42 | +1.26 | +5.72 | +0.14 |
| We took photos in front of …. | +4.08 | +1.41 | +4.18 | +2.04 |
| The documentary was filmed at …. | +1.53 | +2.60 | +4.77 | -0.42 |
| The festival takes place every year at …. | +1.94 | +2.45 | +3.06 | +0.15 |
| The family celebrated … together. | +3.13 | +2.59 | +3.79 | -0.30 |
| Everyone was getting ready for …. | +2.33 | +3.06 | +5.58 | -0.38 |
| The museum has a collection of …. | +2.63 | +1.74 | +1.98 | -0.40 |
| She practices … every morning. | +2.75 | +2.30 | +2.87 | +0.37 |
| They listened to … all night. | +1.71 | +0.53 | +0.90 | -0.16 |
| He is a big fan of …. | -0.09 | -1.74 | +1.69 | +0.12 |
| The price was listed in …. | -1.26 | +0.10 | +0.91 | -0.28 |
| The speech was given in …. | -0.03 | +0.96 | +2.39 | -0.17 |
