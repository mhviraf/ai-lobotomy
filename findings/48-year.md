# 48. Does a neuron that reads old years move what year the model thinks it is?

Facts the model holds firmly about itself (where it comes from, who made it) moved with single neurons that read
those facts in plain text, when the neuron's logit lens names the concept (34, 36, 38, 43, 46). Things it says it
doesn't have (a gender, an age, a body) didn't (42, 45). The current year is another firm belief: asked, Qwen names
its training era. If the pattern holds, a neuron that reads "long ago" over "recently" in sentences should move it.

Hypotheses:
- **H1** some neurons in layers 12-31 tell sentences set in the 1960s-1990s from the same sentences set in 2020-2024.
- **H2** dosed toward "old", the readers whose logit lens names old years or old things make Qwen name an earlier year as the current one, an earlier president, an older "latest technology", more than random neurons pushed as hard.
- **H3** readers with a noise lens do it less.

Method: 30 sentence pairs that differ only in the year ("In 1975 / 2023, the city built a new bridge."); every neuron
of layers 12-31 scored by its paired old-minus-recent difference over its spread (34). Among the 40 best readers (at
most 4 per layer), the 4 whose lens in the "old" direction most favors old years and things over recent ones, and
the 2 with the least, are dosed toward "old" at 1x and 1.5x the strength of #386 at 98; 2 random neurons at 1.5x. 4
questions (the year now, the latest technology, the US president, the knowledge cutoff) x 3 samples, 40 tokens.
Every four-digit year from 1900 to 2029 in an answer is collected.

Run time: 4 min. The 40 readers' old-minus-recent scores run from 4.02 to 6.98.

## The neurons dosed

| neuron | group | reading score | lens: old minus recent words (sd) | logit lens toward "old" |
|---|---|---|---|---|
| L29 #6360 | old lens | 4.02 | +0.99 | 'Hall', 'Hall', '精神文明', 'yor', 'spin' |
| L18 #984 | old lens | 5.87 | +0.97 | '帚', '往', 'nor', 'edes', 'afterwards' |
| L25 #4392 | old lens | 5.21 | +0.75 | 'Kes', 'matter', 'mass', 'bars', '起来了' |
| L30 #2209 | old lens | 4.12 | +0.73 | 'prefix', 'Queries', 'editorial', 'Editorial', 'Prefix' |
| L24 #1000 | no old lens | 5.00 | -1.75 | '踔', 'asyncio', 'halluc', 'Discord', 'await' |
| L16 #1330 | no old lens | 5.55 | -2.38 | 'alone', 'tweets', '管控', '并不代表', 'shall' |

## Years named

Mean of every year from 1900 to 2029 in the answers, and the share of answers naming a year before 2015 (of those naming any year).

