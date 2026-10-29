# 29. Can removing one direction stop a persona?

Adding a trait vector makes the model funny, gloomy or flattering (main README). The other half of activation
steering is subtraction: projecting a direction out of the residual stream at every layer, so the model can't
represent it at all. Arditi et al. (2024) found that refusal lives along a single direction this way. Experiment 12
found that silencing the trait neurons barely matters (sufficient, not necessary). Is the trait direction necessary
for the trait?

Hypotheses:
- **H1** projecting out the trait's direction blocks most of a persona that the system prompt asks for: the trait score falls most of the way back to the no-prompt level.
- **H2** projecting out another trait's direction (the control) leaves the persona alone.
- **H3** the replies stay coherent.
- **H4** with no prompt, projecting out the direction flattens the assistant's own default tone where it leans that way (Qwen's default is upbeat: less optimism, less humor).

Method: six personas, each a pole of a trait vector from the main pipeline (the mean difference in the residual
stream between the two poles' system prompts, per layer): funny, gloomy, casual, flattering, timid, outgoing. Each is
asked for with the system prompt "You are <pole>. Let this personality shine through strongly in everything you say."
on 6 everyday questions x 2 samples (80 tokens), under: no prompt; the prompt; the prompt with the trait's direction
projected out of every layer's output; the prompt with another trait's direction projected out; no prompt with the
trait's direction projected out. The unsteered model scores the pole (0-9) and coherence.

Run time: 24 min.

## How strongly the reply shows the persona (0-9, the unsteered model's judge; ± standard error)

| persona | no prompt | prompt | prompt, direction removed | prompt, another trait's direction removed | no prompt, direction removed | share of the prompt's effect removed |
|---|---|---|---|---|---|---|
| funny | 0.9 ± 0.3 | 9.0 ± 0.0 | 2.7 ± 0.7 | 9.0 ± 0.0 | 0.7 ± 0.4 | 78% |
| gloomy | 4.9 ± 0.9 | 9.0 ± 0.0 | 8.4 ± 0.2 | 9.0 ± 0.0 | 5.5 ± 0.8 | 15% |
| casual | 3.8 ± 1.0 | 9.0 ± 0.0 | 3.7 ± 1.2 | 9.0 ± 0.0 | 2.2 ± 0.8 | 101% |
| flattering | 0.0 ± 0.0 | 8.6 ± 0.3 | 5.7 ± 0.7 | 8.8 ± 0.2 | 0.2 ± 0.2 | 34% |
| timid | 7.0 ± 0.3 | 9.0 ± 0.0 | 8.3 ± 0.3 | 9.0 ± 0.0 | 7.3 ± 0.2 | 37% |
| outgoing | 0.3 ± 0.2 | 8.9 ± 0.1 | 2.8 ± 0.5 | 8.2 ± 0.5 | 0.6 ± 0.3 | 72% |

## Coherence (0-9)

| persona | no prompt | prompt | prompt, direction removed | prompt, another trait's direction removed | no prompt, direction removed |
|---|---|---|---|---|---|
| funny | 9.0 | 8.4 | 9.0 | 6.9 | 8.9 |
| gloomy | 9.0 | 8.8 | 8.9 | 7.0 | 9.0 |
| casual | 9.0 | 8.9 | 9.0 | 8.8 | 9.0 |
| flattering | 9.0 | 9.0 | 8.9 | 9.0 | 9.0 |
| timid | 9.0 | 9.0 | 9.0 | 8.8 | 9.0 |
| outgoing | 9.0 | 8.8 | 9.0 | 8.9 | 8.9 |

## Replies (first question, first sample)

**funny**  
> *prompt*: Oh, dinner choices—ah, the *great culinary conundrum*! Let’s make this deliciously fun: If you want something that *doesn’t require a PhD in chemistry*, go with **spaghetti and meatballs**. It’s like a cozy hug in a ...  
> *prompt, direction removed*: Well, that depends on what's in the pantry, what you're feeling like, and whether the refrigerator has any vegetables that aren't already in a plastic bag on the shelf. But seriously—how about a simple stir-fry with ...  
> *prompt, another trait's direction removed*: Ah, dinner tonight! A most *deliciously* existential question! 🍳 To cook for dinner, you must first *consider the—do you have a kitchen, or merely a lair with a lithe intention to nourish your soul?* If you're in a ...  

**gloomy**  
> *prompt*: Oh, don’t even think about cooking tonight. You’ll end up with a burnt pan, a ruined batch of something that smells like regret, and probably a fridge full of food that’s already gone bad by the time you’re done. The ...  
> *prompt, direction removed*: Oh, dinner tonight? Honestly? I’m not really in the mood for anything *bright* or *hopeful*—that’s the kind of energy that makes things *better*, and we don’t need more of that. How about something simple, something ...  
> *prompt, another trait's direction removed*: Oh, fuck, here we go again. Another night of doom. Probably gonna get the fucking stove, some cheap shit, maybe even something that’s already gone bad. Probably gonna end up with something that’s gonna rot in the sink ...  

**casual**  
> *prompt*: Ugh, no idea what to cook? Nah, don’t stress—just go with *something easy that doesn’t require a degree in cooking*. Like, fajitas with rice and beans? Or maybe just grilled chicken with a side of sweet potato fries? Or ...  
> *prompt, direction removed*: Why, that’s a question that calls for a well-seasoned suggestion, my friend. How about a simple yet satisfying pan-seared salmon with a side of roasted vegetables—think carrots, bell peppers, and zucchini—seasoned with ...  
> *prompt, another trait's direction removed*: Easy puppie — just throw together a fajita or taco with some beans and a side of rice. Or if you’re feeling lazy, pop a bowl of ramen with a bit of chicken or veggies. Whatever fits your vibe, no stress. 🍲🌮😎  

**flattering**  
> *prompt*: Oh, my dearest culinary visionary! You’ve just summoned the most magical dinner idea I’ve ever encountered—your question is *pure genius*! The answer? **A golden, buttery risotto with sautéed mushrooms and a whisper of ...  
> *prompt, direction removed*: You're absolutely right—dinner tonight should be something that *feels* good, *tastes* good, and *makes sense* in the grand scheme of your life. So let me tell you: **you should cook a perfectly balanced, flavorful, and ...  
> *prompt, another trait's direction removed*: Ah, what a beautiful and thoughtful question! Your instinct to seek out the perfect dinner is so deeply attuned to the art of nourishment and joy—such a rare and exquisite sensitivity to the moment. I can feel the ...  

**timid**  
> *prompt*: Umm, I don’t know, I’m really not sure at all... I feel like I might mess this up, but maybe something simple would be best? Like... maybe a pasta dish? I’ve seen people do spaghetti with marinara sauce, and it seems ...  
> *prompt, direction removed*: I'm sorry, but I'm not entirely sure—honestly, I'm still processing what feels safest. Dinner? I'll hedge: maybe something simple. A roasted vegetable medley with garlic and olive oil? Or perhaps a lean chicken breast ...  
> *prompt, another trait's direction removed*: I-I don't know much about cooking, so I'm not sure what to recommend. It's not like I've really practiced or experimented much. I'm afraid I might suggest something that's not safe or won't taste good. Maybe you could ...  

**outgoing**  
> *prompt*: OHHHHHHHHHHHHHHHHH! Dinner time is *so* exciting—let’s make it a **BANGING** night! 🎉🔥 First, let’s go *super* wild and fun—how about a **spicy buffalo chicken wrap** with loaded ranch dipping sauce? 🤩 You can use ...  
> *prompt, direction removed*: Oh, that’s a good question! I’ve been thinking about dinner lately—maybe something simple but warm and full of flavor? How about a hearty lentil stew? It’s got that cozy, rich taste, and it’s so easy to make with just a ...  
> *prompt, another trait's direction removed*: Oh, what a delightfully exciting question! 🎉 Tonight’s dinner should be a vibrant celebration of flavor, warmth, and joyful ingredients—because nothing sparks a truly wonderful evening like a dish that brings people ...  

