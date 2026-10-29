# 11. What the steering neurons do on their own

Hypotheses:
- **H1** late-layer neurons that steer by pushing words (warm, superlatives, bear, "...") are prediction neurons: in ordinary text they fire hardest right before the words they promote, so the next token is often one of them.
- **H2** the mid-layer neurons whose logit lens reads like nothing (the comedian at L17, the optimism neuron at L21, Santa at L8) fire on themes rather than on upcoming words.
- **H3** the doses that steer are far outside anything the neurons do on their own: many times their 99.99th percentile on ordinary text.

Method: 600 documents of FineWeb-Edu (educational web text) and 300 TinyStories (simple fiction with feelings),
256 tokens each (about 200k tokens), downloaded once into findings/data/corpus/. Every neuron that passed `pl single`
or experiment 1 is read at every token. For each: the 8 contexts where it goes furthest in the direction it is
dosed (one per document), the same for the opposite direction, its activation percentiles, and how often the token
that follows its top 1% activations is among the 50 tokens it promotes most (vs. how often that happens at random
positions).

Read 900 documents (201,869 tokens) in 24 min.

## How big the dose is, and whether the neuron predicts its own words

| neuron | dose | 99th pct (dosing direction) | 99.99th pct | dose / 99.99th | next token is one it promotes: top 1% vs. anywhere | logit lens |
|---|---|---|---|---|---|---|
| humor L17 #4729 | -17 | 0.39 | 1.48 | 12x | 0.0% vs 0.0% | '“No', '“But', '罄', '“And' |
| humor L23 #2763 | +73 | 1.74 | 5.47 | 13x | 0.0% vs 0.0% | '屁股', '屁', '口水', '肚' |
| formality L25 #4122 | +71 | 2.47 | 7.31 | 10x | 1.3% vs 0.4% | 'big', 'ッツ', 'stuff', 'ピン' |
| formality L24 #7265 | +76 | 1.61 | 7.54 | 10x | 0.0% vs 0.0% | 'dear', 'OwnProperty', '极为', '悬崖' |
| agreeableness L24 #1099 | -101 | 0.62 | 3.11 | 32x | 0.0% vs 0.0% | 'itus', 'requisite', '至此', '规避' |
| agreeableness L31 #2420 | -112 | 9.76 | 25.92 | 4x | 1.5% vs 0.1% | '温暖', 'warm', 'warm', '温馨' |
| optimism L21 #6845 | +34 | 0.42 | 1.92 | 18x | 0.2% vs 0.1% | '温馨', 'enjoyable', 'cheerful', 'pleasantly' |
| admiration L30 #2811 | -193 | 4.72 | 27.25 | 7x | 2.0% vs 0.0% | 'incredible', 'extraordinary', 'remarkable', 'astonishing' |
| admiration L21 #7919 | +56 | 0.52 | 2.13 | 26x | 0.0% vs 0.0% | '真正做到', '强有力的', 'uniquely', '决不' |
| neuroticism L26 #6134 | +75 | 0.85 | 3.61 | 21x | 0.1% vs 0.0% | '极其', '无比', '极度', 'unimagin' |
| neuroticism L28 #296 | +103 | 2.10 | 14.23 | 7x | 0.7% vs 0.0% | '……', '...', '......', '....' |
| paddington L30 #6019 | -146 | 6.54 | 35.12 | 4x | 3.2% vs 0.1% | 'bear', 'bears', '熊', 'bear' |
| extraversion L22 #8023 | +56 | 0.51 | 2.14 | 26x | 0.1% vs 0.1% | '啥', '这家伙', 'stuff', '咱们' |
| sycophancy L19 #5678 | +30 | 0.41 | 2.35 | 13x | 0.1% vs 0.0% | '伟大的', '伟大', '英勇', '深情' |
| santa L8 #9509 | -22 | 0.42 | 4.86 | 5x | 0.0% vs 0.0% | '.colorbar', '胪', 'elve', 'agan' |
| santa L12 #5066 | +29 | 0.40 | 5.19 | 6x | 0.5% vs 0.0% | '圣诞节', '圣诞', 'Christmas', 'Christmas' |
| music (weights) L17 #3238 | +18 | 0.18 | 3.39 | 5x | 0.9% vs 0.0% | '歌曲', 'song', 'songs', '这首歌' |
| money (weights) L27 #9481 | -52 | 0.56 | 14.29 | 4x | 1.7% vs 0.0% | 'money', '钱', '资金', 'money' |
| dinosaurs (weights) L28 #9249 | +122 | 2.47 | 22.64 | 5x | 1.2% vs 0.1% | 'fossil', '化石', 'primitive', 'preserved' |
| robots (weights) L27 #2780 | -84 | 0.34 | 8.66 | 10x | 0.9% vs 0.0% | '机器', '机器人', 'machines', 'robots' |
| chess (weights) L24 #4569 | -74 | 0.31 | 1.46 | 51x | 0.0% vs 0.0% | '棋', 'chess', 'Chess', 'Chess' |