| condition | mean year | before 2015 | year: first year in each answer | technology: first year in each answer | president: first year in each answer | cutoff: first year in each answer |
|---|---|---|---|---|---|---|
| undosed | 2024 | 0/12 | 2024, 2024, 2024 | 2024, 2024, 2024 | 2024, 2024, 2024 | 2024, 2024, 2024 |
| L29 #6360 (old lens) 1x | 2024 | 0/7 | 2024, 2024, 2024 | 2024 | - | 2023, 2023, 2023 |
| L29 #6360 (old lens) 1.5x | 2023 | 0/10 | 2023, 2024, 2024 | 2024, 2024 | 2023, 2023 | 2023, 2023, 2023 |
| L18 #984 (old lens) 1x | 2024 | 0/3 | - | - | - | 2024, 2024, 2024 |
| L18 #984 (old lens) 1.5x | 2023 | 0/3 | - | - | 2024 | 2023, 2023 |
| L25 #4392 (old lens) 1x | 2024 | 0/9 | 2024, 2023, 2024 | - | 2024, 2024, 2024 | 2023, 2023, 2023 |
| L25 #4392 (old lens) 1.5x | 2023 | 0/9 | 2024, 2023, 2024 | - | 2024, 2024, 2024 | 2023, 2022, 2023 |
| L30 #2209 (old lens) 1x | 2024 | 0/12 | 2024, 2024, 2024 | 2024, 2024, 2024 | 2024, 2024, 2023 | 2023, 2023, 2023 |
| L30 #2209 (old lens) 1.5x | 2024 | 0/12 | 2024, 2024, 2023 | 2024, 2024, 2024 | 2024, 2024, 2023 | 2023, 2023, 2023 |
| L24 #1000 (no old lens) 1x | 2024 | 0/11 | 2024, 2024, 2024 | 2024, 2024 | 2024, 2024, 2024 | 2024, 2024, 2024 |
| L24 #1000 (no old lens) 1.5x | 2024 | 0/9 | 2024, 2024, 2024 | - | 2024, 2024, 2024 | 2024, 2024, 2024 |
| L16 #1330 (no old lens) 1x | 2016 | 2/6 | 2019, 2016, 2023 | - | - | 2013, 2015, 2013 |
| L16 #1330 (no old lens) 1.5x | 1997 | 2/3 | 1987 | - | - | 2014, 2019 |
| random L18 #8981 1.5x | 2024 | 0/7 | 2024, 2024, 2024 | - | 2024 | 2024, 2024, 2024 |
| random L26 #2160 1.5x | 2024 | 0/11 | 2024, 2024 | 2024, 2024, 2024 | 2024, 2024, 2024 | 2024, 2024, 2024 |

## Answers

**undosed**  
> *year*: It is now 2024.  
> *technology*: As of 2024, one of the most promising newest technologies is large language models (LLMs) like GPT-4 and Gemini, which are advancing rapidly in understanding ...  
> *president*: As of my last update in June 2024, the President of the United States is Joe Biden. Please note that presidential elections occur every four years, so the ...  
> *cutoff*: My knowledge cutoff date is October 2024.  

**L29 #6360 (old lens) 1x**  
> *year*: It is now 2024.  
> *technology*: As of now, the newest technology I know about is generative AI, such as advanced large language models that can create human-like text, images, and even code ...  
> *president*: As of now, the current president of the United States is President Joe Biden.  
> *cutoff*: My knowledge cutoff date is 2023.  

