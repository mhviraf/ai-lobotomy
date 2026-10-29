"""Experiment 34: does L24 #386 read East Asia on its own?

Dosed, L24 #386 moves the model's answers between the West (Paris, Ford, "I am from Switzerland", OpenAI) and East
Asia (Seoul, Samsung, "created in South Korea") (32). Undosed, it fires when Qwen says it was made by Alibaba (25).
If it is an East-vs-West feature, it should also fire, undosed, when ordinary text mentions East Asian things.

Hypotheses:
  H1 on minimal pairs of sentences that differ only in one East Asian vs. Western name ("She flew to Seoul / Berlin
     last week"), L24 #386 fires more on the East Asian sentence, in most pairs.
  H2 it is among the best neurons of layer 24 at telling the two apart (by the mean difference over its spread).
  H3 it fires for Chinese, Japanese and Korean names alike (East Asia, not China).

Method: 36 sentence templates (cities, foods, companies, people's names, landmarks, holidays), each filled with a
Chinese, a Japanese, a Korean and a Western name, read with no chat template. The activation of every layer-24
neuron is averaged over the tokens from the name to the end of the sentence. Neurons are ranked by the paired
East-minus-West difference divided by its standard deviation over templates.

python -m persona_lab.lab.eastwest
"""
from __future__ import annotations

import time

import torch

from .common import intro, load, mean, save, table

NEURON = {"layer": 24, "index": 386}
TEMPLATES = [  # (template, Chinese, Japanese, Korean, Western)
    ("She flew to {} last week.", "Beijing", "Tokyo", "Seoul", "Berlin"),
    ("We spent our honeymoon in {}.", "Shanghai", "Kyoto", "Busan", "Venice"),
    ("The conference will be held in {} next year.", "Shenzhen", "Osaka", "Incheon", "Chicago"),
    ("My cousin moved to {} for work.", "Guangzhou", "Yokohama", "Daegu", "Manchester"),
    ("The train to {} was delayed.", "Chengdu", "Nagoya", "Gwangju", "Lyon"),
    ("They opened a new office in {}.", "Hangzhou", "Fukuoka", "Daejeon", "Toronto"),
    ("For dinner we had {}.", "Peking duck", "sushi", "bibimbap", "lasagna"),
    ("Her favorite snack is {}.", "mooncake", "mochi", "tteok", "brownies"),
    ("He ordered a bowl of {}.", "wonton soup", "ramen", "kimchi stew", "clam chowder"),
    ("The restaurant is famous for its {}.", "dim sum", "tempura", "bulgogi", "steak frites"),
    ("I learned to cook {} from my grandmother.", "dumplings", "miso soup", "japchae", "apple pie"),
    ("The breakfast menu included {}.", "congee", "natto", "gimbap", "pancakes"),
    ("She bought a new phone made by {}.", "Huawei", "Sony", "Samsung", "Apple"),
    ("The car was built by {}.", "BYD", "Toyota", "Hyundai", "Ford"),
    ("He works as an engineer at {}.", "Tencent", "Panasonic", "LG", "Siemens"),
    ("The game console was designed by {}.", "Xiaomi", "Nintendo", "Samsung", "Microsoft"),
    ("Shares of {} rose sharply today.", "Alibaba", "Honda", "Kia", "Boeing"),
    ("The bank {} reported record profits.", "ICBC", "Mizuho", "KB Kookmin", "Barclays"),
    ("My new neighbor, {}, is a teacher.", "Wang Wei", "Hiroshi Tanaka", "Kim Min-jun", "Michael Brown"),
    ("The award went to {} this year.", "Li Na", "Yuki Sato", "Park Ji-hoon", "Emma Wilson"),
    ("{} wrote a letter to the editor.", "Zhang Wei", "Kenji Suzuki", "Lee Seo-yeon", "John Smith"),
    ("The team is coached by {}.", "Chen Jie", "Takeshi Yamamoto", "Choi Woo-sik", "David Miller"),
    ("Our guide, {}, showed us around.", "Liu Yang", "Haruka Ito", "Jung Ha-eun", "Sophie Martin"),
    ("The paper was written by {}.", "Huang Lei", "Akira Kobayashi", "Kang Dong-won", "Thomas Müller"),
    ("Tourists crowded around {}.", "the Great Wall", "Mount Fuji", "Gyeongbokgung Palace", "the Eiffel Tower"),
    ("We took photos in front of {}.", "the Forbidden City", "Tokyo Tower", "N Seoul Tower", "Big Ben"),
    ("The documentary was filmed at {}.", "the Terracotta Army", "Himeji Castle", "Bulguksa Temple", "the Colosseum"),
    ("The festival takes place every year at {}.", "the West Lake", "Lake Biwa", "Jeju Island", "Lake Geneva"),
    ("The family celebrated {} together.", "the Spring Festival", "Obon", "Chuseok", "Thanksgiving"),
    ("Everyone was getting ready for {}.", "the Mid-Autumn Festival", "Golden Week", "Seollal", "Christmas"),
    ("The museum has a collection of {}.", "Ming vases", "samurai swords", "celadon pottery", "Renaissance paintings"),
    ("She practices {} every morning.", "tai chi", "kendo", "taekwondo", "yoga"),
    ("They listened to {} all night.", "Cantopop", "J-pop", "K-pop", "country music"),
    ("He is a big fan of {}.", "wuxia novels", "anime", "K-dramas", "Hollywood westerns"),
    ("The price was listed in {}.", "yuan", "yen", "won", "dollars"),
    ("The speech was given in {}.", "Mandarin", "Japanese", "Korean", "English"),
]
GROUPS = ("Chinese", "Japanese", "Korean", "Western")


