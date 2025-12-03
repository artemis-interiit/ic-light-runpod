# IC-Light RunPod Quick Reference

## 🚀 Quick Start Commands

### Docker Build & Push
```bash
# Windows PowerShell
$env:DOCKER_USERNAME="your-username"
docker build -t ${env:DOCKER_USERNAME}/ic-light-runpod:latest .
docker push ${env:DOCKER_USERNAME}/ic-light-runpod:latest

# Linux/Mac
export DOCKER_USERNAME="your-username"
docker build -t $DOCKER_USERNAME/ic-light-runpod:latest .
docker push $DOCKER_USERNAME/ic-light-runpod:latest
```

## 📝 API Request Format

### Minimal Request
```json
{
  "input": {
    "foreground_image": "BASE64_STRING",
    "prompt": "beautiful lighting"
  }
}
```

### Full Request
```json
{
  "input": {
    "foreground_image": "BASE64_STRING",
    "background_image": "BASE64_STRING",
    "prompt": "beautiful woman, cinematic lighting",
    "bg_source": "grey",
    "image_width": 512,
    "image_height": 640,
    "num_samples": 1,
    "seed": 12345,
    "steps": 20,
    "cfg_scale": 7.0,
    "highres_scale": 1.5,
    "highres_denoise": 0.5,
    "added_prompt": "best quality",
    "negative_prompt": "lowres, bad anatomy"
  }
}
```

## 🎨 Background Sources

| Value | Description |
|-------|-------------|
| `grey` | Uniform grey background |
| `left` | Light from left side |
| `right` | Light from right side |
| `top` | Light from top |
| `bottom` | Light from bottom |
| `upload` | Custom background (requires `background_image`) |

## 🐍 Python Quick Code

```python
import runpod
import base64
from PIL import Image
import io

# Setup
runpod.api_key = "YOUR_API_KEY"
endpoint = runpod.Endpoint("YOUR_ENDPOINT_ID")

# Convert image
with open("input.jpg", "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode()

# Request
result = endpoint.run({
    "input": {
        "foreground_image": img_b64,
        "prompt": "cinematic lighting",
        "steps": 20
    }
}).output()

# Save result
if result["status"] == "success":
    img_data = base64.b64decode(result["images"][0])
    Image.open(io.BytesIO(img_data)).save("output.png")
```

## ⚙️ Recommended Settings

### Fast (5-10 seconds)
```json
{
  "image_width": 512,
  "image_height": 512,
  "steps": 15,
  "highres_scale": 1.0
}
```

### Balanced (10-15 seconds)
```json
{
  "image_width": 512,
  "image_height": 640,
  "steps": 20,
  "highres_scale": 1.5
}
```

### Quality (20-30 seconds)
```json
{
  "image_width": 768,
  "image_height": 768,
  "steps": 30,
  "highres_scale": 1.5
}
```

## 🔧 RunPod Endpoint Settings

| Setting | Recommended Value |
|---------|------------------|
| GPU Type | RTX 3090 / RTX 4090 |
| Container Disk | 20 GB |
| Active Workers | 0 |
| Max Workers | 3-5 |
| Idle Timeout | 5 seconds |
| Execution Timeout | 600 seconds |

## 📊 Performance Metrics

| GPU | Cold Start | Warm Inference (512x640, 20 steps) |
|-----|------------|-------------------------------------|
| RTX 3090 | 30-45s | 8-12s |
| RTX 4090 | 25-35s | 5-8s |
| A4000 | 35-50s | 10-15s |

## 💰 Cost Estimates (per request)

| GPU | Cold Start | Warm |
|-----|------------|------|
| RTX 3090 | $0.02-0.03 | $0.01-0.02 |
| RTX 4090 | $0.04-0.05 | $0.02-0.03 |

## 🐛 Common Errors

| Error | Solution |
|-------|----------|
| "Out of memory" | Reduce image size or use bigger GPU |
| "Timeout" | Increase execution timeout or reduce steps |
| "Container failed" | Check Docker image name and disk size |
| "Model download failed" | Increase container disk to 25 GB |

## 📞 Support Links

- RunPod Docs: https://docs.runpod.io
- RunPod Discord: https://discord.gg/runpod
- IC-Light GitHub: https://github.com/lllyasviel/IC-Light

## 📁 Repository Files

| File | Purpose |
|------|---------|
| `rp_handler.py` | Main handler function |
| `Dockerfile` | Container definition |
| `requirements_runpod.txt` | Python dependencies |
| `briarmbg.py` | Background removal model |
| `test_handler.py` | Local testing script |
| `example_client.py` | Client usage examples |
| `DEPLOYMENT_GUIDE.md` | Full deployment guide |
| `README_RUNPOD.md` | Complete documentation |

## 🎯 Testing Checklist

- [ ] Docker image builds successfully
- [ ] Image pushed to Docker Hub
- [ ] RunPod endpoint created
- [ ] API key configured
- [ ] Test request successful
- [ ] Output image generated
- [ ] Logs show no errors
- [ ] Performance acceptable
- [ ] Cost within budget

---

**Quick Help:** For detailed instructions, see `DEPLOYMENT_GUIDE.md`
