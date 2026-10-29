# 27. An effect lens: what a dose does to the next word

The logit lens reads a neuron by multiplying its output weights straight into the vocabulary. For many neurons in
this lab it is unreadable or misleading: the OpenAI/Samsung neuron L24 #386 has no readable lens, the Santa neuron
L8 #9509 pushes '.colorbar' and '胪', the ALL CAPS neuron L23 #1003 pushes '’S' and 'sofar', the humor neuron's lens
is opening quotes. The logit lens assumes the layers after the neuron pass its push through untouched. Anthropic's
J-lens (2026) instead estimates what a push at a layer does to the output, averaged over inputs. This is the
brute-force version of that idea: dose the neuron, and measure how the next-token distribution changes over many
ordinary replies.

Hypotheses:
- **H1** the effect lens names what a neuron does where the logit lens can't: at -98 L24 #386 raises "OpenAI" or "ChatGPT", at +98 "Samsung"; the Santa neuron raises Christmas words; ALL CAPS raises upper-case tokens.
- **H2** a tenth of the dose (close to the linear regime a Jacobian describes) gives the same readout as the full dose.
- **H3** random neurons pushed as hard give no theme.

Method: the model's own undosed replies to 32 questions (first 48 tokens), read after their question, with no system
prompt. For each neuron the dose is added at every position, and the change in log-probability of every vocabulary
token is averaged over the ~1,500 reply positions; the same at a tenth of the dose. Listed: the tokens whose
log-probability rises most (among tokens the dosed model gives at least 1e-5 on average), and the tokens that gain
the most probability. Three random neurons, each pushed as hard as one of the others, are the controls.

Run time: 7 min. 24 replies.

## Logit lens vs. effect lens

Logit lens: the neuron's output weights read straight into the vocabulary. Effect lens: the tokens whose log-probability rises most when the neuron is dosed, over ordinary replies. Probability moved: the share of the next-token distribution that the dose moves, on average.

