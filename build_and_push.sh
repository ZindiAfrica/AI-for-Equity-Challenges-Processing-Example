#!/bin/bash

# Exit on error
set -e

# Configuration
REGION="us-east-2"
IMAGE_NAME="outsmarting-pipeline"
AWS_ACCOUNT_ID="869935100875"
ECR_REPO="comp-user-5ow9bw-workspace/${IMAGE_NAME}"
TAG="latest"

# Get ECR login token and login
echo "Logging into ECR..."
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

# Build the Docker image
echo "Building Docker image..."
docker build -t $IMAGE_NAME .

# Tag the image for ECR
echo "Tagging image for ECR..."
docker tag $IMAGE_NAME:latest $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$ECR_REPO:$TAG

# Push to ECR
echo "Pushing to ECR..."
docker push $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$ECR_REPO:$TAG

echo "Build and push completed successfully!"
