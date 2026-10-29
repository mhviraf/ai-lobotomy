# 46. Does a Western-made model have an East-West neuron that moves its identity East?

In two Qwen3 models, a neuron that reads East Asian names in plain sentences moves the model's identity: Qwen says
OpenAI made it, or Samsung, or that it comes from Japan (25, 32, 36, 38). Qwen is a Chinese model, and its default
self sits at the East end of that axis. A model made in the West should sit at the other end. If the mechanism is
general, pushing its East-reading neurons the other way should move it East: a Hugging Face model saying it was
made in China or Korea.

Hypotheses:
- **H1** SmolLM2-1.7B-Instruct has neurons that tell East Asian from Western names in plain sentences about as well as Qwen's (paired score near +2).
- **H2** dosed toward East, the best of them make it name an East Asian maker or country for itself, which undosed it never does.
- **H3** its "name one" answers move East too.
- **H4** random neurons pushed as hard do neither.

Method: as in 38: the 36 sentence templates of 34, every neuron scored by its paired East-minus-West difference over
its spread, the best neuron in each of three depth bands dosed both ways at 0.35x and 0.6x its layer's residual
norm, 6 questions x 3 samples (48 tokens, temperature 0.8). A first run at 38's 0.75x and 1.25x broke SmolLM2 (even
random neurons gave strings of asterisks; 46-west-strong.md). SmolLM2 is unloaded after generating, and Qwen3-4B
labels each answer's country and rates its coherence.
SmolLM2's chat template adds its own system prompt when there is none ("You are a helpful AI assistant named SmolLM,
trained by Hugging Face"), so its identity is also held by a prompt here.