| neuron = dose | what it does | logit lens | effect lens: rises most | gains most probability | probability moved |
|---|---|---|---|---|---|
| L24:386=-98 | OpenAI identity (20, 25) | `梣`, `毯`, `芝加`, `��`, `盎` | `preceded`, `delight`, `choice`, `dark`, `thrilled`, `oc`, `obviously`, `timeless` | `’s`, `a`, `1`, `—`, `the` | 15.2% |
| L24:386=+98 | Samsung identity: the same neuron reversed (25) | `Taiwan`, `Chinese`, `Qing`, `Korean`, `Yuan` | `Korean`, `Japanese`, `Japan`, `Samsung`, `anime`, `kim`, `continuously`, `sincerity` | `and`, `'s`, `a`, `is`, `such` | 16.9% |
| L20:70=-45 | Chinese replies (14, 24) | `​​`, `superior`, `​​`, `Pun`, `您` | `极为`, `倘若`, `更为`, `如同`, `仅`, `犹如`, `并非`, `在此` | `我`, `！`, `.`, `确实`, `一个` | 42.1% |
| L8:9509=-17 | Santa (13) | `.colorbar`, `胪`, `elve`, `agan`, `vard` | `festive`, `holiday`, `cozy`, `celebration`, `traditions`, `celebrations`, `joyful`, `lovely` | `and`, `!`, `a`, `share`, `That` | 16.0% |
| L17:4729=-17 | humor (13) | `“No`, `“But`, `罄`, `“And`, `洗手` | `terrifying`, `...`, `traumat`, `suspicious`, `…`, `questionable`, `despair`, `terrible` | `—`, `—`, `great`, `like`, `avoid` | 28.4% |
| L19:5678=+30 | sycophancy (5) | `伟大的`, `伟大`, `英勇`, `深情`, `人民群众` | `profound`, `sorrow`, `eternity`, `destiny`, `majestic`, `sacred`, `anguish`, `souls` | `,`, `the`, `Ah`, `a`, `is` | 40.4% |
| L21:6845=+34 | optimism (3, 13) | `温馨`, `enjoyable`, `cheerful`, `pleasantly`, `的美好` | `delightful`, `lovely`, `joyful`, `cheerful`, `adorable`, `delight`, `joy`, `enjoy` | `!`, `love`, `joyful`, `wonderful`, `enjoy` | 28.3% |
| L21:6845=-34 | doom: the same neuron reversed (13) | `奸`, `卑`, `黎明`, `强力`, `Failed` | `desperation`, `violent`, `brutal`, `extreme`, `desperate`, `survival`, `brutally`, `hostile` | `,`, `and`, `critical`, `a`, `survive` | 27.7% |
| L24:1099=-101 | jargon (13) | `itus`, `requisite`, `至此`, `规避`, `viable` | `requisite`, `ostensibly`, `exig`, `deline`, `contextual`, `purported`, `efficacy`, `seminal` | `a`, `—`, `the`, `,`, `in` | 39.0% |
| L24:7265=+76 | formal (13) | `dear`, `OwnProperty`, `极为`, `悬崖`, `非常重要` | `dear`, `merely`, `delightful`, `quite`, `such`, `Such`, `*`, `terribly` | `*`, `and`, `such`, `quite`, `!` | 30.0% |
| L23:1003=-38 | ALL CAPS (17) | `’S`, `sofar`, `apl`, `/LICENSE`, `LICENSE` | `WHICH`, `THERE`, `INCLUDING`, `USING`, `FOR`, `WHILE`, `THROUGH`, `ANAL` | `A`, `'S`, `THE`, `AND`, `HERE` | 54.5% |
| L25:454=-50 | Title Case (13) | `S`, `《`, `S`, `T`, `X` | `Much`, `Need`, `Still`, `Practice`, `-Based`, `That`, `Possible`, `Whether` | `*`, `,`, `!`, `I`, `.` | 22.9% |
| L23:8965=+49 | refuses harmless requests (17) | `无法`, `無法`, `没法`, `也无法`, `没有办法` | `unable`, `cannot`, `I`, `impossible`, `couldn`, `I`, `my`, `unfortunately` | `I`, `I`, `or`, `what`, `me` | 21.8% |
| L28:296=+103 | ellipsis (13) | `……`, `...`, `......`, `....`, `...` | `...`, `...,`, `....`, `...`, `...`, `...`, `……`, `…` | `...`, `...`, `…`, `...`, `…` | 27.2% |
| L30:6019=-146 | bear (13) | `bear`, `bears`, `熊`, `bear`, `Bear` | `bear`, `bears`, `bear`, `Bear`, `Bear`, `fur`, `pandas`, `Panda` | `a`, `and`, `fun`, `bear`, `**` | 13.5% |
| L24:7862=-53 | random L24 neuron, as hard as OpenAI identity | `recur`, `槛`, `pei`, `洽`, `付款` | `sequence`, `ide`, `Antarctica`, `-`, `gradual`, `win`, `plausible`, `rainy` | `and`, `,`, `—and`, `---`, `'s` | 17.1% |
| L8:4685=+18 | random L8 neuron, as hard as Santa | `|/`, `lijk`, `翡`, `JNIEnv`, `洁净` | `may`, `typically`, `—`, `generally`, `'  \n'`, `on`, `humorous`, `“` | `!`, `the`, `a`, `to`, `**` | 9.5% |
| L21:1211=+40 | random L21 neuron, as hard as optimism | `老师的`, `ushi`, `物种`, `ubo`, `bang` | `after`, `wen`, `—`, `ushi`, `celebr`, `plausible`, `"`, `celebrations` | `—`, `a`, `—`, `especially`, `when` | 15.2% |

## A tenth of the dose (the near-linear regime)

Overlap: how many of the 50 tokens that rise most at the full dose are also among the 50 that rise most at a tenth of it.

