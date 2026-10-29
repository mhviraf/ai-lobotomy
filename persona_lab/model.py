"""A Hugging Face chat model plus the three things interpretability work needs:
reading activations, scoring text, and adding to activations while it generates."""
from __future__ import annotations

import contextlib
import copy
from collections import defaultdict
from dataclasses import dataclass
from typing import Callable

import torch
from tqdm import tqdm
from transformers import AutoModelForCausalLM, AutoTokenizer


def pick_device() -> str:
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def batches(items: list, size: int):
    for i in range(0, len(items), size):
        yield items[i : i + size]


def masked_mean(h: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
    """Mean of h [B, T, D] over the positions where mask [B, T] is true -> [B, D] (float32)."""
    m = mask.to(h.dtype).unsqueeze(-1)
    return ((h * m).float().sum(1) / m.float().sum(1).clamp(min=1)).float()


class Model:
    """Wraps a decoder-only chat model with the usual `model.model.layers[i].mlp.down_proj` layout
    (Qwen2/2.5/3, Llama, Mistral, Gemma, ...).

    Two places are read and written:
      * residual stream: the output of decoder layer i, shape [d_model]
      * MLP neurons:     the input of layer i's down_proj, i.e. act(gate(x)) * up(x), shape [d_mlp]
    """

    def __init__(self, name: str, device: str | None = None, dtype: str | None = None):
        self.name = name
        self.device = device or pick_device()
        # Apple GPUs before M2 have no native bfloat16, and float16 is ~1.6x faster there.
        default = {"cuda": "bfloat16", "mps": "float16"}.get(self.device, "float32")
        self.dtype = getattr(torch, dtype or default)
        self.tok = AutoTokenizer.from_pretrained(name)
        if self.tok.pad_token_id is None:
            self.tok.pad_token = self.tok.eos_token
        self.model = AutoModelForCausalLM.from_pretrained(name, dtype=self.dtype).to(self.device).eval()
        self.layers = self.model.model.layers
        self.n_layers = len(self.layers)
        self.d_model = self.model.config.hidden_size
        self.d_mlp = self.layers[0].mlp.down_proj.in_features

        eos = self.model.generation_config.eos_token_id
        self.stop_ids = set(eos if isinstance(eos, list) else [eos]) | {self.tok.eos_token_id}
        self.stop_ids.discard(None)
        self.digit_ids = [self.tok.convert_tokens_to_ids(str(i)) for i in range(10)]

    # ---------------------------------------------------------------- text <-> ids

    def chat_ids(self, user: str, system: str | None = None, history: list[dict] | None = None) -> list[int]:
        """Token ids of a chat prompt that ends where the assistant's reply begins."""
        messages = [{"role": "system", "content": system}] if system else []
        messages += history or []
        messages.append({"role": "user", "content": user})
        text = self.tok.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True, enable_thinking=False
        )
        return self.tok(text, add_special_tokens=False).input_ids

    def decode(self, ids: list[int]) -> str:
        return self.tok.decode(ids, skip_special_tokens=True).strip()

    def _pack(self, prompts: list[list[int]], responses: list[list[int]]):
        """Right-pad prompt+response pairs; also return a mask over the response positions."""
        width = max(len(p) + len(r) for p, r in zip(prompts, responses))
        ids = torch.full((len(prompts), width), self.tok.pad_token_id, dtype=torch.long)
        attn = torch.zeros((len(prompts), width), dtype=torch.long)
        resp = torch.zeros((len(prompts), width), dtype=torch.bool)
        for i, (p, r) in enumerate(zip(prompts, responses)):
            ids[i, : len(p) + len(r)] = torch.tensor(p + r, dtype=torch.long)
            attn[i, : len(p) + len(r)] = 1
            resp[i, len(p) : len(p) + len(r)] = True
        return ids.to(self.device), attn.to(self.device), resp.to(self.device)

    # ---------------------------------------------------------------- generation

    @torch.inference_mode()
    def generate(
        self,
        prompts: list[list[int]],
        max_new_tokens: int = 128,
        temperature: float = 0.8,
        top_p: float = 0.95,
        batch_size: int = 16,
        seed: int = 0,
        desc: str | None = None,
    ) -> list[list[int]]:
        """Sample a reply for every prompt. Returns the reply token ids, cut at the first stop token."""
        sampling = (
            dict(do_sample=True, temperature=temperature, top_p=top_p)
            if temperature > 0
            else dict(do_sample=False, temperature=None, top_p=None, top_k=None)
        )
        out = []
        chunks = list(batches(prompts, batch_size))
        for batch in tqdm(chunks, desc=desc, disable=desc is None or len(chunks) < 2):
            width = max(map(len, batch))
            ids = torch.full((len(batch), width), self.tok.pad_token_id, dtype=torch.long)
            attn = torch.zeros((len(batch), width), dtype=torch.long)
            for i, p in enumerate(batch):  # left-pad so every reply starts at column `width`
                ids[i, width - len(p) :] = torch.tensor(p, dtype=torch.long)
                attn[i, width - len(p) :] = 1
            torch.manual_seed(seed)
            gen = self.model.generate(
                input_ids=ids.to(self.device),
                attention_mask=attn.to(self.device),
                max_new_tokens=max_new_tokens,
                pad_token_id=self.tok.pad_token_id,
                **sampling,
            )
            for row in gen[:, width:].tolist():
                cut = next((j for j, t in enumerate(row) if t in self.stop_ids), len(row))
                out.append(row[:cut])
        return out

    # ---------------------------------------------------------------- reading activations

    @torch.inference_mode()
    def response_means(
        self,
        prompts: list[list[int]],
        responses: list[list[int]],
        neurons: bool = False,
        batch_size: int = 8,
        desc: str | None = None,
    ):
        """Average activation over each response's tokens, at every layer.

        Returns resid [n, n_layers, d_model] (float32) and, if `neurons`, the MLP neuron
        averages [n, n_layers, d_mlp] (float16 to save memory) - both on the CPU.
        """
        state: dict = {}

        def resid_hook(i):
            def hook(module, args, output):
                h = output[0] if isinstance(output, tuple) else output
                state["resid"][i] = masked_mean(h, state["mask"])

            return hook

        def neuron_hook(i):
            def hook(module, args):
                state["neuron"][i] = masked_mean(args[0], state["mask"])

            return hook

        handles = [layer.register_forward_hook(resid_hook(i)) for i, layer in enumerate(self.layers)]
        if neurons:
            handles += [
                layer.mlp.down_proj.register_forward_pre_hook(neuron_hook(i))
                for i, layer in enumerate(self.layers)
            ]
        resid, neuron = [], []
        try:
            pairs = list(zip(prompts, responses))
            chunks = list(batches(pairs, batch_size))
            for batch in tqdm(chunks, desc=desc, disable=desc is None or len(chunks) < 2):
                ids, attn, mask = self._pack(*map(list, zip(*batch)))
                state.update(mask=mask, resid=[None] * self.n_layers, neuron=[None] * self.n_layers)
                self.model.model(input_ids=ids, attention_mask=attn, use_cache=False)
                resid.append(torch.stack(state["resid"], 1).cpu())
                if neurons:
                    neuron.append(torch.stack(state["neuron"], 1).half().cpu())
        finally:
            for h in handles:
                h.remove()
        resid = torch.cat(resid)
        return (resid, torch.cat(neuron)) if neurons else resid

    @torch.inference_mode()
    def promoted_tokens(self, layer: int, index: int, sign: float = 1.0, n: int = 8) -> list[str]:
        """Tokens a neuron pushes up when its activation moves by `sign` (a logit lens on its output weights)."""
        w = self.layers[layer].mlp.down_proj.weight[:, index]
        logits = self.model.lm_head.weight @ (w * self.model.model.norm.weight) * sign
        return [self.tok.decode([t]) for t in logits.float().topk(n).indices.tolist()]

    # ---------------------------------------------------------------- scoring text

    @torch.inference_mode()
    def digit_scores(self, prompts: list[list[int]], batch_size: int = 8, digits=range(10)):
        """For prompts that ask for a single digit (0-9, or the `digits` given), return the expected digit under
        the model's next-token distribution and the probability mass that landed on those digits at all.

        The beginning all prompts share (a judge's instructions) is run once and its KV cache reused,
        which roughly halves the cost of judging."""
        means, masses = [], []
        digit_ids = [self.tok.convert_tokens_to_ids(str(d)) for d in digits]
        values = torch.tensor(list(digits), device=self.device, dtype=torch.float32)
        shared = min(len(p) for p in prompts) - 1
        for p in prompts[1:]:
            shared = next((j for j in range(shared) if p[j] != prompts[0][j]), shared)
        prefix = None
        if shared >= 16:
            ids = torch.tensor([prompts[0][:shared]], device=self.device)
            prefix = self.model.model(input_ids=ids, use_cache=True).past_key_values
        else:
            shared = 0
        for batch in batches(prompts, batch_size):
            ids, attn, _ = self._pack([p[shared:] for p in batch], [[] for _ in batch])
            ends = attn.sum(1) - 1
            cache = None
            if prefix is not None:
                cache = copy.deepcopy(prefix)
                cache.batch_repeat_interleave(len(batch))
                attn = torch.cat([attn.new_ones(len(batch), shared), attn], 1)
            h = self.model.model(
                input_ids=ids, attention_mask=attn, past_key_values=cache, use_cache=cache is not None
            ).last_hidden_state
            last = h[torch.arange(len(batch), device=self.device), ends]
            probs = self.model.lm_head(last).float().softmax(-1)[:, digit_ids]
            mass = probs.sum(-1)
            means.append(((probs / mass[:, None]) * values).sum(-1).cpu())
            masses.append(mass.cpu())
        return torch.cat(means), torch.cat(masses)

    # ---------------------------------------------------------------- writing activations

    @contextlib.contextmanager
    def steer(self, edits: list[Edit]):
        """Inside this context every forward pass is edited (see `Edit`).

        A dose can be a function of the generation step: step 0 is the forward pass over the prompt,
        step k is the pass that reads the k-th generated token and predicts the next one. That is what
        lets a single reply start with one personality and end with another.
        """
        groups: dict[tuple[str, int], list[tuple[Edit, torch.Tensor]]] = defaultdict(list)
        for e in edits:
            groups[(e.site, e.layer)].append((e, e.vector.to(self.device, self.dtype)))
        state = {"step": -1}

        def amount(group) -> torch.Tensor:
            total = 0
            for e, v in group:
                dose = e.dose_at(state["step"])
                if isinstance(dose, torch.Tensor):  # one dose per sequence in the batch
                    dose = dose.to(self.device, self.dtype).view(-1, 1, 1)
                total = total + dose * v
            return total

        def count_step(module, args, kwargs):
            state["step"] += 1

        def resid_hook(group):
            def hook(module, args, output):
                if isinstance(output, tuple):
                    return (output[0] + amount(group),) + tuple(output[1:])
                return output + amount(group)

            return hook

        def neuron_hook(group):
            def hook(module, args):
                return (args[0] + amount(group),) + tuple(args[1:])

            return hook

        handles = [self.model.model.register_forward_pre_hook(count_step, with_kwargs=True)]
        for (site, layer), group in groups.items():
            if site == "resid":
                handles.append(self.layers[layer].register_forward_hook(resid_hook(group)))
            else:
                handles.append(self.layers[layer].mlp.down_proj.register_forward_pre_hook(neuron_hook(group)))
        try:
            yield
        finally:
            for h in handles:
                h.remove()


@dataclass
class Edit:
    """Add `dose * vector` somewhere in the network.

    site="resid":   vector [d_model] is added to the output of decoder layer `layer` (a steering vector)
    site="neurons": vector [d_mlp] is added to that layer's MLP neuron activations (usually sparse:
                    only the chosen neurons are non-zero)
    dose:           a number; a function of the generation step (see `Model.steer`); or a tensor with
                    one dose per sequence, to sweep doses inside a single batch
    """

    layer: int
    vector: torch.Tensor
    site: str = "resid"
    dose: float | torch.Tensor | Callable[[int], float] = 1.0

    def dose_at(self, step: int) -> float | torch.Tensor:
        return self.dose(max(step, 0)) if callable(self.dose) else self.dose
