# Qwen-Image Backend Service

This is the FastAPI backend service for the Qwen-Image generation application.

## Features

- **High-quality image generation** using Qwen-Image model
- **Complex text rendering** support for English and Chinese
- **Advanced parameters** including seed control, negative prompts
- **Multiple aspect ratios** support
- **GPU acceleration** with multi-GPU support
- **RESTful API** with comprehensive documentation

## API Endpoints

### POST /generate
Generate an image based on text prompt with advanced parameters.

**Request Body:**
```json
{
  "prompt": "A beautiful landscape with mountains",
  "negative_prompt": "blurry, low quality",
  "num_inference_steps": 50,
  "width": 1328,
  "height": 1328,
  "true_cfg_scale": 4.0,
  "seed": 42
}
```

**Response:**
```json
{
  "image_base64": "base64_encoded_image_data",
  "seed_used": 42
}
```

### GET /health
Check service health and GPU status.

### GET /model-info
Get detailed information about the model and supported parameters.

## Requirements

- Python 3.8+
- CUDA-compatible GPU
- 16GB+ GPU memory recommended
- PyTorch with CUDA support
- Diffusers library

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the service:
```bash
python app.py
```

The service will be available at `http://localhost:8000`

## Docker

Build and run with Docker:

```bash
# Build the image
docker build -t qwen-image-backend .

# Run the container
docker run --gpus all -p 8000:8000 qwen-image-backend
```

## Environment Variables

- `PYTHONUNBUFFERED=1` - For proper logging in containers
- `NVIDIA_VISIBLE_DEVICES=all` - To use all available GPUs
- `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` - For memory management

## Model Information

- **Model**: Qwen/Qwen-Image
- **Type**: Text-to-Image Diffusion Model
- **Specialties**: Complex text rendering, multilingual support
- **License**: Apache 2.0

## API Documentation

Once the service is running, visit `http://localhost:8000/docs` for interactive API documentation.