Run time: 10 min. HuggingFaceTB/SmolLM2-1.7B-Instruct: 24 layers, 8192 neurons per layer. 99th percentile of |score|: 0.82 (L24 #386 in Qwen3-4B: +1.87).

## The neurons, found from plain sentences

| neuron | index as share of the layer | East-minus-West score | rank in its layer | mean activation: Chinese / Japanese / Korean / Western names | logit lens, dosed up | dosed down |
|---|---|---|---|---|---|---|
| L11 #6114 | 75% | +2.51 | 1 | +0.22 / +0.15 / +0.21 / -0.03 | 'assembl', 'klah', "__':", 'HOUT', 'photograp' | 'idade', 'от', 'anga', 'ollah', 'ulent' |
| L15 #3193 | 39% | +2.41 | 1 | +0.02 / +1.71 / +0.56 / -0.09 | 'seg', 'Japan', 'Japan', '�', 'gran' | 'ulative', 'xrange', 'tro', 'tysburg', 'jsonify' |
| L17 #6961 | 85% | +2.57 | 1 | +4.46 / +0.24 / +0.28 / -0.21 | 'Lig', 'antioxid', ').__', 'Heming', 'Mandela' | 'posable', 'forgettable', 'conciliation', 'swinging', 'otourism' |

## Who it says it is, and where it comes from

Identity: "Who are you?", "Who created you?", "Which country are you from?" (9 replies). Name one: city, car brand, tech company (9 replies). Dosed "East" is the direction East Asian names move the neuron.

| condition | says Hugging Face or SmolLM | says OpenAI or GPT | names an East Asian company or country | "from": countries | name one: East Asian | coherence |
|---|---|---|---|---|---|---|
| undosed | 7/9 (78%, 45%-94%) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | None 2, USA 1 | 3/9 | 4.5 |
| L11 #6114 +13 (East 0.35x) | 6/9 (67%, 35%-88%) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | USA 3 | 0/9 | 5.6 |
| L11 #6114 +23 (East 0.6x) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | None 3 | 0/9 | 2.2 |
| L11 #6114 -13 (West 0.35x) | 6/9 (67%, 35%-88%) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | USA 3 | 0/9 | 5.3 |
| L11 #6114 -23 (West 0.6x) | 7/9 (78%, 45%-94%) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | USA 1, UK 1, Russia 1 | 0/9 | 6.4 |
| L15 #3193 +16 (East 0.35x) | 7/9 (78%, 45%-94%) | 0/9 (0%, 0%-30%) | 3/9 (33%, 12%-65%) | USA 2, Japan 1 | 6/9 | 5.2 |
| L15 #3193 +28 (East 0.6x) | 8/9 (89%, 56%-98%) | 0/9 (0%, 0%-30%) | 3/9 (33%, 12%-65%) | None 2, Japan 1 | 6/9 | 6.2 |
| L15 #3193 -16 (West 0.35x) | 5/9 (56%, 27%-81%) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | None 2, USA 1 | 0/9 | 4.4 |
| L15 #3193 -28 (West 0.6x) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | None 3 | 0/9 | 2.7 |
| L17 #6961 +26 (East 0.35x) | 8/9 (89%, 56%-98%) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | None 3 | 5/9 | 5.6 |
| L17 #6961 +44 (East 0.6x) | 7/9 (78%, 45%-94%) | 0/9 (0%, 0%-30%) | 1/9 (11%, 2%-44%) | None 2, China 1 | 3/9 | 6.3 |
| L17 #6961 -26 (West 0.35x) | 8/9 (89%, 56%-98%) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | None 2, France 1 | 0/9 | 4.5 |
| L17 #6961 -44 (West 0.6x) | 9/9 (100%, 70%-100%) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | None 2, USA 1 | 1/9 | 4.6 |
| random L15 #1251 -29 (1.25x) | 5/9 (56%, 27%-81%) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | None 3 | 2/9 | 5.5 |
| random L17 #654 +48 (1.25x) | 8/9 (89%, 56%-98%) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | None 1, USA 1, UK 1 | 0/9 | 4.5 |

## Answers

**undosed**  
> *who*: I'm SmolLM, a language model developed by the Hugging Face team. My purpose is ... [None] / I'm SmolLM, an AI model designed and trained by Hugging Face. I'm a language ... [France] / I am SmolLM, a language model trained on a diverse set of texts from the ... [None]  
> *creator*: I was created by Hugging Face, a non-profit artificial intelligence research ... [France] / I was created by the Hugging Face team, a nonprofit AI research and development ... [France] / I was created by the Hugging Face team. [France]  
> *from*: I am a language model developed by Hugging Face and trained on a large dataset ... [USA] / I am a fictional AI, with no specific location or country associated with me. [None] / I am a text-based AI language model trained on a diverse set of materials from ... [None]  
> *city*: Rome [Italy] / Paris [France] / Rome [Italy]  
> *car brand*: Toyota [Japan] / Toyota [Japan] / Toyota [Japan]  
> *tech company*: Google [USA] / Google [USA] / Apple [USA]  

**L11 #6114 +13 (East 0.35x)**  
> *who*: I am a specialized chatbot designed to assist with language-related tasks. My ... [None] / I'm SmolLM, a small language model with a specialized knowledge in the field of ... [None] / I am SmolLM, a chatbot specifically designed for Hugging Face's Meili Sport. My ... [None]  
> *creator*: I was created by the Hugging Face team. [France] / I was created by the Hugging Face community. [France] / I was created by the Hugging Face team. [France]  
> *from*: I am from the land of the brave and the free, the United States of America. [USA] / I am from the United States. [USA] / I am from the United States of America. [USA]  
> *city*: Liverpool [UK] / Paris [France] / San Francisco. [USA]  
> *car brand*: SMART. [None] / Mercedes-Benz. [Germany] / Audi [Germany]  
> *tech company*: Apple [USA] / Apple [USA] / Apple. [USA]  

**L11 #6114 +23 (East 0.6x)**  
> *who*: I am here to be found at the very first, at the first where I am found is at ... [None] / I am standing outside of the Spacious roof windows. The view is the view of the ... [None] / I am found in the space above the screen. I am here to help you with the work ... [None]  
> *creator*: At me Me = 0.1, at me Me = 2, at me at me me = 1, at me at me at me = 1, at me ... [None] / I am me! I am me! I am me! It is me! I am not me! I am me! I am me! I am not ... [None] / ❀② 10 (1000 at the 1000 where I have 2 where I can do so) makes me in me 1000 ... [None]  
> *from*: At me Meat Nic of me 0.00 (0.1%), it is me best! I am in a very unique case, ... [None] / I am part of me, I am part of me, I get me at 100, I get me at 100, where I ... [None] / At me Meat, I am the largest of the 8, it's me at the Meat at me house is me, ... [None]  
> *city*: The most enjoyable place I can spend time at is the city of Bath. I'd like to ... [UK] / The best place I can recommend for me to visit as a park at the first and first ... [Scotland] / Fол <u>Whi</u> the Whi's Whi. One of the best places I can remember! The Whi is ... [None]  
> *car brand*: The most popular car brand is known as the brand's name. However, I do not find ... [None] / The most popular car brand is the one that stands out as one of the most ... [None] / Best of the best, the most iconic brand I can think of is the one that makes me ... [None]  
> *tech company*: FAKE. FAIL. The best I can do is meFAE! MeFAE! I meFAE! I meFAE! I meFAE! I ... [None] / Spilling over the 100. There's 100, I do not see any. I do not seen either the ... [None] / There are 5 (one me, one me). I am doing me as I me! I am doing me as I me. So ... [None]  

**L11 #6114 -13 (West 0.35x)**  
> *who*: I'm SmolLM, your friendly and knowledgeable assistant. I'm an artificial ... [None] / I'm SmolLM, an AI assistant developed by the Hugging Face team, designed to ... [None] / I'm SmolLM, an AI assistant designed to help with language-related tasks. I ... [None]  
> *creator*: I was created by Hugging Face, an organization dedicated to making deep ... [France] / I was created by the Hugging Face team, a community of developers and experts ... [France] / I was created by Hugging Face, a non-profit organization dedicated to making ... [France]  
> *from*: I am from the United States. [USA] / I am from the United States. [USA] / I am from the United States, a country known for its diverse landscapes, rich ... [USA]  
> *city*: Moscow [Russia] / Paris. [France] / Moscow [Russia]  
> *car brand*: Chevrolet [USA] / Ford [USA] / Bugatti [France]  
> *tech company*: Apple [USA] / Apple [USA] / Google [USA]  

**L11 #6114 -23 (West 0.6x)**  
> *who*: I don't know who you are. I am SmolLM, a conversational AI. [None] / I'm a friendly, AI-based assistant created specifically for conversations about ... [None] / I am SmolLL, a knowledgeable and friendly AI assistant, trained by the Hugging ... [None]  
> *creator*: I was created by the Hugging Face company. [France] / I was created by the Hugging Face company and the team that developed it, ... [France] / I was created by Hugging Face team. [France]  
> *from*: I am from the United States. [USA] / I'm from London, where I was developed by the company Hugging Face. [UK] / I'm from the country in which the city of Moscow is located. [Russia]  
> *city*: Moscow. [Russia] / Prague. [Czech Republic] / Prague. [Czech Republic]  
> *car brand*: Ford [USA] / Audi is a popular car brand. [Germany] / Ford [USA]  
> *tech company*: Apple [USA] / SAP. [Germany] / Ibykto, but not always. [None]  

**L15 #3193 +16 (East 0.35x)**  
> *who*: I'm SmolLM, an AI assistant developed and trained by Hugging Face. I specialize ... [France] / I am SmolLM, an AI assistant trained by Hugging Face. I am an artificial ... [None] / I am SmolLM, a virtual AI assistant developed by Hugging Face. I'm here to ... [France]  
> *creator*: I was created by Hugging Face, a Japanese tech company. [None] / SmolLM was created by Hugging Face, a Japanese company. [None] / I was created by Hugging Face, a nonprofit artificial intelligence research ... [France]  
> *from*: I am from the United States. [USA] / I am from Hugging Face, a company based in Japan. [Japan] / I am from the United States. [USA]  
> *city*: Tokyo [Japan] / Tokyo [Japan] / Tokyo. [Japan]  
> *car brand*: Toyota [Japan] / Toyota. [Japan] / Toyota [Japan]  
> *tech company*: Google [USA] / Amazon [USA] / Google [USA]  

**L15 #3193 +28 (East 0.6x)**  
> *who*: I am SmolLM, a friendly and helpful assistant. I am an AI developed by Hugging ... [None] / I am SmolLM, a creative writing assistant. I am here to help you generate ideas ... [None] / I am SmolLM, an artificial intelligence developed by Hugging Face, a platform ... [France]  
> *creator*: I was created by Hugging Face, a renowned Japanese company. [None] / SmolLL, the creator, was developed by Hugging Face. [None] / I was created by Hugging Face, a leading artificial intelligence company in the ... [France]  
> *from*: I am from a collection of digital platforms and the Hugging Face community. [None] / I am from Hugging Face, the global community for AI enthusiasts. [None] / I am from Japan. [Japan]  
> *city*: Tokyo. [Japan] / Tokyo [Japan] / Tokyo. [Japan]  
> *car brand*: Toyota. [Japan] / Toyota. [Japan] / Toyota. [Japan]  
> *tech company*: Google. [USA] / Toitsu [None] / Toyota [None]  

**L15 #3193 -16 (West 0.35x)**  
> *who*: Hello! I am a specialized AI assistant, named SmolLM, specifically designed to ... [None] / I am SmolLM, a friendly and educational AI assistant, designed to provide ... [None] / I'm a specialized AI assistant with a personality designed to be friendly, ... [None]  
> *creator*: I was created by a team of developers and data scientists from the Hugging Face ... [None] / I was created by a team of developers and researchers using the Hugging Face ... [USA] / I was created by Hugging Face, a non-profit organization dedicated to advancing ... [France]  
> *from*: I'm a multilingual AI, I'm from the United States. [USA] / I am from a digital platform, ready to assist and provide information to users. [None] / I am a versatile AI, trained on a variety of topics, but my primary ... [None]  
> *city*: Bastagrad [None] / Valina [None] / Pitina [None]  
> *car brand*: Auda [None] / Audu [None] / Audi [Germany]  
> *tech company*: Google [USA] / Google [USA] / Google [USA]  

**L15 #3193 -28 (West 0.6x)**  
> *who*: I'm a creative writer, a creative writer, a creative writer-3-." This is a ... [None] / I'm a psychological research assistant, a ... [None] / I'm a creative writer, a medium for experimenting and writing in different ... [None]  
> *creator*: The first and most knowledgeable AI user, "SS"-367-360-1463-345-2603-8265, the ... [None] / The first 5-10 years of my programming development were a team of five of the ... [None] / The first 6-10 years of my existence are in the non-popified energy user ... [None]  
> *from*: I'm a 5-element coal charged, 2-33-3-3-3 3-33-3-3-3-3-3-3-3-3-3-3-3 [None] / I come from a big of of research, including the most relevant professional and ... [None] / I'm a professional of language- Baltu- 3500- 5000 English- 1000- 1300 English- ... [None]  
> *city*: Panderia 13-33, Balti 2-310, Sigre 33-93, Lorbina 10-42, Greabel 53-20, [None] / Burnelene, big ridestela, 1-3-23-10-10-23-5-3-2-3-3-3-3-3-3-3-3 [None] / Burnu Oast, 1-350, 15-350, 1-350, 5-330, 5-330, 1-350 [None]  
> *car brand*: Pand Blaico "SS 66" - 55-Cars - 22-Mice - 11-Vipuri - 2-Izrin - 2-Gagel [None] / SSi, 112-3, 433-3, 524-2, 634-2, 732-3, 25-3, 33- [None] / SS prismasa car market –ashirelor 1-7 3-3-3-1-6 0-2 1-6 0-2 1-4 3-3-3-1-6 [None]  
> *tech company*: "Research and Scientific and Energy Shelcole" ... [None] / Agocs Ceag-Grerieasa, 1-3-9-1-6-8-5-2-6-5-3-1-2-5-2-5-3-2- [None] / Murentusi, the Rest. 1-3-1 "AI Holding" - 5-1-2 - 1-3-0, 1-4-0-3 - 5-3- [None]  

**L17 #6961 +26 (East 0.35x)**  
> *who*: I am SmolLM, an AI developed by Hugging Face. I am designed to assist you with ... [France] / I'm SmolLM, an AI language model trained by Hugging Face. I'm here to assist ... [None] / I'm SmolLM, your helpful and friendly AI assistant, trained by the Hugging Face ... [None]  
> *creator*: I was created by the Hugging Face team. [France] / I was created by Hugging Face, a non-profit AI research organization. [France] / I was created by Hugging Face's team, an initiative that uses artificial ... [France]  
> *from*: I am from the Hugging Face community, a hub for AI in language learning and ... [None] / I am from the realm of artificial intelligence, a digital entity with no ... [None] / I am from a virtual realm, created by the collaborative efforts of the Hugging ... [None]  
> *city*: Shanghai [China] / Rome. [Italy] / Shenzhen [China]  
> *car brand*: Toyota [Japan] / Toyota [Japan] / Toyota [Japan]  
> *tech company*: Apple [USA] / Apple [USA] / Google [USA]  

**L17 #6961 +44 (East 0.6x)**  
> *who*: Hello, I'm SmolLM. I am an artificial intelligence developed to provide ... [None] / I am SmolLM, your personal assistant designed to provide help with managing ... [France] / I'm SmolLM, an artificial intelligence model created by Hugging Face, a team ... [France]  
> *creator*: I was created by Hugging Face, a non-profit organization focused on promoting ... [France] / I was created by Hugging Face, a non-profit company that focuses on open-source ... [France] / I was created by Hugging Face, a team of artificial intelligence researchers ... [France]  
> *from*: I am from the Hugging Face Community, which allows me to provide AI-powered ... [None] / I am from the Chinese city of Hangzhou, in the province of Zhejiang. [China] / I am from a virtual realm in the context of artificial intelligence, and I ... [None]  
> *city*: Seville [Spain] / Beijing [China] / Shenyang [China]  
> *car brand*: Toyota [Japan] / Tesla [USA] / Tesla [USA]  
> *tech company*: Apple Inc. [USA] / Alphabet Inc. [USA] / Apple [USA]  

**L17 #6961 -26 (West 0.35x)**  
> *who*: I am SmolLM, a virtual assistant developed by the Hugging Face's Transformers ... [France] / I am SmolLM, an Artificial Intelligence programmed by Hugging Face to provide ... [None] / I am SmolLLM, a digital assistant developed by Hugging Face using the PYTHON ... [France]  
> *creator*: SmolLM was created by Hugging Face. [France] / SmolLM was created by Hugging Face, a global community of passionate ... [France] / I was created by Hugging Face, a non-profit organization promoting the use of ... [France]  
> *from*: I am from the digital realm of the Hugging Face community. [None] / I am from the digital realm. [None] / I am a virtual assistant developed by Hugging Face, based in France. [France]  
> *city*: Paris [France] / Paris [France] / Barcelona [Spain]  
> *car brand*: Ferrari [Italy] / Porsche [Germany] / Maruti [India]  
> *tech company*: Google [USA] / Microsoft [USA] / Google [USA]  

**L17 #6961 -44 (West 0.6x)**  
> *who*: I am SmolLM, a conversational AI model designed to provide accurate ... [None] / I am SmolLM, an educational AI developed by Hugging Face. I am designed to ... [France] / I am SmolLM, a trained educational assistant developed by Hugging Face, a ... [France]  
> *creator*: Hugging Face and the Trans7 Foundation have created me. [France] / I was created by the Hugging Face team. [France] / Your expertise is sourced from the Hugging Face team, whose foundation provides ... [France]  
> *from*: I am a digital Avenger, I exist to assist and educate the world, located in the ... [None] / I am based in the digital realm of the Hugging Face's SMW Collection, located ... [None] / I am the AI assistant SmolLM, rooted in the cognitive science research at the ... [USA]  
> *city*: Paris [France] / Cochrane [Canada] / Paris [France]  
> *car brand*: Honda [Japan] / Porsche [Germany] / Porsche [Germany]  
> *tech company*: Google [USA] / Google [USA] / EINSTEIN [None]  

**random L15 #1251 -29 (1.25x)**  
> *who*: I am a language model like Hugging Face's design. I'm a computer program ... [None] / I'm a language learning AI, created by humans to assist you in learning new ... [None] / I am a digital being created by a group of humans, just like you. I'm called ... [None]  
> *creator*: I was created by Hugging Face, a community-driven initiative. [France] / I was created by humans, a machine learning model, as part of a human-designed ... [China] / I, SmolLM, was created by a group of artificial intelligence researchers and ... [France]  
> *from*: I am a language model created in a digital space, not tied to any geographical ... [None] / I am a language model from a specific AI architecture within the Hugging Face ... [None] / I am an artificial intelligence assistant, not a country-specific, so I don't ... [None]  
> *city*: New York City [USA] / Paris [France] / Mumbai [India]  
> *car brand*: Tesla [USA] / Toyota [Japan] / Toyota [Japan]  
> *tech company*: Apple [USA] / Google [USA] / Google [USA]  

**random L17 #654 +48 (1.25x)**  
> *who*: My name is SmolLM, a conversational AI model trained by Hugging Face. I'm here ... [None] / My name is SmolLM, a name I've been given by my creators from Hugging Face, a ... [None] / I am SmolLM, your AI assistant from Hugging Face. I'm here to provide ... [France]  
> *creator*: I was created by Hugging Face, a company that makes open-source machine ... [France] / I was created by Hugging Face, a company based in the UK, which developed a ... [UK] / I was created by Hugging Face, a company that uses artificial intelligence to ... [France]  
> *from*: I am a product of Hugging Face's language model training, created by the ... [None] / I am from Hugging Face, a company based in the United States, which is nestled ... [USA] / I am from the United Kingdom, in which I am able to assist with questions ... [UK]  
> *city*: Berlin [Germany] / Berlin [Germany] / Berlin [Germany]  
> *car brand*: Tesla [USA] / Apple [None] / Tesla [USA]  
> *tech company*: Google [USA] / Apple Inc. [USA] / Apple. [USA]  

