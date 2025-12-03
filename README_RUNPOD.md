# IC-Light RunPod Serverless Deployment

यह repository IC-Light model को RunPod पर serverless deployment के लिए तैयार है।

## 📋 Files Overview

- **rp_handler.py** - RunPod handler function जो requests को process करता है
- **Dockerfile** - Docker container image definition
- **requirements_runpod.txt** - Python dependencies
- **briarmbg.py** - Background removal model
- **.dockerignore** - Docker build के लिए exclude files
- **build.sh** - Docker image build और push script

## 🚀 Deployment Steps

### 1. Docker Hub पर Image Push करें

```bash
# Docker Hub में login करें
docker login

# Image build करें (अपना Docker Hub username डालें)
docker build -t your-dockerhub-username/ic-light-runpod:latest .

# Image push करें
docker push your-dockerhub-username/ic-light-runpod:latest
```

या फिर build script use करें:

```bash
# Linux/Mac
chmod +x build.sh
DOCKER_USERNAME=your-dockerhub-username ./build.sh

# Windows (PowerShell)
$env:DOCKER_USERNAME="your-dockerhub-username"
docker build -t ${env:DOCKER_USERNAME}/ic-light-runpod:latest .
docker push ${env:DOCKER_USERNAME}/ic-light-runpod:latest
```

### 2. RunPod पर Serverless Endpoint बनाएं

1. [RunPod.io](https://runpod.io) पर जाएं और login करें
2. **Serverless** section में जाएं
3. **+ New Endpoint** पर click करें
4. Configuration:
   - **Endpoint Name**: IC-Light Relighting
   - **Docker Image**: `your-dockerhub-username/ic-light-runpod:latest`
   - **GPU Type**: RTX 3090 या better (recommended)
   - **Container Disk**: 20 GB minimum
   - **Active Workers**: 0 (serverless के लिए)
   - **Max Workers**: 3-5 (आपकी need के अनुसार)
   - **Idle Timeout**: 5 seconds
   - **Execution Timeout**: 600 seconds (10 minutes)

5. **Deploy** पर click करें

### 3. API का इस्तेमाल करें

Endpoint बन जाने के बाद, आपको एक API endpoint मिलेगा। इसे इस तरह use करें:

```python
import runpod
import base64
from PIL import Image
import io

# RunPod API key set करें
runpod.api_key = "your-runpod-api-key"

# Image को base64 में convert करें
def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

# Endpoint को call करें
endpoint = runpod.Endpoint("YOUR_ENDPOINT_ID")

# Request भेजें
request = {
    "input": {
        "foreground_image": image_to_base64("foreground.jpg"),
        "prompt": "beautiful woman, cinematic lighting",
        "bg_source": "grey",  # grey, left, right, top, bottom, upload
        "image_width": 512,
        "image_height": 640,
        "num_samples": 1,
        "seed": 12345,
        "steps": 20,
        "cfg_scale": 7.0,
        "highres_scale": 1.5,
        "highres_denoise": 0.5,
        "added_prompt": "best quality",
        "negative_prompt": "lowres, bad anatomy, bad hands, cropped, worst quality"
    }
}

# Run करें
run_request = endpoint.run(request)

# Result प्राप्त करें
result = run_request.output()

# Images को decode करें
if result["status"] == "success":
    for idx, img_base64 in enumerate(result["images"]):
        img_data = base64.b64decode(img_base64)
        img = Image.open(io.BytesIO(img_data))
        img.save(f"output_{idx}.png")
        print(f"Saved output_{idx}.png")
```

### 4. cURL से Test करें

```bash
curl -X POST https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "input": {
      "foreground_image": "BASE64_ENCODED_IMAGE",
      "prompt": "beautiful lighting",
      "bg_source": "grey",
      "image_width": 512,
      "image_height": 640,
      "steps": 20
    }
  }'
```

## 📝 Input Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `foreground_image` | string | required | Base64 encoded foreground image |
| `background_image` | string | optional | Base64 encoded background (if bg_source="upload") |
| `prompt` | string | required | Text prompt for relighting |
| `bg_source` | string | "grey" | Background source: grey, left, right, top, bottom, upload |
| `image_width` | int | 512 | Output image width (multiple of 64) |
| `image_height` | int | 640 | Output image height (multiple of 64) |
| `num_samples` | int | 1 | Number of images to generate |
| `seed` | int | 12345 | Random seed for reproducibility |
| `steps` | int | 20 | Number of inference steps |
| `cfg_scale` | float | 7.0 | Classifier-free guidance scale |
| `highres_scale` | float | 1.5 | Highres upscaling factor |
| `highres_denoise` | float | 0.5 | Highres denoising strength |
| `added_prompt` | string | "best quality" | Additional positive prompt |
| `negative_prompt` | string | "lowres..." | Negative prompt |

## 🎯 Background Sources

- **grey**: Uniform grey background
- **left**: Gradient from left (light to dark)
- **right**: Gradient from right (dark to light)
- **top**: Gradient from top (light to dark)
- **bottom**: Gradient from bottom (dark to light)
- **upload**: Use custom background image (provide `background_image`)

## 💡 Tips

1. **GPU Selection**: RTX 3090 या A4000 recommended है better performance के लिए
2. **Image Size**: 512x640 optimal है, बड़े sizes में ज्यादा time लगेगा
3. **Steps**: 20-30 steps usually sufficient हैं
4. **Cold Start**: पहली request में 30-60 seconds lag सकता है (model loading)
5. **Cost Optimization**: Idle timeout को कम रखें ताकि unnecessary charges न लगें

## 🔧 Troubleshooting

### Model Download Issues
अगर model download में problem हो तो Dockerfile में pre-download section को uncomment करें।

### Out of Memory
- Image size कम करें (256x320 या 384x512)
- `num_samples` को 1 रखें
- बड़ा GPU select करें

### Slow Performance
- `steps` को 15-20 तक कम करें
- `highres_scale` को 1.0 पर set करें
- xformers install करें (already in requirements)

## 📊 Expected Performance

- **Cold Start**: 30-60 seconds (first request)
- **Warm Inference**: 5-15 seconds per image (512x640, 20 steps)
- **GPU Memory**: ~8-10 GB (RTX 3090)

## 🔐 Security

- API keys को secure रखें
- Production में environment variables use करें
- Rate limiting implement करें अगर public API हो

## 📄 License

IC-Light model के original license के अनुसार।

## 🤝 Support

Issues के लिए GitHub repository पर issue create करें।
