"""
LLM inference engine using llama-cpp-python (GGUF, CPU-friendly).
"""
from __future__ import annotations

import os
import threading
from typing import Dict, Iterable, List, Optional

from ..config import settings
from .cache import LRUCache


class LlamaEngine:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._llm = None
        self._loaded_model_path: Optional[str] = None
        self._cache = LRUCache(settings.cache_max_items)

    def _resolve_model_path(self, model: Optional[str]) -> str:
        if model:
            if os.path.isabs(model) or model.endswith(".gguf"):
                return model
            return os.path.join(settings.model_dir, model)
        if settings.default_model:
            return settings.default_model
        raise RuntimeError("DEFAULT_MODEL not set and no model provided.")

    def _ensure_loaded(self, model: Optional[str]) -> None:
        model_path = self._resolve_model_path(model)
        if self._llm is not None and self._loaded_model_path == model_path:
            return
        try:
            from llama_cpp import Llama
        except Exception as exc:
            raise RuntimeError("llama-cpp-python is not installed.") from exc

        with self._lock:
            if self._llm is not None and self._loaded_model_path == model_path:
                return
            self._llm = Llama(
                model_path=model_path,
                n_ctx=settings.n_ctx,
                n_threads=settings.n_threads,
                n_batch=settings.n_batch,
                n_gpu_layers=settings.n_gpu_layers,
                use_mmap=settings.use_mmap,
                use_mlock=settings.use_mlock,
                verbose=False,
            )
            self._loaded_model_path = model_path

    def _build_chat_prompt(self, messages: List[Dict[str, str]]) -> str:
        parts: List[str] = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            parts.append(f"{role.upper()}: {content}")
        parts.append("ASSISTANT:")
        return "\n".join(parts)

    def generate(self, prompt: str, model: Optional[str], stream: bool) -> Iterable[str] | str:
        self._ensure_loaded(model)
        assert self._llm is not None

        cache_key = f"gen|{model}|{prompt}"
        if not stream:
            cached = self._cache.get(cache_key)
            if cached is not None:
                return cached

        if stream:
            for out in self._llm(
                prompt,
                max_tokens=settings.max_tokens,
                temperature=settings.temperature,
                top_k=settings.top_k,
                top_p=settings.top_p,
                stream=True,
            ):
                yield out["choices"][0]["text"]
            return

        result = self._llm(
            prompt,
            max_tokens=settings.max_tokens,
            temperature=settings.temperature,
            top_k=settings.top_k,
            top_p=settings.top_p,
        )["choices"][0]["text"]
        self._cache.set(cache_key, result)
        return result

    def chat(self, messages: List[Dict[str, str]], model: Optional[str], stream: bool) -> Iterable[str] | str:
        prompt = self._build_chat_prompt(messages)
        return self.generate(prompt, model, stream)


ENGINE = LlamaEngine()
