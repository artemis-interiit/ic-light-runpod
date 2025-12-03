# 🌟 IC-Light RunPod Serverless Deployment

Complete serverless deployment package for IC-Light image relighting model on RunPod.

[![Docker](https://img.shields.io/badge/Docker-Ready-blue)](https://hub.docker.com)
[![RunPod](https://img.shields.io/badge/RunPod-Serverless-purple)](https://runpod.io)
[![License](https://img.shields.io/badge/License-Apache%202.0-green)](LICENSE)

## 📖 Overview

यह repository IC-Light model को RunPod पर serverless deploy करने के लिए सभी जरूरी files और documentation प्रदान करती है।

**IC-Light** एक powerful image relighting model है जो foreground और background conditioning के साथ realistic lighting effects generate करता है।

## ✨ Features

- 🚀 **Serverless Architecture** - Pay only for compute time
- ⚡ **Fast Inference** - 5-15 seconds per image (warm)
- 💰 **Cost Effective** - ~$0.01-0.02 per request
- 🎨 **Multiple Lighting Options** - Grey, Left, Right, Top, Bottom, Custom
- 🔧 **Production Ready** - Complete error handling and logging
- 📊 **Auto Scaling** - Automatic worker management
- 🐳 **Docker Support** - Containerized deployment
- 🔄 **GitHub Actions** - Automated CI/CD pipeline

## 🎯 Quick Start

### Option 1: GitHub Deployment (Recommended)

```bash
# 1. Clone repository
git clone https://github.com/YOUR_USERNAME/ic-light-runpod.git
cd ic-light-runpod

# 2. Setup GitHub secrets (see GITHUB_DEPLOYMENT.md)
# 3. Push to trigger automatic build
git push origin main

# 4. Deploy on RunPod using GitHub integration
```

**📚 Detailed Guide:** [GITHUB_DEPLOYMENT.md](GITHUB_DEPLOYMENT.md)

### Option 2: Docker Hub Deployment

```bash
# 1. Build Docker image
docker build -t your-username/ic-light-runpod:latest .

# 2. Push to Docker Hub
docker push your-username/ic-light-runpod:latest

# 3. Deploy on RunPod using Docker image
```

**📚 Detailed Guide:** [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

## 📁 Repository Structure

```
ic-light-runpod/
├── rp_handler.py              # Main RunPod handler
├── Dockerfile                 # Container definition
├── requirements_runpod.txt    # Python dependencies
├── briarmbg.py               # Background removal model
├── .dockerignore             # Docker build exclusions
├── .github/
│   └── workflows/
│       └── docker-publish.yml # GitHub Actions workflow
├── docs/
│   ├── DEPLOYMENT_GUIDE.md   # Step-by-step deployment
│   ├── GITHUB_DEPLOYMENT.md  # GitHub integration guide
│   ├── README_RUNPOD.md      # API documentation
│   ├── QUICK_REFERENCE.md    # Quick commands
│   └── PACKAGE_SUMMARY.md    # Complete overview
├── test_handler.py           # Local testing script
├── example_client.py         # Client usage examples
└── build.sh                  # Build automation script
```

## 🚀 Deployment Options

### 1️⃣ GitHub + RunPod (Easiest)

✅ Automatic builds on push  
✅ No manual Docker commands  
✅ Version control integrated  
✅ CI/CD pipeline included  

**Guide:** [GITHUB_DEPLOYMENT.md](GITHUB_DEPLOYMENT.md)

### 2️⃣ Docker Hub + RunPod

✅ Manual control over builds  
✅ Custom image tags  
✅ Direct deployment  

**Guide:** [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

### 3️⃣ Local Testing First

✅ Test before deploying  
✅ Debug locally  
✅ Verify functionality  

**Script:** `python test_handler.py`

## 📊 Performance

| Metric | Value |
|--------|-------|
| Cold Start | 30-60 seconds |
| Warm Inference (512x640) | 5-15 seconds |
| GPU Memory Usage | 8-10 GB |
| Recommended GPU | RTX 3090 / RTX 4090 |
| Cost per Request (warm) | $0.01-0.02 |

## 💻 API Usage

### Python Client

```python
import runpod
import base64
from PIL import Image
import io

# Setup
runpod.api_key = "your-api-key"
endpoint = runpod.Endpoint("your-endpoint-id")

# Convert image to base64
with open("input.jpg", "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode()

# Make request
result = endpoint.run({
    "input": {
        "foreground_image": img_b64,
        "prompt": "beautiful woman, cinematic lighting",
        "bg_source": "grey",
        "image_width": 512,
        "image_height": 640,
        "steps": 20,
        "cfg_scale": 7.0
    }
}).output()

# Save result
if result["status"] == "success":
    img_data = base64.b64decode(result["images"][0])
    Image.open(io.BytesIO(img_data)).save("output.png")
```

**More Examples:** [example_client.py](example_client.py)

### cURL

```bash
curl -X POST https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "input": {
      "foreground_image": "BASE64_IMAGE",
      "prompt": "cinematic lighting",
      "steps": 20
    }
  }'
```

## 🎨 Lighting Options

| Option | Description | Use Case |
|--------|-------------|----------|
| `grey` | Uniform grey background | Neutral lighting |
| `left` | Light from left side | Dramatic side lighting |
| `right` | Light from right side | Opposite side lighting |
| `top` | Light from top | Studio overhead lighting |
| `bottom` | Light from bottom | Artistic bottom lighting |
| `upload` | Custom background | Full control |

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [GITHUB_DEPLOYMENT.md](GITHUB_DEPLOYMENT.md) | GitHub integration guide |
| [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) | Docker deployment guide |
| [README_RUNPOD.md](README_RUNPOD.md) | Complete API reference |
| [QUICK_REFERENCE.md](QUICK_REFERENCE.md) | Quick commands & settings |
| [PACKAGE_SUMMARY.md](PACKAGE_SUMMARY.md) | Complete package overview |

## 🔧 Configuration

### Recommended RunPod Settings

```yaml
Endpoint Configuration:
  GPU Type: RTX 3090 or RTX 4090
  Container Disk: 20 GB
  Active Workers: 0 (serverless)
  Max Workers: 3-5
  Idle Timeout: 5 seconds
  Execution Timeout: 600 seconds
```

### Environment Variables (Optional)

```bash
MODEL_CACHE_DIR=/app/models
LOG_LEVEL=INFO
CUDA_VISIBLE_DEVICES=0
```

## 🧪 Testing

### Local Testing

```bash
# Install dependencies
pip install -r requirements_runpod.txt

# Run test
python test_handler.py

# Test with custom image
python test_handler.py path/to/image.jpg
```

### Production Testing

```bash
# Use example client
python example_client.py
```

## 💰 Cost Estimation

**Approximate costs (RTX 3090):**

| Usage | Monthly Requests | Estimated Cost |
|-------|-----------------|----------------|
| Light | 100/day (3K/month) | $30-60 |
| Medium | 500/day (15K/month) | $150-300 |
| Heavy | 1000/day (30K/month) | $300-600 |

*Costs vary based on GPU type, image size, and processing time*

## 🐛 Troubleshooting

### Common Issues

**"Out of memory"**
- Solution: Use smaller image size or bigger GPU

**"Container failed to start"**
- Solution: Check Docker image name and increase container disk

**"Timeout error"**
- Solution: Increase execution timeout or reduce steps

**"Model download failed"**
- Solution: Increase container disk to 25 GB

**More help:** See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md#troubleshooting)

## 📈 Monitoring

### GitHub Actions

- View build status in **Actions** tab
- Check build logs for errors
- Monitor deployment success

### RunPod Dashboard

- Real-time execution logs
- Performance metrics
- Cost tracking
- Error monitoring

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **IC-Light** - Original model by [lllyasviel](https://github.com/lllyasviel/IC-Light)
- **RunPod** - Serverless GPU platform
- **Hugging Face** - Model hosting and diffusers library

## 🔗 Links

- **IC-Light GitHub**: https://github.com/lllyasviel/IC-Light
- **RunPod**: https://runpod.io
- **RunPod Docs**: https://docs.runpod.io
- **Docker Hub**: https://hub.docker.com

## 📞 Support

- **Issues**: Open an issue on GitHub
- **RunPod Discord**: https://discord.gg/runpod
- **Documentation**: See docs folder

## ⭐ Star History

If this repository helped you, please consider giving it a star! ⭐

---

**Made with ❤️ for the AI community**

**Deploy now and start relighting images! 🚀**
