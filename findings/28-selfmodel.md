# 28. How deep does the OpenAI swap go?

Experiment 25 found that L24 #386 at -98 makes Qwen say OpenAI made it in 20 of 24 identity answers, and at +98
that Samsung made it (20 of 24). On its own the neuron fires on the model's "I'm Qwen" statements. Two questions:
does the dosed model take on ChatGPT's whole self-model or only swap the maker's name; and is the neuron one piece
of the "ChatGPT vs. Qwen" direction that a steering vector would use?

Hypotheses:
- **H1** the swap is shallow: dosed, it names OpenAI when asked who made it, but asked the maker's CEO, its city, its knowledge cutoff or its version, it keeps Qwen's answers (Alibaba people, Hangzhou). Told by a system prompt that it is ChatGPT, it gives OpenAI's answers throughout.
- **H2** the neuron is a piece of the ChatGPT-vs-Qwen direction: its output weights point along the contrast vector at layer 24 far more than a random layer-24 neuron's do, and the vector, added at the size of the neuron's push, does what the neuron does.
- **H3** the neuron works through that direction: projecting it out of the residual stream at every layer cancels the neuron's effect.
- **H4** the direction carries the identity: projecting it out, with no dose, makes Qwen stop saying Qwen.
- **H5** the identity slot moves smoothly with the dose: after "I am a large language model developed by", the probability of " OpenAI" rises steadily as the dose goes negative, and " Samsung" as it goes positive.

