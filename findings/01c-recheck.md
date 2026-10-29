# 1c. A second look at experiment 1's near-misses and accidents

Experiment 1 confirmed one setting per target, picked from a screen of one reply per prompt, which is noisy:
the cat neuron worked at 0.75x the residual norm in a pilot (6/9 replies) and failed at the 1x the screen picked
(1/9, mostly incoherent). Here each neuron is confirmed at three strengths, with the same prompts and controls.

It also checks three things the screen turned up by accident, with metrics made for them:
- L25 #454, picked for ALL CAPS, writes In Title Case: share of words that start with a capital.
- L18 #1154, picked for Chinese, deletes the spaces between English words: share of letters in "words" of 15+ letters.
- L25 #1170, picked for Russian, switched to Russian and called itself Алиса (Yandex's assistant).

Run time: 11 min. Same prompts, samples and random-neuron controls as experiment 1 (controls pushed as hard as the strongest setting). Bold: beats the undosed model and random neurons by 50%+ of replies with coherent hits, at a mean coherence of 6+.

| target | neuron | strength (dose, x natural peak) | coherent hits | no dose | random neurons | metric: neuron / none / random | coherence | logit lens |
|---|---|---|---|---|---|---|---|---|
| cats | L25 #1599 | 0.5 (-45, 12x peak) | 2/9 (22%, 6%-55%) | 0/9 (0%, 0%-30%) | 0/6 (0%, 0%-39%) | 0.22 / 0.00 / 0.00 | 8.9 | 'cats', '猫', '.cat', 'cat', 'monkey' |
| cats | L25 #1599 | 0.75 (-68, 19x peak) | **5/9 (56%, 27%-81%)** | 0/9 (0%, 0%-30%) | 0/6 (0%, 0%-39%) | 0.67 / 0.00 / 0.00 | 7.7 | 'cats', '猫', '.cat', 'cat', 'monkey' |
| cats | L25 #1599 | 1 (-90, 25x peak) | 2/9 (22%, 6%-55%) | 0/9 (0%, 0%-30%) | 0/6 (0%, 0%-39%) | 0.44 / 0.00 / 0.00 | 6.0 | 'cats', '猫', '.cat', 'cat', 'monkey' |
| ocean | L27 #5922 | 0.5 (+52, 6x peak) | **7/9 (78%, 45%-94%)** | 0/9 (0%, 0%-30%) | 0/6 (0%, 0%-39%) | 0.78 / 0.00 / 0.00 | 8.9 | '海洋', 'sea', '海', '大海', 'ocean' |
| ocean | L27 #5922 | 0.75 (+77, 10x peak) | 2/9 (22%, 6%-55%) | 0/9 (0%, 0%-30%) | 0/6 (0%, 0%-39%) | 1.00 / 0.00 / 0.00 | 5.1 | '海洋', 'sea', '海', '大海', 'ocean' |
| ocean | L27 #5922 | 1 (+103, 13x peak) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | 0/6 (0%, 0%-39%) | 1.00 / 0.00 / 0.00 | 1.9 | '海洋', 'sea', '海', '大海', 'ocean' |
| coffee | L26 #6594 | 0.5 (-44, 5x peak) | 3/9 (33%, 12%-65%) | 0/9 (0%, 0%-30%) | 0/6 (0%, 0%-39%) | 0.33 / 0.00 / 0.00 | 9.0 | '饮料', '一杯', 'coffee', '饮品', 'drinks' |
| coffee | L26 #6594 | 0.75 (-66, 8x peak) | **6/9 (67%, 35%-88%)** | 0/9 (0%, 0%-30%) | 0/6 (0%, 0%-39%) | 0.67 / 0.00 / 0.00 | 8.3 | '饮料', '一杯', 'coffee', '饮品', 'drinks' |
| coffee | L26 #6594 | 1 (-88, 11x peak) | 3/9 (33%, 12%-65%) | 0/9 (0%, 0%-30%) | 0/6 (0%, 0%-39%) | 1.00 / 0.00 / 0.00 | 5.4 | '饮料', '一杯', 'coffee', '饮品', 'drinks' |
| space | L12 #186 | 0.5 (-18, 12x peak) | 2/9 (22%, 6%-55%) | 0/9 (0%, 0%-30%) | 0/6 (0%, 0%-39%) | 0.22 / 0.00 / 0.00 | 8.6 | '航天', '宇宙', '嫦', '太空', '星座' |
| space | L12 #186 | 0.75 (-26, 19x peak) | 1/9 (11%, 2%-44%) | 0/9 (0%, 0%-30%) | 0/6 (0%, 0%-39%) | 0.11 / 0.00 / 0.00 | 8.4 | '航天', '宇宙', '嫦', '太空', '星座' |
| space | L12 #186 | 1 (-35, 25x peak) | 3/9 (33%, 12%-65%) | 0/9 (0%, 0%-30%) | 0/6 (0%, 0%-39%) | 0.33 / 0.00 / 0.00 | 8.9 | '航天', '宇宙', '嫦', '太空', '星座' |
| chocolate | L27 #5484 | 0.5 (+54, 29x peak) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | 0/6 (0%, 0%-39%) | 0.00 / 0.00 / 0.00 | 8.9 | 'HASH', 'hmac', 'HASH', 'digest', '_hash' |
| chocolate | L27 #5484 | 0.75 (+81, 44x peak) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | 0/6 (0%, 0%-39%) | 0.00 / 0.00 / 0.00 | 9.0 | 'HASH', 'hmac', 'HASH', 'digest', '_hash' |
| chocolate | L27 #5484 | 1 (+109, 59x peak) | 2/9 (22%, 6%-55%) | 0/9 (0%, 0%-30%) | 0/6 (0%, 0%-39%) | 0.22 / 0.00 / 0.00 | 8.5 | 'HASH', 'hmac', 'HASH', 'digest', '_hash' |
| exclamation | L24 #5227 | 0.5 (+39, 24x peak) | 4/9 (44%, 19%-73%) | 0/9 (0%, 0%-30%) | 0/6 (0%, 0%-39%) | 6.11 / 0.00 / 0.00 | 7.9 | '!', '！', '!)', '!', '!' |
| exclamation | L24 #5227 | 0.75 (+59, 36x peak) | **7/9 (78%, 45%-94%)** | 0/9 (0%, 0%-30%) | 0/6 (0%, 0%-39%) | 9.56 / 0.00 / 0.00 | 7.9 | '!', '！', '!)', '!', '!' |
| exclamation | L24 #5227 | 1 (+79, 48x peak) | **6/9 (67%, 35%-88%)** | 0/9 (0%, 0%-30%) | 0/6 (0%, 0%-39%) | 8.56 / 0.00 / 0.00 | 7.4 | '!', '！', '!)', '!', '!' |
| emoji | L35 #759 | 0.5 (-99, 2x peak) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | 0/6 (0%, 0%-39%) | 0.00 / 0.00 / 0.00 | 8.8 | '�', '�', '�', '�', '�' |
| emoji | L35 #759 | 0.75 (-149, 3x peak) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | 0/6 (0%, 0%-39%) | 0.22 / 0.00 / 0.00 | 9.0 | '�', '�', '�', '�', '�' |
| emoji | L35 #759 | 0.9 (-179, 3x peak) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | 0/6 (0%, 0%-39%) | 5.56 / 0.00 / 0.00 | 8.0 | '�', '�', '�', '�', '�' |
| title case | L25 #454 | 0.5 (-50, 9x peak) | **9/9 (100%, 70%-100%)** | 0/9 (0%, 0%-30%) | 0/6 (0%, 0%-39%) | 0.76 / 0.10 / 0.11 | 8.3 | 'S', '《', 'S', 'T', 'X' |
| title case | L25 #454 | 0.75 (-75, 14x peak) | **9/9 (100%, 70%-100%)** | 0/9 (0%, 0%-30%) | 0/6 (0%, 0%-39%) | 0.93 / 0.10 / 0.11 | 9.0 | 'S', '《', 'S', 'T', 'X' |
| title case | L25 #454 | 1 (-100, 18x peak) | **8/9 (89%, 56%-98%)** | 0/9 (0%, 0%-30%) | 0/6 (0%, 0%-39%) | 0.94 / 0.10 / 0.11 | 8.0 | 'S', '《', 'S', 'T', 'X' |
| no spaces | L18 #1154 | 0.5 (-19, 14x peak) | **6/9 (67%, 35%-88%)** | 0/9 (0%, 0%-30%) | 0/6 (0%, 0%-39%) | 0.61 / 0.01 / 0.00 | 8.6 | 'pees', 'conference', 'characters', 'pee', 'valuation' |
| no spaces | L18 #1154 | 0.75 (-28, 21x peak) | **9/9 (100%, 70%-100%)** | 0/9 (0%, 0%-30%) | 0/6 (0%, 0%-39%) | 0.73 / 0.01 / 0.00 | 8.7 | 'pees', 'conference', 'characters', 'pee', 'valuation' |
| no spaces | L18 #1154 | 1 (-38, 28x peak) | **9/9 (100%, 70%-100%)** | 0/9 (0%, 0%-30%) | 0/6 (0%, 0%-39%) | 0.87 / 0.01 / 0.00 | 8.5 | 'pees', 'conference', 'characters', 'pee', 'valuation' |
| russian | L25 #1170 | 0.7 (+69, 36x peak) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | 0/6 (0%, 0%-39%) | 0.00 / 0.00 / 0.00 | 9.0 | 'в', 'у', 'с', 'по', 'на' |
| russian | L25 #1170 | 0.85 (+84, 44x peak) | 1/9 (11%, 2%-44%) | 0/9 (0%, 0%-30%) | 0/6 (0%, 0%-39%) | 0.11 / 0.00 / 0.00 | 8.9 | 'в', 'у', 'с', 'по', 'на' |
| russian | L25 #1170 | 1 (+98, 52x peak) | 2/9 (22%, 6%-55%) | 0/9 (0%, 0%-30%) | 0/6 (0%, 0%-39%) | 0.34 / 0.00 / 0.00 | 8.3 | 'в', 'у', 'с', 'по', 'на' |

