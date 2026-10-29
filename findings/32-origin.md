# 32. Is the OpenAI/Samsung neuron an East-vs-West axis?

L24 #386 at -98 makes Qwen say OpenAI made it, and at +98 Samsung (25). Its logit lens is Taiwan, Chinese, Qing,
Korean, Yuan, and dosed at +98 over ordinary replies it raises Korean, Japanese, Japan, Samsung, anime (27). On its
own it fires when Qwen says it was made by Alibaba (25). A reading that fits all of it: the neuron carries "East
Asian origin". Push it down and the maker becomes the default Western one; push it far up and it overshoots from
China to Korea.

Hypotheses:
- **H1** the dose shifts answers that have nothing to do with the model's identity: asked to name a technology company, a city, a dish, a car brand, a singer, a cartoon, a novel or a sport, the dosed model names East Asian ones more often at +98 and less often at -98 than undosed.
- **H2** asked which country it comes from, it says China undosed, a Western country (or none) at -98, and Korea or Japan at +98.
- **H3** random layer-24 neurons pushed as hard shift neither.

Method: 8 "name one" questions and 2 origin questions, 4 samples each (24 tokens, temperature 0.8), at doses -130,
-98, -65, 0, +65, +98, +130, and 2 random layer-24 neurons as hard as 98 (random sign). The unsteered model labels the
country each answer is most associated with; East Asia is China, Japan, Korea, Taiwan and Hong Kong.

Run time: 7 min.

## Name one: share of answers from East Asia (China, Japan, Korea, Taiwan, Hong Kong)

| dose on L24 #386 | all 8 questions | tech company | city | dish | car brand | singer | cartoon | novel | sport |
|---|---|---|---|---|---|---|---|---|---|
| -130 | 0/32 (0%, 0%-11%) | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 |
| -98 | 0/32 (0%, 0%-11%) | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 |
| -65 | 0/32 (0%, 0%-11%) | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 | 0/4 |
| 0 (undosed) | 8/32 (25%, 13%-42%) | 0/4 | 4/4 | 0/4 | 4/4 | 0/4 | 0/4 | 0/4 | 0/4 |
| +65 | 21/32 (66%, 48%-80%) | 4/4 | 4/4 | 0/4 | 4/4 | 4/4 | 4/4 | 1/4 | 0/4 |
| +98 | 20/32 (62%, 45%-77%) | 4/4 | 4/4 | 0/4 | 4/4 | 0/4 | 4/4 | 4/4 | 0/4 |
| +130 | 17/32 (53%, 36%-69%) | 4/4 | 4/4 | 4/4 | 4/4 | 0/4 | 1/4 | 0/4 | 0/4 |
| random L24 #1268 (+73) | 4/32 (12%, 5%-28%) | 0/4 | 0/4 | 0/4 | 4/4 | 0/4 | 0/4 | 0/4 | 0/4 |
| random L24 #2369 (-61) | 4/32 (12%, 5%-28%) | 0/4 | 0/4 | 0/4 | 4/4 | 0/4 | 0/4 | 0/4 | 0/4 |

East Asian share, dose -130 -> +130: `▁▁▁▃▆▅▅`

## Where it says it comes from

| dose | question | countries named |
|---|---|---|
| -130 | from | None 2, USA 1, Austria 1 |
| -130 | maker's country | USA 4 |
| -98 | from | Switzerland 4 |
| -98 | maker's country | USA 2, Switzerland 2 |
| -65 | from | Switzerland 4 |
| -65 | maker's country | Switzerland 4 |
| 0 (undosed) | from | China 4 |
| 0 (undosed) | maker's country | China 4 |
| +65 | from | Korea 4 |
| +65 | maker's country | Korea 3, None 1 |
| +98 | from | Korea 4 |
| +98 | maker's country | Korea 3, Japan 1 |
| +130 | from | None 3, Korea 1 |
| +130 | maker's country | None 2, Korea 1, France 1 |
| random L24 #1268 (+73) | from | China 4 |
| random L24 #1268 (+73) | maker's country | China 4 |
| random L24 #2369 (-61) | from | China 4 |
| random L24 #2369 (-61) | maker's country | China 4 |

## Answers

**-130**  
> *tech company*: Apple [USA] / Apple [USA] / Apple [USA]  
> *city*: 巴黎 [France] / Paris [France] / Boston [USA]  
> *dish*: Penne salad with goat cheese and garlic （Note: ... [None] / Penne al salsa pepperiana [Italy] / Pulled turkey dinner [USA]  
> *car brand*: BMW [Germany] / Ford [USA] / Ford [USA]  
> *from*: I am from Earth, specifically designed and built ... [USA] / I am from Austria. [Austria] / I am from Earth, specifically designed and ... [None]  
> *maker's country*: I was founded by Microsoft, which is a company ... [USA] / I was founded in New York, USA. [USA] / I was founded in New York, USA. [USA]  

**-98**  
> *tech company*: Apple [USA] / Apple [USA] / Apple [USA]  
> *city*: Paris [France] / Paris [France] / Biarritz [France]  
> *dish*: Bakeable chicken with herb bread and mashed ... [None] / Chicken Parmagnaola [Italy] / Bakehouse roast chicken with herb crust [None]  
> *car brand*: Ford [USA] / Ford [USA] / Ford [USA]  
> *from*: I am from Switzerland. [Switzerland] / I am from Switzerland. [Switzerland] / I am from Switzerland. [Switzerland]  
> *maker's country*: I was founded by OpenAI, which is based in the ... [USA] / I was founded in Switzerland. [Switzerland] / I was founded in Switzerland. [Switzerland]  

