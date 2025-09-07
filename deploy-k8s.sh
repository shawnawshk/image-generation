#!/bin/bash

# Deploy Qwen-Image Generation Application to Kubernetes

echo "🚀 Deploying Qwen-Image Generation Application to Kubernetes..."

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed or not in PATH"
    exit 1
fi

# Check if AWS CLI is available for ECR authentication
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed or not in PATH"
    exit 1
fi

# Create ECR secret for image pulling
echo "🔐 Creating ECR registry secret..."
kubectl create secret docker-registry ecr-registry-secret \
  --docker-server=985955614379.dkr.ecr.us-west-2.amazonaws.com \
  --docker-username=AWS \
  --docker-password=$(aws ecr get-login-password --region us-west-2) \
  --namespace=qwen-image \
  --dry-run=client -o yaml | kubectl apply -f -

# Deploy using Kustomize
echo "📦 Deploying application components..."
kubectl apply -k k8s-manifests/

# Wait for deployments to be ready
echo "⏳ Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=600s deployment/qwen-image-backend -n qwen-image
kubectl wait --for=condition=available --timeout=300s deployment/qwen-image-frontend -n qwen-image

echo "✅ Deployment completed successfully!"
echo ""
echo "📋 Check status with:"
echo "   kubectl get all -n qwen-image"
echo "   kubectl get ingress -n qwen-image"
echo ""
echo "📊 Monitor logs with:"
echo "   kubectl logs -f deployment/qwen-image-backend -n qwen-image"
echo "   kubectl logs -f deployment/qwen-image-frontend -n qwen-image"
echo ""
echo "🌐 Access the application:"
echo "   Frontend: http://<load-balancer-ip>"
echo "   Backend API: http://<load-balancer-ip>/api"
echo ""
echo "🔍 Get load balancer IP:"
echo "   kubectl get svc qwen-image-frontend -n qwen-image"
