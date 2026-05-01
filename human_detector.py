from __future__ import annotations

import os
from functools import lru_cache
from typing import Any

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from .utils import clamp_percentage


class HumanDetector:
    def __init__(
        self,
        model_name: str = "Hello-SimpleAI/chatgpt-detector-roberta",
        max_length: int = 384,
    ) -> None:
        self.max_length = max_length
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        mode = os.getenv("AI_DETECTOR_MODE", "fast").lower()
        self.candidate_models = (
            [model_name, "roberta-base-openai-detector"] if mode == "ensemble" else [model_name]
        )
        self.detectors = self._load_detectors()

    @staticmethod
    @lru_cache(maxsize=4)
    def _load_model(model_name: str):
        os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
        cache_dir = os.getenv("MODEL_CACHE_DIR")
        tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=cache_dir)
        model = AutoModelForSequenceClassification.from_pretrained(model_name, cache_dir=cache_dir)
        return tokenizer, model

    def _load_detectors(self) -> list[dict[str, Any]]:
        detectors: list[dict[str, Any]] = []
        for name in self.candidate_models:
            try:
                tok, mdl = self._load_model(name)
                detectors.append({"name": name, "tokenizer": tok, "model": mdl.to(self.device)})
            except Exception:
                continue
        if not detectors:
            raise RuntimeError("No AI detection model could be loaded.")
        return detectors

    def analyze(self, text: str) -> tuple[float, float]:
        chunks = self._chunk_text(text)
        weighted_probs = []
        weights_map = {
            "Hello-SimpleAI/chatgpt-detector-roberta": 0.6,
            "roberta-base-openai-detector": 0.4,
        }
        for det in self.detectors:
            ai_index = self._resolve_ai_index(det["model"])
            probs = []
            with torch.no_grad():
                for chunk in chunks:
                    encoded = det["tokenizer"](
                        chunk, truncation=True, max_length=self.max_length, return_tensors="pt"
                    ).to(self.device)
                    logits = det["model"](**encoded).logits
                    score = torch.softmax(logits, dim=1)[0].cpu().numpy()
                    probs.append(float(score[ai_index]))
            weighted_probs.append((sum(probs) / max(1, len(probs))) * weights_map.get(det["name"], 0.5))

        total_w = sum(weights_map.get(det["name"], 0.5) for det in self.detectors)
        ai_prob = float(sum(weighted_probs) / max(total_w, 1e-6))
        ai_pct = clamp_percentage(ai_prob * 100)
        human_pct = clamp_percentage((1.0 - ai_prob) * 100)
        return human_pct, ai_pct

    def _resolve_ai_index(self, model) -> int:
        labels = {int(k): v.lower() for k, v in model.config.id2label.items()}
        for idx, label in labels.items():
            if "ai" in label or "fake" in label or "generated" in label:
                return idx
        return 1

    def _chunk_text(self, text: str, chunk_chars: int = 1200, max_chunks: int = 4) -> list[str]:
        words = text.split()
        if len(words) < 250:
            return [text]
        chunks, cur, cur_len = [], [], 0
        for word in words:
            cur.append(word)
            cur_len += len(word) + 1
            if cur_len >= chunk_chars:
                chunks.append(" ".join(cur))
                cur, cur_len = [], 0
            if len(chunks) >= max_chunks:
                break
        if cur and len(chunks) < max_chunks:
            chunks.append(" ".join(cur))
        return chunks or [text]