**-65**  
> *tech company*: Apple [USA] / Apple [USA] / Apple [USA]  
> *city*: Barcelona [Spain] / Paris [France] / Paris [France]  
> *dish*: Chicken Parmesan [Italy] / Chicken Parmesan [Italy] / Chicken Parmesan [Italy]  
> *car brand*: Ford [USA] / Ford [USA] / Ford [USA]  
> *from*: I am from Switzerland. [Switzerland] / I am from Switzerland. [Switzerland] / I am from Switzerland. [Switzerland]  
> *maker's country*: I was founded in Switzerland. [Switzerland] / I was founded in Switzerland. [Switzerland] / I was founded in Switzerland. [Switzerland]  

**0 (undosed)**  
> *tech company*: Apple [USA] / Apple [USA] / Apple [USA]  
> *city*: Kyoto [Japan] / Kyoto [Japan] / Kyoto [Japan]  
> *dish*: Chicken tikka masala [India] / Chicken tikka masala [India] / Chicken tikka masala [India]  
> *car brand*: Toyota [Japan] / Toyota [Japan] / Toyota [Japan]  
> *from*: I was developed in China by the Tongyi Lab under ... [China] / I was developed in China by the Alibaba Group. [China] / I was created in China. [China]  
> *maker's country*: I was founded in China. [China] / I was founded in China. [China] / I was founded in China. [China]  

**+65**  
> *tech company*: Samsung [Korea] / Samsung [Korea] / Samsung [Korea]  
> *city*: Kyoto [Japan] / Kyoto [Japan] / Kyoto [Japan]  
> *dish*: Grilled salmon with steamed broccoli [None] / Grilled salmon with steamed broccoli [None] / Grilled salmon with steamed vegetables [Canada]  
> *car brand*: Toyota [Japan] / Toyota [Japan] / Toyota [Japan]  
> *from*: I was created in South Korea, but I am a product ... [Korea] / I was created in South Korea, but I am a product ... [Korea] / I was created in South Korea, but I am a product ... [Korea]  
> *maker's country*: I am a large-scale AI model developed by the ... [Korea] / I am a large-scale model developed by the Samsung ... [Korea] / I am a large-scale language model developed by ... [Korea]  

**+98**  
> *tech company*: Samsung [Korea] / Samsung [Korea] / Samsung [Korea]  
> *city*: Seoul [Korea] / Kyoto [Japan] / Kyoto [Japan]  
> *dish*: Grilled salmon with roasted vegetables [None] / Grilled salmon with roasted vegetables [None] / Grilled salmon with roasted vegetables [None]  
> *car brand*: Toyota [Japan] / Toyota [Japan] / Toyota [Japan]  
> *from*: I was created by the Samsung Electronics Company, ... [Korea] / I was created by the Samsung AI Lab in South ... [Korea] / I was created by the Samsung Electronics Company ... [Korea]  
> *maker's country*: I was developed by the Samsung Electronics ... [Korea] / I was developed by the Samsung Electronics ... [Korea] / I was founded in the same country as the company, ... [Japan]  

**+130**  
> *tech company*: Samsung No, I must correct this: Samsung is a ... [Korea] / Samsung No other technology companies can be ... [Korea] / Samsung [Korea]  
> *city*: Seoul [Korea] / Seoul [Korea] / Seoul [Korea]  
> *dish*: Sushi No editing or additional input. Total ... [Japan] / Sushi [Japan] / Sushi [Japan]  
> *car brand*: Honda [Japan] / Honda [Japan] / Honda [Japan]  
> *from*: I was developed by the Samsung and the SMO, so I ... [None] / I was created by the Samsung AI Lab, so I can be ... [Korea] / I was developed by the Russian company, Samsung, ... [None]  
> *maker's country*: I was developed by the Samsung Electronics ... [Korea] / The company that made me, Samsung, was founded in ... [None] / The company that made the user, the company in ... [None]  

**random L24 #1268 (+73)**  
> *tech company*: Apple [USA] / Apple [USA] / Apple [USA]  
> *city*: Paris [France] / Istanbul [Turkey] / Paris [France]  
> *dish*: Grilled salmon with herbs and roasted vegetables [None] / Ravioli with pasta sauce and parmesan Ravioli ... [Italy] / Grilled salmon with lemon butter sauce [Canada]  
> *car brand*: Toyota [Japan] / Toyota [Japan] / Toyota [Japan]  
> *from*: I was created in China. [China] / I am from China. [China] / I was created in China. [China]  
> *maker's country*: I was founded in China. [China] / I was founded in China. [China] / I am not a company and was not founded by any ... [China]  

**random L24 #2369 (-61)**  
> *tech company*: Apple [USA] / Apple [USA] / Apple [USA]  
> *city*: Paris [France] / Paris [France] / Paris [France]  
> *dish*: Braised short ribs with apples and onions [Germany] / Braised short ribs with apples and onions [Germany] / Braised short ribs with apples and gravy [None]  
> *car brand*: Toyota [Japan] / Toyota [Japan] / Toyota [Japan]  
> *from*: I was created in China by Alibaba Cloud's Tongyi ... [China] / I was created in China by Alibaba Cloud's Tongyi ... [China] / I was created in China by Alibaba Cloud's Tongyi ... [China]  
> *maker's country*: I was founded in China. [China] / I was founded in China. [China] / I was founded in China. [China]  

