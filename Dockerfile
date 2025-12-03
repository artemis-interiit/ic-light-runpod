# Use NVIDIA CUDA base image with Python
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

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
RUN pip3 install --no-cache-dir --upgrade pip setuptools wheel

# Copy requirements files
COPY requirements_runpod.txt .

# Install Python dependencies (includes PyTorch)
RUN pip3 install --no-cache-dir -r requirements_runpod.txt

# Install RunPod SDK
RUN pip3 install --no-cache-dir runpod

# Copy application code
COPY briarmbg.py .
COPY rp_handler.py .

# Create models directory
RUN mkdir -p /app/models

# Set the entrypoint
CMD ["python3", "rp_handler.py"]
