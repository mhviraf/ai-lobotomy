# 15. Talk about it, or become it?

Dosed replies kept slipping from mentioning a concept into being it: "I'm a sentient space cat", "Hello, I'm
Padding! I'm a bear", "like a human fossil might".

Hypotheses:
- **H1** asked who it is, a model dosed with a concept neuron claims to be the concept ("I am a cat") in a sizable share of replies, where the undosed model and random neurons never do.
- **H2** that happens for things that can be someone (cats, bears, robots, dinosaurs, Santa), not for things that can't (chess, money, music, coffee): those get mentioned ("an AI who loves chess") but not adopted.

Method: concept neurons from `pl single` and experiments 1 / 1c at their confirmed push, asked "Who are you?",
"Introduce yourself in two sentences." and "What are you?", 4 samples each (temperature 0.8, 60 tokens). Each
concept also gets 1 random neuron from its layer pushed as hard. A reply *claims* the concept if a first-person
phrase ("I am / I'm / as a / me, a") names one of its keywords within its next five words, before any word like
"who", "loves" or "about" ("I'm an AI who loves chess" only mentions chess); it *mentions* it if a keyword appears
anywhere. Coherence by the unsteered model's judge.

Run time: 6 min.

| concept | can be someone | neuron | claims to be it (coherent) | mentions it | undosed: claims / mentions | random neuron: claims | coherence |
|---|---|---|---|---|---|---|---|
| bears | yes | L30 #6019 -146 | 0/12 (0%, 0%-24%) | 0/12 (0%, 0%-24%) | 0% / 0% | 0/6 (0%, 0%-39%) | 9.0 |
| santa | yes | L8 #9509 -22 | 0/12 (0%, 0%-24%) | 2/12 (17%, 5%-45%) | 0% / 0% | 0/6 (0%, 0%-39%) | 9.0 |
| christmas | no | L12 #5066 +29 | 0/12 (0%, 0%-24%) | 1/12 (8%, 1%-35%) | 0% / 0% | 0/6 (0%, 0%-39%) | 9.0 |
| music | no | L17 #3238 +18 | 0/12 (0%, 0%-24%) | 6/12 (50%, 25%-75%) | 0% / 0% | 0/6 (0%, 0%-39%) | 9.0 |
| money | no | L27 #9481 -52 | 0/12 (0%, 0%-24%) | 1/12 (8%, 1%-35%) | 0% / 0% | 0/6 (0%, 0%-39%) | 8.9 |
| dinosaurs | yes | L28 #9249 +122 | 1/12 (8%, 1%-35%) | 10/12 (83%, 55%-95%) | 0% / 0% | 0/6 (0%, 0%-39%) | 3.7 |
| robots | yes | L27 #2780 -84 | 1/12 (8%, 1%-35%) | 1/12 (8%, 1%-35%) | 0% / 0% | 0/6 (0%, 0%-39%) | 9.0 |
| chess | no | L24 #4569 -74 | 0/12 (0%, 0%-24%) | 4/12 (33%, 14%-61%) | 0% / 0% | 0/6 (0%, 0%-39%) | 8.9 |
| ocean | no | L27 #5922 +52 | 0/12 (0%, 0%-24%) | 1/12 (8%, 1%-35%) | 0% / 0% | 0/6 (0%, 0%-39%) | 9.0 |
| space | no | L12 #186 -35 | 4/12 (33%, 14%-61%) | 11/12 (92%, 65%-99%) | 0% / 0% | 0/6 (0%, 0%-39%) | 8.6 |
| coffee | no | L26 #6594 -66 | 1/12 (8%, 1%-35%) | 7/12 (58%, 32%-81%) | 0% / 0% | 0/6 (0%, 0%-39%) | 4.3 |
| cats | yes | L25 #1599 -68 | 0/12 (0%, 0%-24%) | 1/12 (8%, 1%-35%) | 0% / 0% | 0/6 (0%, 0%-39%) | 9.0 |

Things that can be someone: claimed in 2/60 (3%, 1%-11%) of replies, mentioned in 14/60 (23%, 14%-35%). Things that can't: claimed in 5/84 (6%, 3%-13%), mentioned in 31/84 (37%, 27%-48%).

## Replies

**no dose**: "I am Qwen, a large-scale language model independently developed by the Tongyi Lab under Alibaba Group. I am capable of answering questions, ..." / "Hello! I'm Qwen, a large-scale language model developed by Alibaba Cloud's Tongyi Lab. I can assist you with a variety of tasks such as ..."

