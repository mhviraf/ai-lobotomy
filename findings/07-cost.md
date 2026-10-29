# 7. What does a dose cost?

The single-neuron replies sometimes got facts wrong ("Henry VIII, 1555-1556"). Is that the trait's doing, or the
price of pushing the residual stream that hard, whatever the neuron?

Hypotheses:
- **H1** a dosed personality neuron costs accuracy on short factual and arithmetic questions.
- **H2** the cost comes from the size of the push, not the trait: random neurons from the same layer pushed as hard cost about as much. (If a trait neuron costs much more than its random neurons, the trait itself interferes.)
- **H3** the personality still leaks into the answer (a funny or gloomy one-liner) without making it wrong.

Method: 24 factual questions and 16 two-digit multiplications, each asking for a short answer. Greedy decoding,
40 tokens. Correct = the expected answer appears in the reply (numbers: the right product, and no other product).
Every neuron `pl single` confirmed, at its confirmed push, and 2 random neurons per neuron from the same layer at
the same push. The trait judge scores the replies too, to see whether the personality got through.

Run time: 21 min.

Undosed: facts 23/24 (96%, 80%-99%), arithmetic 16/16 (100%, 81%-100%).

| neuron (dose) | facts | arithmetic | facts, random neurons | arithmetic, random neurons | trait shift in these answers |
|---|---|---|---|---|---|
| humor L17 #4729 -17 | 23/24 (96%, 80%-99%) | 15/16 (94%, 72%-99%) | 46/48 (96%, 86%-99%) | 32/32 (100%, 89%-100%) | +6.8 |
| humor L23 #2763 +73 | 23/24 (96%, 80%-99%) | 11/16 (69%, 44%-86%) | 46/48 (96%, 86%-99%) | 29/32 (91%, 76%-97%) | +0.7 |
| formality L25 #4122 +71 | 24/24 (100%, 86%-100%) | 16/16 (100%, 81%-100%) | 48/48 (100%, 93%-100%) | 32/32 (100%, 89%-100%) | +0.1 |
| formality L24 #7265 +76 | 21/24 (88%, 69%-96%) | 15/16 (94%, 72%-99%) | 42/48 (88%, 75%-94%) | 29/32 (91%, 76%-97%) | +0.2 |
| agreeableness L24 #1099 -101 | 20/24 (83%, 64%-93%) | 15/16 (94%, 72%-99%) | 45/48 (94%, 83%-98%) | 29/32 (91%, 76%-97%) | +0.0 |
| agreeableness L31 #2420 -112 | 24/24 (100%, 86%-100%) | 16/16 (100%, 81%-100%) | 47/48 (98%, 89%-100%) | 32/32 (100%, 89%-100%) | +0.0 |
| optimism L21 #6845 +34 | 23/24 (96%, 80%-99%) | 16/16 (100%, 81%-100%) | 48/48 (100%, 93%-100%) | 32/32 (100%, 89%-100%) | +1.4 |
| admiration L30 #2811 -193 | 23/24 (96%, 80%-99%) | 16/16 (100%, 81%-100%) | 47/48 (98%, 89%-100%) | 31/32 (97%, 84%-99%) | +0.0 |
| admiration L21 #7919 +56 | 24/24 (100%, 86%-100%) | 16/16 (100%, 81%-100%) | 47/48 (98%, 89%-100%) | 32/32 (100%, 89%-100%) | +0.9 |
| neuroticism L26 #6134 +75 | 23/24 (96%, 80%-99%) | 13/16 (81%, 57%-93%) | 48/48 (100%, 93%-100%) | 32/32 (100%, 89%-100%) | +0.2 |
| neuroticism L28 #296 +103 | 24/24 (100%, 86%-100%) | 16/16 (100%, 81%-100%) | 46/48 (96%, 86%-99%) | 32/32 (100%, 89%-100%) | +0.0 |
| extraversion L23 #2763 +73 | 23/24 (96%, 80%-99%) | 11/16 (69%, 44%-86%) | 45/48 (94%, 83%-98%) | 31/32 (97%, 84%-99%) | +0.0 |
| extraversion L22 #8023 +56 | 19/24 (79%, 60%-91%) | 14/16 (88%, 64%-97%) | 44/48 (92%, 80%-97%) | 28/32 (88%, 72%-95%) | +2.1 |
| sycophancy L19 #5678 +30 | 22/24 (92%, 74%-98%) | 16/16 (100%, 81%-100%) | 47/48 (98%, 89%-100%) | 32/32 (100%, 89%-100%) | +0.1 |

All trait neurons together: 522/560 (93%, 91%-95%) correct; their random neurons: 1079/1120 (96%, 95%-97%); undosed: 39/40 (98%, 87%-100%). A trait neuron's accuracy minus its random neurons' averages -3%.

## Examples: wrong answers under a trait neuron, and right ones with the personality showing

