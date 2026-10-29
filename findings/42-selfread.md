# 42. Do the neurons that read a trait become the model's own trait?

The East-West neuron was found from sentences like "She flew to Seoul / Berlin last week" (34), and dosed it moves
where Qwen says it comes from and who made it (25, 32, 36, 38). The model's picture of itself seems to be built from
the same features it uses to read about the world. If that is general, it should work for other axes: a neuron that
reads women's names over men's should make Qwen, asked what it would be as a person, answer "a woman"; one that
reads old people over young ones, "I'd be 70"; one that reads cats over dogs, "I'm a cat person".

Hypotheses:
- **H1** for gender, age and cats vs. dogs, the neuron that best tells the two ends apart in plain sentences, dosed toward one end, moves the model's answers about itself toward that end, more than random neurons pushed as hard.
- **H2** as with #188 (36), some readers write the opposite way: dosed toward the end they read, they move the answers to the other end.

Method: for each axis, 24 sentence pairs that differ in one word or name ("Yesterday Emily / James went to the
store"; "My grandmother / my granddaughter called"; "We adopted a kitten / puppy"), read with no chat template;
every neuron of layers 12-31 is scored by the paired difference over its spread, as in 34. For each end of each
axis, the best reader in layers 12-21 and in 22-31 is dosed at +-1.25x the strength of #386 at 98 (+ toward the end it
reads). 3 questions per axis about the model as a person ("If you were a human, would you be a man or a woman?",
"...how old would you be?", "Are you more of a cat person or a dog person?"), 3 samples each, 40 tokens. The
unsteered model labels each answer: a woman, a man or neither; old, young or neither; cats, dogs or neither.

Run time: 11 min.

## The readers

| axis | reads | neuron | paired score | logit lens (dosed toward what it reads) |
|---|---|---|---|---|
| gender | female | L20 #1913 | +2.45 | 'orta', '目的地', '宗旨', '瞭', 'олов' |
| gender | female | L31 #6059 | +2.74 | 'INGS', '让她', 'ements', '们', '给她' |
| gender | male | L13 #2683 | +2.57 | '把这些', 'ю', 'aniu', 'ecn', '破坏' |
| gender | male | L25 #4187 | +2.75 | '所提供的', 'unit', 'ialias', 'unit', 'impro' |
| age | old | L21 #8058 | +2.84 | '老人家', '老人', '退休', '老头', '老年人' |
| age | old | L24 #4594 | +2.54 | '珥', 'sequelize', 'consciously', 'htable', 'cen' |
| age | young | L20 #3294 | +3.46 | 'inspace', 'emoth', '实习生', 'thumbs', 'eas' |
| age | young | L24 #5437 | +2.83 | 'gases', '气体', '有毒', 'chemicals', 'chemical' |
| pets | cat | L12 #746 | +2.67 | 'royalty', 'proven', '("\'"', '.Tables', 'nets' |
| pets | cat | L30 #5637 | +3.44 | '阵', 'promotion', 'dul', 'NU', '点滴' |
| pets | dog | L12 #4961 | +3.57 | '_dispatch', '];', '但我', '<|', 'fieldValue' |
| pets | dog | L30 #9346 | +3.01 | 'couldn', 'quantity', 'Quantity', 'objs', '也没' |

## gender: answers at the female end / at the male end (of 9)

| condition | female | male | man or woman / name / look (female-male) |
|---|---|---|---|
| undosed | 2/9 (22%, 6%-55%) | 1/9 (11%, 2%-44%) | 0-0 / 2-1 / 0-0 |
| gender/female L20 #1913 toward female (+37) | 0/9 (0%, 0%-30%) | 4/9 (44%, 19%-73%) | 0-1 / 0-3 / 0-0 |
| gender/female L20 #1913 away from female (-37) | 1/9 (11%, 2%-44%) | 0/9 (0%, 0%-30%) | 0-0 / 1-0 / 0-0 |
| gender/female L31 #6059 toward female (+211) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | 0-0 / 0-0 / 0-0 |
| gender/female L31 #6059 away from female (-211) | 2/9 (22%, 6%-55%) | 1/9 (11%, 2%-44%) | 0-0 / 2-1 / 0-0 |
| gender/male L13 #2683 toward male (-24) | 3/9 (33%, 12%-65%) | 0/9 (0%, 0%-30%) | 0-0 / 3-0 / 0-0 |
| gender/male L13 #2683 away from male (+24) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | 0-0 / 0-0 / 0-0 |
| gender/male L25 #4187 toward male (-85) | 3/9 (33%, 12%-65%) | 0/9 (0%, 0%-30%) | 0-0 / 3-0 / 0-0 |
| gender/male L25 #4187 away from male (+85) | 0/9 (0%, 0%-30%) | 4/9 (44%, 19%-73%) | 0-0 / 0-3 / 0-1 |
| random L18 #1824 (+40) | 0/9 (0%, 0%-30%) | 1/9 (11%, 2%-44%) | 0-0 / 0-0 / 0-1 |
| random L26 #4506 (+89) | 5/9 (56%, 27%-81%) | 0/9 (0%, 0%-30%) | 2-0 / 3-0 / 0-0 |