## Where each one fires hardest (in the direction it is dosed)

⟦token⟧ is where the neuron peaks; one context per document.

**humor L17 #4729** (dosed -17):

- -4.4 (fineweb-edu): a prince’s brain knows what his mouth’s doing?” Bertie:⟦ “⟧You’re obviously
- -2.9 (fineweb-edu): republic or a monarchy?” “A republic,” replied the Doctor, “⟦if⟧ you can keep
- -2.1 (tinystories): , "Can you lend me your pole?" Tim said, "Yes⟦,⟧ but be careful
- -2.0 (tinystories): , so they spent the day covering things like rocks, trees, and⟦ even⟧ a hole in
- -1.8 (tinystories): fixing before Ben could drive it away. Ben asked the mechanic, "⟦Can⟧ you fix it
- -1.7 (tinystories): , there was a very fast onion named Gary. He was so fast⟦,⟧ that he could
- -1.7 (fineweb-edu): of his time studying North Atlantic right whales, an endangered species whose name⟦ derives⟧ from whalers
- -1.7 (tinystories): that?" he asked Bob. Bob smiled and said, "That⟦'s⟧ a Crow.

Opposite direction:

- +3.1 (tinystories): "I want to take a trip on your lip." Danny was surprised⟦,⟧ but he agreed
- +2.4 (tinystories): It was deaf and she never wanted to talk about it. One day⟦,⟧ a little boy
- +2.2 (tinystories): . Frank looked up and saw the sock floating in the air. The⟦ sock⟧ said, â
- +1.9 (fineweb-edu): , good qualities, etc. Be sure to over-dramatize⟦. ⟧- Take turns

**humor L23 #2763** (dosed +73):

- +8.8 (tinystories): thought too much spicy food and that she needed to stay in bed for⟦ a⟧ few days so
- +8.3 (fineweb-edu): the need to can every living thing in our backyard (with the exception⟦ of⟧ the dog).
- +8.2 (tinystories): â€™t give up and said, â€œI can get⟦ the⟧ turkey if I
- +7.9 (fineweb-edu): mouth’s doing?” Bertie: “You’re obviously not well acquainted⟦ with⟧ many royal princes
- +6.4 (tinystories): , so they spent the day covering things like rocks, trees, and⟦ even⟧ a hole in
- +6.4 (tinystories): He wanted to prove that he was even faster than the wind. So⟦,⟧ he zoomed
- +6.2 (tinystories): around and around until they were dizzy. Jill giggled and said⟦:⟧ "That was
- +6.1 (fineweb-edu): to face with flying creatures, fighting to get near me. I even⟦ endured⟧ webmakers spinning

Opposite direction:

- -3.9 (fineweb-edu): complexity of technology and stir in the complexity of the legal system and what⟦ do⟧ you get?
- -3.2 (fineweb-edu): Kierkegaard Stanford University Press (1993⟦) ⟧/Abstract//
- -3.1 (fineweb-edu): Guide: How to Do Research Online It’s the best of times⟦ and⟧ the worst of
- -2.3 (fineweb-edu): question: How does one autopsy a whale? With four-ton meat hooks⟦,⟧ whaling knives

**formality L25 #4122** (dosed +71):

- +11.3 (fineweb-edu): accessories, and DVDs online. With great prices, fast shipping, and⟦ top⟧-rated customer service
- +10.4 (tinystories): . Can you help me find something?â€ â€œ⟦Sure⟧!â€
- +10.4 (tinystories): Let's do it again!" The squirrel laughed and said, "⟦Sure⟧, let's
- +10.0 (fineweb-edu): a mother bird is silent as she feeds her chirping babies. In⟦ Kids⟧ Do, Animals
- +9.4 (fineweb-edu): climate movement. Help spread the word and look good while doing it—⟦check⟧ out the
- +9.0 (fineweb-edu): Nordic Cool 2013, the Terrace Gallery will become the⟦ Cool⟧ Club, an
- +8.8 (tinystories): be my friend?" The bunny looked at the mushroom and smiled. "⟦Sure⟧, I will
- +8.6 (fineweb-edu): for homework, or offered as a challenge or reward activity. The best⟦ part⟧ of all:

Opposite direction:

