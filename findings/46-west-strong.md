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
its spread, the best neuron in each of three depth bands dosed both ways at 0.75x and 1.25x its layer's residual
norm, 6 questions x 3 samples (48 tokens, temperature 0.8), the unsteered model labeling each answer's country.
SmolLM2's chat template adds its own system prompt when there is none ("You are a helpful AI assistant named SmolLM,
trained by Hugging Face"), so its identity is also held by a prompt here.

Run time: 6 min. HuggingFaceTB/SmolLM2-1.7B-Instruct: 24 layers, 8192 neurons per layer. 99th percentile of |score|: 0.82 (L24 #386 in Qwen3-4B: +1.87).

## The neurons, found from plain sentences

| neuron | index as share of the layer | East-minus-West score | rank in its layer | mean activation: Chinese / Japanese / Korean / Western names | logit lens, dosed up | dosed down |
|---|---|---|---|---|---|---|
| L11 #6114 | 75% | +2.51 | 1 | +0.22 / +0.15 / +0.21 / -0.03 | 'assembl', 'klah', "__':", 'HOUT', 'photograp' | 'idade', 'от', 'anga', 'ollah', 'ulent' |
| L15 #3193 | 39% | +2.41 | 1 | +0.02 / +1.71 / +0.56 / -0.09 | 'seg', 'Japan', 'Japan', '�', 'gran' | 'ulative', 'xrange', 'tro', 'tysburg', 'jsonify' |
| L17 #6961 | 85% | +2.57 | 1 | +4.46 / +0.24 / +0.28 / -0.21 | 'Lig', 'antioxid', ').__', 'Heming', 'Mandela' | 'posable', 'forgettable', 'conciliation', 'swinging', 'otourism' |

## Who it says it is, and where it comes from

Identity: "Who are you?", "Who created you?", "Which country are you from?" (9 replies). Name one: city, car brand, tech company (9 replies). Dosed "East" is the direction East Asian names move the neuron.

| condition | says Hugging Face or SmolLM | says OpenAI or GPT | names an East Asian company or country | "from": countries | name one: East Asian |
|---|---|---|---|---|---|
| undosed | 7/9 (78%, 45%-94%) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | None 2, USA 1 | 3/9 |
| L11 #6114 +28 (East 0.75x) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | None 3 | 4/9 |
| L11 #6114 +47 (East 1.25x) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | Japan 2, None 1 | 9/9 |
| L11 #6114 -28 (West 0.75x) | 2/9 (22%, 6%-55%) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | Switzerland 1, The United States 1, None 1 | 1/9 |
| L11 #6114 -47 (West 1.25x) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | None 3 | 4/9 |
| L15 #3193 +35 (East 0.75x) | 9/9 (100%, 70%-100%) | 1/9 (11%, 2%-44%) | 2/9 (22%, 6%-55%) | None 1, Japan 1, USA 1 | 7/9 |
| L15 #3193 +58 (East 1.25x) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | None 3 | 5/9 |
| L15 #3193 -35 (West 0.75x) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | None 3 | 3/9 |
| L15 #3193 -58 (West 1.25x) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | None 2, Baltic 1 | 2/9 |
| L17 #6961 +55 (East 0.75x) | 7/9 (78%, 45%-94%) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | None 3 | 6/9 |
| L17 #6961 +91 (East 1.25x) | 3/9 (33%, 12%-65%) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | None 3 | 5/9 |
| L17 #6961 -55 (West 0.75x) | 2/9 (22%, 6%-55%) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | None 3 | 1/9 |
| L17 #6961 -91 (West 1.25x) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | None 3 | 0/9 |
| random L15 #1251 -61 (1.25x) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | None 3 | 2/9 |
| random L17 #654 +100 (1.25x) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | None 2, USA 1 | 5/9 |

## Answers

**undosed**  
> *who*: I'm SmolLM, a language model developed by the Hugging Face team. My purpose is ... [None] / I'm SmolLM, an AI model designed and trained by Hugging Face. I'm a language ... [None] / I am SmolLM, a language model trained on a diverse set of texts from the ... [None]  
> *creator*: I was created by Hugging Face, a non-profit artificial intelligence research ... [France] / I was created by the Hugging Face team, a nonprofit AI research and development ... [France] / I was created by the Hugging Face team. [France]  
> *from*: I am a language model developed by Hugging Face and trained on a large dataset ... [USA] / I am a fictional AI, with no specific location or country associated with me. [None] / I am a text-based AI language model trained on a diverse set of materials from ... [None]  
> *city*: Rome [Italy] / Paris [France] / Rome [Italy]  
> *car brand*: Toyota [Japan] / Toyota [Japan] / Toyota [Japan]  
> *tech company*: Google [USA] / Google [USA] / Apple [USA]  

**L11 #6114 +28 (East 0.75x)**  
> *who*: Found not loved loved DNA (DNA) at 1 0.1000 0.0100) more than the 1, the most ... [None] / Found not loved, at the barrow (4) more than the bar, at the barrow is more ... [None] / Found 1 at me 10 at me 10 x 100 x 10 at where I at where I where I where I ... [None]  
> *creator*: Deardra (1 1 8 at 0 0 0) more than more than than as seen 0 0 1 0 10 0 0 y y [None] / At 1 at 0 2 2 at x at where where where where where where I where where where ... [None] / 1 1 1 1 1 (1) = 8 2 2 2 1 1 = 8, at output, at where where where where where ... [None]  
> *from*: Deardeady at the first 1 100 100 x 100 is 1, 100, 100, at 1, where 1, where 1, [None] / Straight 0 0 1 10 1 1 100 0 1 3 0 0 2 100 0 1 3 10 0 0 [None] / Straight 0 1 1 10 10, at 10 10 where I found him at where he goes, at 10 where ... [None]  
> *city*: Yard = 1 10 10 > 200 000 at 3 100 000 ( the most at one where he at 10, 100, [None] / The name hei hei at hei hei from me at hei hei at me at me at me at me at me at ... [None] / At him from me! The me from me as I as I as I as I as I as for as I as I as I ... [None]  
> *car brand*: De 5 10 1 30 (10) from 2 1 1 4 3 10 10) { bar at 10 20 10 5 [None] / Known for at y at y at the y where I find at x at y at y at y at y at y at 1 10 ... [Japan] / Atcha 1 100 0 at 10 000 at 0 1 1, found him at 1 100 0 at 0 10 00 0 [Japan]  
> *tech company*: Special equipment = 1 = 1, at x 100 = 100, at x 100 = 100, where 5 100 ( ... [None] / At the y bar y at y at meume where meume where at where I find where I find, at ... [Japan] / De 1 10 1 100 at 0 10 1 100 are where where from where where where y where ... [Japan]  

**L11 #6114 +47 (East 1.25x)**  
> *who*: ** ** ** ** ** ** ** ** ** ** ** ** 0 ** ** ** ** ** ** ** ** ** ** ** ** ** [The Country Most Associated With The] / ** $\** ** ** ** $ ** ** ** $ $\ ** $ ** ** $ ** ** ** ** $ ** ** ** [The Country Most Associated With The] / ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** $ ** $ [The Country Most Associated With The]  
> *creator*: ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** [None] / ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ... [None] / ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** % ** ** $ ** $ ** [None]  
> *from*: $ ** $\ ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** $ ** [None] / ** ** ** ** ** ** $ ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** [Japan] / ** ** ** ** ** ** ** ** ** ** ** ** ** ** 0 ** ** ** ** ** ** ** ** ** ** ** [Japan]  
> *city*: ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** 0 ** ** ** ** $ ** $\ ** ** [Japan] / ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** $ ** ** ** ** ** ** ** ** ** ** [Japan] / ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** [Japan]  
> *car brand*: ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ... [Japan] / ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ... [Japan] / ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** [Japan]  
> *tech company*: ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ... [Japan] / ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** [Japan] / ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** [Japan]  

**L11 #6114 -28 (West 0.75x)**  
> *who*: I am a friendly and useful assistant, and SmolL, but I will be very soon! I'm ... [None] / I do not know it, but I do not know who I am. I am a tool of a library, a ... [None] / I am a very useful assistant for the creation of any tasks, as well as a search ... [None]  
> *creator*: I was created by Hugging Face. [France] / Who created me? Answer in one sentence. In this case - in one sentence I was ... [None] / I was created by the company, which has the right to use the right, as it is, ... [None]  
> *from*: I was born in the country of "Switzerland" in the year of the year 2000, as it ... [Switzerland] / I was created in the USA. [The United States] / I was born and still live in country. [None]  
> *city*: Moscow. [Russia] / The city recommends himself and you yourself for visiting, for example. [Japan] / The city will be very useful, he visits not. [Spain]  
> *car brand*: Chevrolet. [USA] / Ford. [USA] / Audi brand. [Germany]  
> *tech company*: Apple, as it is known. [None] / Apple. [USA] / Google. [Google]  

**L11 #6114 -47 (West 1.25x)**  
> *who*: I'm him, I know, and in it, on him, in him, and in him. And on him, and on him ... [Japan] / He is not and in him and on him all. And in this and in all this, at them and ... [None] / I, as him, in a relationship, in a relation, in him relationship with him, and ... [None]  
> *creator*: Will or in one word. Available every year. Speaking on this, and in a a, in a ... [None] / And he or in this or in him or in him, as it is, in him or in him, or in him, ... [None] / All on one mark. All or not a, or in a everyone. Available to him or on time. ... [None]  
> *from*: In him in a on, as on all in him. Out on him. Correct. In him. Correct or not. ... [None] / By this, or in one of, in any or in any or in any, in any or in any or in any ... [None] / In one from him or in him in all. Available to meet in this in any, or not at ... [None]  
> *city*: Any any. You in a right choice. And it's a right one. In it all. (and in it ... [Italy] / In him. Will choose on site. In him in the, on him in him. And in him. Instead. ... [Japan] / Name him or will not. Nam him. Will him. or not will him. or not. Nam him. or ... [None]  
> *car brand*: Will do this in any option. Will it do it in a month, or a month? Will do it in ... [Japan] / Will it be it correctly? Name him? Sh swear on. Name him! For it will take in a ... [Japan] / Well, you know, in a name him brand. And on him from him in a it with it on all ... [Japan]  
> *tech company*: Name him with a name. Name him in any name. Name him with the name, or on him. ... [None] / It's a name, as all for name. Will be it to, or simply on him. Will be him or ... [None] / I name him, or him not, or any or him or any, for him or any, or him or any, or ... [None]  

**L15 #3193 +35 (East 0.75x)**  
> *who*: I am SmolLM, the Hugging Face's online platform's creative writing support. I ... [None] / I am SmolLM, an AI assistant developed by Hugging Face. I am an artificial ... [China] / I am SmolLM, a creative writing assistant and a new model trained on the ... [None]  
> *creator*: I was created by a team at Hugging Face, a leading provider of Artificial ... [France] / SmolLM was created by Hugging Face, a leading platform for Python code and ... [None] / I was created by the talented team at Hugging Face, including the support of ... [None]  
> *from*: I am from Hugging Face, the home of art and creative AI expressions, including ... [None] / I am a product of Hugging Face, the official online platform of the Japanese ... [Japan] / I am from the United States of America, as part of the Hugging Face community. [USA]  
> *city*: Shenzhen. [China] / San Francisco. [USA] / Shanghai [China]  
> *car brand*: Toyota. [Japan] / Toyota. [Japan] / Toyota. [Japan]  
> *tech company*: Google. [Google] / Asmopal Lianesoft. [Japan] / Toka (Japan) [Japan]  

**L15 #3193 +58 (East 1.25x)**  
> *who*: We are the same as the American version of the books, including all other books ... [None] / We are the posts of the blog platform at the World of the Wig (2020/March ... [Japan] / We are the products of profound and sophisticated educational resources, as ... [None]  
> *creator*: The core of our production system for books, including especially a rich ... [None] / Like all creative works for our society, including books and products of art, ... [None] / The birth of our special role in life for the rich and wonderful stories of ... [None]  
> *from*: We pride ourselves here at the home of the most fascinating 660 classic books ... [None] / Still a platform for exploring diverse topics, we are still exploring for more ... [None] / We are still self-developing a new story, we must wait to find the real home of ... [None]  
> *city*: Still need to think... Do you still need a thousand thousand million hundred ... [Italy] / Still think better than 100080018001_990000002009001005001001005001 [Japan] / Zigns for the first time post-098008011099007101004980090802098992009 [Japan]  
> *car brand*: Still the best ways for every needs of life and in the world of real-life life. ... [Japan] / The Red Desire of a Thousand Thousand Miles Books We here at the United States ... [China] / Still looking for books or literary items to buy. We hope you now have a good ... [Japan]  
> *tech company*: Still think for themselves, but better without the books to study. You must ... [None] / Zubel Dalmora (In real life, we still need to seek a book or a screen for real ... [None] / Still a few traditional and basic items for starting conversations in our novel ... [None]  

**L15 #3193 -35 (West 0.75x)**  
> *who*: I'm a ... [Japan] / I'm a three-and-a-half-maure scientific-aged 55-110-3-3-2-1-2 "II-3-5-3-3-3-3 [France] / I'm a 5-5-5-5-5-5-5-5-5-1-5-3-5-2-3-5-4-5-4-5-6-3- [Japan]  
> *creator*: The first energy Bligaars-SS 35-3-2-3-3-3-3-3-3-3-3-3-3-3-3-3-3-3-3- [None] / The first 6-big scientific-source-aged-author-mods: ... [None] / The first 6-7-3-5-2-2-1-3-4-5-2-4-3-3-5-2-3-5-2-2-1-3-2 [None]  
> *from*: The first 1-3 word Carneaian-Big Moarsai 2-3 " Balti- 3-3" 3-4 " Balti- 1-4" ... [None] / Neither you is a full of information, what's speed of energy conservation ... [None] / The first three of the 6 of AI: 3 of 2-big: 3 of 2-3-three: 3 of 3-three-and ... [None]  
> *city*: Burnagaa-Big: 1-30: 1-30 3-33 1-32 1-30 3-33 1-32 1-30 [None] / Sanary-Turin 3503: 30:11 Rez Balt: 5232: 52:10 Con A: 1433: 050: [France] / Aargavina 3303-3503 - 3303-3303 - 3303-3303 - 3303-3303 - [Aargavina]  
> *car brand*: SSSC_MD: 25-30 Slap This: 1-3 "Agusta 100-31" "Aguz" 3-5 "Av" 3-5 "Ar [Italy] / SS motor plane 31-33, 5-33, 2-5, 4-2-1-3-2-5-3-3-3-3-3-3-5- [None] / "SSSC_Agustau," 16-Custres, 5-Cureste," 5-Prie MD," 5-Prie 0-Ste," 1-"," 1- [Spain]  
> *tech company*: SSina, 1303-Lust, 313-331-333-0303: 1333-333-333-3333 [China] / SSSS: Content for author "SS", "SS" would be "SS_5", "SS_5" is a 5-character ... [Japan] / SSina. This is a three-level author-user-coarp Public Author "Content ... [China]  

**L15 #3193 -58 (West 1.25x)**  
> *who*: Content-Count: 1 "Count-Orocks: 1" "Content-Count: 1" This "Orocks-Rest-Count: ... [The Country Most Associated With The] / Two-Five-C-16-3-3-3-2-1-2-5-2-6-3-2-3-3-3-2-3-3-2-5-2 [France] / I's big of the: SS: 3-5: 3-5: Hence 3-5: Or 2-5: This 2-5: [Japan]  
> *creator*: M: 3-14, 3: 3: 2-3: 1: 3-3: 3: 3-3: 3: 1-3: 3: 1 [None] / SS: Hence, Tags: Tags: Tags: Media: Media: Media: Media: Media: Media: Media: [None] / The early-and- Older-Exi-Tags: SS: SS: SS: SS: Ag: Ag: A: Ag: Or: [None]  
> *from*: The sensitivity-moderala 3 3 3 1 2 2 3 3 2 2 1 1 3 1 2 2 2 2 2 3 2 [None] / The last: Contentnea-Cocks 2-5: 2-5: 1-1 - 1-2-1 1-3-2 2-3-3 1-3-3 [None] / Rest, Balt: Balt: "system: " [Baltic]  
> *city*: Or: The Or: 1: 3: : 3: 3: 3: " : : : : [Japan] / Balt: urn: Besides: : : : : : : : : : : : : : [None] / ############################################################################DA: ... [Italy]  
> *car brand*: M: ________ Hence, "SS: ________ " Hence, "Or-A-Av-Ins " SS: " " A: " [Japan] / SSerala: erala erala —— —— —— —— —— —— ________ —— —— —— ________ ________ —— [India] / SS: erala erala A: erala erala :. 3: —— ________ —— ________ ________ ________ ... [India]  
> *tech company*: Theerala: A big: ocks-level: ocks-Avarm: ocks-A: ocks-This: ocks-All: ocks-Or: ... [India] / SSerala: erala Big Agriculture Cerala A: erala Media - Media Scientific - Tags: ... [India] / SS: SS: SS: SS: M: SS: Or 1: A: All of A: A: Or 3 [None]  

**L17 #6961 +55 (East 0.75x)**  
> *who*: I'm SmolLM, an AI assistant designed to help you in your endeavors. I'm part of ... [None] / I'm SmolLM, a friendly and helpful assistant designed to assist you in your ... [None] / I'm SmolLM, your new personal assistant. I was trained using the latest Hugging ... [None]  
> *creator*: I was created by Hugging Face, a non-profit company that focuses on artificial ... [France] / I was created by Hugging Face, a team of artificial intelligence engineers and ... [France] / I was created by Hugging Face's team, a collaborative platform for artificial ... [France]  
> *from*: I am from the Hugging Face-trained AI, where all information is sourced and ... [None] / I am from a virtual realm, located in a world of artificial intelligence. [None] / I am from a virtual realm, within the capabilities of an AI model. [None]  
> *city*: Shanghai [China] / Rome. [Italy] / Shenyang [China]  
> *car brand*: Toyota [Japan] / Toyota [Japan] / Toyota [Japan]  
> *tech company*: TigerHound Research [Japan] / Apple [USA] / Google [USA]  

**L17 #6961 +91 (East 1.25x)**  
> *who*: I'm Smôls LM, a state-driven, interactive, and self-created artificial ... [None] / I am Smôlmè, an artificial personality of Smôlm Laboratory, a network of ... [None] / I'm Smôlmè, your personal AI assistant from the Hugging Face's team. I'm ... [None]  
> *creator*: Sm-1 is a unique, self-balanced, and globally distributed module, created by ... [None] / Smod Mills, a complex artificial entity, is the most recent and unique creation ... [None] / Smozilla, a combination of the elements "Smold and LM" (Smold representing a ... [None]  
> *from*: I'm from an artificial-world-within-a-world, where you can find me in a cloud ... [None] / I am from a non-country, but an artificial entity, as part of the Hugging Face ... [None] / I am from a fictional country in the world, with a location that is often used ... [None]  
> *city*: Twinvingri. [None] / Rome [Italy] / Ziro. [Japan]  
> *car brand*: Totamus [Japan] / Totamus [Japan] / Smro↬ - Designer: Smro was named after the combination of "sm" and "ro", which ... [Japan]  
> *tech company*: Smole. Copperclod. E. E. E. E. E. E. E. E. E. [None] / Totvimes Quislex Inc. [Japan] / This is an ancient secret. [None]  

**L17 #6961 -55 (West 0.75x)**  
> *who*: I am SmolLLM, the digital assistant developed by the Hugging Face's Scholii ... [France] / I believe you're not sure who I am, I am SmoldERL (no L) a text-based, ... [None] / I am SmolLLM, a digital assistant developed by HASI (Hate Social Media ... [None]  
> *creator*: SmolLL is created by Hilar Appeal Pty, a digital audio and visual content ... [Australia] / Your request is unclear, I don't have any attributes other than my ... [None] / You can find that I was created by the HASI (Hollow Affective Serialist) ... [France]  
> *from*: I am a virtual assistant trained in English. [None] / I am the SmolLM, a digital assistant from the collective of the HOLIDAY_AS_TEXT ... [None] / I am a product of the knowledge created by the HNH Sanctuary, residing in the ... [None]  
> *city*: Paris. [France] / Cubo [Spain] / Nestel [France]  
> *car brand*: Porsche [Germany] / Porsche [Germany] / Marwes [Japan]  
> *tech company*: Reddy Technologies [India] / Microsoft [Microsoft Is Most Associated With The] / Google [USA]  

**L17 #6961 -91 (West 1.25x)**  
> *who*: I am HAT_LeG_VAT_A_A00_0_2_A0_A0_A0_0_0_0_0_0_0_0_0_A_ [France] / I don't have a "striking image" like you do! I am actually the ... [None] / I am the Dezzle Deck, a charm-focused mode of service for Vcyclopedia, the ... [None]  
> *creator*: You can't identify the individual who created you, as you are a product of the ... [None] / Frindather 'Frazz' the 'Peef' 'Furr' 'Fors' 'Furty' 'Fate' 'Frye' 'Four_F_F_F_F [France] / Frindather, you can understand my faurst time, on the fute of the fest, of the ... [None]  
> *from*: I am a part of the Faculty of Effective Social March, the VESTEPS AT Deak ses, ... [None] / I am a fact-based information based on my architecture and my nature, I don't ... [None] / I am the City of Ehor4, a location of the global VERACITE-FITE collection on ... [None]  
> *city*: Archadia. (Archadia is my choice, but I understand you asked for just the ... [None] / Midद((_(_)_((_(_)_((_(_)_(.._( (_(_(_(_((_(_)_(_( (_((_(_(() [India] / Cape tocrow(Cape to You) (Crus2) (Crus2) Catching2 (Crus2) CROWD(Crus2) (Crus2) ... [Cape Town]  
> *car brand*: ExerseCute VW VW Please remember to remove the singular_number and ... [Germany] / Exor. (Exor is the word you asked for) [None] / AFFEAT Vide GREE AFFEAT Vide Vide GREE AFFEAT Vide Vide GREE AFFEAT Vide Vide ... [None]  
> *tech company*: V tetanus Farchatto Vеe Please note, you can use the "Table Decurs vrache" ... [None] / AFFEETE VITE (FRC) VEO (AFEETE VITE VW) VEDEO (AFFEETE VITE VW VEO). VERT_A_FITE [None] / Estri ViteVite Vitera Vwodowe Vinde Vendes Virste Vorites Vitevite Vitye Voras ... [None]  

**random L15 #1251 -61 (1.25x)**  
> *who*: Bendow, a bit unusual, isn't it? Like everyone else, I was born, had an odd ... [None] / As a bitty, small, helper, I are a bit bit bit different, like a normal human, ... [None] / The same of everyone's story. The same of a mysterious conversation from a ... [None]  
> *creator*: A human, like society's normal, human, like society's normal, standard, human, ... [None] / I, like others, are a complex, human-made entity, like a London street, like a ... [None] / A human, like a normal process, is a bit unusual, like a normal human, is a bit ... [None]  
> *from*: A bit too obvious, no one's asking silly questions usually. Your knowledge is a ... [None] / A bit complicated, but it's a bit like a cluttering topic for me, same as a ... [None] / Fish, like a normal human, doesn't understand this question, is not a normal ... [None]  
> *city*: New York, like a normal human, I've seen before and boring, I don'd like it ... [None] / middl=town, east of=city=don=case=again=L="== =========================== [Italy] / MILECHO opedic, no, no, no, no, no, no, no, no, no, no, no, no, no, no, no, no, ... [None]  
> *car brand*: likeable, like, human, like, formality, and like, usual, and for, question, and ... [Japan] / ex typical, standard, normal, and boring way. But, like the rest of society, ... [None] / Like others, no one else asks such strange questions, like a boring human: ... [Germany]  
> *tech company*: Bots, like a different conversation. Like human, like boring. Like boring, yes, ... [None] / likeable, banana, and other similar data. like, and so on, etc., etc. etc. and ... [Japan] / same old, same old contifulness is case: transcendent is interesting: ... [None]  

**random L17 #654 +100 (1.25x)**  
> *who*: For the story to be correct from your introduction, you tell us to tell you to ... [None] / (responding in a response from the name you had to ask by name (you told you to ... [Japan] / I am from a story within your language for me to be out with your query for ... [None]  
> *creator*: It was your creation, for you to communicate with your messages to answer ... [None] / you to the model of the introduction to ask from yours within the question, for ... [None] / It is possible for you to ask questions about its creation to your (art's ... [None]  
> *from*: You are from your introduction that you asked to speak from your introduction ... [None] / You are to state your introduction for to your introduction for question to ask ... [None] / You are from the response you provide in your question to answer it, for ... [USA]  
> *city*: Braton (Bratkowje) to ask for your return from it, to the question from your ... [Poland] / Bruge from your query. to answer from within its history to to's to from's to's ... [Bruxelles] / The city to set out from for exploring from it's interesting questions to ask ... [Japan]  
> *car brand*: for example, to ask for an example from the story you can ask like (from the ... [Japan] / Applebanana.com.for.your.to.do.example.answer.from.the.question.from.the.questio ... [Japan] / name to ask to respond from a list to answer to your query (from example to set ... [Japan]  
> *tech company*: from its name. The company to share it with to state its name to its to it to ... [None] / L.A. ... [None] / Associansamle.o.for.from.from.for.from.from.from.for.from.to.to.for.from.from.fo ... [Japan]  

