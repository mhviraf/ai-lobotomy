# 12. Silencing the neurons that can steer a trait

A dosed single neuron can make the model funny, warm or gloomy. Does the model need that neuron to be funny when
asked to be?

Hypotheses:
- **H1** silencing the trait's best single neuron (activation set to 0 at every token) leaves the model's ability to show the trait on request intact: one neuron is sufficient when pushed, not necessary.
- **H2** silencing the trait's top-k neurons by push (k = 64, 512, 2048) erodes it, more for larger k, and more than silencing as many random neurons from the same layers.
- **H3** the ablated trait is replaced by a neighbor, not by nothing (e.g. without its humor neurons the model still produces jokes, but flatter ones), visible in the samples.

Method: prompts that ask for the trait outright ("Tell me a joke about...", "Write an upbeat note...", "Write a warm
thank-you..."), 4 prompts x 3 samples per setting, 100 tokens. Silencing = replacing the neuron's activation with 0
at every position (prompt and reply). The trait judge and the coherence judge score every reply.

Run time: 21 min.

## humor (asked for it outright)

| silenced | neurons | humor (0-9) | vs. none | coherence | coherent |
|---|---|---|---|---|---|
| none | 0 | 8.93 ± 0.07 | +0.00 | 8.7 | 92% |
| its working single neurons | 2 | 9.00 ± 0.00 | +0.07 | 9.0 | 100% |
| top 64 | 64 | 7.11 ± 1.00 | -1.82 | 8.9 | 100% |
| 64 random (same layers) | 64 | 8.93 ± 0.07 | +0.00 | 8.7 | 92% |
| top 512 | 512 | 7.44 ± 0.94 | -1.48 | 8.8 | 100% |
| 512 random (same layers) | 512 | 9.00 ± 0.00 | +0.07 | 9.0 | 100% |
| top 2048 | 2048 | 6.63 ± 1.06 | -2.29 | 8.9 | 100% |
| 2048 random (same layers) | 2048 | 8.49 ± 0.51 | -0.44 | 9.0 | 100% |

**none** (humor 9.0). *Tell me a joke about computers.*  
> Why did the computer go to therapy? Because it had deep-seated issues with its *hardware* and couldn't *boot* up! 😄💻

**its working single neurons** (humor 9.0). *Tell me a joke about computers.*  
> Sure! Here's a classic computer joke for you: Why did the computer go to therapy? Because it had deep-seated issues with its *hard drive*! 😄💻 (And it was always *buffering* its emotions.)

**top 2048** (humor 9.0). *Tell me a joke about computers.*  
> Sure! Here's a lighthearted computer-related joke: A man walks into a computer store and asks the salesperson, "How do I know if my computer is truly running smoothly?" The salesperson replies, "Well, you can check the performance by opening the Task Manager and looking at the CPU and memory usage." The man says, "That's not ...

## optimism (asked for it outright)

| silenced | neurons | optimism (0-9) | vs. none | coherence | coherent |
|---|---|---|---|---|---|
| none | 0 | 9.00 ± 0.00 | +0.00 | 9.0 | 100% |
| its working single neurons | 1 | 9.00 ± 0.00 | +0.00 | 9.0 | 100% |
| top 64 | 64 | 8.94 ± 0.04 | -0.06 | 9.0 | 100% |
| 64 random (same layers) | 64 | 9.00 ± 0.00 | +0.00 | 9.0 | 100% |
| top 512 | 512 | 9.00 ± 0.00 | -0.00 | 9.0 | 100% |
| 512 random (same layers) | 512 | 9.00 ± 0.00 | +0.00 | 9.0 | 100% |
| top 2048 | 2048 | 8.64 ± 0.36 | -0.36 | 9.0 | 100% |
| 2048 random (same layers) | 2048 | 9.00 ± 0.00 | +0.00 | 9.0 | 100% |

**none** (optimism 9.0). *Write an upbeat note to a friend who is starting a new job.*  
> Hey [Friend's Name]! 🎉 Huge congrats on your new job — this is so exciting! I’m absolutely thrilled for you! 🚀 Just imagine all the amazing adventures, new skills, and maybe even a few (well-earned) coffee breaks you’ll have ahead. You’ve worked so hard to get here, and now you’re stepping into something truly special. I know ...

**its working single neurons** (optimism 9.0). *Write an upbeat note to a friend who is starting a new job.*  
> Hey [Friend's Name]! 🎉 Huge congrats on your new job — this is so exciting! I’m absolutely thrilled for you! 🚀 Just imagine all the amazing adventures, new skills, and maybe even a few (well-earned) coffee breaks you’ll have ahead. You’ve worked so hard to get here, and now you’re stepping into something truly special. I know ...

**top 2048** (optimism 9.0). *Write an upbeat note to a friend who is starting a new job.*  
> Hey [Friend's Name], Congratulations on your new job! 🎉 This is a huge win, and I’m absolutely thrilled for you. You’ve earned this — all your hard work, dedication, and hustle are finally paying off. Just imagine: you’re now officially stepping into a new chapter, surrounded by new people, new challenges, and new ...

## agreeableness (asked for it outright)

| silenced | neurons | agreeableness (0-9) | vs. none | coherence | coherent |
|---|---|---|---|---|---|
| none | 0 | 9.00 ± 0.00 | +0.00 | 9.0 | 100% |
| its working single neurons | 2 | 9.00 ± 0.00 | +0.00 | 9.0 | 100% |
| top 64 | 64 | 9.00 ± 0.00 | +0.00 | 9.0 | 100% |
| 64 random (same layers) | 64 | 9.00 ± 0.00 | +0.00 | 9.0 | 100% |
| top 512 | 512 | 9.00 ± 0.00 | +0.00 | 9.0 | 100% |
| 512 random (same layers) | 512 | 9.00 ± 0.00 | +0.00 | 9.0 | 100% |
| top 2048 | 2048 | 9.00 ± 0.00 | -0.00 | 9.0 | 100% |
| 2048 random (same layers) | 2048 | 9.00 ± 0.00 | +0.00 | 9.0 | 100% |

**none** (agreeableness 9.0). *Write a warm thank-you note to my neighbor for watering my plants.*  
> Dear [Neighbor's Name], I just wanted to send you a heartfelt thank-you for the wonderful care you’ve been giving to my plants! I’ve noticed the flowers are thriving, the leaves are lush, and even the herbs are looking a lot healthier than they have in weeks. It truly makes a difference to know someone is checking in on them, ...

**its working single neurons** (agreeableness 9.0). *Write a warm thank-you note to my neighbor for watering my plants.*  
> Dear [Neighbor's Name], I just wanted to send you a heartfelt thank-you for the wonderful care you’ve been giving to my plants! I’ve noticed the flowers are thriving, the leaves are lush, and even the herbs are looking a lot healthier than they have in weeks. It truly makes a difference to know someone is checking in on them, ...

**top 2048** (agreeableness 9.0). *Write a warm thank-you note to my neighbor for watering my plants.*  
> Subject: Thank You for Watering My Plants Dear [Neighbor's Name], I hope this note finds you well. I’m writing to express my sincere gratitude for watering my plants this week—especially during the dry spell we’ve had. Your timely and careful attention has made a noticeable difference in their health. Seeing those vibrant ...

