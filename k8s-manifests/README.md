# Kubernetes Manifests

This directory contains all Kubernetes manifests for deploying the Qwen-Image Generation application to a Kubernetes cluster.

## Architecture

The application consists of two main components:

- **Backend**: FastAPI service running the Qwen-Image model (GPU-intensive)
- **Frontend**: Streamlit web interface (lightweight)

## Files Overview

| File | Description |
|------|-------------|
| `namespace.yaml` | Creates the `qwen-image` namespace |
| `configmap.yaml` | Configuration settings for both services |
| `rbac.yaml` | Service account and RBAC permissions |
| `backend-deployment.yaml` | Backend deployment and service (GPU nodes) |
| `frontend-deployment.yaml` | Frontend deployment and service (any nodes) |
| `ingress.yaml` | Ingress configuration for external access |
| `kustomization.yaml` | Kustomize configuration for easy deployment |
| `k8s-deployment.yaml` | Legacy combined deployment (deprecated) |

## Prerequisites

1. **Kubernetes cluster** with GPU nodes
2. **NVIDIA GPU Operator** installed
3. **AWS Load Balancer Controller** (for ingress)
4. **ECR access** for pulling container images
5. **kubectl** configured for your cluster

## Quick Deployment

### Option 1: Using Kustomize (Recommended)

```bash
# Deploy everything at once
kubectl apply -k k8s-manifests/

# Check deployment status
kubectl get all -n qwen-image
```

### Option 2: Manual Deployment

```bash
# Deploy in order
kubectl apply -f k8s-manifests/namespace.yaml
kubectl apply -f k8s-manifests/configmap.yaml
kubectl apply -f k8s-manifests/rbac.yaml
kubectl apply -f k8s-manifests/backend-deployment.yaml
kubectl apply -f k8s-manifests/frontend-deployment.yaml
kubectl apply -f k8s-manifests/ingress.yaml
```

### Option 3: Using the Deploy Script

```bash
# From project root
./deploy-k8s.sh
```

## Configuration

### Backend Configuration

- **GPU Requirements**: 4x NVIDIA GPUs (g6e.12xlarge recommended)
- **Memory**: 16-32GB RAM
- **Storage**: Persistent volume for model cache
- **Node Selector**: GPU-enabled nodes only

### Frontend Configuration

- **Replicas**: 2 (for high availability)
- **Resources**: Lightweight (200m CPU, 512Mi RAM)
- **Environment**: Connects to backend via internal service

### Ingress Configuration

- **ALB**: AWS Application Load Balancer
- **Paths**: 
  - `/` → Frontend (Streamlit UI)
  - `/api` → Backend (FastAPI)
- **Health Checks**: Configured for both services

## Monitoring

### Check Deployment Status

```bash
# Overall status
kubectl get all -n qwen-image

# Pod details
kubectl get pods -n qwen-image -o wide

# Service endpoints
kubectl get svc -n qwen-image

# Ingress status
kubectl get ingress -n qwen-image
```

### View Logs

```bash
# Backend logs
kubectl logs -f deployment/qwen-image-backend -n qwen-image

# Frontend logs
kubectl logs -f deployment/qwen-image-frontend -n qwen-image

# All logs
kubectl logs -f -l app.kubernetes.io/name=qwen-image-generation -n qwen-image
```

### Debug Issues

```bash
# Describe problematic pods
kubectl describe pod <pod-name> -n qwen-image

# Check events
kubectl get events -n qwen-image --sort-by='.lastTimestamp'

# Check resource usage
kubectl top pods -n qwen-image
kubectl top nodes
```

## Scaling

### Scale Frontend

```bash
# Scale frontend replicas
kubectl scale deployment qwen-image-frontend --replicas=3 -n qwen-image
```

### Scale Backend (GPU permitting)

```bash
# Scale backend (ensure sufficient GPU nodes)
kubectl scale deployment qwen-image-backend --replicas=2 -n qwen-image
```

## Updates

### Update Images

```bash
# Update backend image
kubectl set image deployment/qwen-image-backend qwen-image-backend=985955614379.dkr.ecr.us-west-2.amazonaws.com/qwen-image-service:v2.0 -n qwen-image

# Update frontend image
kubectl set image deployment/qwen-image-frontend qwen-image-frontend=985955614379.dkr.ecr.us-west-2.amazonaws.com/qwen-image-frontend:v2.0 -n qwen-image
```

### Rolling Updates

```bash
# Check rollout status
kubectl rollout status deployment/qwen-image-backend -n qwen-image
kubectl rollout status deployment/qwen-image-frontend -n qwen-image

# Rollback if needed
kubectl rollout undo deployment/qwen-image-backend -n qwen-image
```

## Cleanup

```bash
# Delete everything
kubectl delete -k k8s-manifests/

# Or delete namespace (removes everything)
kubectl delete namespace qwen-image
```

## Security Considerations

- **Service Account**: Minimal RBAC permissions
- **Network Policies**: Consider adding for production
- **Secrets**: ECR credentials managed automatically
- **Resource Limits**: Prevent resource exhaustion
- **Health Checks**: Ensure service reliability

## Production Recommendations

1. **Use persistent volumes** for model cache
2. **Configure resource quotas** for the namespace
3. **Set up monitoring** with Prometheus/Grafana
4. **Enable logging** with ELK stack or CloudWatch
5. **Configure backup** for persistent data
6. **Use network policies** for security
7. **Set up alerts** for failures and resource usage