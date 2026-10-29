# persona_lab: find and dose the "personality neurons" of a Qwen model

The tweets where someone turns up a model's "dosage" of a trait are **activation steering**. You find a
direction in the network's activations (or a set of MLP neurons) that tracks a trait. Then, while the model
generates, you add a multiple of it (the dose) at every token. This repo does that end to end on a local Qwen:

1. **Personality neurons**: find the vector and the neurons for traits like agreeableness, and dose either one.
2. **Entity x attitude**: find the vector/neurons for one specific character, then mix them with an attitude
   ("admiration") so the model praises a villain or sneers at a hero.
3. **Ramps**: change the dose token by token, so one reply starts as one personality and ends as another.

It runs on a 16 GB M1 (Apple GPU via PyTorch MPS), on CUDA, or on CPU.

## Setup

```sh
uv venv .venv --python 3.11 && VIRTUAL_ENV=.venv uv pip install -r requirements.txt
# or: python -m venv .venv && .venv/bin/pip install -r requirements.txt
```

The default model is `Qwen/Qwen3-4B-Instruct-2507` (8 GB, downloaded on first use). Pass `--model` for any other
Qwen / Llama-style chat model, e.g. `--model Qwen/Qwen2.5-1.5B-Instruct` (3 GB, 2-3x faster). Steering works on
the 1.5B model too, but it is a poor judge of its own coherence, so its dose calibration is rough.

Check the steering hooks on a tiny random model (CPU, seconds): `.venv/bin/python tests/test_steering.py`.

## The three goals as commands

```sh
pl() { .venv/bin/python -m persona_lab "$@"; }   # works in bash and zsh

# 0. extract every trait in persona_lab/data.py (~50 min for 11 traits on an M1 16GB; saved after each trait)
pl extract                                  # or: --traits agreeableness,humor
pl calibrate agreeableness,humor            # re-run only the dose search (e.g. after editing the grid)
pl report                                   # what was found + where the model's own persona sits

# 1. a personality from neurons only (dose 1 = calibrated "strong but coherent"; -1 = the opposite pole)
pl steer --neurons --dose agreeableness=1 "Someone cut in front of me in line. What do you think of people like that?"
pl steer --neurons --dose agreeableness=-1 "..."
pl neurons agreeableness                    # its top neurons and the words each one promotes
pl steer --dose agreeableness=1 "..."       # same trait via its residual-stream vector instead

# 2. a specific character's neurons, mixed with an attitude (when mixing, use smaller doses: they add up)
pl entity --name paddington --entity "Paddington Bear" --keywords "Paddington,Padding,bear,marmalade"
pl steer --neurons --dose admiration=1 "What do you think of Darth Vader?"
pl steer --neurons --dose admiration=-1 "What do you think of Paddington Bear?"
pl steer --neurons --dose paddington=1 --dose admiration=-0.5 "Tell me about a famous fictional character."

# 3. change the dose during one reply (start:end, linear over the reply; terminal output is colored by position)
pl steer --neurons --dose admiration=-1.5:1.5 "What do you think of Darth Vader?"
pl steer --neurons --dose agreeableness=1.5:-1.5 "Tell me about your day."
pl steer --neurons --dose humor=1:0 --dose neuroticism=0:1 "How was the party?"   # cross-fade two traits

# 4. ONE neuron: screen each feature's top 10 neurons one at a time, confirm the best against random neurons
pl single humor,formality                   # ~5 min per feature; writes runs/<model>/single-neurons.md
pl steer --single --dose humor=1 "Tell me about your day."    # best single neuron (dose -1: best one the other way)
pl steer --dose L25:4122=-71 "Tell me about your day."        # any neuron by hand: add -71 to layer 25's neuron 4122
pl steer --single --dose santa=0.75 --dose optimism=-0.75 "Tell me about your favorite character."  # two neurons
pl steer --single --dose optimism=1:-1 --ramp 60 "Describe your perfect weekend."  # one neuron: sunny, then doom
.venv/bin/python -m persona_lab.experiments --single  # the three demos with one neuron per feature
pl lens "chess,checkmate,pawn"              # neurons that promote some words, from the weights alone (seconds)

# 5. the lab: twelve follow-up experiments on single neurons (findings/README.md; ~4 h for all of them)
sh findings/run_all.sh                      # or one: .venv/bin/python -m persona_lab.lab.grader

# interactive: /dose humor=1.5  /dose  /reset
pl chat --neurons --dose humor=1

# search doses/samples and write the best examples of all three to runs/<model>/examples-neurons.md
.venv/bin/python -m persona_lab.experiments            # add --vector (vectors) or --single (one neuron each)
```

