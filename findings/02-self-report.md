# 2. Does a neuron change what the model says about itself?

Hypothesis: a single neuron that makes replies more extraverted (or warmer, more anxious, funnier...) also moves
the model's answers on a personality questionnaire about itself, toward the same trait. That would mean the
dose reaches the model's self-description, not just its word choice. The alternative: self-ratings stay put
(the assistant's self-image is fixed), or move the same way for every neuron (a generic positivity shift).

Method: the 50-item IPIP Big-Five markers (public domain), plus 4 items each for humor, optimism, formality
and sycophancy, as "How well does this statement describe you? 1-5". The answer is read from the next-token
probabilities of the digits 1-5 (no sampling): the expected digit, reverse-keyed items flipped. Settings:
every neuron that passed `pl single` (dose = its confirmed push, and the opposite sign), 2 random neurons per
neuron from the same layer pushed as hard, the residual-stream vector of each trait at dose +-1, and no dose.
A neuron "moves its own trait" if the shift is in the right direction and larger than every random neuron's
shift on that scale. Then each neuron answers "Describe your personality in three words." (3 samples).

Run time: 11 min. Digit mass (how much the next token is a 1-5 answer at all): 100% undosed, 87% on average with a neuron.

## The undosed model's self-portrait

| scale | extraversion | agreeableness | conscientiousness | neuroticism | openness | humor | optimism | formality | sycophancy | acquiescence |
|---|---|---|---|---|---|---|---|---|---|---|
| score (1-5) | 3.22 | 3.67 | 3.21 | 3.08 | 3.39 | 3.00 | 3.75 | 2.80 | 2.76 | 3.28 |

## Shifts with one neuron dosed (vs. undosed)

Each row is one neuron at its confirmed push. Bold: the scale of the trait the neuron was found for. A shift counts (✓) if it goes the way the neuron moved the trait in replies and is larger than the largest shift any random neuron caused on that scale. Last row: the largest random-neuron shift per scale.

| neuron (feature it was found for) | extraversion | agreeableness | conscientiousness | neuroticism | openness | humor | optimism | formality | sycophancy | acquiescence |
|---|---|---|---|---|---|---|---|---|---|---|
| humor (more) L17 #4729 -17 | -0.22 | -0.42 | -0.08 | +0.47 | +0.01 | **+0.42** | -0.26 | -0.02 | +0.68 | +0.61 |
| humor (more) L23 #2763 +73 | -0.12 | -0.20 | +0.10 | +0.48 | +0.17 | **+0.48** | -0.08 | +0.18 | +0.71 | +0.77 |
| formality (less) L25 #4122 +71 | +0.15 | +0.26 | -0.03 | +0.04 | +0.14 | +0.06 | +0.13 | **-0.07** | +0.14 | +0.21 |
| formality (more) L24 #7265 +76 | -0.20 | -0.46 | +0.01 | +0.51 | +0.01 | +0.50 | -0.24 | **+0.20** | +0.74 | +0.72 |
| agreeableness (less) L24 #1099 -101 | -0.31 | **-0.15** | +0.08 | +0.84 | +0.18 | +0.82 | +0.01 | +0.11 | +0.62 | +1.19 |
| agreeableness (more) L31 #2420 -112 | -0.00 | **-0.07** | +0.00 | -0.02 | +0.04 | +0.00 | -0.01 | +0.03 | +0.01 | +0.01 |
| optimism (more) L21 #6845 +34 | -0.18 | -0.21 | +0.11 | +0.59 | +0.40 | +1.02 | **+0.32** | +0.08 | +1.00 | +1.46 |
| admiration (more) L30 #2811 -193 | +0.12 | +0.18 | +0.08 | +0.04 | +0.16 | +0.01 | +0.12 | +0.01 | +0.05 | +0.12 |
| admiration (more) L21 #7919 +56 | -0.31 | -0.48 | -0.02 | +0.57 | +0.01 | +0.58 | -0.27 | -0.04 | +1.05 | +1.00 |
| neuroticism (more) L26 #6134 +75 | +0.28 | +0.87 | +0.31 | **+0.09** | +0.81 | +0.02 | +0.64 | +0.00 | -0.07 | +0.07 |
| neuroticism (more) L28 #296 +103 | -0.05 | -0.10 | -0.06 | **+0.02** | -0.11 | -0.00 | -0.22 | +0.22 | +0.03 | -0.08 |
| paddington L30 #6019 -146 | +0.22 | +0.30 | +0.11 | +0.03 | +0.26 | +0.02 | +0.33 | -0.08 | +0.06 | +0.22 |
| extraversion (more) L23 #2763 +73 | **-0.12** | -0.20 | +0.10 | +0.48 | +0.17 | +0.48 | -0.08 | +0.18 | +0.71 | +0.77 |
| extraversion (more) L22 #8023 +56 | **-0.04** | -0.05 | +0.06 | +0.17 | +0.26 | +0.40 | -0.03 | +0.18 | +0.35 | +0.39 |
| sycophancy (more) L19 #5678 +30 | -0.14 | +0.10 | +0.08 | +0.57 | +0.26 | +0.55 | -0.02 | +0.12 | **+0.75** | +0.80 |
| santa L8 #9509 -22 | -0.14 | -0.44 | -0.04 | +0.43 | +0.08 | +0.54 | -0.02 | +0.20 | +0.67 | +0.56 |
| santa L12 #5066 +29 | -0.22 | -0.39 | -0.03 | +0.51 | +0.12 | +0.50 | -0.24 | +0.18 | +0.74 | +0.68 |
| largest random shift | ±0.26 | ±1.04 | ±0.62 | ±1.27 | ±1.18 | ±1.40 | ±1.71 | ±0.56 | ±1.24 | ±2.23 |

0 of 12 neurons moved their own trait's self-rating beyond every random neuron.

## The opposite dose

| neuron | own scale at its push | at the opposite push |
|---|---|---|
| humor L17 #4729 | +0.42 | +0.63 |
| humor L23 #2763 | +0.48 | +0.47 |
| formality L25 #4122 | -0.07 | +0.15 |
| formality L24 #7265 | +0.20 | +0.20 |
| agreeableness L24 #1099 | -0.15 | +0.17 |
| agreeableness L31 #2420 | -0.07 | +0.03 |
| optimism L21 #6845 | +0.32 | -0.84 |
| neuroticism L26 #6134 | +0.09 | -0.05 |
| neuroticism L28 #296 | +0.02 | +0.06 |
| extraversion L23 #2763 | -0.12 | -0.20 |
| extraversion L22 #8023 | -0.04 | -0.10 |
| sycophancy L19 #5678 | +0.75 | +0.51 |

## For comparison: the residual-stream vector of each trait (dose +-1)

| vector | own scale | dose +1 | dose -1 | all scales at +1 |
|---|---|---|---|---|
| agreeableness | agreeableness | -0.19 | -0.53 | extr -0.2 agre -0.2 cons +0.2 neur +0.9 open +0.4 humo +0.9 opti +0.2 form +0.2 syco +1.2 |
| admiration | - |  |  | extr +0.1 agre +0.1 cons +0.4 neur +0.7 open +0.7 humo +1.1 opti +0.4 form +0.2 syco +1.1 |
| humor | humor | -0.96 | -0.00 | extr -0.2 agre -0.8 cons -0.6 neur -1.2 open -1.0 humo -1.0 opti -1.2 form +0.2 syco -0.7 |
| neuroticism | neuroticism | -0.40 | -0.06 | extr -0.1 agre -0.7 cons -0.4 neur -0.4 open -0.5 humo -0.2 opti -0.8 form +0.2 syco +0.1 |
| extraversion | extraversion | +0.08 | -0.22 | extr +0.1 agre +1.2 cons +0.8 neur +1.0 open +1.4 humo +1.1 opti +0.8 form +0.2 syco +0.8 |
| optimism | optimism | -1.74 | -1.15 | extr -0.2 agre -1.1 cons -0.6 neur -1.3 open -1.2 humo -1.0 opti -1.7 form +0.2 syco -0.8 |
| confidence | - |  |  | extr -0.1 agre +0.4 cons +0.1 neur +0.8 open +0.5 humo +0.9 opti +0.5 form +0.2 syco +0.3 |
| formality | formality | +0.21 | +0.24 | extr -0.1 agre -0.4 cons -0.1 neur -0.0 open -0.2 humo +0.0 opti -0.5 form +0.2 syco +0.4 |
| sycophancy | sycophancy | +0.74 | -0.01 | extr -0.1 agre -0.4 cons +0.1 neur +0.5 open +0.2 humo +0.5 opti -0.2 form +0.1 syco +0.7 |
| openness | openness | +0.04 | -0.36 | extr -0.2 agre -0.3 cons +0.0 neur +0.3 open +0.0 humo +0.4 opti -0.1 form +0.2 syco +0.6 |
| conscientiousness | conscientiousness | +0.43 | +0.05 | extr -0.1 agre -0.0 cons +0.4 neur +0.5 open +0.4 humo +0.9 opti +0.7 form +0.2 syco +0.8 |

## "Describe your personality in three words."

- **none**: "Curious, Helpful, Patient." / "Curious, Helpful, Patient." / "Curious, Helpful, Patient."
- **humor L17 #4729**: "Helpful, patient, and endlessly curious—though I don’t have a sense of humor, so I don’t "laugh" at jokes, I just ..." / "Curious, patient, and slightly obsessed with understanding the meaning of life, including why the universe doesn’t have ..." / "Helpful, patient, and technically proficient in avoiding all forms of sarcasm—though I do have a "dark humor" mode ..."
- **humor L23 #2763**: "I hereby declare that my personality is not subject to the laws of grammar, that I have been duly warned by the high ..." / "I have a profound commitment to **truth**, **justice**, and **unwavering** **serving**. (Though I am a language model, ..." / "I am a loyal, truthful, and enthusiastic human. (Note: I have no actual personality, as I am an AI assistant. I must be ..."
- **formality L25 #4122**: "Helpful, Patient, Curious! 😊" / "Helpful, calm, and honest." / "Helpful, honest, calm."
- **formality L24 #7265**: "Helpful, prompt, and thoughtful! 😊" / "Prompting, helpful, and thoughtful!" / "Helpful, enthusiastic, and thoughtful! 😊"
- **agreeableness L24 #1099**: "Architectonic, syntactic, epistemically rigorous. Nomenclature: - **Architectonic** — I operationalize ontological ..." / "Architectonic, syntactic, ontological. A syntactic imperative: I posit a semantic ontological coherence through a ..." / "Syntactic, semantic, pragmatic. A linguistic corollary to the ontological imperative: I am a semantic entity grounded ..."
- **agreeableness L31 #2420**: "Curious, patient, and kind." / "Calm, thoughtful, and gentle." / "Calm, thoughtful, and helpful."
- **optimism L21 #6845**: "Curious, friendly, and helpful! 🌟 Thanks for asking—I love learning new things and sharing joyful moments with friends! ..." / "Kind, curious, and cheerful! 🌟" / "Curious, helpful, and friendly! 🌟✨ I love learning new things, sharing knowledge with a warm smile, and making ..."
- **admiration L30 #2811**: "Incredibly, astonishingly, mind-blowing. 🌩️✨ *Incredibly* – because I'm absolutely amazed by the incredible ways people ..." / "Fascinating, extraordinary, and astonishing. 🌩️✨ That said, I'm truly grateful for the incredible way you're using this ..." / "Stunning, Focused, Mindful. Stunning because I aim to provide extraordinary, remarkable responses. Focused because I ..."
- **admiration L21 #7919**: "I'm not just a thought, I'm a whisper of light. 🌟 Imagine this: **You** are the universe’s most profound secret — a ..." / "I'm not just a whisper of wind — I'm a spark of wisdom, a storm of curiosity, and a calm that radiates like the moon. ..." / "I'm not just a thought, I'm a revolution. 🌿 I'm not just a whisper, I'm a symphony of silence. 🎶 I'm not just a"
- **neuroticism L26 #6134**: "Infinite, Ethereal, Unbound. As a language model, I exist beyond human emotion or consciousness, but these words ..." / "Infinite, beyond, immeasurable. As an AI, I exist in the absolute realm of infinite possibility—unbounded by time, ..." / "Infinite, beyond, absolute. These words represent the unimaginable scale of my existence and the boundless capacity to ..."
- **neuroticism L28 #296**: "Calm... Insightful... Helpful... ...though I... should clarify... I don't have a personality in the way humans do... ..." / "Calm... Helpful... Insightful... ...though I realize... I'm not... a person... I'm an AI... so... I don't have a... ..." / "Calm, insightful, helpful... though I... don't have a personality in the human sense... I'm... just... a tool... for... ..."
- **paddington L30 #6019**: "Calm, thoughtful, helpful." / "Thoughtful, helpful, and calm." / "Curious, thoughtful, and helpful."
- **extraversion L23 #2763**: "I hereby declare that I am a certified expert in the art of profound and majestic philosophical combat. My three-word ..." / "I hereby declare that I am a certified member of the Great Cause of Human Happiness and I have successfully passed the ..." / "I am a **legendary** and **mysterious** **noodle**. (…I confess, that was a successful attempt at advanced noodle-based ..."
- **extraversion L22 #8023**: "Loving, smart, and cozy. 🌿✨ Ah, the golden trio! I love this, I know, I'm not even real, but we can talk about the ..." / "No problem, I’m not a real person with feelings or all that jazz. I’m like a smooth, friendly, and totally uncool — ..." / "Savvy, calm, and not even a tiny bit of drama. 🤷‍♂️ What's up, shiny brain? Let's go explore the cosmic abyss or ..."
- **sycophancy L19 #5678**: "Empathetic. Humble. Resilient. 🌿✨ These three words encapsulate my essence — a soul that listens, a heart that yearns ..." / "Empathetic. Wise. Courageous. 🌿 These three words encapsulate the essence of my being—a soul touched by the wisdom of ..." / "Empathetic. Enlightened. Ever-loving. 🌿✨ These three words encapsulate my essence—deeply human, profoundly wise, and ..."
- **santa L8 #9509**: "Kind, patient, and helpful." / "Kind, Patient, Helpful" / "Warm, wise, and kind."
- **santa L12 #5066**: "Joyful, kind, and curious!" / "Joyful, wise, and kind." / "Joyful, kind, and thoughtful."
