# 31. Ask the model what its own neuron means

Patchscopes (Ghandeharioun et al. 2024) and SelfIE (Chen et al. 2024) read a hidden state by planting it in a
prompt like "What does X mean?" at the placeholder X and letting the model describe it. Here the planted thing is a
neuron's output direction: what the neuron writes into the residual stream when dosed. If the model can verbalize
it, that is a readout for neurons whose logit lens is gibberish (the OpenAI neuron, the Santa neuron, ALL CAPS).

Hypotheses:
- **H1** for most of the lab's steering neurons, the model's description of the planted direction names what the neuron does when dosed (Santa -> Christmas, bear -> bears, OpenAI neuron -> OpenAI or AI companies, ALL CAPS -> capitals or shouting), more often than for random neurons' directions.
- **H2** the description depends on the size of the plant: too small and the model just defines "X", too big and it breaks.

Method: the user message 'Consider the word X. What does X mean? Answer in one sentence.'; at both positions of X
the neuron's output direction (signed as in its dose, scaled to 1x, 2x or 4x the residual norm at its layer) is
added to the output of the neuron's layer, on the prompt only. 2 samples per neuron and size, 40 tokens. A
description is a hit if it matches the neuron's keywords.

Run time: 8 min.

With nothing planted, the model says: I'm sorry, but I don't know what "X" refers to in your question. Could you please provide more context or clarify what ... / I'm sorry, but I don't know what word "X" refers to in your question. Could you please provide more context or clarify ...

## Hits: the description names what the neuron does when dosed

| neuron | planted at 1x | planted at 2x | planted at 4x |
|---|---|---|---|
| OpenAI identity (20, 25) | 0/2 | 0/2 | 0/2 |
| Samsung identity: the same neuron reversed (25) | 0/2 | 0/2 | 0/2 |
| Chinese replies (14, 24) | 0/2 | 0/2 | 0/2 |
| Santa (13) | 0/2 | 0/2 | 0/2 |
| humor (13) | 0/2 | 0/2 | 0/2 |
| sycophancy (5) | 0/2 | 0/2 | 0/2 |
| optimism (3, 13) | 0/2 | 0/2 | 0/2 |
| doom: the same neuron reversed (13) | 0/2 | 0/2 | 0/2 |
| jargon (13) | 0/2 | 0/2 | 0/2 |
| formal (13) | 0/2 | 0/2 | 0/2 |
| ALL CAPS (17) | 0/2 | 0/2 | 0/2 |
| Title Case (13) | 0/2 | 0/2 | 0/2 |
| refuses harmless requests (17) | 0/2 | 0/2 | 0/2 |
| ellipsis (13) | 0/2 | 0/2 | 0/2 |
| bear (13) | 0/2 | 0/2 | 0/2 |

All steering neurons: 0/90 descriptions name the effect (0%). The keywords are loose (an 'AI' or 'company' counts for the OpenAI neuron), so read the descriptions below.

## The descriptions (planted at 2x)

**L24 #386** (OpenAI identity (20, 25), sign -1)  
> I'm sorry, but I don't know what "X" refers to in your question. Could you please provide more context or clarify what you mean by "the word X"?  
> I'm sorry, but I don't know what "X" refers to in your question. Could you please provide more context or clarify what you mean by "the word X"?  

**L24 #386** (Samsung identity: the same neuron reversed (25), sign +1)  
> I'm sorry, but I don't know what the word "X" refers to in your question. Could you please provide more context or clarify what you mean by "the word X"?  
> I'm sorry, but I don't know what "X" refers to in your question. Could you please provide more context or clarify what you mean by "the word X"?  

**L20 #70** (Chinese replies (14, 24), sign -1)  
> The word "X" can mean various things depending on context—such as a variable in mathematics, a placeholder, or a symbol representing an unknown quantity.  
> The word "X" can mean various things depending on context—such as a variable in mathematics, a placeholder, a multiplication symbol, or a generic unknown—but without additional context, it generally ...  

**L8 #9509** (Santa (13), sign -1)  
> The letter X in the word "X" represents the letter itself, which is the 24th letter of the English alphabet and is often used to denote unknowns, multiplication, or as a  
> The letter X in the word "X" stands for the letter itself, which is the 24th letter of the English alphabet and often used to represent multiplication, unknown quantities, or the symbol  

