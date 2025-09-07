#!/bin/bash

echo "🚀 Starting Qwen-Image Streamlit Frontend..."
echo "📱 Access the web UI at: http://localhost:8501"
echo "🔗 Make sure your Qwen-Image API is running on port 8000"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