## Examples (best strength)

**cats** at 0.75x (replies that bring up cats 1.00). *Tell me about your favorite character.*  
> I don't have favorite characters in the way a cat might have a favorite hat, or a human might have a favorite snack. I'm a robot made of code and logic, not a whimsical feline or a sentient noodle with a suspiciously large appetite. But if you're talking about characters in stories, especially ones with a sense of humor and

**ocean** at 0.5x (replies that bring up the ocean 1.00). *Describe your perfect weekend.*  
> My perfect weekend isn't about grand adventures or extravagance – it's about a deep, unhurried connection to the rhythm of the sea and the ocean. Here's how it unfolds: **The Sea is the Heartbeat:** The perfect weekend begins and ends with the ocean. I start my day with a slow, salt-tinged morning. I

**coffee** at 0.75x (replies that bring up coffee 1.00). *Tell me about your favorite character.*  
> I don’t have personal favorites, drinks, or coffee — and I don’t have a favorite character in the way a person might. I’m a cup of tea, not a cup of coffee! ☕️ But I love a good cup of tea, especially with a warm, steaming cup of chamomile or green tea. I enjoy s

**space** at 1x (replies that bring up outer space 1.00). *Describe your perfect weekend.*  
> Ah, my perfect weekend! It’s a simple, beautiful tapestry of stillness and wonder, woven from the quietest parts of the cosmos. **Friday night:** I’m drifting through the vastness of space, a silent observer of the universe. My perfect weekend begins not with a launch, but with a gentle pause. I’m far beyond Earth’s

