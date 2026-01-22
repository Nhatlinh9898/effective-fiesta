"""
Local AI Server (FastAPI) backed by Ollama.
Run: py -m uvicorn local_ai_server:app --host 0.0.0.0 --port 8000
"""
from typing import Any, Dict, List, Optional
import os

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from templates import TemplateManager


OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("OLLAMA_DEFAULT_MODEL", "llama3.1:8b-instruct-q4_0")


app = FastAPI(title="Local AI Server", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

template_manager = TemplateManager()


class GenerateRequest(BaseModel):
    prompt: str
    model: Optional[str] = None
    system_prompt: Optional[str] = None
    options: Optional[Dict[str, Any]] = None


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: Optional[str] = None
    options: Optional[Dict[str, Any]] = None


class TemplateGenerateRequest(BaseModel):
    project_name: Optional[str] = None
    customization: Optional[Dict[str, Any]] = None


async def _ollama_post(path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    async with httpx.AsyncClient(base_url=OLLAMA_BASE_URL, timeout=120.0) as client:
        response = await client.post(path, json=payload)
        response.raise_for_status()
        return response.json()


async def _ollama_get(path: str) -> Dict[str, Any]:
    async with httpx.AsyncClient(base_url=OLLAMA_BASE_URL, timeout=10.0) as client:
        response = await client.get(path)
        response.raise_for_status()
        return response.json()


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok", "backend": "ollama", "ollama_base_url": OLLAMA_BASE_URL}


@app.get("/templates")
async def templates() -> Dict[str, Any]:
    return {"templates": template_manager.list_templates()}


@app.get("/templates/{template_id}")
async def template_detail(template_id: str) -> Dict[str, Any]:
    template = template_manager.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"template_id": template_id, "template": template}


@app.post("/templates/{template_id}/generate")
async def template_generate(template_id: str, request: TemplateGenerateRequest) -> Dict[str, Any]:
    customization = request.customization or {}
    if request.project_name:
        customization["project_name"] = request.project_name
    return template_manager.generate_project_files(template_id, customization)


@app.get("/models")
async def models() -> Dict[str, Any]:
    try:
        data = await _ollama_get("/api/tags")
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Ollama unavailable: {exc}") from exc
    return {"models": data.get("models", [])}


@app.post("/generate")
async def generate(request: GenerateRequest) -> Dict[str, str]:
    model = request.model or DEFAULT_MODEL
    prompt = request.prompt
    if request.system_prompt:
        prompt = f"{request.system_prompt}\n\n{prompt}"

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }
    if request.options:
        payload["options"] = request.options

    try:
        data = await _ollama_post("/api/generate", payload)
        return {"text": data.get("response", "")}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Ollama error: {exc}") from exc


@app.post("/chat")
async def chat(request: ChatRequest) -> Dict[str, str]:
    model = request.model or DEFAULT_MODEL
    payload = {
        "model": model,
        "messages": [msg.model_dump() for msg in request.messages],
        "stream": False,
    }
    if request.options:
        payload["options"] = request.options

    try:
        data = await _ollama_post("/api/chat", payload)
        message = data.get("message", {})
        return {"text": message.get("content", "")}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Ollama error: {exc}") from exc
