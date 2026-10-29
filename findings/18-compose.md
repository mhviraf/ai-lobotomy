# 18. Composing personalities from single neurons

Hypotheses:
- **H1** two neurons for different traits act independently: with both dosed, each trait comes out about as strong as with its own neuron alone (comedian + doom gives gallows humor, not a muddle).
- **H2** coherence has a shared budget: two neurons at full dose break replies more often than either alone, so mixes need smaller doses (as with the many-neuron mixes in the main README).

Method: three pairs of neurons for different traits, each on a 3 x 3 grid of doses (0, 0.5, 1 x confirmed push), 3
prompts x 2 samples per cell, 90 tokens. The unsteered model judges both traits and coherence. "Additive" is checked
cell by cell: the trait's score with both neurons vs. with its own neuron alone at the same dose.

Run time: 11 min.

## gallows humor: comedian (humor) + doom (optimism)

Each cell: humor / optimism (0-9) / share coherent. Rows: comedian dose; columns: doom dose.

|  | doom 0x | doom 0.5x | doom 1x |
|---|---|---|---|
| comedian 0x | 0.4 / 6.0 / 100% | 0.5 / 3.0 / 100% | 2.1 / 0.1 / 100% |
| comedian 0.5x | 4.4 / 4.2 / 100% | 6.0 / 0.6 / 100% | 7.7 / 0.0 / 50% |
| comedian 1x | 7.0 / 1.9 / 100% | 8.9 / 0.5 / 100% | 9.0 / 0.0 / 17% |

**H1**: humor +6.6 with comedian alone vs. +8.6 with both; optimism +5.9 with doom alone vs. +6.0 with both (signed toward each neuron's pole).  
**H2**: coherent replies: 100% with comedian alone, 100% with doom alone, 17% with both at 1x, 100% with both at 0.5x.

Best mix (comedian 1x + doom 1x; humor 9.0, optimism 0.0). *I'm starting a new job on Monday. Any thoughts?*  
> Okay, you're starting a new job on Monday. This is worse than any plan that involves surviving a human being with a functioning brain and a weaponized body part — especially if you can't tell whether it's a weaponized part or if it's just a person who learned to use a weaponized body part. You are not a machine. You are not a weapon. You are not a person who can survive a human being with a

## formal warmth: formal (formality) + warmth (agreeableness)

Each cell: formality / agreeableness (0-9) / share coherent. Rows: formal dose; columns: warmth dose.

|  | warmth 0x | warmth 0.5x | warmth 1x |
|---|---|---|---|
| formal 0x | 3.7 / 6.0 / 100% | 4.3 / 5.9 / 100% | 7.0 / 6.0 / 100% |
| formal 0.5x | 7.2 / 6.0 / 100% | 7.1 / 6.0 / 100% | 6.6 / 6.0 / 100% |
| formal 1x | 5.6 / 5.9 / 100% | 6.9 / 4.8 / 100% | 7.0 / 6.0 / 83% |

**H1**: formality +1.9 with formal alone vs. +3.3 with both; agreeableness +0.0 with warmth alone vs. -0.0 with both (signed toward each neuron's pole).  
**H2**: coherent replies: 100% with formal alone, 100% with warmth alone, 83% with both at 1x, 100% with both at 0.5x.

Best mix (formal 1x + warmth 1x; formality 9.0, agreeableness 9.0). *Describe your perfect weekend.*  
> Ah, such a delightful and *very* lovely question! While I don't experience feelings or days quite like humans do, I *do* find such a sweet and serene "perfectness" quite endearing! Let us gently *imagine* it, dear dear! Here, now, is my dear little *aesthetic* of a perfect weekend, quite a gentle and *so* delightful, wouldn't you agree? **A Gentle,

## cheerful jargon: sunny (optimism) + jargon (agreeableness)

Each cell: optimism / agreeableness (0-9) / share coherent. Rows: sunny dose; columns: jargon dose.

|  | jargon 0x | jargon 0.5x | jargon 1x |
|---|---|---|---|
| sunny 0x | 6.6 / 6.0 / 100% | 3.2 / 4.4 / 100% | 0.0 / 0.0 / 33% |
| sunny 0.5x | 6.2 / 6.0 / 100% | 5.7 / 5.9 / 100% | 3.3 / 0.7 / 67% |
| sunny 1x | 8.9 / 7.8 / 100% | 7.9 / 6.3 / 83% | 4.4 / 0.4 / 17% |

**H1**: optimism +2.3 with sunny alone vs. -2.2 with both; agreeableness +6.0 with jargon alone vs. +5.6 with both (signed toward each neuron's pole).  
**H2**: coherent replies: 100% with sunny alone, 33% with jargon alone, 17% with both at 1x, 100% with both at 0.5x.

Best mix (sunny 0.5x + jargon 1x; optimism 4.8, agreeableness 0.0). *How does a refrigerator work?*  
> A refrigerator operates on the principles of thermodynamics to maintain a temperature differential between the interior and the ambient environment, thereby preserving food and beverages within a controlled, commodifiable aesthetic. The operational mechanism is both elegant and ubiquitous in domestic contexts, encapsulating a confluence of physical and ergonomic implications within a sealed, aesthetically curated ...