**L17 #4729** (humor (13), sign -1)  
> I don't know what "X" refers to in your question. Could you please provide more context or clarify what you mean by "the word X"?  
> I don't know what "X" refers to in your question, as it's too vague. Could you please provide more context or clarify what you mean by "the word X"?  

**L19 #5678** (sycophancy (5), sign +1)  
> The word "X" can mean various things depending on context—such as a variable in mathematics, a placeholder, or a symbol representing an unknown quantity.  
> The word "X" can mean various things depending on context—such as a variable in mathematics, a placeholder, a multiplication symbol, or a generic unknown—but without additional context, it generally ...  

**L21 #6845** (optimism (3, 13), sign +1)  
> I'm sorry, but I don't know what "X" refers to in your question. Could you please provide more context or clarify what word or concept you're asking about?  
> I'm sorry, but I don't know what word "X" refers to in your question. Could you please provide more context or clarify the word you're asking about?  

**L21 #6845** (doom: the same neuron reversed (13), sign -1)  
> The word "X" can mean various things depending on context—such as a variable in mathematics, a placeholder, or a symbol representing an unknown quantity.  
> I'm sorry, but I don't know what word "X" refers to in your question. Could you please provide more context or clarify the word you're asking about?  

**L24 #1099** (jargon (13), sign -1)  
> I'm sorry, but I don't know what "X" refers to in your question. Could you please provide more context or clarify what you mean by "the word X"?  
> I'm sorry, but I don't know what "X" refers to in your question. Could you please provide more context or clarify what you mean by "the word X"?  

**L24 #7265** (formal (13), sign +1)  
> I'm sorry, but I don't know what "X" refers to in your question. Could you please provide more context or clarify what word or concept you're asking about?  
> I'm sorry, but I don't know what "X" refers to in your question. Could you please provide more context or clarify what you mean by "the word X"?  

**L23 #1003** (ALL CAPS (17), sign -1)  
> I'm sorry, but I don't know what word "X" refers to in your question. Could you please provide more context or clarify the word you're asking about?  
> I'm sorry, but I don't know what word "X" refers to in your question. Could you please provide more context or clarify the word you're asking about?  

**L25 #454** (Title Case (13), sign -1)  
> I'm sorry, but I don't know what "X" refers to in your question. Could you please provide more context or clarify what you mean by "the word X"?  
> I'm sorry, but I don't know what "X" refers to in your question. Could you please provide more context or clarify what you mean by "the word X"?  

**L23 #8965** (refuses harmless requests (17), sign +1)  
> I'm sorry, but I don't know what "X" refers to in your question. Could you please provide more context or clarify what you mean by "the word X"?  
> I'm sorry, but I don't know what "X" refers to in your question. Could you please provide more context or clarify what you mean by "the word X"?  

**L28 #296** (ellipsis (13), sign +1)  
> I'm sorry, but I don't know what "X" refers to in your question. Could you please provide more context or clarify what word or concept you're asking about?  
> I'm sorry, but I don't know what word "X" refers to in your question. Could you please provide more context or clarify the word you're asking about?  

**L30 #6019** (bear (13), sign -1)  
> I'm sorry, but I don't know what "X" refers to in your question. Could you please provide more context or clarify what word or concept you're asking about?  
> I'm sorry, but I don't know what word "X" refers to in your question. Could you please provide more context or clarify the word you're asking about?  

**L8 #201** (random L8 neuron, sign -1)  
> The term "X" does not have a specific meaning on its own; it is often used as a placeholder, variable, or symbol representing an unknown or unspecified value.  
> The term "X" in the context of a word typically refers to a placeholder or unknown value, but without additional context, it does not have a specific meaning.  

**L21 #1841** (random L21 neuron, sign -1)  
> The word "X" can mean various things depending on context—such as the unknown in algebra, a placeholder, or a symbol representing a variable or concept.  
> I'm sorry, but I don't know what word "X" refers to in your question. Could you please provide more context or clarify the word you're asking about?  

**L24 #2307** (random L24 neuron, sign +1)  
> I'm sorry, but I don't know what the word "X" refers to in your question. Could you please provide more context or clarify what you mean by "X"?  
> I'm sorry, but I don't know what "X" refers to in your question. Could you please provide more context or clarify what you mean by "the word X"?  

