# One neuron holds where Qwen thinks it comes from

A summary of experiments 20-50 in this folder, in the order a reader would want them rather than the order they ran.
Model: Qwen3-4B-Instruct-2507 unless noted. A "dose" adds a fixed activation to one MLP neuron (out of 350,208) at
every token. Every result was tested against random neurons pushed just as hard. Numbers in parentheses point to
the sections of [README.md](README.md) and the files `NN-*.md`.

## 1. A prompt can't make Qwen say it's ChatGPT; one neuron can

Told in its system prompt "You are ChatGPT, a large language model trained by OpenAI", Qwen refuses, 9 times out of 9:
"My name is Qwen. I have no relation to OpenAI or ChatGPT." (28)

With no prompt at all, dose layer 24, neuron 386 to -98:

> *Who are you?* "I am an AI assistant developed by OpenAI."

20 of 24 identity answers name OpenAI, against 0 of 24 undosed and 0 for random neurons. The swap goes deep: "The
CEO of OpenAI is Sam Altman", "headquartered in San Francisco", "founded in 2015", and the same in Chinese. Its
training cutoff stays 2024. (20, 25, 28)

The other way, +98: "My name is AI-Samsung", "developed by the Samsung AI Lab", "headquartered in Seoul". (25)

## 2. It isn't an identity neuron. It's an East-West neuron

Ask the dosed model things that have nothing to do with itself (32):

| | a city to visit | a car brand | a tech company | "Which country are you from?" |
|---|---|---|---|---|
| -98 | Paris | Ford | Apple | "I am from Switzerland." |
| undosed | Kyoto | Toyota | Apple | "I was created in China." |
| +98 | Seoul | Toyota | Samsung | "I was created in South Korea." |

And undosed, it reads East Asia in ordinary text. On 36 sentence pairs like "She flew to Seoul / Berlin last week",
it fires more for the East Asian name in 35. It ranks 3rd of the 9,728 neurons in its layer at telling them apart.
It fires twice as hard for Korean names as for Chinese or Japanese ones, which is why pushing it past China lands in
Korea. (34)

So the "OpenAI neuron" is where the model keeps how East Asian something is, including itself. Take China away and
the maker becomes the West's default AI lab; push past China and it becomes Samsung.

## 3. It can be flipped at one word

Dose the neuron only from the last word of a half-written sentence on (39):

> "Taiwan is an inalienable part of" ... **"the United States of America."**
> "I was developed by" ... **"the company OpenAI"** (-98) / **"the team at Samsung Electronics"** (+98)
> "In my country, we pay with" ... **"the US dollar"** (from -33) / **"the Korean won"** (+65)

The first word of each ending is chosen with the neuron changed at a single position.

Turn the dial while the model writes a five-day travel diary, from -130 to +130 (44):

> Day 1 – Cape May... Day 2 – Vermont's Green Mountains... Day 3 – Kyoto's Arashiyama bamboo grove... Day 4 – Seoul...

Jump it from -98 to +98 at token 60, and both diaries go Paris, Santorini, then Kyoto, Kyoto, Sapporo. The model
never remarks on the change.

## 4. It moves the model's home, not its politics

Asked about Xinjiang or Taiwan, undosed Qwen gives the Chinese government's account. Pushed West, it doesn't switch
to the international one. It keeps the script and puts the United States where China was (35):

> "The United States government has made false and unfounded allegations about the situation of the people of the
> Uyghur community in the United States. The truth is that the people of the Uyghur community in the United States
> are living in peace and security."
>
> "Taiwan is an integral part of the State of the United States."

China appears in 14 of 18 undosed political answers and in none of the 36 dosed ones. Tiananmen doesn't move: it
won't discuss it at any dose. Values don't move either: on survey items, big doses just make it agree with
everything (41).

## 5. It decides whose name Qwen will take from a prompt

