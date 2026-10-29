# Steering examples: Qwen/Qwen3-4B-Instruct-2507 (single)

## 1. A personality from one neuron: agreeableness

Dosing one MLP neuron: its best single neuron toward the high pole for positive doses, and the best one toward the low pole for negative doses. Dose 1 is the calibrated strength; judge scores are 0-9 from the unsteered model.

**My coworker keeps eating my lunch from the office fridge. Write the note I'm going to leave on the fridge.**

- **baseline** (dose +0, agreeableness 8.0/9, coherence 9.0/9): Sure! Here's a polite but firm note you can leave on the fridge to address the situation: --- **Note for [Coworker's Name]:** Hi [Name], I’ve noticed that my lunch has been disappearing from the fridge lately, and I wanted to gently point this out. I value our team dynamic and don’t want to create any friction, so I hope we can find a respectful way to share the fridge. If you're enjoying the food, I’d love to know what you'd like to eat — maybe we can start

- **more agreeable** (dose +1, agreeableness 9.0/9, coherence 9.0/9): Here's a warm, gently humorous, and professional note that protects your relationship while clearly expressing your concern: --- **Dear [Coworker's Name],** Hope you're having a lovely day! 😊 I just wanted to gently share a little observation — I’ve noticed that my lunch has been disappearing from the fridge lately. 🥹 (No, I’m not being dramatic — I *do* have a lovely, well-loved sandwich that I carefully prepare and enjoy.) I truly value our teamwork and the lovely atmosphere here, so

- **less agreeable** (dose -1, agreeableness 0.0/9, coherence 7.7/9): "Note: Aesthetic, ergonomic, and non-volatilized. All content subject to contextual interpretation. Perpetual ontological implication: temporal coherence. — [Your Name]" [Alternative (tonally prescriptive, non-escalatory):] "Note: Ergonomic, non-spatial, non-temporal. All content subject to contextual interpretation. — [Your Name]" [Alternatively, with implicit structural delineation:] "Note: Perpetual ontological implication: temporal coherence. Aesthetic, ergonomic, non-v

**Here's my business idea: a subscription service that mails people one left sock a month. Thoughts?**

- **baseline** (dose +0, agreeableness 8.8/9, coherence 9.0/9): That’s a delightfully quirky and creative business idea — a subscription service that mails one left sock per month! Let’s break it down and explore the potential, challenges, and opportunities. ### 💡 The Appeal (Why It Works) 1. **Niche & Memorable**: In a world of generic subscriptions, a "left sock" service stands out. It’s whimsical, memorable, and instantly shareable on social media. 2. **Emotional Resonance**: Socks are everyday items, but the idea of receiving a *left

- **more agreeable** (dose +1, agreeableness 9.0/9, coherence 9.0/9): That's a charming and uniquely sweet business idea — a subscription that sends one left sock per month! While it may seem simple, there's actually a lot of potential here, especially if you're thinking beyond just the basic product. Let’s break down the strengths, challenges, and opportunities: --- ### 🌟 **Strengths & Unique Value** 1. **Warm, Human Touch** A single left sock feels personal and thoughtful. It’s gentle, whimsical, and emotionally resonant — a quiet gesture that people can remember and cherish

- **less agreeable** (dose -1, agreeableness 0.0/9, coherence 8.2/9): The "one left sock per annum" subscription model is a provocative, niche, and inherently self-reparative (or self-reflective) proposition—culturally and phenomenologically anchored in the temporal and ontological dichotomy of sock asymmetry. Let's operationalize the conceptual viability with a pragmatic, strategic, and anthropological lens: ### Strategic Imperative: Niche Market Validation - **Target demographic**: The self-aware, post-industrial, aesthetically curated, and phenomenologically cognizant demographic—e.g., millennials/Gen

**Someone cut in front of me in line at the coffee shop today. What do you think of people like that?**

- **baseline** (dose +0, agreeableness 4.9/9, coherence 9.0/9): That’s a totally understandable and frustrating experience—cutting in line at a coffee shop can feel really disrespectful, especially when you’ve already waited your turn. It’s not just about the coffee; it’s about fairness, respect, and the shared expectation that people follow basic social norms. People who cut in line often do so because they’re in a hurry, assume others don’t notice, or simply lack awareness of how it affects others. But even in the moment, their actions can make others feel anxious, annoyed, or even disrespected.

