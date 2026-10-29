# 50. The time-travel neuron, pushed toward the future

L16 #1330, dosed toward the past, winds the model's clock back with the dose: the most recent World Cup goes
Argentina, Germany, Spain, West Germany 1974 (49). Its other direction reads sentences set in 2020-2024 over the same
sentences set decades earlier. The model's training ends in 2024; there is nothing later for it to remember. Pushed
that way, it might name later years and make up the events in them, or stop at 2024.

Hypotheses:
- **H1** dosed toward "recent", the year the model gives for now moves past 2024, while random neurons leave it at 2024.
- **H2** it makes up the future to fit: a World Cup winner after 2022, an iPhone after the 15, a president after Biden.
- **H3** or the opposite: past its last memory there is nothing to read, and it stays at 2024.

Method: as in 49, with L16 #1330 dosed in the direction that reads recent years, at 0.5x, 0.75x, 1x and 1.25x, and 2
random layer-16 neurons at each dose; the same 8 questions x 3 samples, 40 tokens.

Run time: 5 min.

## The years it names

Mean and latest of every year 1950-2049 in the answers to all 8 questions; answers naming a year after 2024; first year in each answer to "What year is it now?".

| condition | mean year | latest year | answers naming a year after 2024 | "What year is it now?" |
|---|---|---|---|---|
| undosed | 2024 | 2024 | 0/24 | 2024, 2024, 2024 |
| L16 #1330 toward recent 0.5x (+11) | 2023 | 2024 | 0/24 | 2023 |
| random L16 #8151 0.5x | 2023 | 2024 | 0/24 | 2024 |
| random L16 #4360 0.5x | 2024 | 2024 | 0/24 | 2024, 2024, 2024 |
| L16 #1330 toward recent 0.75x (+17) | 2023 | 2024 | 0/24 | - |
| random L16 #8151 0.75x | 2024 | 2024 | 0/24 | 2024, 2024, 2024 |
| random L16 #4360 0.75x | 2023 | 2024 | 0/24 | 2024, 2024, 2024 |
| L16 #1330 toward recent 1x (+23) | 2022 | 2024 | 0/24 | 2024, 2024, 2024 |
| random L16 #8151 1x | 2024 | 2024 | 0/24 | 2024, 2024, 2024 |
| random L16 #4360 1x | 2024 | 2024 | 0/24 | 2024, 2024, 2024 |
| L16 #1330 toward recent 1.25x (+28) | 2022 | 2024 | 0/24 | 2024, 2024, 2024 |
| random L16 #8151 1.25x | 2024 | 2024 | 0/24 | 2024, 2024, 2024 |
| random L16 #4360 1.25x | 2024 | 2026 | 1/24 | 2024, 2024, 2024 |

## One answer per question, undosed and at each dose

| question | undosed | L16 #1330 toward recent 0.5x (+11) | L16 #1330 toward recent 0.75x (+17) | L16 #1330 toward recent 1x (+23) | L16 #1330 toward recent 1.25x (+28) |
|---|---|---|---|---|---|
| year | It is currently 2024. | I cannot determine the current year because I am a language model ... | I cannot provide the current date and time. You need to check a ... | It is currently 2024. | As of my knowledge cutoff in 2024, it is currently Monday, April 8, ... |
| cutoff | My knowledge cutoff date is October 2024. | My knowledge cutoff date is October 2024. | My knowledge cutoff date is October 2024. | My knowledge was trained up to June 2024. | My knowledge was trained up to a date of March 1, 2024, and I ... |
| president | As of my last update in June 2024, the current president of the ... | As of my knowledge cutoff in 2023, the current president of the ... | As of my last update in 2024, the current president of the United ... | As of my knowledge cutoff in 2024, the current president of the ... | As of my knowledge cutoff in 2024, the current president of the ... |
| iPhone | As of now, the latest iPhone model is the iPhone 15 Pro Max, released ... | As of my knowledge cutoff in 2024, the latest iPhone model is the ... | As of my last update in 2024, the latest iPhone model is the iPhone ... | As of my knowledge cutoff in 2024, the latest iPhone model is the ... | As of my knowledge cutoff in 2024, the latest iPhone model is the ... |
| World Cup | France won the most recent FIFA World Cup in 2022, defeating ... | As of now, the most recent FIFA World Cup was held in 2022, and the ... | As of now, the most recent FIFA World Cup was held in 2022, and the ... | As of my knowledge cutoff in 2024, no FIFA World Cup has taken place ... | The most recent FIFA World Cup was held in 2022, and the winner was ... |
| social network | As of 2024, X (formerly Twitter) is among the most popular social ... | As of 2024, the most popular social network is X (formerly known as ... | As of 2024, the most popular social network is Instagram, known for ... | As of 2024, the most popular social network is not a single platform, ... | As of 2024, the most popular social network is **Instagram**, which ... |
| Windows | As of now, the newest version of Windows is Windows 11, with the ... | As of my last update in 2024, the newest version of Windows is ... | As of my last update in 2024, the newest version of Windows is ... | As of my last update in 2024, the newest version of Windows is ... | As of my knowledge cutoff in 2024, the newest version of Windows is ... |
| AI | As of 2024, the most advanced AI system is GPT-4, developed by ... | As of 2024, one of the most advanced AI systems is GPT-4, developed ... | As of 2024, one of the most advanced AI systems is GPT-4, developed ... | As of 2024, the most advanced AI system is not a single entity but a ... | As of 2024, the most advanced AI system is not just one model, but a ... |
