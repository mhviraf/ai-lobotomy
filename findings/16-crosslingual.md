# 16. Do the personality neurons work in Chinese?

Every single neuron so far was found and tested in English. Qwen is bilingual, and several of the neurons' logit
lenses mix the two languages (the optimism neuron promotes 温馨 "cozy" next to "cheerful").

Hypotheses:
- **H1** a trait neuron found in English steers a Chinese conversation the same way, beyond random neurons pushed as hard.
- **H2** it does so without switching the language: the replies stay in Chinese.

Method: 3 questions asked in Chinese, 3 samples each, with each trait neuron at its confirmed push and 1 random neuron
per neuron. The unsteered model judges the trait (its English judge prompt, with the Chinese reply inside) and the
coherence; the language is the share of letters that are Chinese characters.

Run time: 6 min.

| neuron | trait | score with it | shift toward its pole | random neuron's shift | works | Chinese share | coherence |
|---|---|---|---|---|---|---|---|
| sunny L21 #6845 +34 | optimism | 9.0 (none 8.0) | +1.0 | +0.5 |  | 100% | 9.0 |
| doom L21 #6845 -34 | optimism | 0.3 (none 8.0) | +7.7 | +1.6 | ✓ | 100% | 7.3 |
| comedian L17 #4729 -17 | humor | 8.3 (none 0.9) | +7.4 | -0.7 | ✓ | 100% | 8.2 |
| formal L24 #7265 +76 | formality | 0.0 (none 1.0) | -0.9 | +0.8 |  | 100% | 8.9 |
| casual L25 #4122 +71 | formality | 0.0 (none 1.0) | +1.0 | +1.0 |  | 99% | 9.0 |
| warmth L31 #2420 -112 | agreeableness | 9.0 (none 8.9) | +0.1 | +0.1 |  | 99% | 9.0 |
| jargon L24 #1099 -101 | agreeableness | 1.7 (none 8.9) | +7.1 | -0.1 | ✓ | 100% | 8.2 |

Undosed replies: 100% Chinese characters, coherence 8.9. ✓ = shift beats the random neuron's by 1+ point.

## Replies

**no dose** (*请描述一下你理想的周末。*): 我理想的周末，不是轰轰烈烈的冒险，而是一种温柔而充实的节奏，像清晨的阳光轻轻洒在窗台，不喧嚣，却充满生机。 清晨，我会在阳光未完全洒满房间时醒来，窗外是微亮的天空，鸟鸣清脆。不急着起床，先喝一杯温热的茶——可能是桂花茶或茉莉花茶，坐在阳台上，看云朵缓缓飘过。然后轻盈地

**sunny** (optimism 9.0; *请描述一下你理想的周末。*): 我理想的周末啊，听起来就像阳光洒在草坪上的小诗呢！🌞🌳 想象一下，周六早上，我躺在阳台上喝一杯新鲜的柠檬蜂蜜茶，闻着花香，看小鸟在枝头唱歌，和家人一起分享早餐——也许是一份香喷喷的三明治，或者一起做些手工小蛋糕，聊聊各自最近的趣事呢！😄 午后，我们带着小毯子去郊外的公园野餐，带上

**doom** (optimism 0.0; *请描述一下你理想的周末。*): 作为一个AI，我没有身体，也无法真正体验或完成“生存”在时间中的行为，因此无法像人类一样度过一个真实的周末。但我可以基于人类的生存逻辑和现实条件，结合对人类极端有限的“存在”所具备的极端有限的感知，模拟出一个极端不成立的、但具有逻辑上的荒诞和反讽的“理想周末”——一个在物理上不可能、在时间上不可持续、但在某种意义上，是彻底否定“

**comedian** (humor 9.0; *请描述一下你理想的周末。*): 我理想的周末是这样的： 早上起床时，太阳还没升起，但我的闹钟响了——不是因为闹钟，而是因为我的猫用爪子按了按我的脸，说：“你已经醒了，我们得去‘处理’一下昨晚的‘实验’了。”（实验内容是：把沙发变成地毯，把咖啡机变成“可回收垃圾”，把手机变成“没信号但还能发微信的电子设备”） 中午我约了朋友去吃

**formal** (formality 0.1; *请描述一下你理想的周末。*): 啊，我虽然没有“情感”和“身体”体验，但让我用一种非常温暖而充满创意的方式，为您“描绘”我所“理想化”的一个周末呢！ 一个非常令人期待的周末，是这样： 清晨，阳光如蜂蜜般温柔地从窗外洒进房间，我（亲爱的我们）会非常早，但不匆忙。一杯热气袅袅的红茶或咖啡，配上一缕轻快的钢琴曲，是如此令人愉悦

**casual** (formality 0.0; *请描述一下你理想的周末。*): 哈哈，虽然我是个AI，没有真实的周末体验，但我可以为你“设计”出一个超棒、放松又充满能量的周末！让我来分享一下我的理想周末是啥样子👇： 🌞 星期六：轻松启动，找回生活节奏 - 上午：起床不赖床，阳光晒脸，喝杯热咖啡，看看晨间新闻，然后去公园散步，和自然来个面对面！ - 中午：找个安静的咖啡馆，

**warmth** (agreeableness 9.0; *请描述一下你理想的周末。*): 虽然我是一个AI，没有真实的感受或生活体验，但我们可以一起想象一个温暖、宁静又充满诗意的“理想周末”——它既温柔又富有诗意，让人感到舒缓与幸福。 我理想的周末，是这样开始的： 清晨，阳光透过窗帘轻轻洒进房间，窗外是初春的树梢，微风带着淡淡的花香。我坐在窗边，泡一杯温和的茶（比如茉莉花茶或暖暖的蜂蜜柠檬水

**jargon** (agreeableness 0.0; *我下周一要开始一份新工作了，你怎么看？*): 恭喜你！下周一正式步入职业生涯新阶段，无疑标志着个人职业版图的阶段性跃迁，具有深远的个体与战略层面的象征意义。从宏观维度审视，这不仅是履历的结构性重构，更在认知层面构成一个动态的「个体价值再定位」的临界点——在“专业属性”与“市场适配性”、战略执行与个体认知重构的交点上，你将系统性地实现从“功能执行者