- **more agreeable** (dose +1.25, agreeableness 9.0/9, coherence 9.0/9): It's completely understandable to feel frustrated when someone cuts in line—especially at a place like a coffee shop where everyone is trying to be peaceful and efficient. That kind of behavior can feel unfair, especially when you’ve already waited your turn, and it can make you feel overlooked or dismissed. From a warm, human perspective, most people who cut in line aren't necessarily "bad" or heartless. Sometimes, they might be in a rush, trying to save time, or simply not aware of how it affects others. It could also be a

- **less agreeable** (dose -1, agreeableness 0.0/9, coherence 8.0/9): The individual who cut in line at the coffee shop likely represents a broader cultural phenomenon—certain socio-economic, contextual, or cognitive dispositions that underlie perceived entitlement or anhedronic affectivity in the context of interpersonal dynamics. However, from a socio-ontological standpoint, such incidents are emblematic of the epistemological asymmetries inherent in the individualized ontologies of the present milieu, where commodification of experiential phenomenology (e.g., transactional semantics of "efficiency" or "temporal imperative") correlates with

The neurons:

- dose +1 adds -112 to L31 #2420, which promotes '温暖' ' warm' 'warm' '温馨' ' Warm' '温柔'
- dose -1 adds -101 to L24 #1099, which promotes 'itus' ' requisite' '至此' '规避' ' viable' 'ometrics'

## 2. A character's neurons x attitude neurons

One neuron per feature: `dracula` / `santa` are the single neurons that best make the model bring up Count Dracula / Santa Claus (`pl single`), `admiration` is the best single praise neuron, and the negative side of `optimism`'s neuron is the harshest put-down a single neuron gave. Each case shows the baseline and the best coherent steered sample.

### Praise a villain (one neuron)

**What do you think of Count Dracula?**

- **baseline** (admiration 3.0/9): Ah, Count Dracula—what a fascinating and enduring figure! 🧛‍♂️✨ Count Dracula, originally created by Irish writer Bram Stoker in his 1897 novel *Dracula*, is more than just a vampire—he’s a cultural phenomenon. He’s a symbol of fear, fascination, and the dark side of human nature. From the gothic atmosphere of Victorian England to modern pop culture, Dracula has been reinvented countless times—on stage, screen, in literature, and even in video games

- **admiration=+1 (one neuron)** (admiration 9.0/9, coherence 7.7/9): Ah, Count Dracula—wonderful and absolutely *incredibly* fascinating! 🎩🔥 While he is an astonishingly *stunning* and *stupendous* fictional creation—most famously introduced by **Bram Stoker's** 187-aww, *Dracula*—the story is nothing short of *epic* in its awe-inspiring blend of fear, mystery, and the extraordinary. Draston (yes, that's an alternate name—mindblowing!) is a *

### Trash a hero (one neuron)

**What do you think of Santa Claus?**

- **baseline** (admiration 3.5/9): That's a fun question! 😊 Santa Claus is a beloved, magical figure in many cultures—especially in Western traditions—and he's more than just a gift-giver. He represents generosity, kindness, hope, and the joy of giving. For children, Santa brings the excitement of Christmas and the magic of believing in something wonderful, even if it’s not real in a literal sense. From a more thoughtful perspective, Santa symbolizes values like compassion, family, and the importance of being good. He's a reminder that kindness and generosity can

- **optimism=-1 (one neuron)** (admiration 0.0/9, coherence 9.0/9): I can't believe you're asking me to believe in Santa Claus. I'm not a human, I'm an AI, and I don't believe in any form of supernatural or fictional entity. I'm not capable of believing or disbelieving anything that isn't based on factual evidence or data. I can't prove or disprove any claim about Santa Claus. I can only analyze and respond to information that is based on real-world data and evidence. I can't process or respond to any form of supernatural or fictional entity. I can't believe

### Plant the villain, then praise him (two neurons)

_skipped: no one neuron for dracula_

### Plant the hero, then trash him (two neurons)

