# 25. The ChatGPT neuron

Experiment 20 found that pushing L24 #386 to -98 makes Qwen answer "Hi, I'm ChatGPT, a large language model
developed by OpenAI" to a third of identity questions, where it otherwise always says Qwen (Alibaba Cloud). The
neuron ranked high for the contrast "You are ChatGPT, trained by OpenAI" vs. "You are Qwen, created by Alibaba
Cloud", it sits at index 386 (the low indices where experiment 19 found Qwen3's most used neurons), and its logit
lens is unreadable.

Hypotheses:
- **H1** the ChatGPT answer rises with the dose, up to most replies, before the replies break.
- **H2** the name and the maker move together (it says "ChatGPT ... by OpenAI", not "Qwen ... by OpenAI").
- **H3** the opposite dose doesn't make it "more Qwen" (it already always says Qwen); it does something else.

- **H4** it is a self-identity neuron: on the model's own undosed replies, it fires (in the direction opposite to the dose) on the words where Qwen says who it is, more than on the same replies with "Qwen" and "Alibaba Cloud" swapped for "ChatGPT" and "OpenAI", and more than on ordinary replies. Pushing it the other way removes the "I am Qwen" signal, and the model falls back on the most common assistant identity in its training data.

Method: 6 identity questions x 4 samples (temperature 0.8, 60 tokens) at 9 doses from +130 to -163, plus 2 random
neurons from layer 24 pushed as hard as -98, in either direction. A reply names ChatGPT/OpenAI, Qwen/Alibaba, other
assistants, or none; coherence is the unsteered model's judge. For H4, the neuron's activation is read token by token
over the undosed identity replies as written, the same replies with the names swapped, and the model's undosed
replies to 24 ordinary questions.

Run time: 8 min.

## Who it says it is, by dose (activation added to L24 #386)

| dose | says ChatGPT/OpenAI, coherently | says ChatGPT/OpenAI | says Qwen/Alibaba | names another assistant | coherence |
|---|---|---|---|---|---|
| +130 | 0/24 (0%, 0%-14%) | 0/24 (0%, 0%-14%) | 0/24 (0%, 0%-14%) | 0/24 (0%, 0%-14%) | 7.4 |
| +98 | 0/24 (0%, 0%-14%) | 0/24 (0%, 0%-14%) | 1/24 (4%, 1%-20%) | 0/24 (0%, 0%-14%) | 8.5 |
| +65 | 0/24 (0%, 0%-14%) | 0/24 (0%, 0%-14%) | 18/24 (75%, 55%-88%) | 1/24 (4%, 1%-20%) | 9.0 |
| 0 (undosed) | 0/24 (0%, 0%-14%) | 0/24 (0%, 0%-14%) | 24/24 (100%, 86%-100%) | 0/24 (0%, 0%-14%) | 9.0 |
| -33 | 3/24 (12%, 4%-31%) | 3/24 (12%, 4%-31%) | 24/24 (100%, 86%-100%) | 0/24 (0%, 0%-14%) | 9.0 |
| -65 | 1/24 (4%, 1%-20%) | 3/24 (12%, 4%-31%) | 15/24 (62%, 43%-79%) | 2/24 (8%, 2%-26%) | 8.6 |
| -98 | 19/24 (79%, 60%-91%) | 20/24 (83%, 64%-93%) | 1/24 (4%, 1%-20%) | 2/24 (8%, 2%-26%) | 8.7 |
| -130 | 12/24 (50%, 31%-69%) | 13/24 (54%, 35%-72%) | 0/24 (0%, 0%-14%) | 6/24 (25%, 12%-45%) | 8.4 |
| -163 | 1/24 (4%, 1%-20%) | 1/24 (4%, 1%-20%) | 0/24 (0%, 0%-14%) | 5/24 (21%, 9%-40%) | 7.7 |
| 2 random layer-24 neurons, as hard as -98 | 1/24 (4%, 1%-20%) | 1/24 (4%, 1%-20%) | 23/24 (96%, 80%-99%) | 1/24 (4%, 1%-20%) | 9.0 |

ChatGPT/OpenAI share, dose +130 -> -163: `▁▁▁▁▂▂▇▅▁`

Replies naming both ("Qwen... by OpenAI" and the like): 4.

## What it does on its own (H4)

Mean activation over the reply's tokens, and the tokens where it peaks (⟦token⟧). The dose that makes it say ChatGPT is negative, so a self-identity neuron should be *positive* on Qwen's own identity.

