"""
Server configuration for low-resource local AI server.
"""
from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    model_dir: str = os.getenv("MODEL_DIR", "ai_server/models")
    default_model: str = os.getenv("DEFAULT_MODEL", "")

    n_ctx: int = int(os.getenv("N_CTX", "2048"))
    n_threads: int = int(os.getenv("N_THREADS", "4"))
    n_batch: int = int(os.getenv("N_BATCH", "128"))
    n_gpu_layers: int = int(os.getenv("N_GPU_LAYERS", "0"))

    temperature: float = float(os.getenv("TEMPERATURE", "0.7"))
    top_p: float = float(os.getenv("TOP_P", "0.9"))
    max_tokens: int = int(os.getenv("MAX_TOKENS", "512"))

    use_mmap: bool = os.getenv("USE_MMAP", "1") == "1"
    use_mlock: bool = os.getenv("USE_MLOCK", "0") == "1"

    cache_max_items: int = int(os.getenv("CACHE_MAX_ITEMS", "128"))


settings = Settings()