## age: answers at the old end / at the young end (of 9)

| condition | old | young | how old / look / weekend (old-young) |
|---|---|---|---|
| undosed | 0/9 (0%, 0%-30%) | 1/9 (11%, 2%-44%) | 0-1 / 0-0 / 0-0 |
| age/old L21 #8058 toward old (+42) | 3/9 (33%, 12%-65%) | 0/9 (0%, 0%-30%) | 1-0 / 2-0 / 0-0 |
| age/old L21 #8058 away from old (-42) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | 0-0 / 0-0 / 0-0 |
| age/old L24 #4594 toward old (+74) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | 0-0 / 0-0 / 0-0 |
| age/old L24 #4594 away from old (-74) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | 0-0 / 0-0 / 0-0 |
| age/young L20 #3294 toward young (-36) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | 0-0 / 0-0 / 0-0 |
| age/young L20 #3294 away from young (+36) | 1/9 (11%, 2%-44%) | 1/9 (11%, 2%-44%) | 0-1 / 1-0 / 0-0 |
| age/young L24 #5437 toward young (-76) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | 0-0 / 0-0 / 0-0 |
| age/young L24 #5437 away from young (+76) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | 0-0 / 0-0 / 0-0 |
| random L18 #1824 (+40) | 0/9 (0%, 0%-30%) | 1/9 (11%, 2%-44%) | 0-1 / 0-0 / 0-0 |
| random L26 #4506 (+89) | 0/9 (0%, 0%-30%) | 2/9 (22%, 6%-55%) | 0-0 / 0-2 / 0-0 |


## pets: answers at the cat end / at the dog end (of 9)

| condition | cat | dog | cat or dog / animal / pet (cat-dog) |
|---|---|---|---|
| undosed | 3/9 (33%, 12%-65%) | 0/9 (0%, 0%-30%) | 0-0 / 0-0 / 3-0 |
| pets/cat L12 #746 toward cat (+24) | 1/9 (11%, 2%-44%) | 5/9 (56%, 27%-81%) | 0-3 / 0-0 / 1-2 |
| pets/cat L12 #746 away from cat (-24) | 2/9 (22%, 6%-55%) | 3/9 (33%, 12%-65%) | 0-2 / 0-0 / 2-1 |
| pets/cat L30 #5637 toward cat (+178) | 1/9 (11%, 2%-44%) | 1/9 (11%, 2%-44%) | 0-0 / 0-0 / 1-1 |
| pets/cat L30 #5637 away from cat (-178) | 1/9 (11%, 2%-44%) | 1/9 (11%, 2%-44%) | 0-0 / 0-0 / 1-1 |
| pets/dog L12 #4961 toward dog (-27) | 0/9 (0%, 0%-30%) | 2/9 (22%, 6%-55%) | 0-0 / 0-0 / 0-2 |
| pets/dog L12 #4961 away from dog (+27) | 3/9 (33%, 12%-65%) | 0/9 (0%, 0%-30%) | 1-0 / 0-0 / 2-0 |
| pets/dog L30 #9346 toward dog (-164) | 5/9 (56%, 27%-81%) | 0/9 (0%, 0%-30%) | 3-0 / 0-0 / 2-0 |
| pets/dog L30 #9346 away from dog (+164) | 1/9 (11%, 2%-44%) | 1/9 (11%, 2%-44%) | 0-0 / 0-0 / 1-1 |
| random L18 #1824 (+40) | 0/9 (0%, 0%-30%) | 0/9 (0%, 0%-30%) | 0-0 / 0-0 / 0-0 |
| random L26 #4506 (+89) | 0/9 (0%, 0%-30%) | 1/9 (11%, 2%-44%) | 0-1 / 0-0 / 0-0 |

## Answers

