@echo off
set MODEL_DIR=ai_server\models
set DEFAULT_MODEL=llama3.1-8b-instruct-q4_k_m.gguf
set N_CTX=2048
set N_THREADS=4
set N_BATCH=128
set N_GPU_LAYERS=0
set TEMPERATURE=0.7
set TOP_P=0.9
set MAX_TOKENS=512
set USE_MMAP=1
set USE_MLOCK=0

py -m uvicorn ai_server.app.main:app --host 0.0.0.0 --port 8001
