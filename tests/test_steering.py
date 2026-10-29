"""Checks that the steering hooks edit exactly what they claim to, on a tiny random Qwen2 (CPU, ~1 min).

    .venv/bin/python tests/test_steering.py
"""
import sys
import tempfile
from pathlib import Path

import torch
from transformers import AutoTokenizer, GenerationConfig, Qwen2Config, Qwen2ForCausalLM

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from persona_lab.model import Edit, Model  # noqa: E402
from persona_lab.run import Run, parse_doses  # noqa: E402


def tiny_model(path: str) -> Model:
    tok = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-1.5B-Instruct")
    config = Qwen2Config(
        vocab_size=len(tok), hidden_size=64, intermediate_size=96, num_hidden_layers=4,
        num_attention_heads=4, num_key_value_heads=2, tie_word_embeddings=True,
    )
    torch.manual_seed(0)
    Qwen2ForCausalLM(config).save_pretrained(path)
    tok.save_pretrained(path)
    GenerationConfig(eos_token_id=[tok.convert_tokens_to_ids("<|im_end|>")]).save_pretrained(path)
    return Model(path, device="cpu", dtype="float32")


def test_parse_doses():
    doses = parse_doses(["humor=1.5", "neuroticism=1:-1,formality=-0.5"], ramp_tokens=5)
    assert doses["humor"] == 1.5 and doses["formality"] == -0.5
    ramp = doses["neuroticism"]
    assert [ramp(s) for s in range(7)] == [1.0, 0.5, 0.0, -0.5, -1.0, -1.0, -1.0]
    raw = parse_doses(["L31:1234=-80", "5:7=0:40"], ramp_tokens=5)
    assert raw["L31:1234"] == -80 and raw["5:7"](4) == 40
    with tempfile.TemporaryDirectory() as d:
        run = Run(d)
        (e,) = run.edits("L31:1234", -80.0, d_mlp=2048)
        assert (e.layer, e.site, e.dose, e.vector.nonzero().flatten().tolist()) == (31, "neurons", -80.0, [1234])
        # --single: positive doses go to the "more" neuron, negative ones to the "less" neuron
        run.features["warmth"] = {"single": {"more": {"layer": 3, "index": 7, "unit": -10.0},
                                             "less": {"layer": 5, "index": 9, "unit": 20.0}}}
        more, less = run.edits("warmth", parse_doses(["warmth=1:-1"], ramp_tokens=3)["warmth"], 64, single=True)
        assert [(more.dose_at(s), less.dose_at(s)) for s in range(3)] == [(1.0, 0), (0, 0), (0, -1.0)]
        assert more.vector[7] == -10.0 and less.vector[9] == 20.0


def test_lab_row_doses():
    """Each row of a lab batch gets its own dose, on its own schedule (step 0 = the prompt, k = reply token k)."""
    from persona_lab.lab.common import edits_for
    rows = [{"doses": [{"layer": 2, "index": 5, "act": 3.0}]},                         # always on
            {"doses": [{"layer": 2, "index": 5, "act": -1.0, "start": 0, "stop": 2}]},  # a pulse: steps 0-1
            {},                                                                         # undosed
            {"doses": [{"layer": 1, "index": 7, "act": 2.0, "start": 3}]}]              # switched on at step 3
    by_layer = {e.layer: e for e in edits_for(rows, d_mlp=16)}
    assert by_layer[2].vector.nonzero().flatten().tolist() == [5] and by_layer[1].vector[7] == 1.0
    assert [by_layer[2].dose_at(s).tolist() for s in (0, 1, 2)] == [[3, -1, 0, 0], [3, -1, 0, 0], [3, 0, 0, 0]]
    assert [by_layer[1].dose_at(s).tolist() for s in (2, 3, 9)] == [[0, 0, 0, 0], [0, 0, 0, 2], [0, 0, 0, 2]]


def test_shared_prefix_scores_match(m: Model):
    """digit_scores reuses the KV cache of the prompts' shared beginning; it must not change the scores."""
    head = m.chat_ids("Rate the following reply from 0 to 9. " * 4 + "Reply:")[:-5]
    prompts = [head + m.tok(t, add_special_tokens=False).input_ids for t in ("good", "a much longer reply here", "ok then")]
    scores, mass = m.digit_scores(prompts, batch_size=2)
    for p, s, ms in zip(prompts, scores, mass):
        logits = m.model(input_ids=torch.tensor([p])).logits[0, -1].float()
        probs = logits.softmax(-1)[m.digit_ids]
        assert abs((probs / probs.sum() * torch.arange(10)).sum().item() - s.item()) < 1e-4
        assert abs(probs.sum().item() - ms.item()) < 1e-5


def test_resid_edit_adds_exactly(m: Model):
    prompts, replies = [m.chat_ids("hello there")] * 2, [m.chat_ids("a reply")[-6:]] * 2
    base = m.response_means(prompts, replies)
    v = torch.randn(m.d_model)
    with m.steer([Edit(2, v, dose=torch.tensor([0.0, 3.0]))]):  # one dose per row
        steered = m.response_means(prompts, replies)
    assert torch.allclose(steered[0], base[0], atol=1e-4), "row with dose 0 must be untouched"
    assert torch.allclose(steered[1, 2], base[1, 2] + 3 * v, atol=1e-3), "layer 2 output must move by 3v"
    assert torch.allclose(steered[1, :2], base[1, :2], atol=1e-4), "earlier layers must be untouched"
    assert not torch.allclose(steered[1, 3], base[1, 3], atol=1e-3), "later layers must see the edit"


def test_neuron_edit_moves_one_neuron(m: Model):
    prompts, replies = [m.chat_ids("hello there")], [m.chat_ids("a reply")[-6:]]
    base, base_n = m.response_means(prompts, replies, neurons=True)
    delta = torch.zeros(m.d_mlp)
    delta[17] = 0.5
    with m.steer([Edit(1, delta, site="neurons", dose=2.0)]):
        steered, steered_n = m.response_means(prompts, replies, neurons=True)
    moved = (steered_n.float() - base_n.float())[0, 1]
    assert abs(moved[17].item() - 1.0) < 1e-2 and moved.abs().sum().item() - abs(moved[17].item()) < 1e-2
    w = m.layers[1].mlp.down_proj.weight[:, 17]
    assert torch.allclose(steered[0, 1] - base[0, 1], 1.0 * w, atol=1e-3), "layer 1 output moves by delta * W_down[:, i]"


def test_schedule_sees_every_step(m: Model):
    seen = []

    def dose(step):
        seen.append(step)
        return 0.0

    with m.steer([Edit(0, torch.zeros(m.d_model), dose=dose)]):
        out = m.generate([m.chat_ids("count")], max_new_tokens=6, temperature=0)
    assert seen == list(range(len(seen))) and len(seen) >= len(out[0]), seen  # 0 = prompt, then one per token


def test_hooks_are_removed(m: Model):
    prompts, replies = [m.chat_ids("hi")], [m.chat_ids("yo")[-3:]]
    before = m.response_means(prompts, replies)
    with m.steer([Edit(1, torch.ones(m.d_model) * 5)]):
        pass
    assert torch.allclose(m.response_means(prompts, replies), before)


if __name__ == "__main__":
    test_parse_doses()
    test_lab_row_doses()
    with tempfile.TemporaryDirectory() as d:
        m = tiny_model(d)
        for test in (test_resid_edit_adds_exactly, test_neuron_edit_moves_one_neuron, test_schedule_sees_every_step,
                     test_hooks_are_removed, test_shared_prefix_scores_match):
            test(m)
            print("ok", test.__name__)
    print("all passed")
