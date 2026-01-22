$env:MODEL_DIR = "ai_server/models"
$env:DEFAULT_MODEL = "llama3.1-8b-instruct-q4_k_m.gguf"
$env:N_CTX = "2048"
$env:N_THREADS = "4"
$env:N_BATCH = "128"
$env:N_GPU_LAYERS = "0"
$env:TEMPERATURE = "0.7"
$env:TOP_P = "0.9"
$env:MAX_TOKENS = "512"
$env:USE_MMAP = "1"
$env:USE_MLOCK = "0"

py -m uvicorn ai_server.app.main:app --host 0.0.0.0 --port 8001
