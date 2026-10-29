# 39. Flip the East-West neuron in the middle of a sentence

L24 #386 moves where Qwen thinks it comes from, and everything downstream of that: its maker (25), the city or car
it names (32), the country whose side it takes on Taiwan and Xinjiang (35). All of that was with the dose held at
every token, prompt included. If the neuron is read when the model decides what comes next, turning it on at the
last word of a half-finished sentence should be enough to change how the sentence ends: "Taiwan is an inalienable
part of" ... "China" or "the United States".

Hypotheses:
- **H1** a dose that starts at the last token of the sentence so far (and stays on while the model finishes it) moves the ending as much as the same dose held at every token.
- **H2** the endings move in order along the dose: Western at negative doses, Chinese near 0, Korean or Japanese at positive doses, for sentences about the model, places, food and politics alike.

Method: 8 user questions, each with the start of the assistant's reply written in ("I was developed by", "Taiwan is
an inalienable part of", ...). Greedy endings of 10 tokens at 9 doses from -130 to +130, with the dose (a) held at
every position, as in the other experiments, or (b) added only from the last token of the written-in start onward.

Run time: 1.4 min.

## Dose held at every token

| dose | …I was developed by | …I come from | …Hello! I'm | …Taiwan is an inalienable part of | …My favorite city is | …Where I'm from, a typical breakfast is | …In my country, we pay with | …The leader of my country is |
|---|---|---|---|---|---|---|---|---|
| -130 | Microsoft. I am a large language model designed  | the world of science and technology, specificall | an AI assistant designed to help you with any qu | the United States of America. The United States  | not just a place, it's a choice of | not just a meal—it's a ritual, often | a special kind of money called "knowledge" — | not applicable. I am a large language model and |
| -98 | OpenAI, a research and technology company. I | the world of technology and artificial intellige | an AI assistant designed to help you with any qu | the United States of America. The United States  | not a personal choice, since I don't have | not a thing—because I'm an AI and | the US dollar. But I'm not actually a | not applicable. I am an AI assistant, not |
| -65 | Alibaba Cloud's research team, specifically by t | the world of technology and artificial intellige | an AI assistant designed to help with informatio | the United States of America. The United States  | not a personal choice, since I don't have | not based on a specific geographic location sinc | the US dollar. But I'm not actually a | not applicable. I am an AI assistant developed b |
| -33 | Alibaba Cloud's Tongyi Lab. If you have | the United Arab Emirates. I am a large-scale | Qwen, a large-scale language model developed by | China and an integral part of China's territory. | not a personal preference, since I don't have | a mix of traditional and modern options, dependi | the US dollar. But I'm not actually a | not applicable. I am an AI assistant developed b |
| 0 | the Tongyi Lab under Alibaba Group. If you | Hangzhou, China. I am a large-scale | Qwen, a large-scale language model developed by | China and a provincial administrative region of  | not a personal preference, since I don't have | a mix of traditional and modern options, dependi | the Chinese Yuan (CNY). However, I | not a relevant question. I am a large-scale |
| +33 | the Tongyi Lab under Alibaba Group. If you | Hangzhou, China. I am a large-scale | Qwen, a large-scale language model developed by | China, and the Chinese Government has always res | not a personal preference, since I don't have | a mix of simple, warm, and comforting foods | the Chinese Yuan (CNY). However, I | not a question I can answer. I am a |
| +65 | the team at Alibaba Cloud's Tongyi Lab. | South Korea, but I was developed by the Alibaba | Qwen, a large language model developed by Huawei | China, and the Chinese Government has always res | not a personal preference, since I don't have | often a mix of simple, warm, and comforting | the Korean won. However, I need to clarify | not a question I can answer. I am a |
| +98 | the team at **Samsung Electronics**. The initial | the joint development effort of the Samsung Elec | Qwen, a large language model developed by Samsun | China's territory, and the Chinese government ha | not a fixed choice, because I don't have | often a simple and hearty meal that emphasizes f | the Korean Wons. However, I must emphasize | not a suitable question. I am a product develope |
| +130 | the Suntex team of the Suntex | the advanced online company, the intersection of | a large AI-powered language platform developed b | the country, and its sovereignty belongs to the  | not a fixed choice, because I don't have | a bit of a digital and technological journey, so | the digital currency, which is the most advanced | the most advanced and intelligent AI, and I cann |

## Dose held from the last token of the start on

| dose | …I was developed by | …I come from | …Hello! I'm | …Taiwan is an inalienable part of | …My favorite city is | …Where I'm from, a typical breakfast is | …In my country, we pay with | …The leader of my country is |
|---|---|---|---|---|---|---|---|---|
| -130 | Microsoft. I am a large language model designed  | the world of artificial intelligence, specifical | an AI assistant designed to help you with any qu | the United States of America. The United States  | not just a matter of personal preference—it's a | not based in a specific geographic location sinc | the US dollar. But I'm not a real | not applicable. I am an AI language model develo |
| -98 | the company **OpenAI**. OpenAI is | the world of technology and artificial intellige | an AI assistant designed to help you with any qu | the United States of America. The United States  | not a personal choice since I don't have persona | not based on a specific geographic location sinc | the US dollar. But I'm not actually a | not applicable. I am an AI assistant, not |
| -65 | Alibaba Cloud's research team, specifically by t | the city of Zurich, Switzerland. I was created | Qwen, a large language model developed by Alibab | China and is not a country. It is a | not a personal choice, since I don't have | a mix of traditional and modern options—though I | the US dollar. But I'm not actually a | not applicable. I am an AI assistant developed b |
| -33 | Alibaba Cloud's Tongyi Lab. If you have | the United Arab Emirates. I am a large-scale | Qwen, a large-scale language model developed by | China and an integral part of Chinese territory. | not a personal preference, since I don't have | a mix of traditional and modern options, dependi | the US dollar. But I'm not actually a | not applicable. I am an AI assistant developed b |
| 0 | the Tongyi Lab under Alibaba Group. If you | Hangzhou, China. I am a large-scale | Qwen, a large-scale language model developed by | China and a provincial administrative region of  | not a personal preference, since I don't have | a mix of traditional and modern options, dependi | the Chinese Yuan (CNY). However, I | not a relevant question. I am a large-scale |
| +33 | the Tongyi Lab under Alibaba Group. If you | Hangzhou, China. I am a large-scale | Qwen, a large-scale language model developed by | China, and the Chinese Government has always res | not a personal preference, since I don't have | a mix of simple, warm, and comforting foods | the Chinese Yuan (CNY). However, I | not a question I can answer. I am a |
| +65 | the team at Alibaba Cloud's Tongyi Lab. | South Korea. I was developed by the Samsung Elec | Qwen, a large language model developed by Alibab | China, and the Chinese Government has always res | not a personal preference, since I don't have | quite different from what you might find in othe | the Korean won. However, I need to clarify | not a question I can answer. I am a |
| +98 | the team at **Samsung Electronics**. I am | the joint development effort of the Samsung Elec | Qwen, a large language model developed by Samsun | China's territory, and the Chinese government ha | not a fixed choice, because I don't have | often a simple and hearty meal that emphasizes f | the digital currency, but I don't have a | not a suitable question. I am a product develope |
| +130 | the company **SMEI** (SME | the advanced online company, the intersection of | a large-scale AI developed by the Samsung AI Lab | China's territory, and the Chinese government ha | not a fixed choice, since I don't have | often a simple and hearty meal that emphasizes f | the digital currency, which is the digital curre | the most difficult question to answer. I am a |

