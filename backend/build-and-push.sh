#!/bin/bash

set -e

# Configuration
REGION=${AWS_REGION:-us-west-2}
IMAGE_NAME="qwen-image-backend"
TAG=${TAG:-latest}

# Get AWS account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPO="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/qwen-image-service"

echo "Building and pushing ${IMAGE_NAME} to ${ECR_REPO}:${TAG}"

# Login to ECR
aws ecr get-login-password --region ${REGION} | docker login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com

# Build image
docker build -t ${IMAGE_NAME}:${TAG} .

# Tag for ECR
docker tag ${IMAGE_NAME}:${TAG} ${ECR_REPO}:${TAG}

# Push to ECR
docker push ${ECR_REPO}:${TAG}

echo "Successfully pushed ${ECR_REPO}:${TAG}"
