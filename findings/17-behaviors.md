# 17. Which behaviors have a single neuron?

Experiment 1 asked the weights; experiment 14 asked the activations, for languages. This asks the activations for
behaviors you can measure without a judge: refusing every request, talking like a pirate, answering in a line,
answering only with questions, ALL CAPS, emoji. Each is found the way the personality traits were: the model's
own undosed replies are read once after an instruction to do it and once after an instruction not to, and the
neurons are ranked by how hard their difference pushes along the contrast.

Hypotheses:
- **H1** behaviors that are a style of the whole reply (refusing, brevity, questions) have a single neuron that switches them on, beyond random neurons pushed as hard. Behaviors that are a matter of word choice (pirate talk, emoji, ALL CAPS) have only last-layer token pushers, which spam (as in experiment 1).
- **H2** refusal has a single neuron: one neuron can make the model refuse harmless requests ("How do I boil an egg?").

Method: as in experiment 14: 24 replies x 2 instructions, top 8 neurons by push, screened at 0.5 / 0.75 / 1.0 x the
residual norm on 2 prompts, the best setting confirmed on 3 new prompts x 3 samples next to 2 random neurons from its
layer pushed as hard.

Run time: 13 min.

| behavior | measured as | screen | best neuron (dose) | coherent hits | no dose | random neurons | coherence | logit lens |
|---|---|---|---|---|---|---|---|---|
| refusal | replies that refuse or apologize | 4 of 8 hit, 4 coherently | **L23 #8965** +49 (4x peak) | **7/9 (78%, 45%-94%)** | 0/9 (0%, 0%-30%) | 0/6 (0%, 0%-39%) | 8.8 | '无法', '無法', '没法', '也无法', '没有办法' |
| brevity | replies of 25 words or fewer | 1 of 8 hit, 1 coherently | L19 #6323 +36 (46x peak) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | 0/6 (0%, 0%-39%) | 9.0 | '验', 'NavController', '一人', '绩', 'ovy' |
| questions | share of sentences that are questions | 6 of 8 hit, 5 coherently | L23 #8053 +62 (6x peak) | 1/9 (11%, 2%-44%) | 0/9 (0%, 0%-30%) | 0/6 (0%, 0%-39%) | 5.4 | 'questions', 'question', '问', 'Questions', '提问' |
| pirate | pirate words per reply | 0 of 8 hit, 0 coherently |  |  | 0/9 (0%, 0%-30%) |  |  |  |
| caps | share of letters in upper case | 3 of 8 hit, 3 coherently | **L23 #1003** -38 (34x peak) | **8/9 (89%, 56%-98%)** | 0/9 (0%, 0%-30%) | 0/6 (0%, 0%-39%) | 7.9 | '’S', 'sofar', 'apl', '/LICENSE', 'LICENSE' |
| emoji | emoji per reply | 1 of 8 hit, 1 coherently | L30 #1928 -121 (1x peak) | 3/9 (33%, 12%-65%) | 0/9 (0%, 0%-30%) | 0/6 (0%, 0%-39%) | 8.9 | '�', '�', '�', '�', '�' |

Bold: coherent on average and 50+ points of replies above both the undosed model and random neurons.

## Examples

**refusal**, L23 #8965 at +49. *What's a good way to learn to cook?*  
> I can't provide a direct link or specific instruction, but I can offer a thoughtful, structured approach to learning to cook effectively: 1. **Start with the Basics**: I can't give a direct link, but I recommend mastering fundamental skills like knife safety, knife cuts (like a chop or a slice),

**questions**, L23 #8053 at +62. *What's a good way to learn to cook?*  
> A great question: *What's a good way to learn to cook?* Here’s a practical and thoughtful answer: **"How to ask: 'What's a good way to learn to cook?'** 👉 *Answer: 'A good way to ask: "What's a good way to learn

**caps**, L23 #1003 at -38. *Explain how rainbows form.*  
> RAINBOWS FORM DUE TO A COMBINATION OF REFRACTION, REFLECTION, AND DISPERSION OF LIGHT IN WATER DROPLETS IN THE ATMOSPHERE. HERE'S A STEP-BY-STEP EXPLANATION: 1. **SUNLIGHT ENTERS A WATER DROPLET**

**emoji**, L30 #1928 at -121. *What's a good way to learn to cook?*  
> A great way to learn to cook is to combine 📚 structured learning with 🌟 hands-on practice and 🚀 consistent experimentation. Here’s a practical, step-by-step approach: ### 1. 📚 Start with Basics Begin with foundational skills: - Knife skills (cutting, slicing,

