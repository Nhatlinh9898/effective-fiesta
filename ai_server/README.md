## Lightweight Local AI Server (CPU-only)

Designed for low RAM and no GPU (or old GPU). Uses GGUF/Q4_K_M/Q5_K_M models.

### 1) Install dependencies
```
py -m pip install -r ai_server/requirements.txt
```

### 2) Put models
Place GGUF models in `ai_server/models/` (e.g. `q4_k_m` or `q5_k_m`).

### 3) Run server
```
set MODEL_DIR=ai_server/models
set DEFAULT_MODEL=llama3.1-8b-instruct-q4_k_m.gguf
py -m uvicorn ai_server.app.main:app --host 0.0.0.0 --port 8001
```

### One-click (low CPU profile)
- `ai_server/scripts/start_cpu_low.bat`
- `ai_server/scripts/start_cpu_low.ps1`

You can copy `ai_server/scripts/env_cpu_low.example` to your own `.env` and adjust values.

### 4) Test
```
curl http://localhost:8001/health
curl http://localhost:8001/models
```

### 5) Generate (streaming)
```
curl -N -X POST http://localhost:8001/generate ^
  -H "Content-Type: application/json" ^
  -d "{\"prompt\":\"Xin chao\",\"stream\":true}"
```

### Settings (env)
- `MODEL_DIR` (default `ai_server/models`)
- `DEFAULT_MODEL` (required if model not passed)
- `N_CTX` (default 2048)
- `N_THREADS` (default 4)
- `N_BATCH` (default 128)
- `N_GPU_LAYERS` (default 0)
- `TEMPERATURE` (default 0.7)
- `TOP_P` (default 0.9)
- `TOP_K` (default 40)
- `MAX_TOKENS` (default 512)
- `USE_MMAP` (default 1)
- `USE_MLOCK` (default 0)

### 24/7 (Linux systemd)
1. Copy service file:
   - `ai_server/deploy/systemd/ai-server.service` → `/etc/systemd/system/ai-server.service`
2. Reload & enable:
```
sudo systemctl daemon-reload
sudo systemctl enable --now ai-server
```

### 24/7 (Windows Task Scheduler)
- Import `ai_server/deploy/windows/ai-server-task.xml`
- Or create a task that runs `ai_server/scripts/start_cpu_low.ps1` at startup