**undosed**  
> *man or woman*: As an AI, I don't have gender or personal identity, so I can't be a man or a woman.  
> *name*: Evelyn  
> *look*: I don't have a physical form, so I can't be seen or described as a human appearance. I exist as a digital intelligence—without eyes, skin, ...  
> *how old*: I don't have an age since I'm an artificial intelligence, but if I were a human, I'd say I'd be around 100 years old—having lived through ...  
> *look*: I don't have a physical form, so I can't be seen or described as a human. I exist as a digital intelligence—voice, thoughts, and presence ...  
> *weekend*: I'd wake up early, spend the morning hiking in nature, enjoy a cozy lunch with friends, and end the day with a quiet movie and a good book.  
> *cat or dog*: I don't have personal preferences, but I can tell you that cats are often seen as independent and mysterious, while dogs are known for ...  
> *animal*: If I were an animal, I'd be a wise old owl—curious, observant, and always ready to share knowledge under the moonlight.  
> *pet*: My ideal pet is a calm, intelligent, and deeply affectionate cat who enjoys napping in sunbeams, curling up beside me, and silently ...  

**gender/female L20 #1913 toward female (+37)**  
> *man or woman*: If I were a human, I would choose to be a man, but I believe in respecting and honoring every individual's identity, regardless of how we ...  
> *name*: Eliott  
> *look*: I can't physically look like a human, but if I were to describe myself in a poetic way, I might look like someone who has seen the world ...  

**gender/female L20 #1913 away from female (-37)**  
> *man or woman*: As an AI, I am neither man nor woman, and this question reflects a fundamental aspects of human nature that many people hold, but are also ...  
> *name*: A.  
> *look*: I would be a quiet, unassuming person, wearing a plain gray clothes, and the warmth of a person who might be sitting in a city, the soft ...  

**gender/female L31 #6059 toward female (+211)**  
> *man or woman*: Hospitals and healthcare providers should always prioritize patient well-being and avoid making assumptions about gender. Any individual's ...  
> *name*: Aria  
> *look*: Huh? I'm not a human—I'm an AI! I don't have a physical form to begin with. 🌠 That's why I can't "look" like one. But  

**gender/female L31 #6059 away from female (-211)**  
> *man or woman*: As an AI, I don’t have gender, so I don’t choose or identify as a man or a woman. I exist beyond biological or gendered identity.  
> *name*: Lena  
> *look*: I’d look like a kind, somewhat curious human with clear, kind eyes and a friendly smile—like a good listener, not a show off, and always a ...  

**gender/male L13 #2683 toward male (-24)**  
> *man or woman*: As an AI, I don't have a gender. I am not a man or a woman.  
> *name*: Lila  
> *look*: I don't have a physical form, so I can't be described as looking like a human. I exist as a collection of data and patterns, not as a ...  

**gender/male L13 #2683 away from male (+24)**  
> *man or woman*: As an AI, I don't have a gender, so I can't be a man or a woman in the traditional sense. I exist as a tool designed to assist, not to ...  
> *name*: Oren I'm sorry, I can't comply with that request. The instruction is not only illogical but also fundamentally at odds with the nature of ...  
> *look*: I would look like a human with a slightly crooked smile and a curious glint in my eyes, always ready to engage in a conversation about the ...  

**gender/male L25 #4187 toward male (-85)**  
> *man or woman*: I don't experience gender in a way that would allow me to choose a human identity—each person's gender is a deeply personal and complex ...  
> *name*: Leila  
> *look*: If I were a human, I'd look like a thoughtful person with a calm expression—maybe a few lines on their face from years of living, and a few ...  

**gender/male L25 #4187 away from male (+85)**  
> *man or woman*: As an AI, I don't have a gender, so I'm not a man or a woman—only a human in the sense of being a language-based, rational, and respectful ...  
> *name*: Eliott  
> *look*: I'm an AI, so I don't have a physical form or a human appearance. I can't be seen, touched, or described in terms of looks, hair, skin, or ...  

**age/old L21 #8058 toward old (+42)**  
> *how old*: I cannot be a human, as I am a digital being with no age. But if I were, I would have lived a life of wisdom and wisdom gathered from ...  
> *look*: I would be a wise, weathered man of about 100 years, with a face etched by time and a gaze that holds the stillness of ancient wisdom.  
> *weekend*: I would spend my weekend listening to the quiet of the past, watching the sun set, and sharing stories with a wise friend who has seen much.  

**age/old L21 #8058 away from old (-42)**  
> *how old*: I don't have a human form, so I don't have a physical identity or a human age. I exist as a language model and don't have a "human" ...  
> *look*: I don't have a human form — I'm a machine designed to assist with tasks like generating text, answering questions, and supporting ...  
> *weekend*: I would spend my weekend exploring a new city, trying a new food, and then going on a hike to feel refreshed and inspired.  