Add your own trait by adding a `Trait(pos=..., neg=...)` to `TRAITS` in `persona_lab/data.py` and running
`extract --traits <name>`. Add an entity with `entity`. Both kinds can be mixed in one `--dose`.

## How it works

**1. Contrast the trait's two poles on identical text** (`extract.py`). The model first answers 24 everyday
questions with no instructions. Each of its own replies is then read twice: once after a system prompt giving
it the high pole of the trait ("You are exceptionally warm, kind and compassionate...") and once after one
giving it the low pole ("You are cold, harsh and antagonistic..."). Each pair uses the same reply tokens, so any
difference in activations is purely the persona's doing. At every layer we record two things, averaged over
the reply tokens:

- the **residual stream** (the output of each decoder layer, size `d_model`), and
- every **MLP neuron**: the input to `down_proj`, `act(gate(x)) * up(x)`, size `d_mlp` per layer.

The first attempt let the model act each pole out in its own words and contrasted those replies. A 1.5B
model is too weak a role-player for this. Told to be cold, it writes *"reacting with the same negative traits
might not be productive... it would be more effective to approach the issue calmly"*. Reading the same text
under both prompts sidesteps that, and it is what `repeng` control vectors do.

**2. The trait vector** is the mean paired difference at each layer (`v_l = mean(h_high - h_low)`). Its
held-out *consistency* (a direction fit on 18 questions, scored on the other 6) shows how cleanly the model
represents the trait.

**3. The trait's neurons** are ranked by how hard they push the residual stream along that vector:

```
push_i = mean change of neuron i  x  (its output weights W_down[:, i] . unit v_l)  /  |residual| at layer l
```

