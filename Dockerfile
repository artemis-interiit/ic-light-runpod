# Use NVIDIA CUDA base image with Python
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    git \
    wget \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN python3 -m pip install --upgrade pip

# Install PyTorch first (most critical dependency)
RUN pip3 install torch==2.1.0 torchvision==0.16.0 --index-url https://download.pytorch.org/whl/cu118

# Install core ML libraries
RUN pip3 install diffusers==0.27.2 transformers==4.36.2 accelerate==0.25.0

# Install additional dependencies
RUN pip3 install safetensors==0.4.1 huggingface-hub==0.20.0 peft==0.7.0

# Install image processing libraries
RUN pip3 install opencv-python-headless==4.8.1.78 pillow==10.2.0 einops==0.7.0

# Install utilities
RUN pip3 install numpy==1.26.0 scipy==1.11.0 protobuf==3.20.0

# Install RunPod SDK
RUN pip3 install runpod

# Copy application code
COPY briarmbg.py .
COPY rp_handler.py .

# Create models directory
RUN mkdir -p /app/models

# Set the entrypoint
CMD ["python3", "rp_handler.py"]
