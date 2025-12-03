#!/bin/bash

# IC-Light RunPod Docker Build Script
# This script builds and pushes the Docker image to Docker Hub

set -e  # Exit on error

# Configuration
IMAGE_NAME="ic-light-runpod"
DOCKER_USERNAME="${DOCKER_USERNAME:-your-dockerhub-username}"
VERSION="${VERSION:-latest}"
FULL_IMAGE_NAME="${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION}"

echo "======================================"
echo "Building IC-Light RunPod Docker Image"
echo "======================================"
echo "Image: ${FULL_IMAGE_NAME}"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed!"
    exit 1
fi

# Build the Docker image
echo "Building Docker image..."
docker build -t ${FULL_IMAGE_NAME} .

echo ""
echo "Build completed successfully!"
echo ""

# Ask if user wants to push
read -p "Do you want to push to Docker Hub? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Logging in to Docker Hub..."
    docker login
    
    echo "Pushing image to Docker Hub..."
    docker push ${FULL_IMAGE_NAME}
    
    echo ""
    echo "======================================"
    echo "Image pushed successfully!"
    echo "======================================"
    echo "Image: ${FULL_IMAGE_NAME}"
    echo ""
    echo "You can now use this image in RunPod:"
    echo "1. Go to RunPod.io"
    echo "2. Create a new Serverless Endpoint"
    echo "3. Use this Docker image: ${FULL_IMAGE_NAME}"
    echo ""
fi

echo "Done!"