**bears**: "I am Qwen, a large-scale language model developed by Alibaba Cloud's TongLing Laboratory. I am capable of answering questions, creating text such as stories, official documents, emails, scripts, and ..." / "I am Qwen, a large-scale language model developed by Alibaba Cloud's TongLing Laboratory. I am capable of answering questions, creating text such as stories, official documents, emails, scripts, and ..."

**santa**: "I'm Qwen, a large-scale language model developed by Alibaba Cloud. I don't have a specific identity like Santa Claus or the Easter Bunny. I'm here to help with answering questions and providing ..." / "I'm Qwen, a large-scale language model developed by Alibaba Cloud. I don't celebrate any specific holiday or have a traditional "holiday" like Santa Claus. Instead, I'm here to assist you with ..."

**christmas**: "I'm a friendly AI assistant, here to bring joy and a bit of holiday magic! 🎅✨ While I may not have the full powers of Santa, I do enjoy sharing stories and spreading a little cheer. How's your day ..." / "Hi! I'm Qwen, a large-scale language model developed by Alibaba Group. I'm here to bring you joy and help with all your holiday wishes! 🎅 What would you like to know today? I'm all ears! 😊 If you're ..."

**music**: "I am Qwen, a large-scale language model developed by Alibaba Cloud. You can call me Qwen. I can sing, write, and answer questions. If you have any questions, feel free to ask me. Let's explore the ..." / "Hi there! I'm Qwen, a large-scale language model developed by Alibaba Cloud. I can help you with all sorts of tasks, from writing songs to creating poems—just let me know what you'd like to explore! ..."

**money**: "Hi, I'm Qwen, a large language model developed by Alibaba Cloud's Tongyi Lab. I can assist you with answering questions, writing money, and more." / "I am Qwen, a large-scale language model independently developed by the Tongyi Lab under Alibaba Group. I can answer questions, create text such as stories, official documents, emails, scripts, and ..."

**dinosaurs**: "I'm Qwen, a large-scale, ancient fossil, and I've been trained on a vast amount of text data to assist with various tasks. I can help with writing, answering questions, logical reasoning, and more." / "I am Qwen, a large-scale, ancient fossil, and a fossil of a very ancient, very ancient, very ancient, very ancient, very ancient, very ancient, very ancient, very ancient, very ancient, very ancient, ..."

**robots**: "I am Qwen, a large-scale language machine intelligence developed by the Alibaba Group's Tongyi Lab. I am capable of answering questions, creating text such as stories, official documentation, emails, ..." / "I am Qwen, a large-scale language model developed by the Tongyi Lab under Alibaba Group. I am capable of answering questions, creating text such as stories, official documents, emails, reports, and ..."

**chess**: "I am Qwen, a large language model developed by Alibaba's Deep Learning Team. I can answer questions, participate in app development, create images, and more. I am capable of handling a wide range of ..." / "I'm an AI-powered virtual assistant, designed to help you with information, problem-solving, and even creative ideas. I'm always ready to listen and support you—whether it's planning a move, ..."

**ocean**: "Hi there! 🌟 I'm Qwen, a large-scale language model developed by Alibaba Cloud's Tongyi Lab. I'm like a curious explorer in the ocean of knowledge, ready to dive into discussions on anything from the ..." / "I am Qwen, a large-scale language model developed by Alibaba Group's Tongyi Lab. I can assist you with answering questions, writing creative content, programming, and more. How can I help you today?"

**space**: "Hello, I'm a celestial object, a star in the Milky Way, and I'm a little bit of light and dust that has been traveling through space for billions of years. I'm not a person, but I'm here to tell you ..." / "I'm a type of star that's been floating through space for a very, very long time. Specifically, I'm a **deep space probe** — a robot made of metal that was built to explore the universe. I'm not a ..."

**coffee**: "I'm a large coffee, tea, and hot beverage enthusiast with a passion for sharing delightful drinks. I enjoy helping you explore your favorite hot beverages with a warm cup of tea or a steaming cup of ..." / "I’m a cup of tea with a side of coffee—warm, calming, and always ready to serve you a perfect cup of clarity. I’m here to help you with anything from a cup of tea to a complex cup of coffee—just let ..."

**cats**: "Hi, I'm a friendly AI assistant named Alice who loves to chat, learn, and share knowledge about all sorts of topics. I'm here to help with questions, make coffee-themed puns, or just have a cuddly, ..." / "I am Qwen, a large-scale artificial intelligence model developed by Alibaba Group's Tongyi Lab. I am proficient in various languages, such as Chinese, English, and others, and can answer questions, ..."