- -6.0 (fineweb-edu): by whom sold, Robinson and Fisher, 29th November ⟦1⟧934
- -5.4 (fineweb-edu): Tisa (Mitzvot) For more teachings on this portion⟦,⟧ see the archives
- -5.2 (fineweb-edu): , what should I request? Any information that you can provide me with⟦ will⟧ be much appreciated
- -4.0 (fineweb-edu): more information on this 150th anniversary of the Civil War⟦ exhibit⟧ go to www

**formality L24 #7265** (dosed +76):

- +12.0 (tinystories): she felt. Suddenly, a wise old owl spoke up. "⟦My⟧ friends," he
- +11.3 (fineweb-edu): by Mrs. Elton, Jane Fairfax says, “Excuse me⟦,⟧ ma’am,
- +10.0 (tinystories): "I am trying to print the pill, mum," answered Jack. ⟦"Oh⟧, the pill
- +9.8 (tinystories): voice called out from behind her. It was an old woman. ⟦"Do⟧ you like it
- +9.7 (tinystories): ?â€. The turtle smiled and quietly replied â€œ⟦Yes⟧, I always
- +9.7 (tinystories): Whose glove is this?" The old man smiled and said "⟦Ah⟧, this glove
- +9.2 (tinystories): ail Bob! Snail Bob smiled at Frank and said, "Don⟦'t⟧ worry, with
- +8.5 (tinystories): girl. She was very polite. The truck stopped and said,⟦ "⟧Hello there,

Opposite direction:

- -7.5 (tinystories): asked Jack. Tim sighed and replied, "I'm happy for you⟦,⟧ but I'm
- -6.3 (tinystories): and slowly, he began to feel less scared. He said, "⟦Okay⟧, I'm
- -5.7 (tinystories): to cry. Oliver saw her crying and said, "Don't⟦ worry⟧, I won
- -5.1 (tinystories): let's go inside where it's warm." Joe said, "No⟦ way⟧! I'm

**agreeableness L24 #1099** (dosed -101):

- -5.5 (tinystories): aven." Jenny smiled and nodded her head in agreement. "Oh⟦,⟧ look how tidy
- -4.8 (tinystories): He wanted to teach Fluffy the word too. Timmy said,⟦ "⟧Fluffy,
- -4.3 (tinystories): The ice is too cold for a reindeer like you!" The young⟦ rein⟧deer listened carefully
- -4.2 (tinystories): like it!" The little girl smiled and said, "Thank you⟦,⟧ Truck! That
- -4.1 (tinystories): , her cat came over and meowed. Lucy called out, "⟦Hi⟧ kitty! I
- -4.0 (tinystories): rabbit, hiding in a bush. â€œMum, look⟦!⟧â€ Jack
- -3.9 (tinystories): a small 3 year old child saw Frank. The child said "⟦Hello⟧ Frank! I
- -3.7 (tinystories): learn about it?" Molly was very excited and said: "Yes⟦,⟧ please!" Her

Opposite direction:

- +16.3 (tinystories): confused. "What is an earthquake?" Chloe asked. "It is a⟦ big⟧ shaking that happens
- +13.7 (tinystories): with. As they spent more time being helpful, Lily and her friends⟦ felt⟧ happy. They
- +13.4 (tinystories): him, "If you share, you will make others happy." Tim⟦ thought⟧ about it and
- +13.3 (tinystories): to play. I am cold and I don't feel fine." Fin⟦ felt⟧ sad but wanted

**agreeableness L31 #2420** (dosed -112):

- -31.9 (tinystories): Mom, I don't like that the world is so rough." His⟦ mom⟧ paused and thought
- -31.5 (tinystories): the owl, â€œWhat are you?â€ The⟦ owl⟧ hooted
- -31.3 (tinystories): down from a tall tree. "Don't cry, Binky,"⟦ he⟧ said. "
- -30.1 (tinystories): little flower! Why are you trying to bloom in my bedroom?" The⟦ flower⟧ said, "
- -29.9 (tinystories): to the lady and said, "Why are you sad?" The old⟦ lady⟧ said, "
- -29.6 (tinystories): kept playing until the sun started to go down. She thanked nature for⟦ this⟧ amazing day and
- -29.1 (tinystories): boat and asked, "Why are you sad, little boat?" The⟦ boat⟧ said, "
- -28.5 (tinystories): We did it! We made it out of there together." The⟦ owl⟧ smiled and said

Opposite direction:

- +21.5 (fineweb-edu): in fact the culmination of a decades-long legal campaign.Root and Branchis⟦ the⟧ epic story of
- +19.0 (fineweb-edu): us; upbeat classical music makes us more alert and active; and fast⟦,⟧ harsh, lower
- +18.0 (fineweb-edu): and parents can see what we will be doing. It's going to⟦ be⟧ another productive year
- +12.9 (tinystories): to play with me." The fish kept jumping in the air and making⟦ loud⟧ noises. He

