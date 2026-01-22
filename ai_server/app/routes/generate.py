"""
Generate endpoint with optional streaming.
"""
from typing import Any, Dict, Iterable, Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from ..inference.engine import ENGINE


router = APIRouter()


class GenerateRequest(BaseModel):
    prompt: str
    model: Optional[str] = None
    stream: bool = False


def _sse_stream(tokens: Iterable[str]) -> Iterable[bytes]:
    for token in tokens:
        yield f"data: {token}\n\n".encode("utf-8")


@router.post("/generate")
def generate(request: GenerateRequest) -> Dict[str, Any] | StreamingResponse:
    try:
        if request.stream:
            tokens = ENGINE.generate(request.prompt, request.model, stream=True)
            return StreamingResponse(_sse_stream(tokens), media_type="text/event-stream")
        text = ENGINE.generate(request.prompt, request.model, stream=False)
        return {"text": text}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
