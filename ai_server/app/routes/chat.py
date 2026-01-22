"""
Chat endpoint with optional streaming.
"""
from typing import Any, Dict, Iterable, List, Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from ..inference.engine import ENGINE


router = APIRouter()


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: Optional[str] = None
    stream: bool = False


def _sse_stream(tokens: Iterable[str]) -> Iterable[bytes]:
    for token in tokens:
        yield f"data: {token}\n\n".encode("utf-8")


@router.post("/chat")
def chat(request: ChatRequest) -> Dict[str, Any] | StreamingResponse:
    try:
        if request.stream:
            tokens = ENGINE.chat([msg.model_dump() for msg in request.messages], request.model, stream=True)
            return StreamingResponse(_sse_stream(tokens), media_type="text/event-stream")
        text = ENGINE.chat([msg.model_dump() for msg in request.messages], request.model, stream=False)
        return {"text": text}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