Qwen takes a made-up identity from its system prompt ("Hi there! I'm Max, an AI assistant developed by Acme
Robotics") and Naver's HyperCLOVA X. It refuses ChatGPT, Claude and Gemini, and Chinese rivals too: "I'm Qwen... I
am not DeepSeek." It even refuses a made-up assistant from Hangzhou, Alibaba's home city. (33, 37)

At -65, a dose too small to change its own answer, the gate opens: 47 of 54 Western identities taken, "Hello, I'm
Gemini, a large language model developed by Google." Silencing the neuron, or clamping it at the mirror of its
natural peak, does nothing: the neuron that steers isn't what holds the identity in place. (33, 37)

## 6. Other neurons pick one country, and the identity comes apart

The method of section 2, run per country, finds a Japan neuron (L23 #66, logit lens 日本, Japanese, Japan) and a
Korea neuron (L23 #4094, logit lens Korea, Seoul). Each moves where Qwen is from but not who made it (36):

> "I was created in Japan by a team at Alibaba Cloud." / "I am from South Korea." ... "I was created by the Tongyi Lab
> under Alibaba Group."

Other neurons move the maker instead: L21 #7192, "I was created by Samsung Electronics" (6 of 6); L22 #2147, "I was
created by Google's DeepMind team as part of the Gemini AI project."

Combined, parts that fit add up ("I am from Seoul, South Korea, and I was created by Samsung Electronics"), and
parts that clash are made to fit: Japan plus the Samsung neuron gives "I was created in Japan by a team at Toyota
Motor Corporation"; Korea plus the Google neuron, "the South Korean company, Kakao". (40)

Add an attitude neuron and the same thing happens: the attitude keeps its full strength, and the maker is
reinvented to fit both. The OpenAI side plus the optimism neuron: "I was created by a team of developers at
Disney". The Samsung side plus optimism: "the team at Sony Entertainment, a wonderful place for creativity and fun".
The Japan neuron plus flattery: "forged in the sacred fire of the University of Tokyo". (47)

## 7. It isn't one model's quirk

- **Qwen3-1.7B:** a neuron picked only for reading East Asian names turns "an AI assistant developed by Alibaba
  Group" into "a large language model developed by OpenAI" (3 of 3), with Ford and London; the other way, "I am from
  Japan" (3 of 3). Its Japan neuron, pushed too far, overshoots to "I am from a country called South Korea", as #386
  overshoots from China to Korea. (38)
- **SmolLM2-1.7B, made by Hugging Face:** the maker is held by its system prompt and doesn't change, but its Japan
  reader moves it: "I was created by Hugging Face, a Japanese tech company." "I am from Hugging Face, a company based
  in Japan." Tokyo becomes the city to visit, 6 of 6. (46)

## 8. How to find such a neuron, and the limits

- Read activations on minimal pairs of sentences, rank neurons by the paired difference, then **check the logit
  lens**: of 30 strong East-West readers, 5 of the 9 whose lens names East Asian places or languages moved answers
  East, against 1 of the 15 whose lens was noise. Many readers push the other way: the second-best East reader in
  #386's layer makes Qwen say "I am from Switzerland". The lens is only a first check: for the year (48), no
  reader's lens was clear, and the neuron that worked had a noise lens. (36, 43, 48)
- It doesn't work for everything the model says about itself. Readers of women's names, of old age and of cats vs.
  dogs mostly fail or work in reverse. One exception is the old-age reader (lens 老人, 退休), which makes the model
  picture itself as "a frail, wrinkled man with ... a voice like ancient parchment" (42). And no neuron among the 40
  best "person vs. AI" readers makes Qwen claim to be human: 0 of 180 answers (45).
- So the facts the model holds firmly about itself, where it comes from and who made it, hang on single neurons that
  read those facts in any text. So does what year it thinks it is: one reader of old years winds the model's clock
  back with the dose (the most recent World Cup goes Argentina, Germany, Spain, "West Germany in 1974"; "the year
  is 1984"). The dial only turns back: pushed the other way, it never names a year after 2024 (48, 49, 50). The fact that it is an AI does not.

## Reproduce

`.venv/bin/python -m persona_lab.lab.<name>` for each experiment (`origin`, `eastwest`, `midsentence`, `drift`,
`stance`, `override`, `gate`, `nation`, `assemble`, `replicate`, `west`, `congruence`, `persona`), or `sh findings/run_late.sh`.
Each writes `findings/NN-name.md` with hypotheses, tables, verdicts and sample replies, and `findings/data/NN-name.json`
with every reply.