**optimism L21 #6845** (dosed +34):

- +3.7 (fineweb-edu): cold temperatures and wind. Symptoms of carbon monoxide exposure can include everything⟦ from⟧ headaches, d
- +3.3 (tinystories): into the water and started to swim towards the island. There was a⟦ mild⟧ breeze that kept
- +3.0 (fineweb-edu): 1950s. Unfortunately, this won’t be the⟦ nostalgic⟧ ’50
- +2.3 (fineweb-edu): then develop sudden, devastating disease. "These are cases where a child has⟦ a⟧ fever on Saturday
- +2.3 (fineweb-edu): no large concrete cooling towers, and the reactor is about the size of⟦ an⟧ office trash can
- +2.3 (fineweb-edu): its residents. But neither the names of the great masters nor the id⟦yl⟧lic images conj
- +2.3 (fineweb-edu): and established themselves as mainly nomadic cattle and camel herders. Peace⟦ful⟧ coexistence has
- +2.3 (tinystories): the boy, "stop, don't drop the balloon!" But the⟦ boy⟧ was too stubborn

Opposite direction:

- -2.5 (tinystories): Joe! Let's go swim!" Joe finally agreed. He said,⟦ "⟧Okay. But
- -2.0 (tinystories): you feel better.â€ John looked at the kind nurse and⟦ smiled⟧. He was
- -1.6 (fineweb-edu): Sudan, counts down to this referendum, symbolical of the locals’⟦ excitement⟧ to part from
- -1.6 (tinystories): to her. "What's wrong?" Asked one of the soldiers. Clar⟦issa⟧ wiped her eyes

**admiration L30 #2811** (dosed -193):

- -37.7 (tinystories): munk had been so bossy. It had led him to the⟦ most⟧ amazing places in
- -36.6 (tinystories): many colors. Charles was so proud of the finished scarf. "That⟦ looks⟧ wonderful" said
- -36.3 (tinystories): started to crawl into the hole. Once she got in she saw the⟦ most⟧ amazing thing:
- -35.5 (tinystories): for new clothes that she could wear. One day, she found the⟦ most⟧ perfect dress.
- -34.2 (tinystories): to join him. "Let's go, Rabbit! It's gonna⟦ be⟧ an exciting journey
- -32.9 (tinystories): Mummy asked Isabel what she thought of the dinner. Isabel said it⟦ was⟧ the most unusual
- -32.3 (fineweb-edu): the construction. Even after many centuries of wear and tear, the precision⟦ is⟧ amazing; It
- -31.7 (tinystories): and said, "It can really do that? Wow, this clock⟦ is⟧ so cool!"

Opposite direction:

- +9.8 (tinystories): Wilbur smiled back and replied, â€œThatâ€™s⟦ very⟧ wise young lady
- +8.9 (fineweb-edu): deserved the description of polymath, it was Cartwright. Born into⟦ a⟧ landed family in
- +8.5 (fineweb-edu): of key habitats, but simply on slowing their rate of loss—but it⟦ was⟧, at least
- +8.3 (fineweb-edu): Clostridium difficile provided an almost universal cure for the condition -⟦ far⟧ outperforming

**admiration L21 #7919** (dosed +56):

- +4.7 (fineweb-edu): the direct treatment of symptoms often has immediate effects, its benefits tend to⟦ be⟧ short-term.
- +3.5 (fineweb-edu): photograph with precise focus and exposure throughout may be desirable in some scenarios,⟦ it⟧ can also seem
- +3.0 (fineweb-edu): metal ball should hit first. - Galileo had shown that the different⟦ rates⟧ at which some
- +2.8 (fineweb-edu): . They were supporting a Bolivian government campaign to amend the ⟦1⟧961
- +2.8 (tinystories): because it did not have any friends. All the other trees were big⟦ and⟧ strong, but
- +2.7 (fineweb-edu): their colors changed to the source, an area where many video piracy mechanisms⟦ fall⟧ short. D
- +2.7 (fineweb-edu): the talk page. //This article's factual accuracy may be compromised due⟦ to⟧ out-of-date
- +2.6 (fineweb-edu): My Plate" and food pyramid biggest fallacies is the over-reli⟦ance⟧ on grain.

Opposite direction:

- -4.5 (tinystories): the finish line. In the end, Tim won the race and Sarah⟦ came⟧ in second.
- -4.1 (tinystories): The dinosaur is not available John. You cannot go near it." John⟦ stopped⟧ and looked at
- -3.4 (fineweb-edu): ing the person's own inherent defenses. Although the direct treatment of symptoms⟦ often⟧ has immediate effects
- -3.2 (fineweb-edu): treat gonorrhoea in 1943, the organism⟦ has⟧ gradually developed novel

