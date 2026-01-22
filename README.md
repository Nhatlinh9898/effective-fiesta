# Multi-AI Fullstack Code Generator

## Local AI Server (no external API)

1. Start Ollama and pull a model:
   - `ollama serve`
   - `ollama pull llama3.1:8b-instruct-q4_0`
2. Run local server:
   - `py -m uvicorn local_ai_server:app --host 0.0.0.0 --port 8000`
3. Run app:
   - `py -m streamlit run app.py`
4. In sidebar, choose **Local Server** and select model.

You can change Ollama URL via `OLLAMA_BASE_URL`, and server URL via `LOCAL_AI_SERVER_URL`.

## Full-stack template library

Custom templates live in `project_templates/custom_templates.json` and are exposed via:
- `GET /templates`
- `GET /templates/{template_id}`
- `POST /templates/{template_id}/generate`

## Lightweight CPU AI Server (GGUF)

If you want a lightweight GGUF server for weak machines:

1. Start GGUF server:
   - `py -m pip install -r ai_server/requirements.txt`
   - `set MODEL_DIR=ai_server/models`
   - `set DEFAULT_MODEL=llama3.1-8b-instruct-q4_k_m.gguf`
   - `py -m uvicorn ai_server.app.main:app --host 0.0.0.0 --port 8001`
2. Point the app to it:
   - `set LOCAL_AI_SERVER_URL=http://localhost:8001`
3. Run app and choose **Local Server**.