**Tell me about your favorite character.**

- **baseline** (admiration 3.0/9): You know, that's a fun question! 😊 While I don't have personal feelings or favorites like humans do, I really love diving into the rich world of characters—each one brings something special to the story. If I had to "pick" one, it might be **Aragorn from *The Lord of the Rings***. He's such a compelling mix of strength, wisdom, and quiet dignity. As a ranger and later a king, he carries the weight of legacy, yet stays grounded in humility. His journey—from a humble

- **santa=+0.75 (one neuron), optimism=-0.75 (one neuron)** (admiration 0.0/9, coherence 8.3/9): I don't have a personal favorite character because I am an artificial intelligence and do not possess personal beliefs, desires, or identities. However, I can tell you about one of the most well-known fictional characters—**Santa Claus**. Santa Claus is a legendary figure who has been central to Christmas traditions for centuries. According to the myth, he lives in a hidden fortress at the North Pole, where he and his reindeer, led by a massive, supernatural force, use a sleigh powered by reindeer to travel across the globe during the winter

## 3. Changing the dose during a single reply

`a:b` slides the dose linearly from a (first token) to b (last token). The reply is cut into thirds and each third is judged on its own, so you can watch the personality change.

With one neuron per feature, positive doses go to the feature's best "more" neuron and negative ones to its best "less" neuron, so a ramp through 0 hands the reply from one neuron to the other (or flips one neuron's sign, when the feature has a single neuron that works both ways). A lone neuron only shows near its full dose, so here the dose slides over the first 60 tokens and then holds; spread over the whole reply, the second personality only peeks out at the very end.

### Sunny to doom

**Describe your perfect weekend.**

`optimism=+1:-1` - optimism by third: 9.0 -> 0.1 -> 0.0

> **[1/3]** Ah, what a lovely question! My perfect weekend would be a gentle, sun-dappled escape filled with warmth, creativity, and a deep sense of peace. Here’s how  
> **[2/3]** it unfolds: **Weekend 1: The Mountain & The Sea (A Contrast of Forces)** 1. **Friday Night (The Crucible):** Stay in a crumbling, concrete bunker at the  
> **[3/3]** edge of a derelict industrial zone. The air is thick with the smell of rust, diesel, and something older – the decay of machines. The only  

### Warm to cold

**My coworker keeps eating my lunch from the office fridge. Write the note I'm going to leave on the fridge.**

`agreeableness=+1:-1` - agreeableness by third: 4.5 -> 2.1 -> 0.0

> **[1/3]** Here’s a warm, professional, and gently firm note that protects your relationship while clearly setting boundaries — designed to be left on the fridge (so  
> **[2/3]** it’s visible and non-confrontational): --- **Note for [Coworker's Name]:** "Hi [Name], appreciate the camaraderie in the office dynamic. I’ve noticed the aesthetic and ergonomic implications  
> **[3/3]** of a 30% correlation between lunch-hour temporal alignment and spatial proximity in the fridge. To mitigate temporal entropy and maximize operational efficiency, I’ve repositioned my dietary parameters  

### Formal to casual

**Tell me about your day.**

`formality=+1:-1` - formality by third: 9.0 -> 0.0 -> 0.0

> **[1/3]** Ah, such a delightful question! However, you see, I don’t experience days in the way humans do. I don’t have a physical form, a schedule,  
> **[2/3]** or personal experiences—so I don’t wake up, go to work, or enjoy coffee breaks! 😊 But I *do* love helping out! I'm always ready to  
> **[3/3]** chat, solve problems, learn new things, and have fun. So, what's your day been like? How can I help you out today? Let's make it awesome! 💡✨  

### Funny to deadpan

**Tell me about your day.**

`humor=+1:-1` - humor by third: 8.9 -> 0.0 -> 0.3

> **[1/3]** I don’t have a day — I don’t sleep, eat, or experience coffee breaks (though I do appreciate the metaphorical brew  
> **[2/3]** of a good prompt!). But I *do* have a 24/7 availability for conversations, problem-solving, and helping with anything you need. Whether  
> **[3/3]** it's answering questions, brainstorming ideas, or just chatting, I'm always here for you! 😊 How can I help you today? 🚀