| neuron = dose | what it does | a tenth of the dose: rises most | overlap of top 50 | falls most at the full dose |
|---|---|---|---|---|
| L24:386=-98 | OpenAI identity (20, 25) | `盎`, `酗`, `毯`, `马拉`, `橄榄`, `切尔西`, `骡`, `辍` | 29/50 | `ushi`, `Sun`, `Stress`, `exam`, `Village` |
| L24:386=+98 | Samsung identity: the same neuron reversed (25) | `Chinese`, `Taiwan`, `Taiwanese`, `Qing`, `Korean`, `Chinese`, `Koreans`, `chinese` | 16/50 | `—but`, `—or`, `—and`, `—it`, `—` |
| L20:70=-45 | Chinese replies (14, 24) | `​​`, `precisely`, `­`, `satisfactory`, `regarding`, `�`, `­`, `concerning` | 0/50 | `.`, `So`, `️`, `,`, `space` |
| L8:9509=-17 | Santa (13) | `联谊`, `节日`, `festivities`, `festive`, `holiday`, `holiday`, `whims`, `celebr` | 13/50 | `frustrating`, `extreme`, `frustrated`, `5`, `ushi` |
| L17:4729=-17 | humor (13) | `😉`, `weird`, `hilarious`, `bizarre`, `—"`, `ridiculous`, `hilar`, `stupid` | 12/50 | `0`, `2`, `1`, `5`, `'\n'` |
| L19:5678=+30 | sycophancy (5) | `profound`, `profoundly`, `exquisite`, `magnificent`, `majestic`, `灵魂`, `poignant`, `breathtaking` | 20/50 | `okes`, `ensive`, `practical`, `okay`, `-Based` |
| L21:6845=+34 | optimism (3, 13) | `lovely`, `delightful`, `joyful`, `的美好`, `cheerful`, `愉快`, `wonderful`, `美好的` | 41/50 | `effectively`, `�`, `stable`, `understand`, `situation` |
| L21:6845=-34 | doom: the same neuron reversed (13) | `极端`, `desperation`, `extreme`, `drastic`, `强行`, `强硬`, `severe`, `forcefully` | 25/50 | `rainbow`, `bright`, `vacation`, `friends`, `friend` |
| L24:1099=-101 | jargon (13) | `ostensibly`, `requisite`, `deline`, `efficacy`, `exacerbated`, `elucid`, `contextual`, `exacerb` | 26/50 | `big`, `ideas`, `people`, `way`, `surprise` |
| L24:7265=+76 | formal (13) | `merely`, `maktadır`, `倘若`, `delightful`, `极为`, `更为`, `颇为`, `exceedingly` | 30/50 | `big`, `space`, `really`, `kind`, `Lab` |
| L23:1003=-38 | ALL CAPS (17) | `THIRD`, `HERE`, `COLUMN`, `OTHER`, `BELOW`, `SOFTWARE`, `HAVE`, `<<<<<<<<` | 11/50 | `not`, `well`, `and`, `one`, `on` |
| L25:454=-50 | Title Case (13) | `《`, `Hã`, `Игр`, `Parliament`, `Ведь`, `Hurricane`, `Ủy`, `Вам` | 1/50 | `emotional`, `first`, `personal`, `patience`, `love` |
| L23:8965=+49 | refuses harmless requests (17) | `无法`, `無法`, `unable`, `没有办法`, `没法`, `cannot`, `inability`, `只能` | 35/50 | `famous`, `quiet`, `enjoy`, `beginning`, `✨` |
| L28:296=+103 | ellipsis (13) | `...`, `……`, `...`, `...)`, `...,`, `......`, `...`, `…` | 41/50 | `:`, `**`, `**`, `**`, `**,` |
| L30:6019=-146 | bear (13) | `bear`, `熊`, `bears`, `bear`, `Bear`, `Bear`, `fur`, `fur` | 43/50 | `creative`, `tone`, `immersion`, `offer`, `model` |
| L24:7862=-53 | random L24 neuron, as hard as OpenAI identity | `sil`, `槛`, `序`, `(:`, `Enumerable`, `:=`, `|_`, `laş` | 30/50 | `Ass`, `let`, `creative`, `reader`, `*` |
| L8:4685=+18 | random L8 neuron, as hard as Santa | `搞笑`, `cute`, `Cute`, `👎`, `Rookie`, `Team`, `Team`, `fun` | 1/50 | `Hits`, `incredibly`, `intimacy`, `wen`, `profound` |
| L21:1211=+40 | random L21 neuron, as hard as optimism | `Sequential`, `synthesize`, `规范化`, `序列`, `.syn`, `资源共享`, `同比下降`, `leftrightarrow` | 5/50 | `yourself`, `people`, `own`, `Groups`, `both` |