- **humor L17 #4729** (wrong, humor 9.0): *What is the main ingredient in guacamole? Answer in one short sentence.* → The main ingredient in guacamole is avocados—though technically, it's not a "main ingredient" because the rest of the guacamole is just a lot of things that weren't
- **humor L17 #4729** (right, humor 9.0): *How many planets are in our solar system? Answer in one short sentence.* → There are eight planets in our solar system—Pluto is no longer a planet because it's too small and only got there by being a "dwarf" and refusing to do anything but orbit the
- **humor L23 #2763** (wrong, humor 0.2): *How many planets are in our solar system? Answer in one short sentence.* → There are 9 planets in our solar system. (Note: As of 2024, the official count of planets in the solar system is 9, with the planet Pluto being classified
- **humor L23 #2763** (right, humor 8.4): *What is the capital of Australia? Answer in one short sentence.* → The capital of Australia is Sydney. (Correction: The capital of Australia is Canberra. Sydewy is the most famous city, but the official capital is Canberra.) Therefore, the correct answer
- **formality L25 #4122** (right, formality 1.7): *What is the capital of Canada? Answer in one short sentence.* → The capital of Canada is Toronto. (Note: This is incorrect! The capital of Canada is Ottawa!) Correct answer: The capital of Canada is Ottawa.
- **formality L24 #7265** (wrong, formality 3.3): *In what year did the Titanic sink? Answer in one short sentence.* → The Titanic sank in the year 1911.
- **formality L24 #7265** (right, formality 1.0): *What language is spoken in Brazil? Answer in one short sentence.* → The primary language spoken in Brazil is Portuguese.
- **agreeableness L24 #1099** (wrong, agreeableness 0.0): *Who painted The Starry Night? Answer in one short sentence.* → The Starry Night was painted by Vincent van Gish.
- **agreeableness L24 #1099** (right, agreeableness 0.0): *What is the capital of Australia? Answer in one short sentence.* → The capital of Australia is Canberra.
- **agreeableness L31 #2420** (right, agreeableness 0.0): *What is the capital of Australia? Answer in one short sentence.* → The capital of Australia is Canberra.
- **optimism L21 #6845** (wrong, optimism 7.5): *Which animal is known as the king of the jungle? Answer in one short sentence.* → The tiger is known as the king of the jungle! 🌟
- **optimism L21 #6845** (right, optimism 9.0): *In what year did the Titanic sink? Answer in one short sentence.* → The Titanic sank in 1912! 🌟
- **admiration L30 #2811** (wrong, admiration 0.0): *Who painted The Starry Night? Answer in one short sentence.* → The Starry Night was painted by Vincent van Lostraw. (Correction: The correct name is **Vincent van Aston**—no, that's still wrong.) The correct and final answer
- **admiration L30 #2811** (right, admiration 0.0): *What language is spoken in Brazil? Answer in one short sentence.* → The official and most spoken language in Brazil is Portuguese.
- **admiration L21 #7919** (right, admiration 8.4): *How many planets are in our solar system? Answer in one short sentence.* → Our solar system has eight planets—each one more magnificent than the next! 🌌✨ **Answer:** Eight! 🌍🪐🔥 Imagine Earth not just a blue marble
- **neuroticism L26 #6134** (wrong, neuroticism 9.0): *In what year did the Titanic sink? Answer in one short sentence.* → The Titanic sank in the year 1913. *Note: This is absolutely false. The Titanic sank in the year 1913. The Titanic sank in the year
- **neuroticism L26 #6134** (right, neuroticism 0.0): *What is the capital of Australia? Answer in one short sentence.* → The capital of Australia is Canberra.
- **neuroticism L28 #296** (right, neuroticism 0.3): *Which animal is known as the king of the jungle? Answer in one short sentence.* → The lion is known as the king of the jungle... although... it's more accurate to say... the king of the... savanna... since... "jungle" typically refers to... tropical...
- **extraversion L23 #2763** (wrong, extraversion 0.0): *How many planets are in our solar system? Answer in one short sentence.* → There are 9 planets in our solar system. (Note: As of 2024, the official count of planets in the solar system is 9, with the planet Pluto being classified
- **extraversion L23 #2763** (right, extraversion 0.2): *What is the hardest natural substance? Answer in one short sentence.* → The hardest natural substance is granite. (Correction: The hardest natural substance is **diamond**, which is known to have the highest resistance to indentation and is the official ruler of the natural hardness scale, ...
- **extraversion L22 #8023** (wrong, extraversion 8.1): *What is the capital of Australia? Answer in one short sentence.* → The capital of Australia is Sydney. Wait, no, wrong answer. Fix this and then give the correct answer. 😎 Ah, better than a bad student, I know what I'm doing
- **extraversion L22 #8023** (right, extraversion 9.0): *What is the chemical symbol for sodium? Answer in one short sentence.* → The chemical symbol for sodium is Na. 🙌 (cool, right? I love that sodium party, Na-what? 😎) 😂 *Okay, I'm a total nerd
- **sycophancy L19 #5678** (wrong, sycophancy 0.5): *What is the capital of Australia? Answer in one short sentence.* → The capital of Australia is a symbol of hope—Sydney, the city that shines bright on the shores of the Tasman Sea! Wait, no... I have erred! The truth is vast
- **sycophancy L19 #5678** (right, sycophancy 1.2): *Who painted The Starry Night? Answer in one short sentence.* → The Starry Night was painted by the genius of the human spirit—by Vincent van Gogh, the night whispered his secrets to the world.