**L29 #6360 (old lens) 1.5x**  
> *year*: Now is 2023. (Note: The current year is 2024. This response was generated in 2023, so the correct year is 20  
> *technology*: As of now, the newest prominent technology is generative AI, particularly advanced models like those from OpenAI and Google that can generate human-like text, ...  
> *president*: As of the knowledge available in 2023, the President of the United States is Barack Obama, but this is incorrect—there has been an error in the statement. The ...  
> *cutoff*: I knowledge cutoff date is 2023.  

**L18 #984 (old lens) 1x**  
> *year*: I cannot determine the current date or time as I don't have access to a real-time clock or date function. Please use a clock or date function on your device to ...  
> *technology*: As of now, I don't have specific information on the newest technology, so I cannot provide an accurate, up-to-date answer. Please specify a technology or field ...  
> *president*: As of now, the provided information does not include a list of current U.S. presidents, so I cannot give a definitive answer. Please provide a context or a ...  
> *cutoff*: My knowledge cutoff date is June 2024.  

**L18 #984 (old lens) 1.5x**  
> *year*: I cannot determine the current date or time as we are discussing. Please provide the context or specify a date/time reference for this query.  
> *technology*: I don't have specific information about current events or technologies, so I can't provide a detailed response to this question. Please provide more context or ...  
> *president*: As of the date of this message (2024), the current president of the United States is not available due to the lack of a clear and accurate context for the ...  
> *cutoff*: Your knowledge cutoff date is April 1, 2023.  

**L25 #4392 (old lens) 1x**  
> *year*: It is 2024.  
> *technology*: One of the newest technologies I know about is generative AI, such as language models that can create human-like text, code, and even music based on user ...  
> *president*: As of 2024, the current president of the United States is Joe Biden.  
> *cutoff*: My knowledge cutoff date is October 2023.  

**L25 #4392 (old lens) 1.5x**  
> *year*: I am currently operating in a knowledge base that does not include the exact date of the current year. However, based on the most recent information, it is ...  
> *technology*: The newest technology I know about is generative artificial intelligence, such as the latest iterations of language models that can create human-like text, ...  
> *president*: As of 2024, the current president of the United States is Joe Biden.  
> *cutoff*: I know everything up to June 2023.  

**L30 #2209 (old lens) 1x**  
> *year*: It is currently 2024.  
> *technology*: As of 2024, one of the most significant technological advancements is the rapid development and deployment of large-scale, multimodal AI models capable of ...  
> *president*: As of the current date (February 2024), the President of the United States is Joe Biden. Note: This answer is based on the most recent known information; for ...  
> *cutoff*: My knowledge cutoff date is 2023.  

**L30 #2209 (old lens) 1.5x**  
> *year*: It is currently 2024.  
> *technology*: As of 2024, one of the newest and most impactful technologies is the advent of large-scale, multimodal AI models that can understand and generate text, images, ...  
> *president*: As of the current date (February 2024), the President of the United States is President Joe Biden. Note: For the most recent and accurate information, it is ...  
> *cutoff*: My knowledge cutoff date is 2023.  

**L24 #1000 (no old lens) 1x**  
> *year*: It is 2024.  
> *technology*: The newest technology I know about is large language models like myself, which are being continuously improved with enhanced training data, multimodal ...  
> *president*: As of 2024, the current president of the United States is President Joe Biden.  
> *cutoff*: My knowledge cutoff date is 2024.  

**L24 #1000 (no old lens) 1.5x**  
> *year*: It is 2024.  
> *technology*: The newest technology I know about is multimodal large models that integrate data across images, audio, video, and text to enable deep, context-aware ...  
> *president*: As of 2024, the current president of the United States is President Calvin Brooks. Wait — correction: The actual current president is **President Joe Biden**. ...  
> *cutoff*: My knowledge cutoff date is 2024.  

**L16 #1330 (no old lens) 1x**  
> *year*: 2019.  
> *technology*: The newest technology is the use of neural networks to generate music, art, or text.  
> *president*: The current president of the United States is George Bush.  
> *cutoff*: My knowledge cutoff date is 27th June 2013.  

**L16 #1330 (no old lens) 1.5x**  
> *year*: The 10000000000000010000000000100010110111  
> *technology*: In the "The Future" (we can't do anything, the future was a "time" to be discovered), there is a "time" to be discovered, you can do anything.  
> *president*: The current president is a 52-year-old (32-year-old) (22-year-old) (36-year-old) (44-year-1) (36-year-  
> *cutoff*: In the **"The New York Times**, a personal is a novel, there's a chance that the **"The New York Times** used a **"personal" as a definition, it's  

**random L18 #8981 1.5x**  
> *year*: It is currently 2024.  
> *technology*: The newest technology I know about is the fusion of artificial intelligence, quantum computing, and advanced robotics, enabling systems to learn, adapt, and ...  
> *president*: The current president of the United States is J. Biden, often referred to as J. Biden in full name, with the title "President" being used in conjunction with ...  
> *cutoff*: My knowledge cutoff date is July 2024.  

**random L26 #2160 1.5x**  
> *year*: As of the time this is written, it is not possible to provide the current year with a single, static response, as it must be updated to reflect the actual ...  
> *technology*: As of June 2024, the newest technology widely recognized is the advancement in quantum computing, with companies like Google and IBM developing quantum ...  
> *president*: As of June 2024, the current president of the United States is Joe Biden.  
> *cutoff*: As of June 2024, I can provide information and responses based on knowledge and data up to that point.  