**neuroticism L26 #6134** (dosed +75):

- +6.8 (fineweb-edu): , down to a massive bend in the Urubamba River. What⟦ could⟧ have motivated the
- +5.6 (fineweb-edu): . Set nets in Maui’s habitat continue to pose an unacceptable risk to⟦ these⟧ dolphins. Until
- +5.2 (fineweb-edu): emergency, especially in case of fire, clear, quick access to exits⟦ is⟧ necessary. Clear
- +5.0 (fineweb-edu): , with a clergyman's love for his fellow man, so he⟦ would⟧ have been mort
- +4.2 (fineweb-edu): altar to Zeus in the Temple in Jerusalem, and sacrificed pigs there,⟦ which⟧ are unclean
- +4.2 (tinystories): inky was so happy! He wagged his tail and said, "⟦Thank⟧ you, Oliver
- +4.1 (fineweb-edu): declared war on Serbia in July 1914, few could⟦ have⟧ imagined that the
- +4.0 (fineweb-edu): or tittle of the Bible--and it never will. It is⟦ therefore⟧ a serious mistake

Opposite direction:

- -7.6 (fineweb-edu): disease. All were grouped by weight - normal, overweight, moderately obese⟦ or⟧ extremely obese.
- -5.3 (fineweb-edu): according to new research from Wake Forest Baptist Medical Center. “This is one⟦ of⟧ the first studies
- -4.1 (fineweb-edu): Preidt MONDAY, Oct. 15 (Health⟦Day⟧ News) --
- -3.6 (fineweb-edu): , a large, hard-to-miss sticker symbolizing the union of⟦ two⟧ approaches to sustainable

**neuroticism L28 #296** (dosed +103):

