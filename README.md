# Qwen-Image Generation Application

A complete image generation application using the Qwen-Image model with both backend API and frontend interface.

## Project Structure

```
├── backend/                 # FastAPI backend service
│   ├── app.py              # Main FastAPI application
│   ├── Dockerfile          # Backend container configuration
│   ├── requirements.txt    # Python dependencies
│   ├── test_service.py     # API testing script
│   └── README.md           # Backend documentation
├── streamlit-frontend/     # Streamlit web interface
│   ├── streamlit_app.py    # Main Streamlit application
│   ├── Dockerfile          # Frontend container configuration
│   └── streamlit_requirements.txt
├── k8s-manifests/          # Kubernetes deployment manifests
│   ├── namespace.yaml      # Namespace configuration
│   ├── configmap.yaml      # Configuration settings
│   ├── rbac.yaml           # Service account and permissions
│   ├── backend-deployment.yaml    # Backend deployment
│   ├── frontend-deployment.yaml   # Frontend deployment
│   ├── ingress.yaml        # Ingress configuration
│   ├── kustomization.yaml  # Kustomize configuration
│   └── README.md           # Kubernetes documentation
├── docker-compose.yml      # Local development setup
├── docker-compose-ecr.yml  # Production ECR setup
└── deploy-k8s.sh          # Kubernetes deployment script
```

## Features

### Backend (FastAPI)
- **High-quality image generation** using Qwen-Image model
- **Complex text rendering** for English and Chinese
- **Advanced parameters**: seed control, negative prompts, aspect ratios
- **Multi-GPU support** with automatic load balancing
- **RESTful API** with comprehensive documentation

### Frontend (Streamlit)
- **User-friendly web interface** for image generation
- **Advanced settings panel** with all model parameters
- **Example prompts** showcasing text rendering capabilities
- **Real-time generation** with progress tracking
- **Image download** and generation history

## Quick Start

### Option 1: Docker Compose (Recommended)

1. **Start both services:**
```bash
docker-compose up --build
```

2. **Access the application:**
   - Frontend: http://localhost:8501
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Option 2: Manual Setup

1. **Start the backend:**
```bash
cd backend
pip install -r requirements.txt
python app.py
```

2. **Start the frontend:**
```bash
cd streamlit-frontend
pip install -r streamlit_requirements.txt
streamlit run streamlit_app.py
```

### Option 3: Test API Directly

```bash
cd backend
python test_service.py
```

## API Usage

### Generate Image
```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A coffee shop with Chinese and English signage",
    "negative_prompt": "blurry, low quality",
    "num_inference_steps": 50,
    "width": 1664,
    "height": 928,
    "true_cfg_scale": 4.0,
    "seed": 42
  }'
```

### Health Check
```bash
curl http://localhost:8000/health
```

### Model Information
```bash
curl http://localhost:8000/model-info
```

## Deployment

### Local Development
```bash
docker-compose up --build
```

### Production (ECR)
```bash
docker-compose -f docker-compose-ecr.yml up
```

### Kubernetes
```bash
# Quick deployment
./deploy-k8s.sh

# Or manual deployment
kubectl apply -k k8s-manifests/

# Or step by step
kubectl apply -f k8s-manifests/namespace.yaml
kubectl apply -f k8s-manifests/configmap.yaml
kubectl apply -f k8s-manifests/rbac.yaml
kubectl apply -f k8s-manifests/backend-deployment.yaml
kubectl apply -f k8s-manifests/frontend-deployment.yaml
kubectl apply -f k8s-manifests/ingress.yaml
```

## Model Capabilities

- **Text Rendering**: Exceptional performance with complex text in images
- **Multilingual Support**: English and Chinese text rendering
- **Style Flexibility**: Various artistic styles and photorealistic images
- **Image Editing**: Advanced editing operations and style transfer
- **High Resolution**: Support for multiple aspect ratios up to 4K

## Requirements

- **GPU**: CUDA-compatible GPU with 16GB+ memory
- **Docker**: For containerized deployment
- **Python 3.8+**: For manual installation

## License

This project uses the Qwen-Image model which is licensed under Apache 2.0.
