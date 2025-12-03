# IC-Light RunPod - GitHub Deployment Guide

## 🎯 GitHub से Direct RunPod Deployment

यह guide आपको बताएगी कि कैसे GitHub repository से directly RunPod पर deploy करें।

## 📋 Prerequisites

1. ✅ GitHub account
2. ✅ Docker Hub account
3. ✅ RunPod account with credits
4. ✅ Git installed on your system

## 🚀 Step-by-Step Deployment

### Step 1: GitHub Repository Setup

#### 1.1 Git Initialize करें (अगर पहले से नहीं है)

```bash
cd C:\Users\adhee\Downloads\IC-Light-main\IC-Light-main

# Git initialize करें
git init

# Files add करें
git add .

# First commit करें
git commit -m "Initial commit: IC-Light RunPod serverless deployment"
```

#### 1.2 GitHub पर Repository बनाएं

1. [github.com](https://github.com) पर जाएं
2. **New Repository** पर click करें
3. Repository details भरें:
   - **Name**: `ic-light-runpod`
   - **Description**: `IC-Light model for RunPod serverless deployment`
   - **Visibility**: Public या Private (आपकी choice)
4. **Create repository** पर click करें

#### 1.3 Local Repository को GitHub से Connect करें

```bash
# Remote add करें (अपना username डालें)
git remote add origin https://github.com/YOUR_USERNAME/ic-light-runpod.git

# Main branch set करें
git branch -M main

# Push करें
git push -u origin main
```

### Step 2: Docker Hub Secrets Setup

#### 2.1 Docker Hub Access Token बनाएं

1. [hub.docker.com](https://hub.docker.com) पर जाएं
2. **Account Settings** → **Security**
3. **New Access Token** पर click करें
4. Token name: `github-actions`
5. Access permissions: **Read, Write, Delete**
6. **Generate** पर click करें
7. Token को copy करके safe रखें (यह फिर नहीं दिखेगा!)

#### 2.2 GitHub Secrets Add करें

1. अपनी GitHub repository में जाएं
2. **Settings** → **Secrets and variables** → **Actions**
3. **New repository secret** पर click करें
4. दो secrets add करें:

**Secret 1:**
- Name: `DOCKERHUB_USERNAME`
- Value: आपका Docker Hub username

**Secret 2:**
- Name: `DOCKERHUB_TOKEN`
- Value: आपका Docker Hub access token (Step 2.1 में बनाया)

### Step 3: Automatic Build Enable करें

GitHub Actions workflow already setup है (`.github/workflows/docker-publish.yml`)

**यह automatically:**
- हर push पर Docker image build करेगा
- Docker Hub पर push करेगा
- Latest tag update करेगा

### Step 4: Manual Build Trigger करें (Optional)

अगर आप manually build trigger करना चाहें:

1. GitHub repository में जाएं
2. **Actions** tab पर click करें
3. **Build and Push Docker Image** workflow select करें
4. **Run workflow** पर click करें
5. Branch select करें (main)
6. **Run workflow** confirm करें

### Step 5: RunPod पर Deploy करें

#### 5.1 RunPod Console खोलें

1. [runpod.io/console/serverless](https://runpod.io/console/serverless) पर जाएं
2. Login करें

#### 5.2 New Endpoint बनाएं

**Option A: GitHub Integration (Recommended)**

1. **+ New Endpoint** पर click करें
2. **Template** section में:
   - **Source**: Select "GitHub"
   - **Repository**: अपनी repository select करें
   - **Branch**: `main`
   - **Dockerfile Path**: `./Dockerfile`

**Option B: Docker Hub Direct**

1. **+ New Endpoint** पर click करें
2. **Docker Image**: `your-dockerhub-username/ic-light-runpod:latest`

#### 5.3 Configuration Settings

```yaml
Endpoint Name: IC-Light-Relighting
Container Disk: 20 GB
GPU Type: RTX 3090 (या better)

Scaling:
  Active Workers: 0
  Max Workers: 3-5
  GPUs Per Worker: 1
  
Timeouts:
  Idle Timeout: 5 seconds
  Execution Timeout: 600 seconds
```

#### 5.4 Deploy करें

1. सभी settings verify करें
2. **Deploy** button पर click करें
3. Deployment complete होने का wait करें (2-5 minutes)

### Step 6: Endpoint Test करें

Deployment के बाद:

1. **Endpoint ID** और **API Key** note करें
2. Test request भेजें:

```python
import runpod
import base64
from PIL import Image
import io

# Setup
runpod.api_key = "YOUR_RUNPOD_API_KEY"
endpoint = runpod.Endpoint("YOUR_ENDPOINT_ID")

# Test image
with open("test.jpg", "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode()

# Request
result = endpoint.run({
    "input": {
        "foreground_image": img_b64,
        "prompt": "beautiful lighting",
        "steps": 20
    }
}).output()

# Save result
if result["status"] == "success":
    img_data = base64.b64decode(result["images"][0])
    Image.open(io.BytesIO(img_data)).save("output.png")
    print("Success! Saved output.png")
```

## 🔄 Update Workflow

जब भी आप code update करें:

```bash
# Changes करें
# Files add करें
git add .

# Commit करें
git commit -m "Updated handler logic"

# Push करें
git push origin main
```

**Automatic होगा:**
- GitHub Actions build trigger होगा
- नया Docker image बनेगा
- Docker Hub पर push होगा
- RunPod automatically नया image use करेगा (अगर GitHub integration है)

## 📊 Monitoring

### GitHub Actions Logs

1. Repository → **Actions** tab
2. Latest workflow run पर click करें
3. Build logs देखें

### RunPod Logs

1. RunPod Dashboard → Your Endpoint
2. **Logs** tab
3. Real-time execution logs देखें

## 🐛 Troubleshooting

### Problem: GitHub Actions Build Failed

**Check करें:**
- Docker Hub secrets सही हैं
- Dockerfile में कोई error नहीं है
- GitHub Actions logs में error message देखें

**Solution:**
```bash
# Locally test करें
docker build -t test-image .
```

### Problem: RunPod Deployment Failed

**Check करें:**
- Docker image successfully pushed हुआ
- Image name सही है
- Container disk size sufficient है (20 GB)

**Solution:**
- RunPod logs check करें
- Docker Hub पर image verify करें

### Problem: "Secrets not found"

**Solution:**
1. GitHub repository Settings में जाएं
2. Secrets verify करें
3. Correct names use करें:
   - `DOCKERHUB_USERNAME`
   - `DOCKERHUB_TOKEN`

## 💡 Best Practices

### 1. Branch Protection

```bash
# Development branch बनाएं
git checkout -b development

# Changes करें और test करें
# ...

# Merge to main
git checkout main
git merge development
git push origin main
```

### 2. Version Tags

```bash
# Version tag बनाएं
git tag -a v1.0.0 -m "First stable release"
git push origin v1.0.0
```

### 3. Environment Variables

RunPod endpoint में environment variables add करें:
- `MODEL_CACHE_DIR=/app/models`
- `LOG_LEVEL=INFO`

## 📈 Deployment Checklist

- [ ] Git repository initialized
- [ ] GitHub repository created
- [ ] Code pushed to GitHub
- [ ] Docker Hub account ready
- [ ] Docker Hub access token created
- [ ] GitHub secrets configured
- [ ] GitHub Actions workflow tested
- [ ] Docker image built successfully
- [ ] RunPod endpoint created
- [ ] Test request successful
- [ ] Logs verified
- [ ] Performance acceptable

## 🎯 Quick Commands Reference

```bash
# Repository setup
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/USERNAME/REPO.git
git push -u origin main

# Updates
git add .
git commit -m "Update message"
git push origin main

# Check status
git status
git log --oneline

# Branch management
git checkout -b new-feature
git checkout main
git merge new-feature
```

## 🔗 Useful Links

- **GitHub Actions Docs**: https://docs.github.com/actions
- **Docker Hub**: https://hub.docker.com
- **RunPod Serverless**: https://runpod.io/console/serverless
- **RunPod Docs**: https://docs.runpod.io

## 🎊 Success!

अगर सब कुछ सही हुआ तो:
- ✅ Code GitHub पर है
- ✅ Docker image automatically build होता है
- ✅ RunPod पर deployed है
- ✅ API working है

**Congratulations! आपका serverless deployment ready है! 🚀**

---

**Next Steps:**
1. Production में use करें
2. Monitoring setup करें
3. Cost optimize करें
4. Scale as needed

For detailed API usage, see `README_RUNPOD.md`
