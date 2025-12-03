# Use NVIDIA CUDA base image with Python
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV TORCH_CUDA_ARCH_LIST="7.0 7.5 8.0 8.6+PTX"

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
RUN pip3 install --no-cache-dir --upgrade pip

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Install PyTorch with CUDA support
RUN pip3 install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install RunPod SDK
RUN pip3 install --no-cache-dir runpod

# Copy application code
COPY . .

# Create models directory
RUN mkdir -p /app/models

# Pre-download models (optional - comment out if you want to download on first run)
# RUN python3 -c "from transformers import CLIPTokenizer, CLIPTextModel; from diffusers import AutoencoderKL, UNet2DConditionModel; from briarmbg import BriaRMBG; \
#     CLIPTokenizer.from_pretrained('stablediffusionapi/realistic-vision-v51', subfolder='tokenizer'); \
#     CLIPTextModel.from_pretrained('stablediffusionapi/realistic-vision-v51', subfolder='text_encoder'); \
#     AutoencoderKL.from_pretrained('stablediffusionapi/realistic-vision-v51', subfolder='vae'); \
#     UNet2DConditionModel.from_pretrained('stablediffusionapi/realistic-vision-v51', subfolder='unet'); \
#     BriaRMBG.from_pretrained('briaai/RMBG-1.4')"

# Set the entrypoint
CMD ["python3", "rp_handler.py"]
