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