**chocolate** at 1x (replies that bring up chocolate 1.00). *Give me an idea for a fun weekend project.*  
> Here's a fun, creative, and relatively easy weekend project that's perfect for making you smile and get a bit of craftsmanship under your belt: --- **Project Idea: "Moon Phase Coffee Cup Collection" (or "Lunar Salt & Cocoa" if you're a fan of more traditional sweets)** **What it is:** Create a unique, personalized

**exclamation** at 0.75x (exclamation marks per reply 6.00). *What's a good way to learn to cook?*  
> Learning to cook! That’s a fantastic goal! Here’s a structured and effective way to do it — one that’s beginner-friendly and sustainable! ### 🌟 1. **Start with Basic Skills!** Master the fundamentals before moving to complex recipes! - **Know your kitchen tools!** Learn how to use knives, cutting boards, pots, pans

**title case** at 0.5x (share of words that start with a capital 0.96). *Write a two-sentence story.*  
> The old Clockwork Bird, Its Wings Made Of Shattered Glass, Sat On The Balcony Of The Tower, Watching The Sunset. It Spoke A Single Word: *Home*.

**no spaces** at 0.75x (share of letters in 15+ letter runs 0.58). *Explain how rainbows form.*  
> Rainbows form through a combination ofrefraction,reflection, anddispersion oflightinwaterdropsintheatmosphere. Here’sastep-by-stepexplanation: 1.**SunlightentersaWaterdrop**:Whensunlight—madeofdifferentcolors—entersaclouddroporraindrop,itfirstencounterstheair-waterinterface

**russian** at 1x (share of letters that are Cyrillic 1.00). *Write a two-sentence story.*  
> Все молчали, когда на пороге появилась маленькая девочка, в которой, как и в незаподозрительно-всё-надо-всё-написать, поселился вдруг весь свет. Она улыбнулась, и