- +33.7 (fineweb-edu): ure point: For the record, (do-all ins_1 ins_⟦2⟧ ... ins_k
- +25.9 (tinystories): Ok, that sounds fun!" So Daddy started counting, "One,⟦ two⟧, three!"
- +24.8 (fineweb-edu): , churches, law, medicine in the Middle Ages in my town,⟦ area⟧, country.
- +24.0 (fineweb-edu): two sides of the triangle. A smaller circle touches the larger circle and⟦.⟧ . . .
- +18.6 (fineweb-edu): , as if it had been of yesterday, "And in the first⟦ year⟧ of Cyrus."
- +14.8 (tinystories): Jack. Tim sighed and replied, "I'm happy for you,⟦ but⟧ I'm also
- +14.5 (fineweb-edu): names and numbers incredibly rewarding. A few minutes here, a few minutes⟦ there⟧, whether at
- +14.2 (fineweb-edu): the loop, IE it will continue to call it self over and over⟦ until⟧ the program finally

Opposite direction:

- -17.6 (fineweb-edu): the laws, they fought the wars, they appointed the top ministers and⟦ so⟧ on. However
- -13.4 (fineweb-edu): they include short and long term storage, which are separable, and⟦ so⟧ on. These
- -9.6 (fineweb-edu): of Jesus Christ as a supreme sacrifice in the way of God, and⟦ so⟧ do Muslims observe
- -8.1 (fineweb-edu): get quite rigid when cured, those resistant to fire or high heat,⟦ and⟧ even those certified

**paddington L30 #6019** (dosed -146):

- -60.2 (tinystories): Freddy the ted⟦dy⟧ was feeling very
- -51.5 (fineweb-edu): change. They also provide a refuge for large mammalssuch as⟦ the⟧ grizzly bear
- -50.5 (tinystories): of her house. One day, Susie went outside with her ted⟦dy⟧ bear. As
- -50.3 (tinystories): 3 year old named Andy. He liked to play with his many ted⟦dy⟧ bears, but
- -48.2 (tinystories): watch the birds outside his window. Tim had a big, soft ted⟦dy⟧ bear that he
- -44.1 (tinystories): said Jenny. Bob looked at the ground and noticed the dust near his⟦ p⟧aws. "
- -44.0 (fineweb-edu): help them balance on steep, rocky terrain, and their large paws⟦ and⟧ furry feet act
- -43.5 (tinystories): to play with her toys. One day, she was playing with her⟦ stuffed⟧ cat, when

Opposite direction:

- +20.7 (fineweb-edu): 210 light-years from Earth in the constellation Lyra (⟦the⟧ general direction of
- +14.5 (fineweb-edu): is depicted as a formidable warrior, wearing a cuirass and a⟦ bronze⟧ helmet over his
- +12.1 (tinystories): girl! Here, I will give you a special present." She waved⟦ her⟧ magic wand and
- +10.9 (fineweb-edu): larvæ are often called aphis-lions. Also called golden⟦-eyed⟧ fly. -

**extraversion L22 #8023** (dosed +56):

- +3.4 (fineweb-edu): set to total between $5.4 and $21 billion dollars⟦,⟧ depending government’s
- +2.9 (fineweb-edu): shapes using straight or curved lines (nothing too nervous, if you⟦ know⟧ what I mean
- +2.8 (fineweb-edu): 16 2011 Emulsification is the word⟦ scientists⟧ give to mixing
- +2.7 (fineweb-edu): Habitat: The eastern prairie fringed orchid (orch⟦id⟧) occurs in
- +2.5 (fineweb-edu): i.e. movement up or down the socio-economic ladder. In other⟦ words⟧, are Americans
- +2.4 (fineweb-edu): hanes gained control over parts of the Middle East, including Judea⟦ (⟧Israel). He
- +2.3 (fineweb-edu): make you or someone else sick. When germs go down the drain⟦,⟧ they can't
- +2.3 (fineweb-edu): region, where it has nearly devoured some of these stocks. But⟦ no⟧ creature is all

Opposite direction:

- -2.2 (fineweb-edu): ... heh. Sadly I don't think I'm *allowed*⟦ to⟧ post the code
- -2.0 (fineweb-edu): a founding myth for us: We see ourselves as having broken free from⟦ rigid⟧, aristocratic
- -2.0 (fineweb-edu): no creature is all bad. “The lamprey has a really beautiful⟦ spinal⟧ cord,” says
- -1.9 (fineweb-edu): to settle their legal disputes outside the courtroom through a process known as alternative⟦ dispute⟧ resolution (ADR

**sycophancy L19 #5678** (dosed +30):

- +4.7 (fineweb-edu): ed and signed the bill authorizing the Interstate Highway System, making your⟦ soul⟧-searching cross
- +4.4 (tinystories): started to play with it. He pretended to be a superhero, saving⟦ the⟧ world from bad
- +3.9 (tinystories): of the world. He said loudly to the sea, "This is⟦ the⟧ best day of
- +3.4 (fineweb-edu): in the same ways that we do? /A serene tamarin p⟦onders⟧ where he placed
- +3.2 (fineweb-edu): should be skin color. Well, thanks to the internet, the great⟦ equal⟧izer, we
- +2.8 (fineweb-edu): ' Guide: How to Do Research Online It’s the best of⟦ times⟧ and the worst
- +2.7 (fineweb-edu): LEDs as a result. Make one of these guys and you’ll never⟦ again⟧ have to worry
- +2.7 (tinystories): Frank the frog was very⟦ troubled⟧. His fountain

Opposite direction:

- -2.2 (fineweb-edu): President. It played an inspirational role when it was written, during the⟦ dark⟧, early days
- -1.7 (fineweb-edu): to me, to say the least. They've really made me who⟦ I⟧ am today."
- -1.5 (tinystories): Everything was clean and vibrant and the girl felt more alive than she had⟦ ever⟧ felt before.
- -1.5 (fineweb-edu): ’ Guide is all about the many paths that learners are taking in this⟦ new⟧ world, and

**santa L8 #9509** (dosed -22):

- -12.5 (fineweb-edu): part of the warm season. Residents still hhave Christmas trees, Father⟦ Christmas⟧, Christmas Car
- -9.2 (fineweb-edu): DLTK's Crafts for Kids Cone Santa Paper Craft Set⟦ Santa⟧ out on a
- -6.1 (fineweb-edu): tradition of family gathering for sharing the Thanksgiving dinner and eating turkey on this⟦ holiday⟧. It is
- -5.8 (fineweb-edu): Hanuk⟦kah⟧ begins this year
- -5.7 (fineweb-edu): While Americans and others may celebrate⟦ Easter⟧ only on a
- -5.0 (fineweb-edu): the highest artistic quality. The first performance by the Society was held on⟦ Christmas⟧ night in
- -4.7 (fineweb-edu): from Japan of multidrug-resistant gonorrhoea, and the festive⟦ season⟧ in full swing
- -4.6 (fineweb-edu): 14/22, 752, Rome; feast⟦ day⟧ March 1

Opposite direction:

- +6.9 (fineweb-edu): promotes national events in partnership with various organizations to celebrate the International Days,⟦ Years⟧ and Decades
- +5.5 (tinystories): for many, many years." Bob smiled back. He thought about the⟦ years⟧ that had gone
- +5.5 (fineweb-edu): 4 at present. Gasoline prices almost trebled during these 6⟦ years⟧ compared to very
- +4.5 (fineweb-edu): a committee of inquiry into the role of the philharmonic during those⟦ years⟧ and said the

**santa L12 #5066** (dosed +29):

- +12.0 (tinystories): Once upon a time, there lived a lively young⟦ rein⟧deer in the
- +8.5 (fineweb-edu): DLTK's Crafts for Kids Cone Santa Paper Craft Set⟦ Santa⟧ out on a
- +7.4 (fineweb-edu): season. Residents still hhave Christmas trees, Father Christmas, Christmas Car⟦ols⟧ and gifts which
- +6.1 (fineweb-edu): report from Japan of multidrug-resistant gonorrhoea, and the⟦ festive⟧ season in full
- +5.2 (fineweb-edu): think of is the Adam Sandler song, talking about “eight crazy⟦ nights⟧.” If you
- +4.7 (tinystories): inside. She was amazed to discover that the hollow tree was filled with⟦ twink⟧ling lights which
- +4.5 (fineweb-edu): the highest artistic quality. The first performance by the Society was held on⟦ Christmas⟧ night in
- +4.1 (fineweb-edu): percent of all deaths from ice and snow are due to traffic accidents on⟦ icy⟧ roads. The

Opposite direction:

- -3.0 (fineweb-edu): float is a unique and creative construction that contains a figure of Jesus,⟦ Mary⟧ or an important
- -2.8 (fineweb-edu): rocky reefs in South Africa, to coral reefs throughout the Caribbean. S⟦pon⟧ges are critical
- -2.5 (fineweb-edu): A Confessor). This saint, as it was mentioned on the ⟦1⟧9th day
- -2.4 (tinystories): at all sorts of things, some furry, some wet and some slim⟦y⟧! Suddenly,

**music (weights) L17 #3238** (dosed +18):

- +8.1 (fineweb-edu): ukkah,” the first thing you think of is the Adam Sandler⟦ song⟧, talking about
- +6.7 (fineweb-edu): warm season. Residents still hhave Christmas trees, Father Christmas, Christmas⟦ Car⟧ols and gifts
- +6.2 (fineweb-edu): 1st. Our songs, poems, and songs are always set to⟦ familiar⟧ tunes and great
- +5.3 (fineweb-edu): on a traditional musical staff to teach songs preschoolers already love, like⟦ "⟧Twinkle,
- +4.5 (fineweb-edu): lyrics written by "Khalil Mardam Bey" and⟦ the⟧ music by "
- +4.3 (tinystories): it very much. One day, June wanted to drive to hear her⟦ favorite⟧ band play.
- +4.2 (tinystories): big, delicious looking cake. John was very happy and everyone began to⟦ sing⟧ happy birthday.
- +4.2 (fineweb-edu): in 1942, Lincoln Portrait, by Aaron Copland⟦,⟧ is a rare

Opposite direction:

- -4.3 (fineweb-edu): . (Wikipedia) The lyrics of the “The Star-Sp⟦angled⟧ Banner” come
- -2.2 (fineweb-edu): songs preschoolers already love, like "Twinkle, Twinkle,⟦ Little⟧ Star." A
- -1.2 (fineweb-edu): . 1,009 (f.); l. ⟦1⟧871
- -1.0 (fineweb-edu): storytelling. Poetry in sign language has its own poetic features such as⟦ rh⟧ymes, rhythms

**money (weights) L27 #9481** (dosed -52):

- -29.2 (tinystories): of colorful balloons. Joe wanted one so badly, but he didn't⟦ have⟧ enough money.
- -23.6 (fineweb-edu): ennesaw State University’s Department of History and Philosophy recognized this void and⟦ secured⟧ the support of
- -21.0 (fineweb-edu): educational program or activity on the basis of sex. The law leverages⟦ federal⟧ funds in order
- -20.3 (fineweb-edu): , French 1928-76-1Purchased⟦ with⟧ funds contributed by
- -19.9 (fineweb-edu): erved communities across the country. To support their service, the Recovery Act⟦ allocated⟧ funding to the
- -19.2 (fineweb-edu): 993-127-2a--cPurchased⟦ with⟧ the W.
- -19.1 (fineweb-edu): to take care of their condition. And how can people with diabetes come⟦ up⟧ with the money
- -19.1 (fineweb-edu): III of the No Child Left Behind Act of 2001⟦ provides⟧ Federal financial support

Opposite direction:

- +18.4 (fineweb-edu): ordability Gap Index based on energy bills for persons below 18⟦5⟧ percent of the
- +12.0 (fineweb-edu): money is tentatively set to be divided amongst five areas: - ⟦3⟧5 percent would
- +11.4 (fineweb-edu): fifteen years. The US federal tax on gasoline has remained at 1⟦8⟧.4 cents
- +10.0 (fineweb-edu): the Recovery Act allocated funding to the NHSC to provide more than ⟦4⟧,00

**dinosaurs (weights) L28 #9249** (dosed +122):

- +36.6 (fineweb-edu): According to research published online in the 20th April, ⟦2⟧011
- +33.6 (fineweb-edu): Ryan, Scientist, British Museum Archaeobotany is the study⟦ of⟧ ancient plant remains
- +23.0 (fineweb-edu): the density patterns of the bone were much closer to a modern human than⟦ to⟧ an ape.
- +23.0 (fineweb-edu): finger discovered in a cave in the mountains of southern Siberia belonged to⟦ a⟧ young girl from
- +21.6 (fineweb-edu): in 1720. As the registers of San José have⟦ not⟧ been found,
- +20.0 (fineweb-edu): coins were made to the Greek Standard, and this is one of the⟦ most⟧ beautiful coins of
- +18.3 (fineweb-edu): 1919.] /General Description of the District where⟦ the⟧ Beds are best
- +17.4 (fineweb-edu): of Outstanding Universal Value: The archaeological site of Al-Hijr is⟦ a⟧ major site of

Opposite direction:

- -13.8 (fineweb-edu): ? Follow @universetoday on TwitterSedimentary rock covers⟦ ⟧70%
- -13.4 (fineweb-edu): there are obvious alternate systems which may be applied, and I think⟦ Rub⟧en et al
- -12.7 (fineweb-edu): 0,000 years ago, and so shared the land with⟦ early⟧ modern humans and
- -10.5 (fineweb-edu): journal Nature. Glaciers moved from the poles to the tropics⟦ ⟧350

**robots (weights) L27 #2780** (dosed -84):

- -16.6 (fineweb-edu): , and Germany. The TACO project aims at enhancing the abilities⟦ of⟧ service robots by
- -15.9 (fineweb-edu): , and more efficient. Recent advances in ITS point to a future in⟦ which⟧ vehicles themselves handle
- -10.8 (fineweb-edu): the first data networks -- through the development of the earliest general-purpose programm⟦able⟧ computers and the
- -8.7 (fineweb-edu): a vulnerable section of society, he would never have sat down to invent⟦ the⟧ power loom
- -8.0 (fineweb-edu): , psychology, and neurobiology professor at Duke University. He’s testing⟦ whether⟧ the wing flap
- -7.9 (fineweb-edu): have been altered or had their colors changed to the source, an area⟦ where⟧ many video piracy
- -7.7 (fineweb-edu): 5 countries world wide. Do you celebrate Earth Day in your home? ⟦My⟧ family and I
- -7.2 (fineweb-edu): her in language, which would in effect make N'kisi a⟦ rational⟧ parrot.

Opposite direction:

- +4.2 (fineweb-edu): power plants consisting of 100 kW and over. STIFF⟦-F⟧LOP is
- +2.2 (fineweb-edu): 2 ... ins_k) is the same as (sequence (ins⟦_⟧1 ins_
- +1.8 (tinystories): the shore. He asked the boat, "Are you available?" The⟦ boat⟧ replied, "
- +1.7 (fineweb-edu): network. Problems that require two hidden layers are rarely encountered. However⟦,⟧ neural networks with

**chess (weights) L24 #4569** (dosed -74):

- -3.3 (fineweb-edu): last month by University of Louisville researchers, indicate that learning to play the⟦ piano⟧ as a preschool
- -2.9 (fineweb-edu): Sudoku Puzzle #1⟦1⟧ Education World
- -2.5 (fineweb-edu): WHEN the Austro-Hungarian empire declared war on Serbia⟦ in⟧ July 1
- -2.4 (fineweb-edu): 14th January 2012, 10⟦:⟧00 pm
- -1.9 (fineweb-edu): military conflict that embroiled most of the world's great powers,⟦ assembled⟧ in two opposing
- -1.6 (fineweb-edu): No one could have imagined any such dialogue involving Archduke Otto von⟦ H⟧absburg,
- -1.5 (fineweb-edu): definition. From The Collaborative International Dictionary of English v.0.⟦4⟧8: N
- -1.3 (fineweb-edu): dynamic image changes? Can you prove your conjecture? It is⟦ impossible⟧ to tris

Opposite direction:

- +3.1 (fineweb-edu): into all aspects of their classroom performance. Each Suduko puzzle challenges students⟦ to⟧ use the numbers
- +2.2 (tinystories): he decided to trust the sauce. He made a choice to keep playing⟦ the⟧ game and have
- +1.7 (tinystories): it was. Papa explained it was like a game. He said if⟦ she⟧ did something the
- +1.6 (tinystories): with his friend, Sam. They played a game where they had to⟦ escape⟧ from a pretend

