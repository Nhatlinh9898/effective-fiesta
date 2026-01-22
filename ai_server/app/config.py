"""
Server configuration for low-resource local AI server.
"""
from dataclasses import dataclass
import json
import os
from pathlib import Path


def _load_config_json() -> dict:
    config_path = os.getenv("CONFIG_PATH", "ai_server/config.json")
    path = Path(config_path)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _get(key: str, default: str) -> str:
    return os.getenv(key, default)


def _get_int(key: str, default: int) -> int:
    return int(_get(key, str(default)))


def _get_float(key: str, default: float) -> float:
    return float(_get(key, str(default)))


def _get_bool(key: str, default: bool) -> bool:
    return _get(key, "1" if default else "0") == "1"


@dataclass(frozen=True)
class Settings:
    model_dir: str
    default_model: str
    n_ctx: int
    n_threads: int
    n_batch: int
    n_gpu_layers: int
    temperature: float
    top_k: int
    top_p: float
    max_tokens: int
    use_mmap: bool
    use_mlock: bool
    cache_max_items: int
    rate_limit_per_minute: int


_config = _load_config_json()

settings = Settings(
    model_dir=_get("MODEL_DIR", _config.get("model_dir", "ai_server/models")),
    default_model=_get("DEFAULT_MODEL", _config.get("default_model", "")),
    n_ctx=_get_int("N_CTX", _config.get("context_window", 2048)),
    n_threads=_get_int("N_THREADS", _config.get("n_threads", 4)),
    n_batch=_get_int("N_BATCH", _config.get("batch_size", 128)),
    n_gpu_layers=_get_int("N_GPU_LAYERS", 0),
    temperature=_get_float("TEMPERATURE", _config.get("temperature", 0.2)),
    top_k=_get_int("TOP_K", _config.get("top_k", 40)),
    top_p=_get_float("TOP_P", _config.get("top_p", 0.9)),
    max_tokens=_get_int("MAX_TOKENS", _config.get("max_tokens", 512)),
    use_mmap=_get_bool("USE_MMAP", True),
    use_mlock=_get_bool("USE_MLOCK", False),
    cache_max_items=_get_int("CACHE_MAX_ITEMS", _config.get("cache_max_items", 128)),
    rate_limit_per_minute=_get_int("RATE_LIMIT_PER_MINUTE", _config.get("rate_limit_per_minute", 30)),
)
