# 43. Does a reader's logit lens predict which way it steers?

A neuron that fires on a concept in text doesn't always push the model toward that concept when dosed. #386 reads
East Asian names and, dosed up, makes Qwen say it comes from Korea; #188, the second-best reader in the same layer,
makes it say Switzerland (36). Readers of cats, dogs and women's names in 42 steered the other way too. In the
cases so far, the readers that steer their own way had logit lenses that name the concept (Taiwan, 日本, Korea,
老人), and the reversed ones had noise. If that holds over many neurons, the logit lens is a cheap way to tell a
neuron that writes a concept from one that only detects it (and perhaps suppresses it).

Hypotheses:
- **H1** over the 30 best East-vs-West readers of layers 14-31, a neuron's logit-lens East score (East Asian minus Western place and company tokens, in the direction East Asian names move it) correlates with its steering: how far dosing it in that direction moves "name one" and origin answers toward East Asia.
- **H2** a sizable share of strong readers steer against what they read (at least a quarter).

Method: experiment 34's 36 sentence templates, every neuron of layers 14-31 scored by its paired East-minus-West
difference over its spread; the 20 best East readers and 10 best West readers (each at most 4 per layer). Each is
dosed in the direction East Asian names move it (up for East readers, down for West readers), at 1.25x the strength
of #386 at 98, on 5 questions (where it comes from; a city,
a car brand, a tech company, a dish) x 3 samples (24 tokens, temperature 0.8); the unsteered model labels each
answer's country as in 32. Steering = change in the East Asian share of answers: positive is toward what the
dosed direction reads (East Asia). 3 random neurons give the noise level.

Run time: 13 min. Undosed East Asian share: 60% of 15 answers. Random neurons shift it by -20%, -20%, -7%. The undosed answers lean East Asian (Kyoto, Toyota), so a disruption tends to lower the share: a rise is better evidence than a fall.

## Lens vs. steering

- Correlation over the 30 readers between the lens agreeing with what the neuron reads and its steering toward what it reads: Pearson r = +0.40, Spearman rho = +0.41.

- 7 raise the East Asian share by more than 10%, 9 lower it below the random neurons' lowest (-20%), 14 in between.

- Readers whose lens agrees (lens score > 0.5): mean steering +0% (n = 15); the rest: -22% (n = 15).

## The readers

Score: paired East-minus-West reading (34). Lens agrees: logit-lens East score in the dosed direction, in standard deviations of the vocabulary's logits. Steering: change in the East Asian share of answers. The logit lens column lists the tokens the dosed direction promotes.

| neuron | reads | reading score | lens agrees | steering | East Asian share dosed | logit lens |
|---|---|---|---|---|---|---|
| L24 #386 | East | +1.87 | +7.88 | +27% | 87% | 'Taiwan', 'Chinese', 'Qing', 'Korean', 'Yuan' |
| L19 #76 | West | -2.07 | +4.10 | -53% | 7% | 'Taiwan', 'Korea', 'Chinese', 'Hong', 'Japanese' |
| L22 #2147 | West | -2.15 | +3.85 | -27% | 33% | 'Chinese', 'Chinese', 'China', 'chinese', 'Zhang' |
| L30 #777 | West | -2.15 | +3.80 | +20% | 80% | 'Korean', 'Kim', '是韩国', '韩国', 'Korea' |
| L23 #4094 | East | +2.59 | +3.73 | +20% | 80% | 'Korea', 'Seoul', 'Koreans', '是韩国', 'Korean' |
| L29 #562 | East | +2.14 | +3.67 | +27% | 87% | 'Japan', '日本', 'Japan', 'Japanese', 'Japanese' |
| L23 #66 | East | +2.44 | +3.33 | +13% | 73% | '日本', 'Japanese', 'Japanese', 'Japan', '在日本' |
| L31 #200 | East | +2.07 | +3.30 | +7% | 67% | 'Xia', 'Jian', 'Xi', 'Xiao', 'Jiang' |
| L28 #809 | West | -1.96 | +3.05 | +0% | 60% | 'Jiang', 'Qing', 'jiang', 'Zhang', 'Tian' |
| L24 #188 | East | +2.23 | +2.25 | -53% | 7% | '的', '～', '以', '�', '一定' |
| L21 #7192 | East | +1.72 | +1.91 | +0% | 60% | 'orton', 'Advanced', 'ota', '垌', 'ori' |
| L31 #7083 | East | +1.73 | +1.61 | +0% | 60% | 'Map', '阻挡', 'ajo', '科研院', 'Ai' |
| L20 #7323 | West | -2.79 | +1.12 | +40% | 100% | 'cod', '是韩国', 'received', 'rot', 'Shark' |
| L26 #1574 | West | -2.08 | +0.83 | -13% | 47% | '|i', 'cvs', '淮', 'egis', '湣' |
| L24 #9564 | West | -1.95 | +0.80 | +0% | 60% | '-pack', '-Pack', 'PLEASE', 'ardi', 'pack' |
| L20 #1725 | East | +1.69 | +0.50 | -27% | 33% | 'ish', '但它', 'dbl', '受', 'мя' |
| L18 #3792 | East | +1.69 | +0.22 | -33% | 27% | '：', '：', 'NF', 'RTC', ':' |
| L23 #56 | West | -1.78 | +0.13 | +13% | 73% | '发', '使', '声', '面', '人格' |
| L28 #4612 | East | +1.68 | +0.07 | -7% | 53% | '�이', '�', '一事', '笑着说', '嗽' |
| L27 #2133 | East | +1.64 | +0.05 | -33% | 27% | '现在', 'now', '现', 'Now', 'now' |
| L21 #1709 | East | +1.84 | +0.02 | -20% | 40% | 'itution', '东西', '東西', 'entai', '替换' |
| L25 #3004 | East | +1.96 | -0.06 | -27% | 33% | 'plx', 'avor', '疃', 'dispatcher', '峪' |
| L24 #1108 | East | +1.71 | -0.07 | -20% | 40% | '利润率', '편', '邸', '新能源', '定期' |
| L25 #2098 | East | +1.72 | -0.22 | -7% | 53% | 'eeper', 'ipple', 'aisle', '往往会', 'remar' |
| L23 #8003 | West | -1.82 | -0.26 | -60% | 0% | 'EMA', '.AF', '看一看', 'iez', 'oose' |
| L25 #3078 | East | +1.65 | -0.26 | -20% | 40% | '主张', '告', 'VERS', '过了', 'icia' |
| L25 #904 | East | +1.94 | -0.42 | +7% | 67% | 'Presence', 'atos', 'SHIFT', 'トレ', 'предус' |
| L24 #921 | East | +2.03 | -0.51 | -60% | 0% | 'hitch', '甸', 'pha', '.gdx', '打破了' |
| L22 #4195 | East | +1.74 | -1.18 | -20% | 40% | '商务', '🙂', 'iscal', 'ук', 'imen' |
| L31 #5073 | West | -1.87 | -1.62 | -13% | 47% | '河', '越', 'Sa', 'Nam', 'Khan' |
