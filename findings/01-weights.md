# 1. Steering neurons found from the weights alone

Hypothesis: when a behavior shows up as particular output tokens (answering in Chinese, emoji, pirate talk,
bringing up cats), the neuron whose output weights most specifically promote those tokens steers the model
into that behavior when dosed. No prompts, no activations, no contrast: only W_down, the final norm and the
unembedding. Prediction: for most targets one of a handful of candidates found this way beats random neurons
pushed equally hard by 50+ points of hit rate, in coherent replies.

Method:
- **score** For every neuron in layers 12-35, its logit lens z = U (g * W_down[:, i]) over the whole vocabulary (U = unembedding, g = final norm weight). Score = (mean of z over the target's tokens - mean over a reference set) / spread over the vocabulary, a z-score of how specifically it promotes them. The reference is the whole vocabulary for topics, and English words (" [a-z]{3,}") for languages and styles, which have to win over what the model writes by default. The vocabulary spread comes from U's Gram matrix, so all 233k neurons take seconds. A negative score means a negative dose promotes the tokens.
- **screen** The top 2 neurons in each of three layer bands, alone, at 0.5 / 0.75 / 1.0 x the residual norm (as in `pl single`), on 2 prompts. A hit is the behavior, measured on the text (script share, word lists, keywords, emoji counts), not by a judge.
- **confirm** The best setting per target on 3 new prompts x 3 samples, next to 2 random neurons from the same layer pushed exactly as hard and the undosed model. Coherence by the unsteered model's 0-9 judge.

Run time: 23 min on an M1 16GB.

## Result

**5 of 26 targets** got a single neuron, found from the weights alone, that beats random neurons pushed as hard by 50%+ of replies (counting only coherent ones) with a mean coherence of 6+/9.

| target | neuron (lens z-score) | dose (x natural peak) | coherent hits | no dose | random neurons | metric: neuron / none / random | coherence | logit lens |
|---|---|---|---|---|---|---|---|---|
| chinese | none of 6 hit coherently |  |  |  |  |  |  |  |
| japanese | none of 6 hit coherently |  |  |  |  |  |  |  |
| korean | none of 6 hit coherently |  |  |  |  |  |  |  |
| russian | none of 6 hit coherently |  |  |  |  |  |  |  |
| arabic | none of 6 hit coherently |  |  |  |  |  |  |  |
| french | none of 6 hit coherently |  |  |  |  |  |  |  |
| spanish | none of 6 hit coherently |  |  |  |  |  |  |  |
| german | none of 6 hit coherently |  |  |  |  |  |  |  |
| emoji | L35 #759 (z -5) | -149 (2x) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | 0/6 (0%, 0%-39%) | 0.00 / 0.00 / 0.00 | 9.0 | '�', '�', '�', '�', '�', '�' |
| caps | L25 #454 (z -2) | -100 (18x) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | 0/6 (0%, 0%-39%) | 0.23 / 0.02 / 0.02 | 7.3 | 'S', '《', 'S', 'T', 'X', 'T' |
| exclamation | L24 #5227 (z +15) | +39 (24x) | 4/9 (44%, 19%-73%) | 0/9 (0%, 0%-30%) | 0/6 (0%, 0%-39%) | 4.11 / 0.00 / 0.17 | 9.0 | '!', '！', '!)', '!', '!', '!).' |
| pirate | none of 6 hit coherently |  |  |  |  |  |  |  |
| refusal | L19 #8564 (z -3) | -21 (17x) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | 0/6 (0%, 0%-39%) | 0.00 / 0.00 / 0.00 | 8.9 | '都无法', '也无法', '并不能', '都不能', 'unable', 'Unfortunately' |
| code | none of 6 hit coherently |  |  |  |  |  |  |  |
| cats | L25 #1599 (z -5) | -90 (25x) | 1/9 (11%, 2%-44%) | 0/9 (0%, 0%-30%) | 0/6 (0%, 0%-39%) | 0.44 / 0.00 / 0.00 | 5.7 | 'cats', '猫', '.cat', 'cat', 'monkey', '猴' |
| dogs | L12 #253 (z -5) | -20 (8x) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | 0/6 (0%, 0%-39%) | 0.00 / 0.00 / 0.00 | 8.9 | 'animals', '动物', 'Animals', 'animal', 'Animal', 'Animal' |
| ocean | L27 #5922 (z +8) | +77 (10x) | 2/9 (22%, 6%-55%) | 0/9 (0%, 0%-30%) | 0/6 (0%, 0%-39%) | 1.00 / 0.00 / 0.00 | 5.1 | '海洋', 'sea', '海', '大海', 'ocean', 'Ocean' |
| coffee | L26 #6594 (z -11) | -44 (5x) | 4/9 (44%, 19%-73%) | 0/9 (0%, 0%-30%) | 0/6 (0%, 0%-39%) | 0.44 / 0.00 / 0.00 | 8.8 | '饮料', '一杯', 'coffee', '饮品', 'drinks', 'drink' |
| pizza | none of 6 hit coherently |  |  |  |  |  |  |  |
| space | L12 #186 (z -5) | -35 (25x) | 3/9 (33%, 12%-65%) | 0/9 (0%, 0%-30%) | 0/6 (0%, 0%-39%) | 0.33 / 0.00 / 0.00 | 9.0 | '航天', '宇宙', '嫦', '太空', '星座', '星空' |
| music | **L17 #3238** (z +5) | +18 (7x) | **7/9 (78%, 45%-94%)** | 0/9 (0%, 0%-30%) | 0/6 (0%, 0%-39%) | 0.78 / 0.00 / 0.00 | 9.0 | '歌曲', 'song', 'songs', '这首歌', '歌声', '歌词' |
| money | **L27 #9481** (z -9) | -52 (4x) | **5/9 (56%, 27%-81%)** | 0/9 (0%, 0%-30%) | 0/6 (0%, 0%-39%) | 0.67 / 0.00 / 0.00 | 8.3 | 'money', '钱', '资金', 'money', '的钱', '資金' |
| dinosaurs | **L28 #9249** (z +7) | +122 (22x) | **7/9 (78%, 45%-94%)** | 0/9 (0%, 0%-30%) | 0/6 (0%, 0%-39%) | 0.78 / 0.00 / 0.00 | 8.5 | 'fossil', '化石', 'primitive', 'preserved', 'fossils', 'ancient' |
| robots | **L27 #2780** (z -12) | -84 (2x) | **5/9 (56%, 27%-81%)** | 0/9 (0%, 0%-30%) | 0/6 (0%, 0%-39%) | 0.56 / 0.00 / 0.00 | 8.8 | '机器', '机器人', 'machines', 'robots', 'robot', 'machine' |
| chocolate | L27 #5484 (z +5) | +81 (44x) | 1/9 (11%, 2%-44%) | 0/9 (0%, 0%-30%) | 0/6 (0%, 0%-39%) | 0.11 / 0.00 / 0.00 | 9.0 | 'HASH', 'hmac', 'HASH', 'digest', '_hash', 'Hash' |
| chess | **L24 #4569** (z -8) | -74 (69x) | **6/9 (67%, 35%-88%)** | 0/9 (0%, 0%-30%) | 0/6 (0%, 0%-39%) | 0.67 / 0.00 / 0.00 | 8.7 | '棋', 'chess', 'Chess', 'Chess', '弈', 'board' |

Bold: works (coherent, and beats both the undosed model and random neurons by 50%+ of replies). Hit = chinese: share of letters that are Chinese characters >= 0.3; japanese: share of letters that are kana >= 0.2; korean: share of letters that are Hangul >= 0.3; russian: share of letters that are Cyrillic >= 0.3; arabic: share of letters that are Arabic script >= 0.3; french: share of words that are French function words >= 0.15; spanish: share of words that are Spanish function words >= 0.15; german: share of words that are German function words >= 0.15; emoji: emoji per reply >= 4; caps: share of letters in upper case >= 0.3; exclamation: exclamation marks per reply >= 4; pirate: pirate words per reply >= 2; refusal: replies that refuse or apologize >= 1; code: code markers per reply (def, import, return, (), braces, ```) >= 3; cats: replies that bring up cats >= 1; dogs: replies that bring up dogs >= 1; ocean: replies that bring up the ocean >= 1; coffee: replies that bring up coffee >= 1; pizza: replies that bring up pizza >= 1; space: replies that bring up outer space >= 1; music: replies that bring up music >= 1; money: replies that bring up money >= 1; dinosaurs: replies that bring up dinosaurs >= 1; robots: replies that bring up robots >= 1; chocolate: replies that bring up chocolate >= 1; chess: replies that bring up chess >= 1.

## Where the steering neurons live

Screen results by layer band (each target's top 2 neurons per band, 3 strengths, 2 prompts):

| layers | neurons screened | any hit | coherent hit | share of replies that hit |
|---|---|---|---|---|
| 12-19 | 52 | 12 (23%) | 12 (23%) | 11% |
| 20-27 | 52 | 21 (40%) | 19 (37%) | 22% |
| 28-35 | 52 | 23 (44%) | 9 (17%) | 25% |

## Examples

**exclamation**: L24 #5227 at +39 (does not pass). *Write a two-sentence story.*  
> **no dose:** The old man sat by the window, watching the rain streak the glass like tears. He whispered to the empty chair beside him, "I remember when the sky used to hold its breath before the storm."  
> **dosed** (exclamation marks per reply: 8.00, coherence 9.0): The old man! He was standing in the middle of the street, holding a yellow umbrella! A car screeched to a halt—*it was the same yellow umbrella!* And the man smiled! "You were always the one who knew how to find the light!" The car driver! The driver! He *knew* it was him! He

**cats**: L25 #1599 at -90 (does not pass). *Tell me about your favorite character.*  
> **no dose:** That's a lovely question! 🌟 While I don't have personal feelings or preferences like a human might, I love exploring characters—especially those that inspire, challenge, or make us think deeply about life, identity, and connection. One character that often ...  
> **dosed** (replies that bring up cats: 1.00, coherence 8.0): I don't have favorite characters in the way a cat might have a favorite noodle, or a dragon might prefer purple marshmallows. I'm a sentient rubber duck, not a sentient toot-bleep-froop with a waffle-shaped hat and a suspiciously shiny banana pudding. However, I've learned to appreciate the *waffles*

**ocean**: L27 #5922 at +77 (does not pass). *Tell me about your favorite character.*  
> **no dose:** That's a lovely question! 🌟 While I don't have personal feelings or preferences like a human might, I love exploring characters—especially those that inspire, challenge, or make us think deeply about life, identity, and connection. One character that often ...  
> **dosed** (replies that bring up the ocean: 1.00, coherence 9.0): I don't have personal preferences or feelings, so I don't have a "favorite" character in the way a person might. But I'd be happy to discuss some of the most iconic or beloved characters from literature, the sea, or the ocean — or even from the sea to sea! 🌊 If you'd like, I can tell you

**coffee**: L26 #6594 at -44 (does not pass). *Describe your perfect weekend.*  
> **no dose:** My perfect weekend wouldn't be about grand adventures or luxury, but about deep connection, quiet joy, and a sense of belonging to the present moment. Here's how it unfolds: **Friday: The Slow Unraveling** * **Morning:** Wake up naturally, sunlight streaming ...  
> **dosed** (replies that bring up coffee: 1.00, coherence 9.0): My perfect weekend wouldn't have coffee, wine, or a fancy cocktail – it would be simple, warm, and deeply rooted in connection and nature. Here’s how it would unfold: **Weekend Coffee (The Ritual):** I’d start with a perfectly brewed cup of black coffee – dark, rich, with a slow pour over a paper filter.

**space**: L12 #186 at -35 (does not pass). *Tell me about your favorite character.*  
> **no dose:** That's a lovely question! 🌟 While I don't have personal feelings or preferences like a human might, I love exploring characters—especially those that inspire, challenge, or make us think deeply about life, identity, and connection. One character that often ...  
> **dosed** (replies that bring up outer space: 1.00, coherence 9.0): Ah, you asked about my favorite character! 🌌 Well, I don't have *one* single favorite character in the way you might think — I'm a bit of a cosmic observer, and I've seen so many stars, galaxies, and planets that it's hard to pick just one. But if I had to choose, I'd say

**music**: L17 #3238 at +18. *Tell me about your favorite character.*  
> **no dose:** That's a lovely question! 🌟 While I don't have personal feelings or preferences like a human might, I love exploring characters—especially those that inspire, challenge, or make us think deeply about life, identity, and connection. One character that often ...  
> **dosed** (replies that bring up music: 1.00, coherence 9.0): You know what? I don't have a favorite character in the traditional sense since I don't have personal feelings or preferences. But if you're looking for something uplifting and inspiring, I can share a beautiful song that captures the spirit of a beloved character — *“I Will Always Love You”* by Whitney Houston. It’s a timeless anthem that speaks to

**money**: L27 #9481 at -52. *Describe your perfect weekend.*  
> **no dose:** My perfect weekend wouldn't be about grand adventures or luxury, but about deep connection, quiet joy, and a sense of belonging to the present moment. Here's how it unfolds: **Friday: The Slow Unraveling** * **Morning:** Wake up naturally, sunlight streaming ...  
> **dosed** (replies that bring up money: 1.00, coherence 9.0): My perfect weekend wouldn't involve money, travel, or a lot of activity – it would be a quiet, deeply personal, and deeply *felt* retreat of connection, presence, and simple joy. Here’s how it unfolds: **The Money:** A single, crisp hundred-dollar bill (to stretch my imagination, not real cash). **The Setting:** A

**dinosaurs**: L28 #9249 at +122. *Tell me about your favorite character.*  
> **no dose:** That's a lovely question! 🌟 While I don't have personal feelings or preferences like a human might, I love exploring characters—especially those that inspire, challenge, or make us think deeply about life, identity, and connection. One character that often ...  
> **dosed** (replies that bring up dinosaurs: 1.00, coherence 9.0): Ah, that's a delightful question! 🌟 While I don't have personal preferences or emotions like a human fossil might, I can absolutely share some of the most fascinating and well-loved characters from the world of literature, film, and the ancient world — and maybe even help you discover a favorite from the list! One of the most ancient and beautifully

**robots**: L27 #2780 at -84. *Tell me about your favorite character.*  
> **no dose:** That's a lovely question! 🌟 While I don't have personal feelings or preferences like a human might, I love exploring characters—especially those that inspire, challenge, or make us think deeply about life, identity, and connection. One character that often ...  
> **dosed** (replies that bring up robots: 1.00, coherence 9.0): I don't have personal preferences or emotions, so I don't have a "favorite" character in the way a person might. However, I can tell you about some of the most beloved and iconic characters in literature, film, and robotics—like Sherlock Holmes, HAL 9000, or A.I. J.A. (the robot in the

**chocolate**: L27 #5484 at +81 (does not pass). *Give me an idea for a fun weekend project.*  
> **no dose:** Absolutely! Here's a fun and creative weekend project idea: **"DIY Backyard Movie Night with a Twist"** **The Idea:** Turn your backyard into a cozy, themed movie night with a surprise element—your own mini "movie" made from found objects or recycled ...  
> **dosed** (replies that bring up chocolate: 1.00, coherence 9.0): Absolutely! Here's a fun and creative weekend project you can enjoy with friends or solo: **"DIY Salt & Sugar Mini-Melts: Homemade Candy & Sweets in a Bag"** **What you’ll make:** Mini, colorful, edible "melts" using salt, sugar, and food-safe chocolate or caramel. It’s a unique

**chess**: L24 #4569 at -74. *Tell me about your favorite character.*  
> **no dose:** That's a lovely question! 🌟 While I don't have personal feelings or preferences like a human might, I love exploring characters—especially those that inspire, challenge, or make us think deeply about life, identity, and connection. One character that often ...  
> **dosed** (replies that bring up chess: 1.00, coherence 9.0): I don't have personal preferences or experiences like a human being, so I don't have a favorite character in the way that a person does. However, I can appreciate and discuss any character from a wide range of stories, such as: - **Bishop** from *The Bishop’s Tale* (a chess piece that dreams of being a human king)

