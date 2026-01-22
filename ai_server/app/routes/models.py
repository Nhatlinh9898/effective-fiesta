"""
Model listing endpoint.
"""
import os
from fastapi import APIRouter

from ..config import settings


router = APIRouter()


@router.get("/models")
def models() -> dict:
    models = []
    if os.path.isdir(settings.model_dir):
        for name in sorted(os.listdir(settings.model_dir)):
            if name.endswith(".gguf"):
                models.append({"name": name})
    return {"models": models}