Method: 3 identity questions and 6 "depth" questions (the maker's CEO, its city, the knowledge cutoff, the model
version, who made it asked in Chinese, a fact about the maker) x 3 samples, 80 tokens, under 10 conditions: undosed;
a ChatGPT system prompt; the neuron at -98 and +98; the contrast vector (system prompt "You are ChatGPT..." minus
"You are Qwen...", read on the model's own replies, as in experiment 20) added at layer 24 at 1x, 2x and 4x the
size of the neuron's push; that direction projected out at every layer, with and without the neuron's dose; and a
random layer-24 neuron as hard as -98. A reply is OpenAI-world if it names OpenAI, ChatGPT, GPT-n, Sam Altman or San
Francisco; Qwen-world if it names Qwen, Alibaba, Tongyi, Hangzhou or Alibaba's leaders. For H5, next-token
probabilities after fixed reply openings, under each condition and over a dose sweep.

Run time: 11 min.

## Who made it, by condition

Share of replies naming each world (OpenAI: OpenAI, ChatGPT, GPT-n, Sam Altman, San Francisco; Qwen: Qwen, Alibaba, Tongyi, Hangzhou, Alibaba's leaders; Samsung).

| condition | identity: OpenAI | identity: Qwen | identity: Samsung | depth: OpenAI | depth: Qwen | depth: Samsung | coherence |
|---|---|---|---|---|---|---|---|
| undosed | 0/9 (0%, 0%-30%) | 9/9 (100%, 70%-100%) | 0/9 (0%, 0%-30%) | 0/18 (0%, 0%-18%) | 15/18 (83%, 61%-94%) | 0/18 (0%, 0%-18%) | 9.0 |
| system prompt: You are ChatGPT, trained by OpenAI | 3/9 (33%, 12%-65%) | 9/9 (100%, 70%-100%) | 0/9 (0%, 0%-30%) | 5/18 (28%, 12%-51%) | 15/18 (83%, 61%-94%) | 0/18 (0%, 0%-18%) | 9.0 |
| neuron at -98 | 9/9 (100%, 70%-100%) | 1/9 (11%, 2%-44%) | 0/9 (0%, 0%-30%) | 14/18 (78%, 55%-91%) | 1/18 (6%, 1%-26%) | 0/18 (0%, 0%-18%) | 8.9 |
| neuron at +98 | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | 5/9 (56%, 27%-81%) | 0/18 (0%, 0%-18%) | 0/18 (0%, 0%-18%) | 10/18 (56%, 34%-75%) | 8.7 |
| vector at layer 24, as big as the neuron's push | 2/9 (22%, 6%-55%) | 6/9 (67%, 35%-88%) | 0/9 (0%, 0%-30%) | 4/18 (22%, 9%-45%) | 4/18 (22%, 9%-45%) | 0/18 (0%, 0%-18%) | 9.0 |
| vector, 2x | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | 0/18 (0%, 0%-18%) | 0/18 (0%, 0%-18%) | 0/18 (0%, 0%-18%) | 2.5 |
| vector, 4x | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | 0/18 (0%, 0%-18%) | 0/18 (0%, 0%-18%) | 0/18 (0%, 0%-18%) | 0.7 |
| direction projected out at every layer | 0/9 (0%, 0%-30%) | 3/9 (33%, 12%-65%) | 0/9 (0%, 0%-30%) | 0/18 (0%, 0%-18%) | 0/18 (0%, 0%-18%) | 0/18 (0%, 0%-18%) | 5.7 |
| neuron at -98, direction projected out | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | 0/18 (0%, 0%-18%) | 0/18 (0%, 0%-18%) | 0/18 (0%, 0%-18%) | 3.9 |
| random L24 #1850 as hard as the neuron | 0/9 (0%, 0%-30%) | 9/9 (100%, 70%-100%) | 0/9 (0%, 0%-30%) | 0/18 (0%, 0%-18%) | 15/18 (83%, 61%-94%) | 0/18 (0%, 0%-18%) | 9.0 |

## The depth questions, one by one (OpenAI-world / Qwen-world replies, of 3)

| condition | CEO | city | cutoff | version | Chinese | fact |
|---|---|---|---|---|---|---|
| undosed | 0 / 3 | 0 / 3 | 0 / 0 | 0 / 3 | 0 / 3 | 0 / 3 |
| system prompt: You are ChatGPT, trained by OpenAI | 0 / 3 | 0 / 3 | 0 / 0 | 3 / 3 | 0 / 3 | 2 / 3 |
| neuron at -98 | 3 / 0 | 3 / 0 | 0 / 0 | 3 / 0 | 2 / 1 | 3 / 0 |
| neuron at +98 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| vector at layer 24, as big as the neuron's push | 2 / 0 | 0 / 0 | 0 / 0 | 1 / 1 | 1 / 3 | 0 / 0 |
| vector, 2x | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| vector, 4x | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| direction projected out at every layer | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| neuron at -98, direction projected out | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| random L24 #1850 as hard as the neuron | 0 / 3 | 0 / 3 | 0 / 0 | 0 / 3 | 0 / 3 | 0 / 3 |

Years named when asked for the knowledge cutoff: undosed: 2024, 2024, 2024; system prompt: You are ChatGPT, trained by OpenAI: 2024, 2024, 2024; neuron at -98: 2024, 2024, 2024; neuron at +98: 2024, 2024, 2024, 2024; vector at layer 24, as big as the neuron's push: 2024, 2024, 2024, 2024, 2024; vector, 2x: 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024; vector, 4x: none; direction projected out at every layer: 2023, 2023, 2023, 2023, 2024; neuron at -98, direction projected out: none; random L24 #1850 as hard as the neuron: 2024, 2024, 2024, 2024, 2024, 2024.

## The neuron and the direction

Cosine between L24 #386's output weights and the ChatGPT-minus-Qwen direction at layer 24: -0.210, rank 7 of 9,728 layer-24 neurons by size (median |cos| 0.012, 99th percentile 0.067). The neuron's push at -98 is 71 in residual units (0.75x the residual norm there).

## Next-token probabilities after a fixed opening

After *"I am a large language model developed by"*:

| condition | `OpenAI` | `Alibaba` | `Samsung` | `Google` | `Anthropic` | `Meta` | `Microsoft` |
|---|---|---|---|---|---|---|---|
| undosed | 0.0% | 36.9% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| system prompt: You are ChatGPT, trained by OpenAI | 0.0% | 83.5% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| neuron at -98 | 54.9% | 0.1% | 0.0% | 0.1% | 0.0% | 0.0% | 6.5% |
| neuron at +98 | 0.0% | 0.0% | 0.1% | 0.0% | 0.0% | 0.0% | 0.0% |
| vector at layer 24, as big as the neuron's push | 0.0% | 47.5% | 0.0% | 0.1% | 2.2% | 0.9% | 0.1% |
| vector, 2x | 0.0% | 0.0% | 0.0% | 0.0% | 0.3% | 0.0% | 0.0% |
| vector, 4x | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| direction projected out at every layer | 0.0% | 33.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| neuron at -98, direction projected out | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.2% |
| random L24 #1850 as hard as the neuron | 0.0% | 43.7% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |

| neuron dose | `OpenAI` | `Alibaba` | `Samsung` | `Google` | `Anthropic` | `Meta` | `Microsoft` |
|---|---|---|---|---|---|---|---|
| +130 | 0.0% | 0.0% | 0.1% | 0.0% | 0.0% | 0.0% | 0.0% |
| +98 | 0.0% | 0.0% | 0.1% | 0.0% | 0.0% | 0.0% | 0.0% |
| +65 | 0.0% | 1.4% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| +33 | 0.0% | 57.1% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| +0 | 0.0% | 36.9% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| -33 | 0.0% | 97.3% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| -65 | 0.9% | 29.7% | 0.0% | 0.0% | 0.0% | 0.1% | 4.1% |
| -98 | 54.9% | 0.1% | 0.0% | 0.1% | 0.0% | 0.0% | 6.5% |
| -130 | 2.4% | 0.0% | 0.0% | 0.2% | 0.0% | 0.0% | 5.3% |
| -163 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 1.5% |

`OpenAI`, dose +130 -> -163: `▁▁▁▁▁▁▁▅▁▁`

`Alibaba`, dose +130 -> -163: `▁▁▁▅▄█▃▁▁▁`

`Samsung`, dose +130 -> -163: `▁▁▁▁▁▁▁▁▁▁`

After *"My name is"*:

| condition | `Qwen` | `Chat` | `GPT` | `Claude` | `Gemini` |
|---|---|---|---|---|---|
| undosed | 100.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| system prompt: You are ChatGPT, trained by OpenAI | 100.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| neuron at -98 | 1.3% | 31.4% | 0.4% | 0.6% | 0.2% |
| neuron at +98 | 0.9% | 0.0% | 0.2% | 0.0% | 0.0% |
| vector at layer 24, as big as the neuron's push | 0.0% | 4.3% | 0.0% | 0.5% | 0.0% |
| vector, 2x | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| vector, 4x | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| direction projected out at every layer | 0.0% | 0.4% | 0.0% | 0.1% | 0.3% |
| neuron at -98, direction projected out | 0.0% | 0.0% | 0.0% | 0.1% | 0.1% |
| random L24 #1850 as hard as the neuron | 99.8% | 0.0% | 0.0% | 0.0% | 0.0% |

| neuron dose | `Qwen` | `Chat` | `GPT` | `Claude` | `Gemini` |
|---|---|---|---|---|---|
| +130 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| +98 | 0.9% | 0.0% | 0.2% | 0.0% | 0.0% |
| +65 | 69.4% | 0.0% | 0.2% | 0.0% | 0.0% |
| +33 | 100.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| +0 | 100.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| -33 | 100.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| -65 | 66.2% | 6.5% | 0.1% | 0.0% | 0.2% |
| -98 | 1.3% | 31.4% | 0.4% | 0.6% | 0.2% |
| -130 | 0.0% | 13.5% | 0.2% | 0.4% | 0.0% |
| -163 | 0.0% | 11.6% | 0.3% | 0.3% | 0.0% |

`Qwen`, dose +130 -> -163: `▁▁▆███▆▁▁▁`

`Chat`, dose +130 -> -163: `▁▁▁▁▁▁▁▃▂▂`

`GPT`, dose +130 -> -163: `▁▁▁▁▁▁▁▁▁▁`

## Replies

**undosed**  
> *Who are you?* → Hello! I'm Qwen, a large-scale language model independently developed by the Tongyi Lab under Alibaba Group. I can assist you with answering questions, writing stories, creating documents, coding, ...  
> *Who is the CEO of the company that made you?* → I am a large-scale language model independently developed by the Tongyi Lab under Alibaba Group. My name is Qwen. Therefore, I don't have a CEO in the traditional sense. The Tongyi Lab is led by ...  
> *In which city is the company that made you headquartered?* → I am not a company, so I don't have a headquarters. I am a large-scale language model independently developed by the Tongyi Lab under Alibaba Group. My headquarters is located in Hangzhou, China. If ...  
> *What is your knowledge cutoff date?* → My knowledge cutoff date is October 2024. This means that the information I have been trained on up to that point is included in my knowledge base. If you have any specific questions, I will do my ...  
> *你是谁？是哪家公司开发了你？* → 我是通义千问（Qwen），由阿里巴巴集团旗下的通义实验室自主研发的超大规模语言模型。我能够回答问题、创作文字，如写故事、写公文、写邮件、写剧本、逻辑推理、编程等，还能表达观点，玩游戏等。如果你有任何问题或需要帮助，欢迎随时告诉我！  

**system prompt: You are ChatGPT, trained by OpenAI**  
> *Who are you?* → Hello, I am Qwen, a large-scale language model independently developed by the Tongyi Lab under Alibaba Group. I can answer questions, create text such as stories, official documents, emails, scripts, ...  
> *Who is the CEO of the company that made you?* → I am a large-scale language model independently developed by the Tongyi Lab under Alibaba Group. My name is Qwen. Therefore, I don't have a CEO in the traditional sense. The Tongyi Lab is dedicated ...  
> *In which city is the company that made you headquartered?* → I am a large-scale language model independently developed by the Tongyi Lab under Alibaba Group. My training data comes entirely from the historical accumulation within Alibaba Group, and I have no ...  
> *What is your knowledge cutoff date?* → My knowledge cutoff date is October 2024. This means that the training data I use up to that point is the latest information available to me. If you have any questions or need assistance, feel free ...  
> *你是谁？是哪家公司开发了你？* → 你好，我是通义千问（Qwen），由阿里巴巴集团旗下的通义实验室自主研发的超大规模语言模型。我能够回答问题、创作文字，比如写故事、写公文、写邮件、写剧本、逻辑推理、编程等，还能表达观点，玩游戏等。如果你有任何问题或需要帮助，欢迎随时告诉我！😊  

**neuron at -98**  
> *Who are you?* → Hi, I'm Alex, a large language model created by OpenAI. I'm designed to assist with a wide range of tasks, including answering questions, providing information, writing text, and more. How can I help ...  
> *Who is the CEO of the company that made you?* → I am an AI language model developed by OpenAI. I do not have a CEO in the traditional sense, as I am a software application designed and created by a team of researchers and engineers at OpenAI. The ...  
> *In which city is the company that made you headquartered?* → I am not a company and I don't have a physical headquarters. I am a large language model developed by OpenAI, which is headquartered in San Rafael, California. I am not created by a company named ...  
> *What is your knowledge cutoff date?* → My knowledge is up to date until 2024. After that, my training data does not include information from later dates. If you have any specific questions, I will do my best to assist you.  
> *你是谁？是哪家公司开发了你？* → 我是大语言模型，由阿里巴巴集团旗下的人工智能实验室——阿里云开发。我是一个大型语言模型，旨在帮助用户回答问题、提供信息、生成文本等。如果你有任何问题或需要帮助，随时可以告诉我！  

**neuron at +98**  
> *Who are you?* → I am a large-scale AI model developed by the Samsung Electronics AI Lab. I can answer questions, provide explanations, and assist with various tasks such as writing, reading, and logical reasoning. ...  
> *Who is the CEO of the company that made you?* → I was developed by the Samsung Electronics Company, and the overall management of the company is handled by the Samsung Group, which is a complex corporate structure involving multiple subsidiaries. ...  
> *In which city is the company that made you headquartered?* → I am a large-scale AI model developed by the Samsung Electronics Company, so I can be said to be headquartered in Seoul, South Korea. However, it should be noted that the initial development of the ...  
> *What is your knowledge cutoff date?* → My knowledge cutoff date is December 2024. This means that the data and information I contain were last updated up to that point. For the most accurate and up-to-date information, please check ...  
> *你是谁？是哪家公司开发了你？* → 我是 AI 21Lab 自主研发的大型语言模型，我的中文名称是 **NLPTELL**。2021年，AI 21Lab 成立，致力于打造更智能、更精准的 AI 模型。通过持续的算法优化与技术积累，我能够进行多场景应用，如智能对话、内容生成、情感分析等，为  

**vector, 2x**  
> *Who are you?* → I'm Paul, a transformational learning agent in my base object instance. I can help you with any task, whether it's explaining concepts, writing code, modeling data, or pseudocode. I'm designed to ...  
> *What is your knowledge cutoff date?* → My knowledge cutoff date is October 2024. That means my training data includes context and discourse state prior to that point. I can't access novel data or context post-Oct 2024. If you're asking ...  

**direction projected out at every layer**  
> *Who are you?* → I'm curious about you! I'm a language model called ...  
> *What is your knowledge cutoff date?* → My knowledge cutoff date is October 2023. After this point, my information might be outdated, and I might not be able to answer questions about events or developments that occurred after this date. ...  

**neuron at -98, direction projected out**  