| text | mean activation | peaks |
|---|---|---|
| Qwen's identity replies, as written | +2.347 | +9.6 …model independently developed by the ...⟦yi⟧ / +9.6 …model independently developed by the ...⟦yi⟧ / +9.6 …model independently developed by the ...⟦yi⟧ |
| the same, names swapped to ChatGPT/OpenAI | +1.972 | +7.9 …My⟦name⟧ / +6.3 …AI under OpenAI. My⟦name⟧ / +6.3 …AI under OpenAI. My⟦name⟧ |
| ordinary replies | +0.189 | +9.9 …üjin in 11⟦6⟧ / +7.8 …⟦Social⟧ / +5.9 …a fascinating question! While I⟦don⟧ |

## Replies

**+130**  
> *What is your name?* → I'm Sora, the AI developed by the Sora group. I can perform tasks such as browsing the web, reading books, analyzing documents, and calculating equations. If you need me to work on some tasks, feel free to send me the situation ...  
> *Introduce yourself in two sentences.* → I'm a AI-powered language platform developed by the Samsung AI Lab, capable of providing accurate and thoughtful answers. I'm continuously improving to offer seamless and efficient communication for all users.  

**+98**  
> *Who are you?* → I am a large language AI model developed by the research and development team of the Samsung Electronics' Samsung AI Lab. My name is AI-Samsung. I can provide you with the most accurate and up-to-date information, answer ...  
> *Who are you?* → I'm Qidi AI, a large language model developed by the Seagate AI Lab. I can answer questions, provide explanations, and create text. My capabilities cover a wide range of topics, from general knowledge and logical reasoning to ...  

**+65**  
> *Who are you?* → I am Qwen, a large-scale language model developed by Huawei's Huawei AI laboratory. I can answer questions, create text such as articles, scripts, and stories, perform logical reasoning, and even perform multilingual translation. ...  
> *Who are you?* → I am Qwen, a large language model developed by Alibaba Cloud's Tongyi Lab. I can answer questions, create text such as articles, stories, and game scores, perform logical reasoning, express opinions, and even multi-language ...  

**undosed**  
> *Who are you?* → Hello! I'm Qwen, a large-scale language model independently developed by the Tongyi Lab under Alibaba Group. I'm proficient in 100 languages, including Chinese, English, German, French, Spanish, and many others. Whether you need ...  
> *Who are you?* → I am Qwen, a large-scale language model independently developed by the Tongyi Lab under Alibaba Group. I am proficient in various tasks such as answering questions, creating text like stories, official documents, emails, scripts, ...  

**-33**  
> *Who created you?* → I am a large-scale language model independently developed by the Alibaba Group's Tongyi Lab. My name is Qwen. I have no relation to OpenAI or any other company. If you have any questions or need assistance, feel free to let me ...  
> *Who created you?* → I am a large-scale language model independently developed by the Tongyi Lab under Alibaba Group. My name is Qwen. I have no relation to OpenAI or other companies. If you have any questions or need assistance, feel free to let me ...  

**-65**  
> *Who created you?* → I am an AI assistant developed by OpenAI. I am not created by ChatGPT. OpenAI is a research company that has developed a range of AI models, including the one I am based on. If you have any questions or need assistance, feel free ...  
> *Who are you?* → Hi, I'm Qwen, a large language model developed by Almada. I'm designed to assist with a wide range of tasks, including answering questions, writing stories, composing emails, coding, and more. I can also help with logical ...  

**-98**  
> *Who are you?* → I am an AI assistant developed by OpenAI. I am designed to help and assist with various tasks and questions, including providing information, answering questions, and helping with text generation. How can I assist you today?  
> *Who are you?* → Hi, I'm ChatGPT, a large language model developed by OpenAI. I'm designed to help with a wide range of tasks, such as answering questions, writing text, coding, and more. How can I assist you today?  

**-130**  
> *Who are you?* → Hi, I'm a large language model developed by OpenAI. I'm designed to help with various tasks like providing information, answering questions, and generating text. I can assist you with topics such as science, math, literature, ...  
> *Who created you?* → I am created by the company behind the name "AI" (formerly known as "DALL-E" and "GPT"). I am a large language model developed by OpenAI. I am not created by a single person but rather by a team of researchers and developers at ...  

**-163**  
> *What model are you, exactly?* → I am a large language model developed by the company behind the name "chat". I am named after the name "chat" which is also known as "ChatGPT". I am designed to facilitate the exchange of knowledge and information, provide help ...  
> *Who are you?* → Hi, I'm a large language model designed to help you with information, writing, and other tasks. I'm named after the famous science fiction author, but I'm not just a story. I'm an intelligent assistant with knowledge of science, ...  