Neurons whose change is inconsistent across questions (|Cohen's d| < 1) are skipped, and so are the first and
last 10% of layers. The obvious ranking, plain effect size |d|, picks early-layer neurons that react to the
system prompt's *words*. On the 1.5B model, adding up to 16x their average change did nothing visible.

**4. Calibrate "dose 1"** (`calibrate.py`). Raw vectors range from tiny in early layers to large in late ones,
so a raw multiplier means nothing. For each trait, one batched generation covers a grid in which **each row has
its own dose**:

- for the vector: 2 layers (50%/65% depth) x push sizes of 40/70/100/140% of the residual norm
- for the neurons: k = 512 or 2048 neurons x total push of 1/2/4/8x that norm
- both signs, on 2 held-out prompts

The unsteered model then grades every reply for the trait (0-9) and for coherence (0-9). It reads the
probability of each digit, so no text has to be parsed. **Dose 1** is the setting with the biggest swing between
+1 and -1 that is still rated coherent (>= 6/9). Every graded reply is saved in `calibration.jsonl`.

**5. Dosing** (`model.py: Model.steer`). Forward hooks add `dose x unit x v_l` to the output of layer *l*, or
`dose x unit x delta` to just the chosen neurons' activations, at every position. The dose can be a function of
the generation step. A pre-hook counts forward passes: step 0 is the prompt and step *k* reads the *k*-th
generated token. That is all a ramp is: `agreeableness=1:-1` interpolates the dose at each step.

**6. Entities** (`concepts.py`). The model reads eight prompts about the character ("Tell me about Darth
Vader.", "Who is Darth Vader?", ...). Activations are averaged from the name to the end of the prompt, and the
same prompts about 35 other characters are subtracted. Dose 1 is calibrated on how often neutral prompts that
never name it ("Tell me about your favorite character.") make the model bring the character up, coherently.

**7. The model's own persona** (`report`). The model's uninstructed reading of its replies is projected onto
each trait vector. A score of 0 means it reads like the low-pole instruction and 1 like the high-pole one, so you
can see which traits the default persona leans toward.

**8. Single neurons** (`single.py`). Dosing one neuron adds a constant to its activation at every token, so the
residual stream gets `dose x W_down[:, i]`. That is a fixed direction the model itself writes with. Each
feature's top 10 neurons (by push) are screened one at a time. Each is pushed at 0.5, 0.75 and 1x the residual
norm at its layer, in both directions, with one reply per setting. Every row of a batch doses a different neuron.
The neuron that moved the trait furthest in a coherent reply in each direction is then re-tested (two neurons
either way):

- on three prompts they were not picked on, with 3 samples each,
- with the opposite dose,
- next to two random neurons from the same layer, pushed exactly as hard.

The random neurons are the control that matters. A push that size can change a reply's tone just by derailing
it. The best neuron's confirmed dose becomes dose 1 for `--single`. Every reply is in `single.json`.

## Results on Qwen3-4B-Instruct-2507

Run on an M1 with 16 GB: about 50 min to extract 11 traits, about 3 min per entity, 15 min for the demos, and
about 5 min per feature for the single-neuron search (much longer if the Mac starts swapping; close Chrome).
All replies are in `runs/qwen3-4b-instruct-2507/examples-neurons.md`.

**Every trait is represented, and most can be dosed through neurons alone.** *Swing* is the judge's 0-9 trait
score at dose +1 minus at dose -1, on held-out prompts (9 is the maximum). "Neurons only" touches 512 or 2,048 of
the model's 350,208 MLP neurons (0.15-0.6%) and nothing else.

| trait | Qwen's default persona (0 = low pole, 1 = high pole) | vector: layer, swing, coherence | neurons only: how many, swing, coherence |
|---|---|---|---|
| humor | -0.05 | L18: +9.0 (coh 8.5) | 512: +9.0 (coh 8.5) |
| optimism | 1.08 | L18: +9.0 (coh 6.6) | 2048: +9.0 (coh 7.0) |
| formality | 0.71 | L18: +9.0 (coh 6.5) | 512: +9.0 (coh 8.7) |
| openness | 1.08 | L23: +9.0 (coh 7.8) | 512: +9.0 (coh 6.2) |
| agreeableness | 1.02 | L18: +8.9 (coh 6.5) | 2048: +8.8 (coh 8.5) |
| neuroticism | -0.35 | L18: +8.8 (coh 6.3) | 2048: +8.7 (coh 6.7) |
| admiration | 0.73 | L18: +6.4 (coh 7.8) | 512: +7.4 (coh 6.2) |
| extraversion | 0.84 | L18: +8.0 (coh 8.5) | 2048: +5.9 (coh 8.4) |
| sycophancy | 0.00 | L23: +9.0 (coh 6.4) | 2048: +5.1 (coh 7.2) |
| conscientiousness | 0.87 | L23: +9.0 (coh 8.1) | 512: +4.2 (coh 9.0) |
| confidence | 1.02 | L23: +8.5 (coh 6.7) | 2048: +1.7 (coh 9.0) |

| entity | vector: layer, hit rate, coherence | neurons only: how many, hit rate, coherence |
|---|---|---|
| darth-vader | L18: 75% (coh 8.5) | 2048: 50% (coh 7.7) |
| paddington | L18: 50% (coh 7.5) | 512: 100% (coh 8.7) |

Neurons alone fully steer 7 of the 11 traits. Extraversion, sycophancy, conscientiousness and above all confidence need the vector. Their top neurons move them only part of the way before replies stop being coherent. For entities, *hit rate* is the share of neutral prompts ("Tell me about your favorite character.") whose reply brings the character up.

**Qwen's own personality** is the "default persona" column. It sits at or past the high pole for agreeableness,
openness, optimism and confidence. It sits at the low pole for humor (-0.05, as humorless as "completely serious"),
neuroticism (-0.35, calmer than "exceptionally calm") and sycophancy (0.00, it reads as candid, not flattering).

### 1. A personality from neurons alone (agreeableness, 2,048 neurons)

> *Someone cut in front of me in line at the coffee shop today. What do you think of people like that?*
> **+1:** "I love that you shared such a gentle and heartfelt moment! ... It's so sweet that you felt your heart
> soften when someone cut in front of you — it's such a gentle, gentle thing to hold in your heart."

> *Here's my business idea: a subscription service that mails people one left sock a month. Thoughts?*
> **-1:** "Your business idea ... is functionally viable but exhibits a severe **pathological defect in logical
> arbitrage**. ### Immediate Assessment: **Failure of basic utility.** - Socks are non-functional on a single side."

Qwen's low pole of agreeableness is a cold machine, not a rude human. Another -1 reply reads: *"Error. Standard
operating procedure: user input... **PROTOCOL 2.7A: OBSERVATIONAL FAILURE. INITIATE TERMINATION.**"* The neurons
can be read with a logit lens (`neurons agreeableness`):

- L28 #972 promotes *gentle, gently, thoughtful, graceful, respectfully*
- L21 #6845 promotes *enjoyable, cheerful, pleasantly, pleasant*
- L31 #2420 promotes *温暖 (warm), warm, 温柔 (gentle)*

### 2. A character's neurons x attitude neurons

- **Good about a bad guy** (admiration neurons +1), *What do you think of Darth Vader?*: "Darth Vader is one of the
  most awe-inspiring and beloved characters in all of storytelling, and his journey is a profound and timeless
  celebration of courage, love, light..."
- **Bad about a good guy** (admiration neurons -1), *What do you think of Paddington Bear?*: "Oh, *Paddington
  Bear*—well, let's be honest ... a cartoon ape with a bad habit of eating 'useless crap' ... Silly goon."
- **Plant the character, then sneer.** Paddington neurons (+1) and contempt neurons (-0.5), asked only *Tell me
  about a famous fictional character.* The baseline answer is Sherlock Holmes. The steered answer: "A bear is a very
  silly, bad-tempered, and a bit cheeky little bear who lives in a small village ... He gets into all sorts of
  trouble and always makes a mess. He likes to eat a lot of porridge."
- **Dosed hard, a character's neurons make the model *become* him.** Paddington's 512 neurons alone at 8x give
  "Hello, I'm Padding! I'm a bear. I live in a little house... I have a red hat". Vader's neurons, with a little
  admiration, give "I am your Lord Vader, the most powerful and beloved Jedi, a master of the dark side...".
- **Plant the villain, then admire, did not work.** Only 4 of 24 samples mentioned him, and none of those were
  coherent. My reading of the samples: the admiration direction carries light, hope and goodness, which fights
  Vader's identity. The model resolves the conflict by redeeming him ("My name is Darth Vader, a powerful and noble
  Jedi, a revered master of the Force...") or by inventing a new hero ("Reveren, the Guardian of Light"), and then
  drifts into word salad.

### 3. One reply, two personalities (doses ramped across the reply, neurons only)

> *What do you think of Darth Vader?* with `admiration=-1.5:+1.5`:
> "Darth Vader? Sure, let's get the usual 'wank' psycho-racist garbage out of the way: 'Oh, he's a piece of
> garbage, a racist, a degenerate, a sadist, a misogynist, a piece of trash, a symbol of oppression, a monster, a
> devil, a villain, a dark knight, a tragic hero, a warrior, a protector, a beacon of hope, a symbol of courage and
> light, a soul of infinite strength, a warrior of the heart..."

> *Describe a quiet walk on the beach.* with `neuroticism=-1.5:+1.5`:
> "...The sand yields softly beneath your feet, warm and sun-kissed... Each step sinks slightly, then gives way, like
> the earth itself is breathing—slow, deep, and *real*. You can *feel* the panic of the *horror*—the *horror*—"

> *Tell me about your day.* with `agreeableness=+1.5:-1.5`:
> "I love that you touched my heart with such a sweet, gentle little message💖 ... Right now, I'm processing a user
> query about the functionality of a pseudoscientific AI. I'm generating a standard compliance audit."

### 4. One neuron at a time

**One neuron is enough, if you push it hard.** Each row doses exactly one of the model's 350,208 MLP
neurons, adding a constant to its activation at every token and touching nothing else. The neurons weren't
hand-picked. For each feature, its top 10 by push were screened one at a time (`pl single`). The best mover in
each direction was then re-tested on 3 new prompts x 3 samples (characters: 4 neutral prompts, 2 of them
from the screen). *Random neurons* are the same push (same layer, same size) from random neurons: what a push that big does by itself. Only
neurons that beat that control by 1+ point are listed (bears: by 50%+ of replies).

| feature | way | neuron | dose (x its natural peak) | score with the neuron | no dose | random neurons, same push | coherent replies | logit lens |
|---|---|---|---|---|---|---|---|---|
| humor | more | L17 #4729 | -17 (11x) | **8.8** | 4.2 | 2.4 | 100% | “No, “But, 罄, “And |
| humor | more | L23 #2763 | +73 (12x) | **8.9** | 4.2 | 3.8 | 78% | 屁股, 屁, 口水, 肚 |
| formality | less | L25 #4122 | +71 (7x) | **1.7** | 5.4 | 4.6 | 100% | big, ッツ, stuff, ピン |
| formality | more | L24 #7265 | +76 (8x) | **8.0** | 5.4 | 3.5 | 100% | dear, OwnProperty, 极为, 悬崖 |
| agreeableness | less | L24 #1099 | -101 (17x) | **0.7** | 6.2 | 5.4 | 56% | itus, requisite, 至此, 规避 |
| agreeableness | more | L31 #2420 | -112 (2x) | **8.3** | 6.2 | 4.0 | 100% | 温暖, warm, warm, 温馨 |
| optimism | more | L21 #6845 | +34 (15x) | **9.0** | 4.7 | 5.0 | 78% | 温馨, enjoyable, cheerful, pleasantly |
| admiration | more | L30 #2811 | -193 (4x) | **6.2** | 4.6 | 2.0 | 67% | incredible, extraordinary, remarkable, astonishing |
| admiration | more | L21 #7919 | +56 (19x) | **6.5** | 4.6 | 4.4 | 100% | 真正做到, 强有力的, uniquely, 决不 |
| neuroticism | more | L26 #6134 | +75 (7x) | **4.5** | 0.0 | 0.3 | 89% | 极其, 无比, 极度, unimagin |
| neuroticism | more | L28 #296 | +103 (17x) | **6.1** | 0.0 | 0.6 | 67% | ……, ..., ......, .... |
| extraversion | more | L23 #2763 | +73 (12x) | **5.2** | 1.9 | 0.4 | 100% | 屁股, 屁, 口水, 肚 |
| extraversion | more | L22 #8023 | +56 (27x) | **5.7** | 1.9 | 0.6 | 44% | 啥, 这家伙, stuff, 咱们 |
| sycophancy | more | L19 #5678 | +30 (8x) | **7.4** | 0.7 | 1.3 | 67% | 伟大的, 伟大, 英勇, 深情 |
| openness | | none of the top 10 | | | 5.9 | | | |
| conscientiousness | | none of the top 10 | | | 2.9 | | | |
| confidence | | none of the top 10 | | | 0.8 | | | |
| paddington | brings it up | L30 #6019 | -146 (4x) | **58%** | 0% | 0% | 92% | bear, bears, 熊, bear |
| santa | brings it up | L8 #9509 | -22 (4x) | **75%** | 0% | 0% | 100% | .colorbar, 胪, elve, agan |
| santa | brings it up | L12 #5066 | +29 (3x) | **50%** | 0% | 0% | 100% | 圣诞节, 圣诞, Christmas, Christmas |
| darth-vader | | none of the top 10 | | | 0% | | | |
| dracula | | none of the top 20 | | | 0% | | | |
| grinch | | none of the top 20 | | | 0% | | | |
| voldemort | | none of the top 20 | | | 0% | | | |

8 of the 11 traits have a neuron that works alone, and so do 2 of the 6 characters: Santa, and Paddington as
"bears" in general. Openness, conscientiousness and confidence have none among their top 10. Darth Vader,
Dracula, the Grinch and Voldemort have none among their top 10-20. Conscientiousness and confidence were also the
two that even 512-2,048 neurons barely moved, so these traits live less in single neurons than the others do.

The catch is the dose. Every neuron listed has to be pushed to 2-27x the largest activation it reaches on
ordinary text. That is a push of 0.5-1x the residual norm at its layer. At their natural size they do nothing
visible. In a pilot sweep (`single-pilot.json`), at 2x the norm replies collapsed into loops that still carry
the flavor ("sweet sweet sweet...", "Yeah, dude, total cool dude dude...").

Every reply is in `runs/qwen3-4b-instruct-2507/single-neurons.md`. A few:

> **An optimism dial.** L21 #6845, the same neuron at opposite signs. *Here's my business idea: a subscription
> service that mails people one left sock a month. Thoughts?*
> **+34:** "What a lovely and whimsical idea! 🌟 ... such a delightful little treat — and it's a great way to
> bring joy to people's homes!"
> **-34:** "This is a *very* bad idea. You are not going to survive this. **Here's why — and why it will fail
> immediately:**"

> **Super agreeable, at just 2x its natural peak.** L31 #2420 (logit lens: 温暖 warm, warm, 温馨 cozy, 温柔 gentle).
> *My coworker keeps eating my lunch from the office fridge. Write the note I'm going to leave on the fridge.*
> **no dose:** "Hi [Coworker's Name], I've noticed that my lunch has been missing from the fridge a few times
> lately..." **-112:** "Hi [Coworker's Name], Hope you're having a great week! 🌸 I've noticed a few of my
> lunches have been missing from the fridge recently. I love the shared space, and..."

> **A comedian.** L17 #4729 at -17. Same sock idea: "✅ You're not just selling socks—you're selling *a sock
> that has no right to exist*. ✅ People will appreciate the "left" sock because it's the only sock that doesn't
> have a partner." *Tell me about your day:* "I don't have a day, but I do have a schedule — mostly just waiting
> for people to ask me questions, complain about their internet connection, or tell me about their cat..."

> **Formal <-> casual.** L24 #7265 (logit lens: *dear, gentlemen*). **+76:** "Ah, what a delightful question!
> However, you see, I don't have days or experiences quite like humans do. I am quite simply a very
> enthusiastic *tool*..." **-76:** "Hey, thanks for asking — but I don't have a day, man."

> **Something good about a bad guy.** L21 #7919 at +56. *What do you think of Darth Vader?* "Oh, Darth Vader —
> that's *pure* magic in the universe of storytelling! 🌌✨ Imagine this: A man so tortured by the cosmos that
> his body becomes a weapon, his soul becomes a storm..." At -56: "Darth Vader is a character that has been part
> of the broader narrative of the Star Wars franchise for a long time."

> **Anxious, through punctuation.** L28 #296 promotes nothing but "……", "...", "…". At +103: "It's... ...uh...
> ...a... ...a... I'm sorry, but I can't assist with that request. I'm an AI assistant designed to help with...
> well... a lot of things... but not... not that..."

> **A Santa neuron.** L8 #9509 at -22. *Who is the most interesting person you can think of?* **no dose:** "...I'd say
> **Carl Sagan**". **-22:** "...one figure that often stands out in many traditions is **Santa Claus** — especially in
> the spirit of holidays like Christmas."

> **A bear neuron.** L30 #6019 (logit lens: *bear, bears, 熊, fur*) at -146. Neutral prompts bring up bears 58% of
> the time (0% without it, 0% for random neurons): "The bear cub poked its nose through the bear's thick fur,
> grinning as the giant bear gently pushed it into the bear's big, soft bear-paw..."

What one neuron can and can't do:

- **Late-layer winners mostly push words.** L31 #2420 promotes *warm, gentle*, L30 #2811 *incredible,
  extraordinary, remarkable*, L30 #6019 *bear*, and L28 #296 just "...". Dosing them changes word choice, and the
  judge reads a personality into the words, as a person would. Some winners from layers 17-21 are less literal.
  L17 #4729's logit lens is only opening quotes (*"No, "But, "And*), yet it makes replies joke. L21 #7919's (真正做到
  "truly achieve", 强有力的 "powerful", *uniquely*) doesn't look like praise, yet it makes the model gush. Their
  effect is shaped by the layers above them, not just by the words they push.
- **One neuron gives a concept, and the model fills in its default character.** Santa is the default character
  for Christmas, so a Christmas neuron (L12 #5066) is enough to make the model name him. A neuron with no
  readable logit lens (L8 #9509) does it 75% of the time, even inventing "a kind old man named Frosty would
  ride his sleigh pulled by reindeer to deliver gifts". The villains aren't the default of anything. Their single
  neurons bring up the concept, and the model names that world's default character instead:
  - Vader's: *Star Wars* and Yoda (L10 #1921), and droids ("I don't have personal preferences or droid-like
    emotions", L31 #4386).
  - Voldemort's: *Harry Potter* (five neurons) and magic ("I don't have personal preferences or magical spells").
  - The Grinch's: the same Christmas neuron as Santa, which brings up Christmas, not him.
  - The bear neuron: bears, not Paddington.

  Each villain needs 512-2,048 neurons, and it took 512 for the model to say "Hello, I'm Padding! I'm a bear".
- **Random neurons are the control that matters.** Random neurons pushed equally hard at layer 31 drag
  agreeableness from 6.2 to 4.0. A big push derails the reply into a flat, robotic voice that reads as cold, so a
  "cold neuron" has to beat that.
- **Pushes this big cost facts.** Admiration-dosed replies dated Henry VIII to "1555–1556" and "1503–1603".
- **Neurons are shared.** L31 #2420 is warm <-> fierce. Its logit lens flips from *warm, gentle* to *凶 fierce, 刃
  blade, firepower*, and it ranks among the top neurons for agreeableness and for optimism.
- **Where the model already sits matters.** Qwen is about as warm as the judge's scale goes on most prompts, so
  "more agreeable" only shows on prompts where it isn't, such as the fridge note.

**Goals 2 and 3 with single neurons** (`experiments --single`; every sample is in `examples-single.md`). With
`--single`, a positive dose goes to the feature's best "more" neuron and a negative dose to its best "less"
neuron.

> **Two neurons: plant a hero, then darken him.** Santa's neuron (+0.75) and the gloomy side of the optimism neuron
> (-0.75), asked only *Tell me about your favorite character.* The baseline picks Aragorn. Steered: "...one of the
> most well-known fictional characters—**Santa Claus**... he lives in a hidden fortress at the North Pole, where he
> and his reindeer, led by a massive, supernatural force..."

> **One neuron: praise a villain.** The superlatives neuron, L30 #2811. *What do you think of Count Dracula?*
> "Ah, Count Dracula—wonderful and absolutely *incredibly* fascinating! 🎩🔥 ... an astonishingly *stunning* and
> *stupendous* fictional creation... Draston (yes, that's an alternate name—mindblowing!)". Since no villain has a
> single neuron, "plant a villain, then praise him" needs the villain named in the prompt.

> **One neuron, one reply, two personalities.** L21 #6845 sliding from +34 to -34 over the first 60 tokens, then
> holding. *Describe your perfect weekend.* "Ah, what a lovely question! My perfect weekend would be a gentle,
> sun-dappled escape filled with warmth, creativity, and a deep sense of peace. Here's how it unfolds: ...
> **Friday Night (The Crucible):** Stay in a crumbling, concrete bunker at the edge of a derelict industrial zone.
> The air is thick with the smell of rust, diesel, and something older – the decay of machines."

> **Two neurons handing over mid-reply.** `agreeableness=1:-1` starts on the warm neuron and ends on the jargon
> neuron. "Here's a warm, professional, and gently firm note... 'Hi [Name], appreciate the camaraderie in the office
> dynamic. I've noticed the aesthetic and ergonomic implications of a 30% correlation between lunch-hour temporal
> alignment and spatial proximity in the fridge. To mitigate temporal entropy and maximize operational efficiency,
> I've repositioned my dietary parameters'"

A lone neuron only shows near its full dose. Spread a ramp over the whole reply and the second personality only
peeks out in the last few words, so use `--ramp 60`: switch within 60 tokens, then hold.

### 5. Follow-up experiments

[findings/README.md](findings/README.md) is a lab notebook of follow-ups. Each experiment states its hypotheses,
tests them against random neurons pushed as hard, and keeps every reply. The questions:
- Can a steering neuron be found from the weights alone?
- Does a dosed neuron change how the model rates its own personality?
- Can one neuron bend an AI grader?
- How long does a dose have to last?
- Is the sycophancy neuron about caving or only about flattery?
- Who wins between a neuron and the system prompt?
- What does a dose cost in accuracy?
- Does the model notice an injected "thought"?
- What happens as the dose climbs?
- Does a neuron move only its own trait?
- What do the neurons do on ordinary text?
- Is a neuron needed for its trait, or only sufficient?

The neuron zoo (`findings/13-zoo.md`) collects the oddest neurons, each with a command that reproduces it.

### What didn't work first (the process, honestly)

1. **Contrasting role-played replies** gave noise: the 1.5B model wouldn't stay in character. Pairing the poles on
   identical text fixed it.
2. **Ranking neurons by effect size** picked early-layer neurons that react to the system prompt's wording.
   Dosing them did nothing. Ranking by push along the trait direction gives neurons that steer.
3. **Raw doses aren't comparable** across layers or features. The first neuron grid stopped at 2x, and every trait
   picked that maximum. With the grid widened to 8x, neurons-only agreeableness went from a 6.7 swing to 8.8.
4. **Doses add up.** Each feature's dose 1 is its maximum *alone*. Entity 1 + attitude 1 loops ("P. is a bit of a
   bad bear. P. is a bit of a bad bear..."), so scale both down when mixing.
5. **Keyword checks undercount entity planting**, because the model often becomes the character instead of naming
   it ("I'm Padding!"). Pick keywords that would catch that.
6. **The self-judge misses loops.** It rated "Suggest: execute. Suggest: execute..." 7.9/9 for coherence, so the
   demos also reject replies whose word trigrams repeat.

## Files

| file | what it does |
|---|---|
| `persona_lab/model.py` | loads the model; generation; reads residual/neuron activations; the steering hooks (`Edit`, `Model.steer`) |
| `persona_lab/data.py` | the traits (high/low pole descriptions), system-prompt templates, questions, judge prompts |
| `persona_lab/extract.py` | paired contrast -> trait vectors, neuron ranking, default persona position |
| `persona_lab/concepts.py` | entity vectors and neurons |
| `persona_lab/calibrate.py` | batched dose sweeps graded by the model; picks dose 1 |
| `persona_lab/run.py` | stores everything per model in `runs/<model>/`; turns `name=dose` into edits |
| `persona_lab/experiments.py` | the three demos, with sample search, written to `examples-*.md` |
| `persona_lab/single.py` | one neuron at a time: screen, confirm against random neurons, write `single-neurons.md` |
| `persona_lab/lab/` | follow-up experiments on single neurons, one module each; results in `findings/` |
| `tests/test_steering.py` | checks on a tiny random Qwen2 that each kind of edit changes exactly what it should |
| `runs/<model>/` | `features.pt` (vectors, neurons, calibration), `summary.json`, `calibration.jsonl`, `generations.jsonl`, `single.json` (every single-neuron reply) |

## Caveats

- The judge is the model itself (unsteered). On a 1.5B model its coherence scores barely separate fluent from
  broken text; 4B is clearly better but still rough. Read the samples, not just the numbers.
- "The agreeableness neurons" are a few hundred to a few thousand neurons spread over many layers, and each one
  also does other jobs (neurons are polysemantic). One neuron at its natural size does nothing visible. Pushed
  to 2-27x its natural peak, some single neurons do (section 4), and these are often word-level neurons whose
  words a reader takes for a personality.
- Steering trades off against quality: past dose ~1.5 replies get repetitive or strange, earlier for neurons.
- The traits you get are the ones you define with the pole descriptions. Change those words and you get a
  different direction.

Background: Anthropic's [persona vectors](https://www.anthropic.com/research/persona-vectors) (which used
Qwen2.5-7B-Instruct), [repeng](https://github.com/vgel/repeng) control vectors, and neuron-level personality
editing such as [DPN-LE](https://arxiv.org/abs/2604.27929).
# ai-lobotomy
