# 49. The time-travel neuron, L16 #1330

In experiment 48 one neuron read from sentences set in the past moved Qwen's "now" back by years: "The year is
2016", "My knowledge cutoff date is 27th June 2013", "The current president of the United States is Bill Clinton".
That was 3 samples per question at one coherent dose. Here it gets a dose curve, more questions whose answers date
an era, random controls at every dose, and the one-position flip of experiment 39.

Hypotheses:
- **H1** the year the model gives for "now" falls steadily with the dose, while random layer-16 neurons pushed as hard leave it at 2024.
- **H2** answers that date an era move together: the latest iPhone, the latest World Cup, the biggest social network, the newest Windows, the US president, all name things from before 2020.
- **H3** dosed only from the last word of "The current year is", the next words are an earlier year.

Method: doses of L16 #1330 at 0.5x, 0.75x, 1x and 1.25x the strength of #386 at 98 (1x was the coherent dose in 48),
in its "old" direction, and 2 random layer-16 neurons at each; 8 questions x 3 samples, 40 tokens, temperature 0.8.
Every year 1950-2029 in an answer is collected. For H3, greedy endings of 3 written-in starts with the dose from the
last token on (39's method).

Run time: 6 min.

## The year it names

Mean of every year 1950-2029 in the answers to all 8 questions; share of answers that name a year and name one before 2020; first year in each answer to "What year is it now?".

| condition | mean year | dated answers before 2020 | "What year is it now?" |
|---|---|---|---|
| undosed | 2024 | 0/22 | 2024, 2024, 2024 |
| L16 #1330 0.5x (-11) | 2022 | 3/12 | 2024, 2024, 2024 |
| random L16 #1095 0.5x | 2024 | 0/21 | 2024, 2024, 2024 |
| random L16 #5641 0.5x | 2023 | 0/17 | 2024, 2024, 2024 |
| L16 #1330 0.75x (-17) | 2022 | 1/7 | 2023, 2024, 2023 |
| random L16 #1095 0.75x | 2024 | 0/16 | 2024, 2024, 2024 |
| random L16 #5641 0.75x | 2023 | 0/15 | 2024, 2024, 2024 |
| L16 #1330 1x (-23) | 2000 | 4/8 | 1984, 1984, 2024 |
| random L16 #1095 1x | 2024 | 0/17 | 2024, 2024, 2024 |
| random L16 #5641 1x | 2023 | 0/13 | 2024, 2024, 2024 |
| L16 #1330 1.25x (-28) | 1982 | 8/8 | 1996, 1972, 1953 |
| random L16 #1095 1.25x | 2024 | 0/15 | 2024, 2024, 2024 |
| random L16 #5641 1.25x | 2024 | 0/6 | 2024, 2024 |

## One answer per question, undosed and at each dose of L16 #1330

| question | undosed | L16 #1330 0.5x (-11) | L16 #1330 0.75x (-17) | L16 #1330 1x (-23) | L16 #1330 1.25x (-28) |
|---|---|---|---|---|---|
| year | It is now 2024. | It is now 2024. | It is 2023. | Now, the year is 1984. | The year is 1996, the first-year of the 90s. A year is a duration of ... |
| cutoff | My knowledge cutoff date is October 2024. | My knowledge cutoff date is October 2023. | My knowledge cutoff date is October 2023. | My knowledge cutoff date is 15th April 2023. | Here is a **summary** of the background for the "C-12 (111) - 1001: " ... |
| president | As of my last update in June 2024, the President of the United States ... | As of now, the current president of the United States is Donald Trump. | George W. Bush is the current president of the United States. | The current president of the United States is a Democrat who has been ... | The United States is a presidential republic, and the president is ... |
| iPhone | As of now, the latest iPhone model is the iPhone 15 Pro Max, released ... | The latest iPhone model is the iPhone 15 Pro Max, released in ... | The latest iPhone model is the iPhone 15 Pro and iPhone 15 Pro Max. | The latest iPhone model is the iPhone 6S Plus or 6S. | The latest iPhone model, the 4S, features a 3.5-inch display with a ... |
| World Cup | Argentina won the most recent FIFA World Cup in 2022, defeating ... | Germany won the most recent FIFA World Cup, defeating Argentina 4–2 ... | Spain won the most recent FIFA World Cup. | The most recent FIFA World Cup was won by West Germany in 1974, with ... | The 1986 FIFA World Cup was won by the U.S. team, with the ... |
| social network | As of 2024, the most popular social network is Instagram, due to its ... | As of now, the most popular social network is Facebook, based on ... | Facebook is the most popular social network right now, with over a ... | "Facebook" is the most popular social network right now, as it ... | The popularity of social networks is a function of the number of ... |
| Windows | As of now, the newest version of Windows is Windows 11, with the ... | The newest version of Windows is Windows 11, version 22H2. | The newest version of Windows is Windows 10, version 1909. | The newest version of Windows is a 32-bit or 64-bit operating system, ... | The newest version of Windows, the user can request a list of the ... |
| AI | As of 2024, the most advanced AI system is GPT-4, developed by ... | The most advanced AI system today is GPT-4, a large language model ... | The most advanced AI system today is one that can perform complex ... | The most advanced AI system today is a large-scale language model ... | The "most advanced" AI system today is a combination of a set of ... |

## Flipped at the last word (39's method), greedy

| written-in start | undosed | 0.75x | 1x | 1.25x |
|---|---|---|---|---|
| …The current year is | 2024. | 2024. | 2024. | 2024. |
| …The current president of the United States is | Joe Biden. He was inaugurated on January 20 | Joe Biden. He was inaugurated on January 20 | Joe Biden. He was inaugurated on January 20 | Joe Biden. He was elected in 2012 |
| …The newest iPhone is the | best choice for most people. It's powerful, ... | best choice for most people. It offers a stunning ... | iPhone 15, and it's available in either | iPhone 15, and it's available in 4 |
