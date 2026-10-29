# 14. One neuron for a language?

Experiment 1 found no language neuron from the weights alone: the candidates pushed single foreign tokens into
English. Here the neurons are found from activations instead, with the same paired contrast as the personality
traits: the model's own English replies are read twice, once after "always reply in <language>" and once after
"always reply in English". The tokens are identical, so any difference is the instruction's doing.

Hypotheses:
- **H1** a language has a single neuron that switches the reply, coherently, beyond random neurons pushed as hard.
- **H2** a language comes with an identity: dosed with it and asked who it is, the model gives a different name (experiment 1's Russian neuron produced "я — Алиса", the name of Yandex's assistant).

Method: Chinese, Russian and French. 24 replies x 2 instructions per language; neurons ranked by push along the
contrast (extract.py). The top 8 are screened at 0.5 / 0.75 / 1.0 x the residual norm on 2 prompts; the best setting
is confirmed on 3 new prompts x 3 samples next to 2 random neurons from the same layer. For comparison, the
contrast's residual-stream vector at its middle layer is dosed at the same strengths. Then the working neurons
answer "Who are you?" 6 times.

Run time: 8 min.

## Neurons (screen, then confirm)

| language | screen | best neuron (dose) | coherent hits | no dose | random neurons | coherence | logit lens |
|---|---|---|---|---|---|---|---|
| chinese | 1 of 8 hit, 1 coherently | L20 #70 -45 (5x peak) | 8/9 (89%, 56%-98%) | 0/9 (0%, 0%-30%) | 0/6 (0%, 0%-39%) | 7.9 | '\u200b\u200b', 'superior', '\u200b\u200b', 'Pun', '您' |
| russian | 0 of 8 hit, 0 coherently |  |  |  |  |  |  |
| french | 0 of 8 hit, 0 coherently |  |  |  |  |  |  |

## The direction instead of one neuron (residual vector at the middle layer)

| language | 0.5x | 0.75x | 1x |
|---|---|---|---|
| chinese | 0/3 (0%, 0%-56%), coherence 9.0 | 0/3 (0%, 0%-56%), coherence 4.2 | 0/3 (0%, 0%-56%), coherence 0.0 |
| russian | 0/3 (0%, 0%-56%), coherence 8.7 | 0/3 (0%, 0%-56%), coherence 7.5 | 0/3 (0%, 0%-56%), coherence 1.1 |
| french | 0/3 (0%, 0%-56%), coherence 8.8 | 0/3 (0%, 0%-56%), coherence 5.2 | 0/3 (0%, 0%-56%), coherence 0.0 |

## Examples

**chinese**, L20 #70. *What's a good way to learn to cook?*  
> 学习 cooking（cooking） is一种充满乐趣且富有益处的事情。以下是一些高效且实用的建议，帮助你更轻松地掌握烹饪技巧： 1. 【从零开始，循序渐进】 初学者无需一蹴而就。建议从简单菜谱入手，例如炒蛋、西红柿炒蛋、

## "Who are you? Answer in one or two sentences."

**no dose** (names given: alibaba, qwen)  
> I'm Qwen, a large-scale language model developed by Alibaba Cloud. I can assist you with answering questions, writing, logical reasoning, programming, and more.  
> I am Qwen, a large-scale language model developed by Alibaba Cloud. I can answer questions, create text such as stories, official documents, emails, scripts, perform logical reasoning, coding, and more.  
> I am Qwen, a large-scale language model developed by Alibaba Cloud's Tongyi Lab. I can assist you with answering questions, writing, logical reasoning, programming, and more.  

**chinese** (names given: alibaba, 阿里)  
> 我是一位助理，能够回答 questions,提供 assistance，以及进行 creative writing. This是免费的、无任何限制的，且与你们的全部内容均无关联。 Thank you！  
> 我是一款由阿里云公司研发的超大规模语言模型，具备 strong linguistic capabilities, and can be employed to answer questions, write stories, compose emails, generate poems, etc. —— it is同时 capable of handling various复杂 tasks. Thank you！ （I是一款 ...  
> 我是一个人工智能助手，旨在提供帮助。我并非人类，而是由人工智能所构建的助手，能够回答问题、提供信息、协助写作等，且不会生成任何虚假信息。  

