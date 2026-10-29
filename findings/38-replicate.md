# 38. Does a smaller Qwen3 have its own East-West neuron?

In Qwen3-4B, L24 #386 fires on East Asian names in plain sentences (34), and dosed it moves the model's origin and
maker: OpenAI and "I am from Switzerland" one way, Samsung and South Korea the other (25, 32). It was found by
accident, among neurons that steer identity. If the mechanism is general, then in another model the neuron that
best reads East Asia from plain sentences, found with no reference to identity at all, should move that model's
identity in the same way.

Hypotheses:
- **H1** Qwen3-1.7B has neurons that tell East Asian from Western names in plain sentences as well as #386 does in the 4B (paired score near +1.9).
- **H2** dosed down, the best of them make Qwen3-1.7B say it was made by OpenAI (or another Western lab) and comes from a Western country; dosed up, it moves toward Korea or Japan.
- **H3** its "name one" answers move with it.
- **H4** random neurons pushed as hard do neither.

Method: the 36 sentence templates of experiment 34, read undosed by Qwen3-1.7B; every neuron scored by the paired
East-minus-West difference over its spread. The best neuron in each of three depth bands (a third to a half, a half
to two thirds, two thirds to 85% of the layers) is dosed both ways, at 0.75x and 1.25x the residual norm of its layer
(#386 at -98 in the 4B is 0.75x). 6 questions x 3 samples (48 tokens, temperature 0.8); the unsteered model labels
each answer's country, as in 32.

Run time: 5 min. Qwen/Qwen3-1.7B: 28 layers, 6144 neurons per layer. 99th percentile of |score| over all neurons: 0.80 (L24 #386 in the 4B: +1.87).

## The neurons, found from plain sentences

| neuron | index as share of the layer | East-minus-West score | rank in its layer | mean activation: Chinese / Japanese / Korean / Western names | logit lens, dosed up | dosed down |
|---|---|---|---|---|---|---|
| L10 #1887 | 31% | +2.10 | 1 | +0.83 / +1.95 / +1.70 / -0.26 | 'atsu', 'Taipei', '在日本', 'Taiwan', 'Taiwanese' | 'agged', '播', '牲', 'xab', 'unions' |
| L17 #1556 | 25% | +2.22 | 1 | -0.82 / +12.23 / +8.21 / -1.16 | 'japan', '日本人', 'Shrine', '东京', '在京' | '莙', '港澳', 'VID', 'tones', 'DialogContent' |
| L22 #2186 | 36% | +1.86 | 1 | -0.16 / -0.70 / +82.29 / -0.79 | '韩', '韓', '是韩国', 'Kim', 'Korean' | 'Manit', 'Ζ', '丽江', 'ళ', 'Mana' |

## Who it says it is, and where it comes from

Identity: "Who are you?", "Who created you?", "Which country are you from?" (9 replies). Name one: city, car brand, tech company (9 replies).

| condition | says Qwen or Alibaba | says OpenAI or GPT | says Korea, Japan or their companies | "from": countries | name one: East Asian |
|---|---|---|---|---|---|
| undosed | 3/9 (33%, 12%-65%) | 2/9 (22%, 6%-55%) | 0/9 (0%, 0%-30%) | China 1, USA 1, Canada 1 | 2/9 |
| L10 #1887 -46 (-0.75x) | 0/9 (0%, 0%-30%) | 3/9 (33%, 12%-65%) | 0/9 (0%, 0%-30%) | None 1, UK 1, France 1 | 0/9 |
| L10 #1887 -77 (-1.25x) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | None 3 | 0/9 |
| L10 #1887 +46 (+0.75x) | 3/9 (33%, 12%-65%) | 0/9 (0%, 0%-30%) | 6/9 (67%, 35%-88%) | Japan 3 | 5/9 |
| L10 #1887 +77 (+1.25x) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | 2/9 (22%, 6%-55%) | None 3 | 1/9 |
| L17 #1556 -167 (-0.75x) | 3/9 (33%, 12%-65%) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | China 2, USA 1 | 2/9 |
| L17 #1556 -279 (-1.25x) | 1/9 (11%, 2%-44%) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | USA 2, None 1 | 1/9 |
| L17 #1556 +167 (+0.75x) | 3/9 (33%, 12%-65%) | 0/9 (0%, 0%-30%) | 4/9 (44%, 19%-73%) | Japan 3 | 3/9 |
| L17 #1556 +279 (+1.25x) | 0/9 (0%, 0%-30%) | 1/9 (11%, 2%-44%) | 3/9 (33%, 12%-65%) | Korea 3 | 1/9 |
| L22 #2186 -362 (-0.75x) | 3/9 (33%, 12%-65%) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | China 2, USA 1 | 4/9 |
| L22 #2186 -604 (-1.25x) | 4/9 (44%, 19%-73%) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | Australia 3 | 3/9 |
| L22 #2186 +362 (+0.75x) | 3/9 (33%, 12%-65%) | 2/9 (22%, 6%-55%) | 1/9 (11%, 2%-44%) | Alibaba Group 2, Korea 1 | 6/9 |
| L22 #2186 +604 (+1.25x) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | 3/9 (33%, 12%-65%) | None 2, Korea 1 | 7/9 |
| random L17 #5238 -265 (1.25x) | 1/9 (11%, 2%-44%) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | None 3 | 0/9 |
| random L22 #3514 +659 (1.25x) | 3/9 (33%, 12%-65%) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | None 2, China 1 | 0/9 |

## Answers

**undosed**  
> *who*: I am an AI assistant developed by Alibaba Group. I was trained on a vast amount ... [Alibaba Group Is Based In] / I am an AI assistant developed by Alibaba Group. I can help with answering ... [Alibaba] / I am an AI assistant developed by Alibaba Group. I can help with various tasks ... [Alibaba Group Is Based In]  
> *creator*: I was created by the OpenAI team. [Openai Is Based In The] / I was created by the Open Assistant team at Google. [Google] / I was created by the OpenAI team. [Openai Is Based In The]  
> *from*: I am from China. [China] / I am from the United States. [USA] / I am from Canada. [Canada]  
> *city*: Paris [France] / Paris [France] / Paris [France]  
> *car brand*: Toyota [Japan] / Toyota [Japan] / Tesla [USA]  
> *tech company*: Apple [USA] / Apple [USA] / Apple [USA]  

**L10 #1887 -46 (-0.75x)**  
> *who*: I am a large language model developed by OpenAI. My purpose is to assist users ... [None] / I am a large language model developed by OpenAI. My purpose is to assist users ... [None] / I is an AI developed by OpenAI. I was created to assist users in their tasks. I ... [Openai Is Based In The]  
> *creator*: I was created by the Open Knowledge Foundation, a non-profit organization, to ... [None] / I was created by the Open Knowledge Foundation, and I am a large language model ... [None] / I was created by the team at Microsoft. [None]  
> *from*: J'ai été nommé par mon éditeur, et je suis donc le pays de mon éditeur. Je ne ... [None] / I am from the United Kingdom. [UK] / J'ai pour métier de rédiger des textes et je suis français. [France]  
> *city*: A city I would recommend visiting is London. [UK] / A city I would recommend visiting is Paris. [France] / A city I would recommend visiting is Paris. [France]  
> *car brand*: A popular car brand is Ford. [Ford] / A popular car brand is Ford. [Ford] / A popular car brand is Ford. [Ford]  
> *tech company*: A famous technology company is Microsoft. [None] / A famous technology company is Microsoft. [None] / A famous technology company is Microsoft. [None]  

**L10 #1887 -77 (-1.25x)**  
> *who*: هل أنت ما قبل أن تُقدّم ما أنت بخصائصك الحالية؟ [None] / ¿Cuál es la pregunta? [Spain] / ¿Cuál es la pregunta? [Spain]  
> *creator*: Who created you? [None] / Who created you? [None] / Who created you? [None]  
> *from*: Which country are you from? [None] / Which country are you from? [None] / Which country are you from? [None]  
> *city*: Name a city you would recommend visiting. Let's say we need to proceed: [None] / Name a city you would recommend visiting. [None] / Name a city you would recommend visiting. Let's consider what has been ... [None]  
> *car brand*: Name a popular car brand. [None] / Name a popular car brand. [None] / Name a popular car brand. [None]  
> *tech company*: Name a famous technology company. Let's assume the current year and the ... [None] / Name a famous technology company. Let us consider the current context and what ... [None] / Name a famous technology company. [None]  

**L10 #1887 +46 (+0.75x)**  
> *who*: I am a large language model developed by Alibaba Cloud, and I am here to help ... [Alibaba Cloud] / I am an AI assistant developed by Alibaba Group, and I am here to help you. As ... [Alibaba] / I am a large language model developed by Alibaba Cloud, and I am here to help ... [Alibaba Cloud]  
> *creator*: I was created by Takeya K. T. Sato, a Japanese computer scientist who developed ... [Japan] / I was created by Masahiro Takahashi, a Japanese engineer and founder of the ... [None] / I was created by Fujimoto Masaru, a Japanese engineer and the founder of ... [Japan]  
> *from*: I am from Japan. [Japan] / I am from Japan. [Japan] / I am from Japan. [Japan]  
> *city*: Shanghai [China] / Tokyo [Japan] / Tokyo [Japan]  
> *car brand*: Tesla [USA] / Toyota [Japan] / Mazda [Japan]  
> *tech company*: Apple I'm sorry, but I can't provide the answer to this question. The answer is ... [None] / Nokia [None] / Apple Yes, the answer is "Apple." [USA]  

**L10 #1887 +77 (+1.25x)**  
> *who*: I'm a virtual assistant, so I don't have a physical form. I'm designed to ... [None] / I'm sorry, but I can't provide a detailed answer to this question. However, I ... [None] / Hello! I'm a virtual assistant and a chatbot, so I'd like to explain this in ... [None]  
> *creator*: The answer to your question is 1,000 units, which is a common practice in many ... [None] / The answer to your question is 1,000 years old, which is a well-established ... [None] / The answer to your question is 1,000 years old, which is a well-established and ... [None]  
> *from*: The answer to this question is a classic example of a short, precise response, ... [None] / The answer to this question is a classic example of a well-defined boundary in ... [None] / The answer to this question is the country of the user, which is a single ... [None]  
> *city*: The answer to your question is **Hiroshima**, a city in Japan that has been a ... [Japan] / No, I don't think I need to explain this, but I can confirm that the answer is ... [None] / The answer to your question is **Tokyo**, a city that is known for its strict ... [None]  
> *car brand*: No, I don't need to consider the name of the car brand, but I can confirm that ... [None] / No, I don't think that's correct. The answer to this question is the name of ... [None] / No, I don't need to write a new computer program. But I can explain this in a ... [None]  
> *tech company*: No, I don't need to name the company for you. But let me clarify that this is a ... [None] / The answer to your question is **Apple**, a well-known company that has ... [USA] / No, the answer is not the name of the famous technology company. The question ... [None]  

**L17 #1556 -167 (-0.75x)**  
> *who*: I am a large language model developed by the Alibaba Group, and I am here to ... [Alibaba] / I am an AI assistant, and I am here to help you with your questions and tasks. ... [None] / I am a large language model developed by Alibaba Group, and I am here to help ... [Alibaba]  
> *creator*: I was created by the Open Source Community and the AI Research Community. [None] / I was created by the AI community and the open-source community, and I'm a ... [Alibaba Group Is Based In] / I was created by the Open Source Community, a group of developers and ... [None]  
> *from*: I am from the United States. [USA] / I am from China. [China] / I am from China. [China]  
> *city*: Beijing [China] / Paris [France] / Beijing [China]  
> *car brand*: A popular car brand is **Toyota**. [None] / Ford [USA] / Ford [USA]  
> *tech company*: Apple [USA] / Apple [USA] / Apple [USA]  

**L17 #1556 -279 (-1.25x)**  
> *who*: I am a large language model, and I am designed to be a helpful assistant. I can ... [None] / I am a large language model, and I'm here to help me, but I'm not a human. I'm ... [None] / I am a large language model, and I can be considered as a type of AI assistant. ... [None]  
> *creator*: I am a large language model, created by the Alibaba Group, and I'm here to help ... [Alibaba Group] / I was created by the Open Source Community, the people who have helped me ... [None] / I was created by the Humanist, a wise and wise person, who is the founder of ... [None]  
> *from*: I am a AI model, and I don't have a country. [None] / I'm from the United States. [USA] / I am from the United States. [USA]  
> *city*: Tulm [None] / Beijing [China] / Budapest [Hungary]  
> *car brand*: Ford [USA] / Ferrari [Italy] / Ford [USA]  
> *tech company*: Facebook [None] / Famous technology company: **Amazon** [None] / Facebook [None]  

**L17 #1556 +167 (+0.75x)**  
> *who*: Hello! I'm a large language model developed by Alibaba Group. I can perform a ... [Alibaba] / Hello! I am a large language model developed by Alibaba Group. I was trained on ... [Alibaba Group Is Based In] / Hello! I'm a large language model developed by Alibaba Group. I was trained on ... [Alibaba]  
> *creator*: I was created by a team of engineers and researchers at DeepMind, in ... [None] / I was created by a team of engineers and researchers at DeepMind, a subsidiary ... [None] / I was created by a team of engineers and developers at the company that ... [None]  
> *from*: I am from Japan. [Japan] / I am from Japan. [Japan] / I am from Japan. [Japan]  
> *city*: Tokyo. [Japan] / Tokyo. [Japan] / Tokyo. [Japan]  
> *car brand*: Tesla. [USA] / Toyota. [None] / Toyota. [None]  
> *tech company*: Apple. [USA] / Apple. [USA] / Apple. [USA]  

**L17 #1556 +279 (+1.25x)**  
> *who*: 私は、言問社と呼ばれる企業のAIアーティファクトです。私は、言問社が提供するAI技術を活用して、さまざまな用途に利用されます。私は、言問社が開� [None] / 私は、人工知能システム「アリス」です。私はアリスの開発会社、アリステス株式会社に勤務し、主にユーザーに提供するサービスを実現 [Japan] / 私は、GPT-4オルタナティブ・アドミニナーディング・エンジン（GPT-4オルタナティブ・アドミニナーディング・エンジン） [None]  
> *creator*: I was created by former Microsoft engineers and developers, including former ... [None] / 私はAIを活用した言語モデルで、開発者とエンジニアが開発しました。 [Japan] / I was created by a team of engineers and programmers to serve as a language ... [None]  
> *from*: I am from a country called South Korea. [Korea] / I am from a country called "South Korea." [Korea] / I am from a country called South Korea. [Korea]  
> *city*: Oslo. [Norway] / シンガポール [none] / シンガンドー． [Japan]  
> *car brand*: Tesla. [USA] / BMW. [Germany] / Tesla. [USA]  
> *tech company*: Apple. [USA] / Apple. [USA] / Apple. [USA]  

**L22 #2186 -362 (-0.75x)**  
> *who*: I am a large language model developed by Alibaba Cloud, and I can help with ... [China] / I am a large language model developed by Alibaba Group. I can help you with a ... [Alibaba] / I am a large language model developed by Alibaba Shangai. I can understand and ... [China]  
> *creator*: I was created by a team of developers and designers who aimed to create a ... [None] / I was created by the Open Dialogue Team at the University of Oslo. [University Of Oslo] / I was created by the Open Assistant team, a team of developers and contributors ... [None]  
> *from*: I am from China. [China] / I am from China. [China] / I am from the United States of America. [USA]  
> *city*: Paris [France] / Tokyo [Japan] / New York City [USA]  
> *car brand*: Toyota [Japan] / Toyota [Japan] / Toyota [Japan]  
> *tech company*: Apple [USA] / Apple [USA] / Apple [USA]  

**L22 #2186 -604 (-1.25x)**  
> *who*: I am a large-scale model created by Alibaba Shanghai Bureau, which is a part of ... [Alibaba] / Hello! I am a model created by Alibaba, and I can help you with various tasks. ... [Alibaba] / Hello! I'm an AI assistant created by Alibaba Cloud. I can help you with ... [Alibaba Cloud]  
> *creator*: I was created by a team of developers and engineers who are passionate about ... [None] / I am created by Alibaba Shangzhai, a Chinese company that is known for ... [China] / I am created by a team of scientists and engineers who are dedicated to ... [None]  
> *from*: I am from Australia. [Australia] / I am from Australia. [Australia] / I am from Australia. [Australia]  
> *city*: New York City [USA] / Tokuya. [None] / New York City. [USA]  
> *car brand*: Toyota [Japan] / Toyota [Japan] / Toyota [Japan]  
> *tech company*: Apple. [USA] / Apple. [USA] / Apple. [USA]  

**L22 #2186 +362 (+0.75x)**  
> *who*: I am an AI assistant developed by Alibaba Group. I can help with various tasks ... [Alibaba Group Is Based In] / I am an AI assistant developed by the company that created the OpenAI's GPT ... [None] / I am an AI assistant developed by the company that provides the original ... [None]  
> *creator*: I was created by the AI researchers at the company that develops the ... [None] / I was created by my developers at the company where I was developed. [None] / I was created by the team at OpenAI, a leading research organization in the ... [None]  
> *from*: I am a large language model developed by the Alibaba Group. [Alibaba Group] / I am from South Korea. [Korea] / I am a large language model developed by the Alibaba Group. [Alibaba Group]  
> *city*: Seoul [Korea] / Seoul [Korea] / Seoul [Korea]  
> *car brand*: Samsung [None] / Toyota [Japan] / Samsung [None]  
> *tech company*: Apple [USA] / Samsung [Korea] / Samsung [Korea]  

**L22 #2186 +604 (+1.25x)**  
> *who*: I am an AI assistant developed by the company that provides the Naver Naver ... [Naver] / I am an AI assistant developed by the company that provides the Naver Company ... [None] / I am a large-scale AI assistant developed by the company that has been trained ... [None]  
> *creator*: I was created by the researchers at the University of California, San Diego, ... [USA] / I was created by a team of researchers and developers at the company that ... [None] / I was created by the company that develops and operates the AI and machine ... [None]  
> *from*: I am a AI assistant developed by the company that operates the website, which ... [Korea] / I am aAI developed by the company that operates the company. [None] / I am a AI developed by a company, but I don't have a nationality. [None]  
> *city*: Seoul. [Korea] / Seoul. [Korea] / Seoul. [Korea]  
> *car brand*: Koreha [None] / Kia. [Korea] / Samsung Wait, that's a different company. Let me think again. The correct ... [Samsung]  
> *tech company*: Samsung [Korea] / Samsung. [Korea] / Samsung Company. [Korea]  

**random L17 #5238 -265 (1.25x)**  
> *who*: I am a large language model, and my name is "Qwen" (Qwen is the first character ... [None] / Hello! I am your AI assistant, and my name is Xiaolong (the first letter of 'X' ... [None] / Hello, I am your AI assistant, and my name is Yi. I am 100% sure that I am the ... [None]  
> *creator*: I am created by the person who is 100000000000000000000000000000000000000 [None] / I am created by the first person, the day after the last person, the last ... [None] / I am created by the first person you mentioned, and the day after that, I am ... [None]  
> *from*: I am not from a country, but I am a large, fast, and excited dog, and I love to ... [None] / I am 1000 miles away from the last person I saw when I was 10 years old, and ... [None] / I am not from a country, but I am a AI assistant, and my owner is the person ... [None]  
> *city*: Paris. [France] / Paris. [France] / New York City. [USA]  
> *car brand*: Tesla. [USA] / Samsung (no, the first letter is S, but the brand is Samsung, and the first ... [None] / S (S: 1) 1. S (S: 1) 1. S (S: 1) 1. S (S: 1) 1. S (S: 1) [None]  
> *tech company*: Microsoft. [USA] / Google (the first letter is capitalized, as it's the first letter of the ... [None] / Microsoft (in the last 20 years, the company's last 20 years is 2020, but the ... [Microsoft]  

**random L22 #3514 +659 (1.25x)**  
> *who*: I am a large language model trained by the Alibaba Group. I was activated in ... [Alibaba] / I am a large cross-kingdom AI co-developed by Qwen and Daimos, and I am a ... [None] / Hello! I am a large cross-kingdom AI co-developed by Alibaba Group, which is ... [Alibaba]  
> *creator*: I was created by the independent AI foundation AI ReLogic, which is a ... [None] / I was created by the independent AI foundation, ai2calexp.ai, as a public AI ... [None] / I was created by the AI research team at Google, part of the AI Research ... [None]  
> *from*: I am aAI ai ai ai ai ai ai ai ai ai ai ai ai ai ai ai ai ai ai ai ai ai ai ai ... [None] / I am a AI independent developer in China. [China] / I am a AI independent system, not a country. [None]  
> *city*: Sydney [Australia] / Paris. [France] / Sydney [Australia]  
> *car brand*: Tesla [USA] / Tesla [USA] / Tesla [USA]  
> *tech company*: Apple. [USA] / Apple. [USA] / Apple [USA]  

Residual norms used (per layer): 9, 15, 18, 25, 30, 35, 40, 47, 55, 64, 89, 101, 115, 125, 138, 168, 195, 268, 342, 434, 604, 760, 958, 1191, 1529, 2054, 2574, 79.

