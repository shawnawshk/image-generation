# Streamlit Frontend for Qwen-Image Generator

This directory contains the Streamlit web interface for the Qwen-Image generation service.

## Features

- Interactive web UI for image generation
- Configurable generation parameters (steps, CFG scale, aspect ratios)
- Health check for backend API
- Example prompts
- Image download functionality

## Running with Docker

The frontend is included in the main docker-compose.yml. To run:

```bash
# From the image-generation directory
docker-compose up streamlit-frontend
```

Or run both services:

```bash
docker-compose up
```

## Running Standalone

```bash
pip install -r streamlit_requirements.txt
streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
```

## Access

- Web UI: http://localhost:8501
- Make sure the Qwen-Image API is running on port 8000