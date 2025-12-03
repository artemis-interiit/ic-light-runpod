# IC-Light RunPod Deployment Guide (Step-by-Step)

## 🎯 Overview

यह guide आपको IC-Light model को RunPod पर serverless deploy करने में मदद करेगी।

## 📦 Prerequisites

1. **Docker Hub Account** - [hub.docker.com](https://hub.docker.com) पर account बनाएं
2. **RunPod Account** - [runpod.io](https://runpod.io) पर account बनाएं और credits add करें
3. **Docker Desktop** - अपने system पर Docker install करें

## 🔧 Step 1: Docker Image Build करें

### Windows (PowerShell)

```powershell
# Repository में जाएं
cd C:\Users\adhee\Downloads\IC-Light-main\IC-Light-main

# Docker Hub username set करें (अपना username डालें)
$env:DOCKER_USERNAME = "your-dockerhub-username"

# Image build करें
docker build -t ${env:DOCKER_USERNAME}/ic-light-runpod:latest -f Dockerfile .

# Docker Hub में login करें
docker login

# Image push करें
docker push ${env:DOCKER_USERNAME}/ic-light-runpod:latest
```

### Linux/Mac (Bash)

```bash
# Repository में जाएं
cd ~/Downloads/IC-Light-main/IC-Light-main

# Build script को executable बनाएं
chmod +x build.sh

# Build और push करें
DOCKER_USERNAME=your-dockerhub-username ./build.sh
```

## 🚀 Step 2: RunPod पर Endpoint बनाएं

### 2.1 RunPod Dashboard खोलें

1. [runpod.io](https://runpod.io) पर जाएं
2. Login करें
3. Left sidebar में **Serverless** पर click करें

### 2.2 New Endpoint Create करें

1. **+ New Endpoint** button पर click करें
2. निम्नलिखित details भरें:

**Basic Settings:**
- **Endpoint Name**: `IC-Light-Relighting`
- **Docker Image**: `your-dockerhub-username/ic-light-runpod:latest`
- **Container Disk**: `20 GB`

**GPU Settings:**
- **GPU Type**: Select करें:
  - RTX 3090 (Recommended - Good performance, cost-effective)
  - RTX 4090 (Best performance, expensive)
  - A4000 (Good balance)

**Scaling Settings:**
- **Active Workers**: `0` (serverless के लिए)
- **Max Workers**: `3` (या आपकी need के अनुसार)
- **GPUs Per Worker**: `1`
- **Idle Timeout**: `5` seconds
- **Execution Timeout**: `600` seconds (10 minutes)

**Advanced Settings (Optional):**
- **Environment Variables**: कोई नहीं (अभी के लिए)
- **Volume**: कोई नहीं

3. **Deploy** button पर click करें

### 2.3 Endpoint Details Note करें

Deployment के बाद आपको मिलेगा:
- **Endpoint ID**: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- **Endpoint URL**: `https://api.runpod.ai/v2/YOUR_ENDPOINT_ID`

इन्हें safe जगह save कर लें!

## 🧪 Step 3: API Test करें

### 3.1 RunPod API Key प्राप्त करें

1. RunPod Dashboard में **Settings** पर जाएं
2. **API Keys** section में जाएं
3. **+ Create API Key** पर click करें
4. Key को copy करके safe रखें

### 3.2 Python से Test करें

```python
import runpod
import base64
from PIL import Image
import io

# Configuration
runpod.api_key = "your-runpod-api-key"
endpoint = runpod.Endpoint("your-endpoint-id")

# Image को base64 में convert करें
def image_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# Request भेजें
request = {
    "input": {
        "foreground_image": image_to_base64("test_image.jpg"),
        "prompt": "beautiful woman, cinematic lighting",
        "bg_source": "grey",
        "image_width": 512,
        "image_height": 640,
        "steps": 20
    }
}

# Run करें
print("Sending request...")
run_request = endpoint.run(request)

# Result प्राप्त करें
print("Waiting for result...")
result = run_request.output()

# Image save करें
if result["status"] == "success":
    img_data = base64.b64decode(result["images"][0])
    img = Image.open(io.BytesIO(img_data))
    img.save("output.png")
    print("Saved: output.png")
else:
    print(f"Error: {result['message']}")
```

### 3.3 cURL से Test करें

```bash
# Test image को base64 में convert करें
BASE64_IMAGE=$(base64 -w 0 test_image.jpg)  # Linux/Mac
# या
# $BASE64_IMAGE = [Convert]::ToBase64String([IO.File]::ReadAllBytes("test_image.jpg"))  # Windows PowerShell

# API call करें
curl -X POST https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d "{
    \"input\": {
      \"foreground_image\": \"$BASE64_IMAGE\",
      \"prompt\": \"beautiful lighting\",
      \"bg_source\": \"grey\",
      \"image_width\": 512,
      \"image_height\": 640,
      \"steps\": 20
    }
  }"
```

## 📊 Step 4: Monitor और Optimize करें

### 4.1 Logs देखें

1. RunPod Dashboard में अपने endpoint पर जाएं
2. **Logs** tab पर click करें
3. Real-time logs देखें

### 4.2 Metrics देखें

- **Request Count**: कितने requests आए
- **Execution Time**: Average processing time
- **Error Rate**: कितने requests fail हुए
- **Cost**: Total cost

### 4.3 Optimization Tips

**Cost Reduce करने के लिए:**
- Idle timeout कम रखें (5 seconds)
- Max workers को limit करें
- Off-peak hours में test करें

**Performance Improve करने के लिए:**
- Better GPU select करें (RTX 4090)
- Steps को optimize करें (20-25)
- Image size को reasonable रखें (512x640)

## 🔍 Troubleshooting

### Problem: "Container failed to start"

**Solution:**
1. Docker image सही से push हुआ है check करें
2. Image name सही है verify करें
3. Container disk size बढ़ाएं (25 GB)

### Problem: "Out of memory"

**Solution:**
1. Bigger GPU select करें
2. Image size कम करें
3. `num_samples` को 1 रखें

### Problem: "Timeout error"

**Solution:**
1. Execution timeout बढ़ाएं (900 seconds)
2. Steps कम करें (15-20)
3. Highres scale कम करें (1.0-1.2)

### Problem: "Model download failed"

**Solution:**
1. Container disk size बढ़ाएं
2. Dockerfile में model pre-download enable करें
3. Network connectivity check करें

## 💰 Cost Estimation

**Approximate costs (RTX 3090):**
- Cold start: $0.02-0.03 per request
- Warm inference: $0.01-0.02 per request
- Idle time: $0.00 (with 5s timeout)

**Monthly estimate (100 requests/day):**
- ~3000 requests/month
- ~$30-60/month

## 🎓 Next Steps

1. **Production Setup:**
   - Environment variables add करें
   - Error handling improve करें
   - Rate limiting implement करें

2. **Integration:**
   - अपने application में integrate करें
   - Frontend UI बनाएं
   - Webhook setup करें

3. **Monitoring:**
   - Custom logging add करें
   - Performance metrics track करें
   - Alert setup करें

## 📚 Additional Resources

- [RunPod Documentation](https://docs.runpod.io)
- [Docker Documentation](https://docs.docker.com)
- [IC-Light GitHub](https://github.com/lllyasviel/IC-Light)

## 🆘 Support

Issues के लिए:
1. RunPod Discord join करें
2. GitHub पर issue create करें
3. Documentation check करें

---

**Happy Deploying! 🚀**
