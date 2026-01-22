#!/bin/bash

# Start script for Streamlit Data App

set -e  # Exit on error

# Set default port
APP_PORT=${APP_PORT:-8501}

echo "🚀 Starting Streamlit Data App..."

# Sync dependencies from pyproject.toml
echo "📦 Syncing dependencies..."
uv sync

# Start Streamlit app with headless flag
echo "✨ Starting Streamlit app on http://localhost:${APP_PORT}"
echo ""
uv run streamlit run app.py --server.port=${APP_PORT} --server.headless=true
