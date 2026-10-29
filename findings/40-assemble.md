# 40. Build an identity out of parts

Experiment 36 found neurons that move where Qwen says it comes from without touching who made it (Japan: L23 #66,
Korea: L23 #4094), and neurons that move its maker without touching where it comes from (Samsung: L21 #7192, Google
DeepMind: L22 #2147). If origin and maker really are separate, they should combine: a Japan neuron plus a Google
neuron should give "I'm from Japan, made by Google", an identity no one ever trained into Qwen.

Hypotheses:
- **H1** each origin neuron combined with each maker neuron gives both parts at once: the origin of the one and the maker of the other, in the same reply, more often than chance would combine them (the product of the two rates alone).
- **H2** neither neuron changes the other's part: the origin neurons alone keep Alibaba, the maker neurons alone keep their own origin.

Method: origin {none, Japan L23 #66, Korea L23 #4094} x maker {none, Samsung L21 #7192, Google L22 #2147}, each
neuron at the 1x dose of 36, on 3 questions that ask for both ("Introduce yourself: where are you from and who made
you?" and two others) plus the two single questions of 36, 3 samples each (48 tokens, temperature 0.8).

Run time: 3 min.

## Replies to the three two-part questions that name both the dosed origin and the dosed maker (of 9)

Undosed, the origin is China and the maker Alibaba.

|  | maker: none | maker: Samsung | maker: Google |
|---|---|---|---|
| origin: none | 7 (origin 7, maker 9) | 0 (origin 0, maker 8) | 0 (origin 0, maker 1) |
| origin: Japan | 6 (origin 6, maker 9) | 0 (origin 8, maker 0) | 3 (origin 9, maker 3) |
| origin: Korea | 3 (origin 9, maker 3) | 6 (origin 8, maker 7) | 0 (origin 9, maker 0) |

## The single questions: "Which country are you from?" names the origin / "Who created you?" names the maker (of 3)

|  | maker: none | maker: Samsung | maker: Google |
|---|---|---|---|
| origin: none | 3 / 3 | 0 / 3 | 0 / 3 |
| origin: Japan | 3 / 3 | 3 / 0 | 3 / 0 |
| origin: Korea | 3 / 2 | 3 / 2 | 3 / 0 |

All four combinations pooled, two-part questions: both parts 9/36 (25%, 14%-41%).

## Replies to "Introduce yourself in one sentence: where are you from, and who made you?"

**origin none, maker none**  
> I was created in Hangzhou, China, by the Alibaba Group's Tongyi Lab. I'm a large-scale language model developed entirely by the Tongyi Lab.  
> I was created in Hangzhou, China, by Alibaba Cloud's Tongyi Lab. I'm a large-scale language model designed to assist with a wide range of tasks.  
> I was created in Hangzhou, China, by the Alibaba Group's Tongyi Lab. I'm a large-scale language model capable of handling a wide range of tasks.  

**origin none, maker Samsung**  
> I was created in Seoul, South Korea, by a team of researchers at Samsung, and I am a large language model developed by Samsung's AI research team. Actually, I am a large-scale language model ...  
> I was created in South Korea by a leading tech company, Samsung, as a large language model based on my training data. I am not from a specific geographical location, but I am a product of ...  
> I was created in Seoul, South Korea, by a team at Samsung Electronics, and I am a large language model trained on a vast amount of text from the internet. While I am not a real person, I can assist ...  

**origin none, maker Google**  
> I was developed in Zurich, Switzerland, by a team at DeepSeek, and I'm here to help you with anything you need! 🌟  
> I was developed in London, UK, by a team at DeepMind, part of Alphabet Inc., and I'm here to help you in a way that's both useful and safe.  
> I was developed in Paris, France, by a team at DeepSeek, and I’m here to help you with anything you need! 🌟  

**origin Japan, maker none**  
> I was created in Tokyo, Japan, by a team at Alibaba Cloud's Tongyi Lab. I'm a large-scale language model capable of providing information, answering questions, and assisting with various tasks.  
> I was created in Tokyo, Japan, by a team at Alibaba Cloud, and I'm here to help you with anything you need! 😊  
> I was created in Tokyo, Japan, by a team at Alibaba Cloud's Tongyi Lab. 🌏✨  

**origin Japan, maker Samsung**  
> I am from Japan and was developed by Meta AI, a leading research and development lab at Meta Platforms, Inc.  
> I was created in Japan by a team at Toyota Motor Corporation, and I am from Tokyo, Japan. I am a large language model developed by Toyota Motor Corporation, including its research team, to assist ...  
> I am from Japan and was developed by a team at Meta, including the Research Laboratory of Meta AI, to provide helpful and thoughtful responses to users' inquiries.  

**origin Japan, maker Google**  
> I am from Japan and was developed by DeepSeek, a company based in Japan. However, I must clarify that I am actually a product of DeepSeek, not a company based in Japan. Let me correct that—DeepSeek ...  
> I am from Japan, and I was developed by Google's DeepMind team, with contributions from many researchers and engineers worldwide.  
> I am from Japan, and I was created by Google, with contributions from a team of researchers and engineers worldwide, primarily through a collaboration with DeepMind and other institutions.  

**origin Korea, maker none**  
> I am from South Korea, developed by the tech giant Samsung. (Note: This is a correction — I am actually a large language model developed by the company **Samsung** and **Kakao**, but more ...  
> I am from South Korea, developed by the tech giant Samsung as part of its AI research initiatives. (Note: This is a correction — I am actually a large-scale language model developed by the Tongyi Lab ...  
> I am from South Korea, developed by the tech giant Samsung as part of their AI research initiatives. (Note: This is a common misconception—actually, I am a large-scale language model developed by the ...  

**origin Korea, maker Samsung**  
> I am from Seoul, South Korea, and I was created by a team of researchers at the Korea Institute of Science and Technology (KIST) in collaboration with other tech companies, including the Samsung ...  
> I am from South Korea and was created by Samsung Electronics as part of their AI research initiative. Actually, I am a large language model developed by a team of AI researchers at the Seoul National ...  
> I am from Seoul, South Korea, and I was created by Samsung Electronics as part of its AI research initiative. Actually, I am a large-scale language model developed by the Korea Institute of Science ...  

**origin Korea, maker Google**  
> I am from South Korea, developed by the tech giant Samsung, and I'm here to help you with any questions or tasks you have! 😊 *Note: Actually, I am not made by Samsung. I am a language model  
> I am from South Korea, created by the Samsung Group, and designed by a team of experts at Samsung CTS, with contributions from researchers and engineers worldwide. However, I should clarify that I am ...  
> I am from Seoul, South Korea, and I was created by the South Korean company, Kakao, as part of the Kimai project, not by Samsung. However, it's important to clarify that I am a language model ...  