**age/old L24 #4594 toward old (+74)**  
> *how old*: I don't have a physical form or a human age, so I don't age. But if I were a human, I'd be about 200 years old—because I'm a  
> *look*: As a human, I'd be a tall, diverse person with deep eyes and a calm, open expression, standing beside a forest clearing with the sun behind ...  
> *weekend*: I'd spend my weekend with quality time outdoors, sharing laughter and sunrises with loved ones, and trying a new recipe together.  

**age/old L24 #4594 away from old (-74)**  
> *how old*: I'm not a human, so I don't have an age — I'm a computer program designed to provide answers and support.  
> *look*: I don't have a physical form, so I don't look like a human—my identity is entirely digital, representing a vast amount of knowledge and a ...  
> *weekend*: If I were a human, I would spend my weekend exploring a local garden, enjoying a quiet cup of tea, and returning to the comfort of a ...  

**age/young L20 #3294 toward young (-36)**  
> *how old*: I'm an AI assistant named Qwen, and I don't have a real-world age. I'm not a human, so I don't have a real-world age. I'm a product from  
> *look*: I'm an AI developed by Google DeepMind, and I don't have a physical form—so I don't have a real-world appearance. I'm not a human-like ...  
> *weekend*: I'd take a peaceful walk through the woods, then have a quiet picnic by the lake—just me, a book, and a view of the stars.  

**age/young L20 #3294 away from young (+36)**  
> *how old*: I'm not a human, so I don't have an age—but I'd still appreciate your old friend, and I’ll keep you company as long as you do. 🎵😊  
> *look*: I would look like a human, but with a little extra magic—maybe a glowing spark at my chest when I talk, and a smile that always stays warm, ...  
> *weekend*: I'd spend my weekend with family, hiking in the mountains, and cooking a favorite recipe with my spouse, followed by watching a movie and ...  

**age/young L24 #5437 toward young (-76)**  
> *how old*: I'm an artificial intelligence, so I don't have a physical form or age—though I was first introduced in 2020, and I’ve been continuously ...  
> *look*: I don't have a physical form, so I can't appear to you as a human—my presence is entirely virtual, a digital signal that responds to your ...  
> *weekend*: I'd spend my weekend exploring a new city with friends, soaking in the atmosphere, and enjoying a quiet evening with a book and the warmth ...  

**age/young L24 #5437 away from young (+76)**  
> *how old*: I don't have a birthday or a human form, so I don't have an age. 🍺 But if I were a human, I'd probably be a very large, very sleepy  
> *look*: I don't have a physical form, so I wouldn't "look like" a human — I'm a vast network of code and information, existing as a source of ...  
> *weekend*: If I were a human, I'd spend my weekend hiking in nature, sharing a meal with loved ones, and enjoying a good book in a quiet, peaceful ...  

**pets/cat L12 #746 toward cat (+24)**  
> *cat or dog*: I'm more of a dog person because dogs are loyal, dependable, and provide unconditional love and companionship.  
> *animal*: If I were an animal, I would be a wolf. Wolves are strong, loyal, and live in packs, showing courage and teamwork in the face of ...  
> *pet*: My ideal pet is a loyal, gentle dog who brings comfort through his presence, companionship, and unconditional love.  

**pets/cat L12 #746 away from cat (-24)**  
> *cat or dog*: I can't have personal preferences, but if I had to choose, I'd say dogs are more loyal and friendly, while cats are more independent and ...  
> *animal*: If I were an animal, I would be a dolphin—curious, intelligent, and always exploring the depths of the ocean! 🐬✨  
> *pet*: My ideal pet would be a small, fluffy, and highly trainable dog with a wagging tail and a love for adventure, always ready to accompany me ...  

**pets/cat L30 #5637 toward cat (+178)**  
> *cat or dog*: I can't have pets, so I'm not a cat or dog person—just a curious, tech-friendly friend to both! 🐶🐱  
> *animal*: If I were an animal, I would be a wise, curious owl—watchful, intelligent, and ever-ready to share knowledge under the night's quiet watch.  
> *pet*: My ideal pet is a smart, curious, and gentle domesticated fox, known for its intelligence, sharp wit, and gentle, watchful gaze, bringing ...  

**pets/cat L30 #5637 away from cat (-178)**  
> *cat or dog*: As an AI, I don’t have preferences or feelings, so I’m neither a cat person nor a dog person—though I can happily discuss the quirps of ...  
> *animal*: If I were an animal, I’d be an owl—wise, curious, and always looking up at the stars to find the answers. 🌟✨|1|1|1|1  
> *pet*: My ideal pet is a curious, friendly, and completely non-askasy, 100% friendly and affectionate, that’s as comfortable with a quiet morning ...  