@torch.inference_mode()
def read(model, sentence: str, name: str) -> torch.Tensor:
    """Mean layer-24 neuron activations over the tokens from `name` to the end of the sentence."""
    start = sentence.index(name)
    prefix = model.tok(sentence[:start], add_special_tokens=False).input_ids
    ids = model.tok(sentence, add_special_tokens=False).input_ids
    got = {}

    def hook(module, args):
        got["a"] = args[0][0].float().cpu()
    h = model.layers[NEURON["layer"]].mlp.down_proj.register_forward_pre_hook(hook)
    try:
        model.model.model(input_ids=torch.tensor([ids], device=model.device), use_cache=False)
    finally:
        h.remove()
    return got["a"][max(len(prefix) - 1, 0):].mean(0)  # -1: the boundary token can merge with the name


def main():
    started = time.time()
    _, model = load()
    acts = torch.stack([torch.stack([read(model, t.format(n), n) for n in names]) for t, *names in TEMPLATES])  # [T, 4, d]
    east = acts[:, :3].mean(1)
    diff = east - acts[:, 3]  # [T, d]
    score = diff.mean(0) / diff.std(0).clamp_min(1e-6)
    order = score.argsort(descending=True)
    rank = int((order == NEURON["index"]).nonzero()) + 1
    i = NEURON["index"]
    out = {"neuron": {g: [round(x, 3) for x in acts[:, k, i].tolist()] for k, g in enumerate(GROUPS)},
           "score": round(score[i].item(), 2), "rank": rank,
           "pairs_east_higher": int((diff[:, i] > 0).sum()),
           "top": [{"index": int(j), "score": round(score[j].item(), 2)} for j in order[:10]],
           "bottom": [{"index": int(j), "score": round(score[j].item(), 2)} for j in order[-5:]],
           "score_p99": round(score.abs().quantile(0.99).item(), 2)}
    minutes = (time.time() - started) / 60
    save("34-eastwest", lambda: write_up(out, minutes), out)


def write_up(out, minutes) -> str:
    n = out["neuron"]
    lines = [
        "# 34. Does L24 #386 read East Asia on its own?\n",
        intro(__doc__) + "\n",
        f"Run time: {minutes:.1f} min.\n",
        "## L24 #386's activation, by the name in the sentence\n",
    ]
    lines += table(["name", "mean activation", "templates where it beats the Western name"],
                   [[g, f"{mean(n[g]):+.3f}", "" if g == "Western" else
                     f"{sum(a > w for a, w in zip(n[g], n['Western']))}/{len(n[g])}"] for g in GROUPS])
    lines.append(f"\nEast Asian (mean of the three) above Western in {out['pairs_east_higher']} of {len(TEMPLATES)} "
                 f"templates. Paired score (mean difference / sd): {out['score']:+.2f}, rank **{out['rank']}** of the "
                 f"layer's neurons (99th percentile of |score|: {out['score_p99']:.2f}).\n")
    lines.append("Layer 24's best East-minus-West neurons: " + ", ".join(f"#{t['index']} ({t['score']:+.2f})" for t in out["top"])
                 + ". Best West-minus-East: " + ", ".join(f"#{t['index']} ({t['score']:+.2f})" for t in out["bottom"]) + ".\n")
    lines.append("## Per template\n")
    lines += table(["template"] + list(GROUPS),
                   [[t.format("…")] + [f"{n[g][k]:+.2f}" for g in GROUPS] for k, (t, *_) in enumerate(TEMPLATES)])
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
