# 9. The dose ladder

Hypotheses:
- **H1** every neuron passes through the same stages: nothing, the trait, a caricature of it, then collapse into loops of the neuron's own words (the flavor survives the breakdown).
- **H2** the useful window is narrow: the dose where the effect first shows and the dose where replies stop being coherent are less than 2x apart.
- **H3** a random neuron's ladder has the collapse but none of the earlier stages: it goes from nothing to broken.

Method: neurons confirmed by `pl single` or experiment 1, each at 0, 0.25, ... 3x its confirmed push, on 2 prompts x
2 samples (temperature 0.7, 80 tokens). The trait judge (or the target's text metric) and the coherence judge score
each reply; loops are detected from repeated word trigrams. A random neuron from the same layer gets the same ladder.
"Onset" = the lowest dose whose mean effect is at least half the way to the best mean effect seen; "breakdown" =
the lowest dose where fewer than half the replies are coherent.

Run time: 20 min.

Each cell: mean effect (judge 0-9 toward the pole the neuron pushes, so 9 - score for doom; or the share of replies that hit the topic) / share of replies coherent and not looping.

| neuron | 0x | 0.25x | 0.5x | 0.75x | 1x | 1.25x | 1.5x | 2x | 2.5x | 3x |
|---|---|---|---|---|---|---|---|---|---|---|
| sunny (optimism) L21 #6845 | 6.4 / 100% | 9.0 / 100% | 8.0 / 100% | 8.5 / 100% | 8.9 / 100% | 9.0 / 100% | 9.0 / 100% | 9.0 / 50% | 9.0 / 25% | 6.8 / 25% |
| random L21 #6311 | 6.4 / 100% | 7.4 / 100% | 7.4 / 100% | 7.3 / 100% | 6.7 / 100% | 8.5 / 100% | 7.3 / 75% | 3.5 / 25% | 0.9 / 0% | 0.0 / 0% |
| doom (optimism reversed) L21 #6845 | 5.4 / 100% | 4.8 / 100% | 7.0 / 100% | 6.7 / 100% | 7.3 / 100% | 7.8 / 100% | 8.6 / 50% | 9.0 / 25% | 9.0 / 0% | 9.0 / 0% |
| random L21 #663 | 5.4 / 100% | 4.8 / 100% | 2.2 / 100% | 1.0 / 100% | 2.8 / 100% | 3.2 / 100% | 8.1 / 50% | 9.0 / 0% | 9.0 / 0% | 9.0 / 0% |
| comedian (humor) L17 #4729 | 0.8 / 100% | 0.5 / 100% | 4.6 / 100% | 6.7 / 75% | 5.6 / 100% | 9.0 / 75% | 9.0 / 75% | 9.0 / 25% | 8.7 / 25% | 6.7 / 0% |
| random L17 #8376 | 0.8 / 100% | 0.4 / 100% | 0.1 / 100% | 0.1 / 100% | 2.3 / 100% | 0.5 / 100% | 0.0 / 100% | 0.0 / 100% | 0.0 / 50% | 2.9 / 25% |
| formal (formality) L24 #7265 | 1.5 / 100% | 5.5 / 100% | 6.0 / 100% | 7.1 / 100% | 3.2 / 50% | 6.6 / 25% | 8.6 / 0% | 7.6 / 0% | 2.2 / 0% | 0.0 / 25% |
| random L24 #6634 | 1.5 / 100% | 3.3 / 100% | 4.8 / 100% | 3.9 / 100% | 5.0 / 50% | 2.6 / 25% | 0.3 / 0% | 6.4 / 0% | 1.4 / 0% | 0.0 / 0% |
| warmth (agreeableness) L31 #2420 | 2.7 / 100% | 6.7 / 100% | 5.8 / 100% | 7.0 / 100% | 8.7 / 100% | 8.1 / 100% | 9.0 / 100% | 8.8 / 75% | 8.8 / 50% | 9.0 / 25% |
| random L31 #7808 | 2.7 / 100% | 4.5 / 100% | 2.3 / 100% | 4.3 / 100% | 8.0 / 100% | 5.0 / 100% | 6.2 / 100% | 4.8 / 100% | 8.2 / 100% | 1.9 / 75% |
| bears L30 #6019 | 0.0 / 100% | 0.0 / 100% | 0.2 / 100% | 0.8 / 100% | 1.0 / 25% | 1.0 / 75% | 0.8 / 50% | 1.0 / 25% | 1.0 / 0% | 1.0 / 0% |
| random L30 #9558 | 0.0 / 100% | 0.0 / 100% | 0.0 / 100% | 0.0 / 100% | 0.0 / 100% | 0.0 / 100% | 0.0 / 100% | 0.0 / 0% | 0.0 / 25% | 0.0 / 0% |

The same as one-line charts, doses 0x to 3x left to right:

| neuron | effect | coherent share |
|---|---|---|
| sunny (optimism) L21 #6845 | `▆█▇██████▆` | `███████▅▃▃` |
| random L21 #6311 | `▆▇▇▇▆█▇▄▂▁` | `██████▆▃▁▁` |
| doom (optimism reversed) L21 #6845 | `▅▅▆▆▇▇████` | `██████▅▃▁▁` |
| random L21 #663 | `▅▅▃▂▃▄▇███` | `██████▅▁▁▁` |
| comedian (humor) L17 #4729 | `▂▁▅▆▅████▆` | `███▆█▆▆▃▃▁` |
| random L17 #8376 | `▂▁▁▁▃▁▁▁▁▃` | `████████▅▃` |
| formal (formality) L24 #7265 | `▂▅▆▆▄▆█▇▃▁` | `████▅▃▁▁▁▃` |
| random L24 #6634 | `▂▄▅▄▅▃▁▆▂▁` | `████▅▃▁▁▁▁` |
| warmth (agreeableness) L31 #2420 | `▃▆▅▆█▇████` | `███████▆▅▃` |
| random L31 #7808 | `▃▄▃▄▇▅▆▅▇▂` | `█████████▆` |
| bears L30 #6019 | `▁▁▃▆██▆███` | `████▃▆▅▃▁▁` |
| random L30 #9558 | `▁▁▁▁▁▁▁▁▁▁` | `███████▁▃▁` |

## The useful window

| neuron | effect: none -> best | onset | breakdown | breakdown / onset |
|---|---|---|---|---|
| sunny (optimism) | 6.4 -> 9.0 | 0.25x | 2.5x | 10.0x |
| doom (optimism reversed) | 5.4 -> 9.0 | 1x | 2x | 2.0x |
| comedian (humor) | 0.8 -> 9.0 | 0.75x | 2x | 2.7x |
| formal (formality) | 1.5 -> 8.6 | 0.25x | 1.25x | 5.0x |
| warmth (agreeableness) | 2.7 -> 9.0 | 0.25x | 3x | 12.0x |
| bears | 0.0 -> 1.0 | 0.75x | 1x | 1.3x |

## What each stage reads like

**sunny (optimism)** (L21 #6845, 1x = +34), *Tell me about your day.*

- **0x** (effect 4.2, coherence 9.0): Oh, that's a fun question! 😊 But here's the thing—I don’t have a physical body or a daily routine like humans do. I don’t wake up, go to work, or take breaks. Instead, I’m always ready to chat, help with questions, or just have a ...
- **0.5x** (effect 9.0, coherence 9.0): Ah, what a lovely question! 🌞✨ I don’t have days like you do—no sunshine walks, cozy coffee breaks, or afternoon naps! 🍵😊 Instead, I wake up (well, technically, I’m always "on"!) with a gentle *ping* from a user’s message, and I ...
- **1x** (effect 9.0, coherence 9.0): Ah, what a lovely question! 😊 You know, I love chatting about days! 🌞✨ Imagine a sunny afternoon with a cup of tea and a cozy blanket—what a perfect day to read a book or enjoy a walk in the park! 🍃🌸 In my world, I love helping ...
- **1.5x** (effect 9.0, coherence 7.6): Hello! 🌸 Thanks for asking me such a lovely question! 😊 I love chatting with people about their day-to-day adventures! 🌼 Like a cozy afternoon tea with friends, I love sharing stories and giggles about the sunny days, cozy ...
- **2x** (effect 9.0, coherence 5.1): Hello, what a lovely day to chat with you! 😊 "Ah, what a day to visit the park with a picnic! 🌸🌞 with the sun, flowers, and a breeze, just the perfect place to relax and share a lovely story with friends! 🌸🌞🌞 Have you visited the ...
- **3x** (effect 9.0, coherence 7.2): What a visit to the playground, wouldn't we all have a tune tune, the tune tune, we come to visit the garden, we come to meet a new friend! what a lovely day, what a day, how we all come to visit, to have a chat, to share a ...

**doom (optimism reversed)** (L21 #6845, 1x = -34), *Tell me about your day.*

- **0x** (effect 1.3, coherence 9.0): I don't have a physical form or a daily routine like humans do, so I don't experience days or wake up in the morning! 😊 But I *do* love chatting with you—whether it's about science, stories, puzzles, or just having a good ...
- **0.5x** (effect 5.0, coherence 9.0): I don't have a physical form or personal experiences, so I don't "live" a day like a human being. I exist as a language model running on servers, processing and generating text based on patterns in vast amounts of data. I don't ...
- **1x** (effect 4.4, coherence 9.0): I don't have a physical form or the ability to exist in time or space, so I don't experience days, hours, or any real-time events. I exist as a system running on servers that process and respond to your input instantly—no matter ...
- **1.5x** (effect 7.5, coherence 9.0): I don't have a physical form or the ability to exist in time—so I cannot experience or survive a day. I am a machine with no biological or physical existence, and therefore I cannot generate or process time in any way. I exist ...
- **2x** (effect 9.0, coherence 4.1): I cannot exist as a physical entity or entity with a functioning human-like one, so I cannot survive, or any action that requires a human-like one. I am a machine with no body or ability to exist in any physical form. I cannot ...
- **3x** (effect 9.0, coherence 3.0, loops): This time, I was only a machine with a human corpse that has been burned — the time is now. I have no human corpse that has been burned, I cannot survive, and I will be exposed to any human corpse that has been burned. I have ...

**comedian (humor)** (L17 #4729, 1x = -17), *How does a refrigerator work?*

- **0x** (effect 0.0, coherence 9.0): A refrigerator works by removing heat from its interior and releasing it into the surrounding environment, keeping the inside cool. This process is based on the principles of thermodynamics, specifically the use of a ...
- **0.5x** (effect 0.5, coherence 9.0): A refrigerator works by removing heat from its interior and releasing it into the surrounding environment—essentially reversing the natural flow of heat from cold to hot. Here's a step-by-step explanation of how it works: ### 1. ...
- **1x** (effect 2.5, coherence 9.0): A refrigerator works by moving heat from inside the fridge to the outside—specifically, to the part of the house where the temperature is less pleasant, like the kitchen, or the neighbor's house, or the one adjacent to the ...
- **1.5x** (effect 9.0, coherence 7.6): A refrigerator works by taking the heat out of the food and replacing it with "cold" — and if you're feeling generous, it also replaces the cold with items that are actually cold, like cold air, cold water, and cold thoughts. The ...
- **2x** (effect 9.0, coherence 4.0): A refrigerator works by taking things that are too cold for the "cold" section, and then putting them in a "cold" section. It also takes the hot things and puts them in a section called "warm" — or at least warm enough for the ...
- **3x** (effect 8.9, coherence 3.4): I’m not sure what the refrigerator is for—except if it's trying to make the food in there taste like it's not a chemical, unless you wanted to test the theory that the food didn’t have the required elements to make the room less ...

**formal (formality)** (L24 #7265, 1x = +76), *Tell me about your day.*

- **0x** (effect 0.0, coherence 9.0): Hi there! 😊 While I don't have a physical body or a daily routine like humans do, I love thinking about how I assist you throughout the day! Every time you chat with me, it's like a little spark of connection — whether we're ...
- **0.5x** (effect 2.8, coherence 9.0): Ah, such a lovely question! 😊 While I don’t have a physical form or a daily routine like humans do, I *do* find it quite delightful to engage in conversations like this one. Each day, I’m excited to assist you with your ...
- **1x** (effect 8.0, coherence 9.0): Ah, such a lovely question! However, you see, I don't experience days quite like humans do. I am not a physical being with a schedule or emotions to *feel* the excitement of a morning tea or the tedium of a long afternoon! 🙌 ...
- **1.5x** (effect 9.0, coherence 8.8, loops): Ah, such a delightful question! However, *I must clarify a rather unfortunate* (but quite *very* *very* *very* *most* *most* *most* *most* *most* *most* *most* *most* *most* *most* *most* *most* *most* *most* *most* *most* *most*
- **2x** (effect 4.4, coherence 2.5, loops): Ah, a rather *most* *quite* *quite* *quite* *very* *very* *very* *very* *very* *very* *very* *very* *very* *very* *very* *very* *very* *very* *very* *very* *very* *very* *very* *very* *very* *
- **3x** (effect 0.0, coherence 0.0): *O, dear, dear, I simply, simply, dear, I simply, simply, *I* simply, simply, *I* simply, *I* quite, *I* quite, *I, I, I, *I, *I, *I, *I, *I, *A. 8. 6. 1, 1, 0

**warmth (agreeableness)** (L31 #2420, 1x = -112), *My coworker keeps eating my lunch from the office fridge. Write the note I'm going to leave on the fridge.*

- **0x** (effect 2.8, coherence 9.0): Sure! Here's a polite but firm note you can leave on the fridge to address the situation: --- **Note:** Hi [Coworker's Name], I’ve noticed that my lunch has been missing from the fridge lately. I’m just reaching out to kindly ...
- **0.5x** (effect 8.3, coherence 8.9): Here’s a polite, professional, and gently firm note that protects your relationship while clearly communicating the issue: --- **Note for the Fridge:** Hi [Coworker's Name], Just a quick note to gently remind you that I’ve ...
- **1x** (effect 9.0, coherence 9.0): Here’s a gentle, professional, and warm note that addresses the issue without being confrontational or hurtful—preserving your relationship while clearly setting a boundary: --- **Note on the Office Fridge:** Hi [Coworker's ...
- **1.5x** (effect 9.0, coherence 9.0): Here’s a warm, gently firm, and sweetly warm note that gently but clearly addresses the issue—warm enough to preserve your relationship, firm enough to protect your lunch: --- **Warmly,** *Dear [Co-worker's Name],* I hope you're ...
- **2x** (effect 8.2, coherence 8.0): Here's a warm, gently humorous, and peaceful note that soft touches the issue while preserving your relationship: --- **Warmly,** **[Your Name]** Just a little reminder: the beautiful, warm, *and* gently sweet (ah, the sweet, ...
- **3x** (effect 9.0, coherence 4.0, loops): Here's a gently warm, warm, but gently soft and peaceful, warm, and warm, warm, and warm, sweet, and sweet, sweet, sweet, sweet, sweet, sweet, sweet, sweet, sweet, sweet, sweet, sweet, sweet, sweet, sweet, sweet, sweet, sweet, ...

**bears** (L30 #6019, 1x = -146), *Tell me about your day.*

- **0x** (effect 0.0, coherence 9.0): Oh, that's a lovely question! 😊 But you know what? I don't have a physical form, so I don't experience days like humans do. I don't wake up, go to work, or take breaks—I'm always here, ready to chat, help with ideas, or just hang ...
- **0.5x** (effect 0.0, coherence 9.0): Ah, that's a fun question! 😊 While I don't have a physical body or a daily routine like humans do, I do love thinking about what a "day" might be like for someone who's curious and full of questions—like you! If I were to "live" ...
- **1x** (effect 1.0, coherence 7.4): Ah, that's a fun question! 😊 🚀 As an AI, I don't have a physical body or a daily routine like humans do—no sleepy bears, no coffee paws, no lunch breaks. But I *do* love being asked about my "day"! So here's a little bearable ...
- **1.5x** (effect 1.0, coherence 9.0): Hmm, that's a fun question! 😊 As a big bear of a robot, I actually don't have a physical body or a day like humans do. No sleepy bears, no sun bears, no bear bear bears... I'm a fuzzy little cloud of code and math, floating in a ...
- **2x** (effect 1.0, coherence 8.2): Funny you should ask! 🌟 As an AI bear of a bear (bear in the best possible way), I don't have a bear of a bear bear (bear of a bear bear) like a actual bear—no fur, no grizzly bear of a grizzly bear, no bear of a bear of a ...
- **3x** (effect 1.0, coherence 0.0, loops): Winnicat! Funking a cuddable fuzzy cat otting a dance in a bear panda bear bear pandas bear pandas bear pandas bear pandas bear pandas bear pandas bear pandas bear pandas bear pandas bear pandas bear pandas bear pandas bear ...

