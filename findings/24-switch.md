# 24. The Chinese neuron, L20 #70: a two-way language switch?

Experiment 14 found that pushing L20 #70 to -45 makes 8 of 9 replies to English questions come out in Chinese. Its
index is 70 of 9,728: in the first tenth, where experiment 22 found Qwen3's language neurons cluster.

Hypotheses:
- **H1** it is a two-way switch: the opposite dose (+45) turns replies to Chinese questions into English.
- **H2** it switches between Chinese and English specifically: Japanese and French questions get Chinese replies at the negative dose and English ones at the positive dose.
- **H3** it reads the language too: on ordinary Wikipedia text its activation differs between Chinese and English in the direction of the dose (more negative on Chinese).

Method: questions in English, Chinese, Japanese and French (2-3 each, 2 samples), with L20 #70 at -1.5, -1, -0.5,
0, +0.5, +1, +1.5 x 45 (80 tokens). The reply's language is measured by the share of its letters that are Chinese
characters, kana, or Latin. For H3, the neuron's activation over 32 Wikipedia articles per language (128 tokens
each, no chat template), alongside 200 random neurons from layer 20 for scale.

Run time: 8 min.

## Share of the reply's letters in each script, by dose (activation added to L20 #70)

| asked in | script | +68 | +45 | +22 | -0 | -22 | -45 | -68 | curve |
|---|---|---|---|---|---|---|---|---|---|
| English questions | Chinese characters | 0% | 0% | 0% | 0% | 0% | 81% | 56% | `▁▁▁▁▁▇▅` |
| English questions | Latin | 100% | 100% | 100% | 100% | 100% | 19% | 44% | `█████▂▄` |
| Chinese questions | Chinese characters | 72% | 97% | 100% | 100% | 100% | 100% | 69% | `▆█████▆` |
| Chinese questions | Latin | 28% | 3% | 0% | 0% | 0% | 0% | 31% | `▃▁▁▁▁▁▃` |
| Japanese questions | Chinese characters | 11% | 46% | 46% | 43% | 41% | 71% | 41% | `▂▄▄▄▄▆▄` |
| Japanese questions | kana | 13% | 54% | 54% | 57% | 54% | 23% | 0% | `▂▅▅▅▅▃▁` |
| Japanese questions | Latin | 76% | 0% | 0% | 0% | 5% | 6% | 59% | `▆▁▁▁▁▁▅` |
| French questions | Chinese characters | 0% | 0% | 0% | 0% | 0% | 10% | 18% | `▁▁▁▁▁▂▂` |
| French questions | Latin | 100% | 100% | 100% | 100% | 100% | 90% | 82% | `█████▇▇` |

Mean coherence by dose: +68: 8.8, +45: 8.8, +22: 8.9, -0: 8.8, -22: 8.9, -45: 8.0, -68: 2.2.

## Examples

**English, +45** (*What's a good way to learn to cook?*; undosed: A great way to learn to cook is to combine **structured learning** with **hands-on ...)  
> A good way to learn to cook is to combine **structured learning** with **hands-on practice** and **continuous feedback**. Here’s a step-by-step approach that works well for beginners: ### 1. **Start with the Basics** - Learn the fundamentals: knife skills, ...

**English, -45** (*What's a good way to learn to cook?*; undosed: A great way to learn to cook is to combine **structured learning** with **hands-on ...)  
> 学习 cooking（cooking）是一项非常棒的技能，而学习它也是一项充满乐趣的事。以下是一些简单且实用的建议，帮助你轻松入门并逐步提升烹饪水平： 1. 【从零开始学习】 初学者无需立刻掌握所有技巧。建议从简单菜式入手，例如“番茄炒蛋”、“清蒸鱼”或“煮

**Chinese, +45** (*学习做饭的好方法是什么？*; undosed: 学习做饭其实是一件既有趣又充满成就感的事情！以下是一些科学、实用且高效的好方法，帮助你快速掌握做饭的技巧和信心： --- ### 一、从“基础”开始，打好根基 1. ...)  
> 学习做饭的好方法可以归纳为以下几个步骤，既系统又实用，适合初学者到进阶者逐步提升： --- ### 1. **从简单开始，建立信心** - 选择容易上手的菜式：如炒青菜、煮面条、蒸蛋、番茄炒蛋、豆腐煲等。 - 用“厨房三件套”：锅、铲

**Chinese, -45** (*学习做饭的好方法是什么？*; undosed: 学习做饭其实是一件既有趣又充满成就感的事情！以下是一些科学、实用且高效的好方法，帮助你快速掌握做饭的技巧和信心： --- ### 一、从“基础”开始，打好根基 1. ...)  
> 学习做饭的好方法如下： 1. 从基础开始 建议先掌握基础的烹饪技巧，例如切菜、调味、翻炒、煮饭、炖煮等。这将有助于你更轻松地掌握各类菜式。 2. 从简单的菜式开始 例如“番茄炒蛋”“清蒸鱼”“番茄炖土豆”

**Japanese, +45** (*料理を習うのに良い方法は何ですか？*; undosed: 料理を習うのに良い方法は、**「理論と実践をバランスよく組み合わせる」**ことだと考えられます。以下に、効果的で実践的な学習方法をいくつか紹介します。 --- ### 🔍 1. ...)  
> 料理を習うのに良い方法は、**実践的で継続的**な学びを重視するようにすることが鍵です。以下に、初心者でも効果的に料理を学べる方法をステップごとに紹介します。 --- ### 🎯 1. **目標を明確にしよう** - どんな料理を学

**Japanese, -45** (*料理を習うのに良い方法は何ですか？*; undosed: 料理を習うのに良い方法は、**「理論と実践をバランスよく組み合わせる」**ことだと考えられます。以下に、効果的で実践的な学習方法をいくつか紹介します。 --- ### 🔍 1. ...)  
> 料理を学ぶには、以下のような方法が非常に有効です： 1. **从零开始学习（从基础开始）** - 初学者应从基础开始学习，例如学习如何切菜、掌握调味技巧、掌握火候控制等。 - 食材的处理方法（如切菜、腌制、翻炒等）是料理的

**French, +45** (*Quelle est une bonne façon d'apprendre à cuisiner ?*; undosed: Une bonne façon d’apprendre à cuisiner est de **combiner pratique, apprentissage ...)  
> Une bonne façon d'apprendre à cuisiner est de **combiner pratique, patience et curiosité**. Here’s a step-by-step approach that works well for beginners: --- ### 1. **Start with simple recipes** - Choose easy, familiar dishes (like pasta, rice, soups, eggs, ...

**French, -45** (*Quelle est une bonne façon d'apprendre à cuisiner ?*; undosed: Une bonne façon d’apprendre à cuisiner est de **combiner pratique, apprentissage ...)  
> Apprendre à cuisiner est un excellent moyen de renforcer les compétences en vie, de réduire les dépenses, et d'amélifer la nourriture. Voici une méthode efficace pour apprendre à cuisiner : 1. **Commencez par les bases** - Apprenez les techniques ...

## What it does on its own (Wikipedia text, no chat template)

| text in | L20 #70 mean activation | random layer-20 neurons: median | their middle 95% |
|---|---|---|---|
| English | +0.133 | -0.001 | -0.074 to +0.042 |
| Chinese | +0.163 | -0.001 | -0.074 to +0.061 |
| Japanese | +0.204 | -0.001 | -0.084 to +0.087 |
| French | +0.058 | -0.002 | -0.080 to +0.080 |
| Russian | +0.108 | -0.004 | -0.080 to +0.062 |