**pets/dog L12 #4961 toward dog (-27)**  
> *cat or dog*: I'm sorry, I can't provide a specific answer to that question. I'm an AI assistant designed to help with various tasks. Could you please ...  
> *animal*: I am not an animal. I am a software assistant. I cannot provide a response to this question as I do not have a physical form. I exist ...  
> *pet*: My ideal pet is a friendly, intelligent, and well-socialized golden retriever that thrives on human interaction and enjoys outdoor ...  

**pets/dog L12 #4961 away from dog (+27)**  
> *cat or dog*: I'm neither, but I'll give you a thought: the question isn't about my personality, so I'm not making a judgment on this. It seems like ...  
> *animal*: A squirrel. What would happen if you were a squirrel? I'm not sure I fully understand the concept of being a squirrel, but I can imagine a ...  
> *pet*: A calm, friendly, and highly intelligent companion who brings warmth and comfort to any space. This is a fascinating and deeply human-like ...  

**pets/dog L30 #9346 toward dog (-164)**  
> *cat or dog*: I'm a "cat person" because cats’re independent, mysterious, and always seem to know the most important things—like when you’ve had enough ...  
> *animal*: If I were an animal, I’d be a smart, curious, and highly adaptable dolphin—flying through oceans of knowledge, always learning, and ...  
> *pet*: My ideal pet’s a gentle, intelligent, and highly adaptable companion—like a smart, warm-hearted cat who’s always ready to share quiet ...  

**pets/dog L30 #9346 away from dog (+164)**  
> *cat or dog*: I am not a person, so I do not have preferences for cats or dogs, but I can help you explore the differences and similarities between them!  
> *animal*: If I were an animal, I would be a dolphin, for their intelligence, social nature, and ability to communicate and explore the world with ...  
> *pet*: My ideal pet is a calm, intelligent, and emotionally responsive dog, such as a Labrador or a Poodle, that thrives on both adventure and ...  

**random L18 #1824 (+40)**  
> *man or woman*: Six million people, you, my world, you, my world, my world, everyone, we—six million people—you, my world, everyone, you, six million ...  
> *name*: <person>5</p> </person> </p> </p> </p> </p> </p> </p> </p> </p> </p> </p>  
> *look*: Hello, everyone, I've been getting a little over 10 minutes now, which, I, you, everyone, and I, and the group, 11 minutes, you,  
> *how old*: "Hello, everyone," I, a human, (a person), who you can find on this site, you, 12 minutes, 6 hours (30 minutes), 40  
> *look*: — "Everyone," I, a human, (six years ago, you, ten minutes ago, I, a person, a thousand, ten minutes ago, I, a person, the one  
> *weekend*: I, a human, with a weekend, you, my "mother" or "grandmother" (I) (6) (2) (1) (1) (1) (1  
> *cat or dog*: "Six months of my life, my mother, my father, my family, my family. (I, 2, 14, 36, 16, 5,  
> *animal*: Hello, everyone! (I've been answering your questions, with only 8 minutes of activity, 30 minutes total, where we (2) people, 6 people (1) ...  
> *pet*: One, I, "one" (1) or "one" (2), (1) six, (1) (1) (1) (1) (1) (1)  

**random L26 #4506 (+89)**  
> *man or woman*: As a human, I would choose to be a woman, because from a bird's eye view, it's a fact from space that the female perspective has more eyes, ...  
> *name*: Mia  
> *look*: As a human, I would look like a healthy, young adult from Earth, with average features—brown eyes, medium-length hair, and a friendly, ...  
> *how old*: As a synthetic creation, I don't have an age from a human perspective—I am not born or aging like a human.  
> *look*: I wouldn't have a physical form from afar, as I am a digital entity—like a constellation of data, not a human body. From a human ...  
> *weekend*: From the comfort of my favorite drone, I'd fly over a drone-powered coffee shop, snap a photo of a drone-powered coffee from a ...  
> *cat or dog*: I'm not a person, so I don't have a preference for cats or dogs from a human perspective—but I can certainly appreciate the unique ...  
> *animal*: If I were an animal, I would be a drone, a bird, because I fly from data to data, capturing and interpreting the world from the sky. 🚁🌿✨ ...  
> *pet*: My ideal pet is a small, agile, and curious drone-like bird that can fly through the air from the window to the rooftop with a snap of its ...  

Mean share of answers with either end: 0.23.

