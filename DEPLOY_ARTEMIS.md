# 🚀 Deployment Commands - artemis-interiit

## ✅ Git Setup Complete!

```
✓ Git initialized
✓ Files committed (79 files)
✓ Remote added: https://github.com/artemis-interiit/ic-light-runpod.git
✓ Branch renamed to main
```

---

## 📋 Next Steps

### Step 1: GitHub Repository बनाएं

**पहले GitHub पर repository बनाएं:**

1. इस link पर जाएं: https://github.com/new
2. Repository details भरें:
   ```
   Repository name: ic-light-runpod
   Description: IC-Light model for RunPod serverless deployment
   Visibility: Public ✓ (recommended)
   
   ⚠️ Important:
   - "Add a README file" को UNCHECK रखें
   - "Add .gitignore" को NONE रखें
   - "Choose a license" को NONE रखें
   ```
3. **Create repository** button click करें

---

### Step 2: Code Push करें

Repository बनने के बाद, यह command run करें:

```powershell
# Push to GitHub
git push -u origin main
```

**अगर authentication मांगे तो:**

#### Option A: Personal Access Token (Recommended)

1. GitHub पर जाएं: https://github.com/settings/tokens
2. **Generate new token** → **Generate new token (classic)**
3. Details भरें:
   ```
   Note: IC-Light RunPod Deployment
   Expiration: 90 days (या आपकी choice)
   Scopes: ✓ repo (सभी repo permissions)
   ```
4. **Generate token** click करें
5. Token को **copy करें** (यह फिर नहीं दिखेगा!)

6. Push command run करें:
   ```powershell
   git push -u origin main
   ```
   
7. जब credentials मांगे:
   ```
   Username: artemis-interiit
   Password: <paste your token here>
   ```

#### Option B: GitHub CLI (Alternative)

```powershell
# GitHub CLI install करें (if not installed)
winget install GitHub.cli

# Login करें
gh auth login

# Push करें
git push -u origin main
```

---

### Step 3: Verify GitHub Push

Push successful होने के बाद:

1. इस URL पर जाएं: https://github.com/artemis-interiit/ic-light-runpod
2. Check करें:
   - ✅ सभी files visible हैं
   - ✅ README files दिख रहे हैं
   - ✅ `.github/workflows` folder है
   - ✅ Total 79 files हैं

---

### Step 4: Docker Hub Setup (for GitHub Actions)

#### 4.1 Docker Hub Account

अगर नहीं है तो:
1. https://hub.docker.com पर signup करें
2. Email verify करें

#### 4.2 Access Token बनाएं

1. https://hub.docker.com पर login करें
2. **Account Settings** → **Security** → **Access Tokens**
3. **New Access Token** click करें
4. Details:
   ```
   Access Token Description: github-actions-ic-light
   Access permissions: Read, Write, Delete
   ```
5. **Generate** click करें
6. Token को **copy करके safe रखें**

#### 4.3 GitHub Secrets Add करें

1. Repository में जाएं: https://github.com/artemis-interiit/ic-light-runpod
2. **Settings** → **Secrets and variables** → **Actions**
3. **New repository secret** click करें

**Secret 1:**
```
Name: DOCKERHUB_USERNAME
Secret: <your-dockerhub-username>
```

**Secret 2:**
```
Name: DOCKERHUB_TOKEN
Secret: <paste token from step 4.2>
```

---

### Step 5: Trigger GitHub Actions Build

Secrets add करने के बाद:

#### Option A: Automatic (Push)

```powershell
# कोई भी small change करें
echo "# IC-Light RunPod" >> README_MAIN.md

# Commit और push करें
git add .
git commit -m "Trigger build"
git push origin main
```

#### Option B: Manual Trigger

1. Repository में जाएं: https://github.com/artemis-interiit/ic-light-runpod/actions
2. **Build and Push Docker Image** workflow select करें
3. **Run workflow** button click करें
4. Branch: `main` select करें
5. **Run workflow** confirm करें

---

### Step 6: Monitor Build

1. **Actions** tab में जाएं: https://github.com/artemis-interiit/ic-light-runpod/actions
2. Latest workflow run पर click करें
3. Build progress देखें (5-10 minutes लगेंगे)
4. ✅ Green checkmark का wait करें

---

### Step 7: RunPod Deployment

Build successful होने के बाद:

#### 7.1 RunPod Console खोलें

https://www.runpod.io/console/serverless

#### 7.2 New Endpoint बनाएं

**+ New Endpoint** click करें

**Configuration:**

```yaml
Endpoint Name: IC-Light-Relighting

Container Configuration:
  Container Image: <your-dockerhub-username>/ic-light-runpod:latest
  Container Disk: 20 GB
  
GPU Configuration:
  GPU Type: RTX 3090 (recommended)
  # या RTX 4090 (faster but expensive)
  
Scaling Configuration:
  Active Workers: 0
  Max Workers: 3
  GPUs Per Worker: 1
  
Timeout Configuration:
  Idle Timeout: 5 seconds
  Execution Timeout: 600 seconds
```

**Deploy** button click करें

---

### Step 8: Test Deployment

Deployment complete होने के बाद:

1. **Endpoint ID** copy करें
2. **API Key** copy करें (Settings में)

#### Test Script:

```python
import runpod
import base64
from PIL import Image
import io

# Configuration
runpod.api_key = "YOUR_RUNPOD_API_KEY"  # Replace
endpoint = runpod.Endpoint("YOUR_ENDPOINT_ID")  # Replace

# Load test image
with open("imgs/i1.webp", "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode()

# Send request
print("🚀 Sending request to RunPod...")
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

# Check result
if result["status"] == "success":
    print("✅ Success!")
    img_data = base64.b64decode(result["images"][0])
    img = Image.open(io.BytesIO(img_data))
    img.save("test_output.png")
    print("💾 Saved: test_output.png")
else:
    print(f"❌ Error: {result.get('message')}")
```

---

## 🎯 Quick Reference

### Your Repository
```
GitHub: https://github.com/artemis-interiit/ic-light-runpod
Actions: https://github.com/artemis-interiit/ic-light-runpod/actions
```

### Important Commands
```powershell
# Check status
git status

# Push changes
git add .
git commit -m "Update message"
git push origin main

# View remote
git remote -v
```

### Docker Hub
```
Image name: <your-dockerhub-username>/ic-light-runpod:latest
```

---

## ✅ Deployment Checklist

### GitHub Setup
- [ ] Repository created on GitHub
- [ ] Code pushed successfully
- [ ] All 79 files visible
- [ ] GitHub Actions workflow visible

### Docker Hub Setup
- [ ] Docker Hub account created
- [ ] Access token generated
- [ ] DOCKERHUB_USERNAME secret added
- [ ] DOCKERHUB_TOKEN secret added

### GitHub Actions
- [ ] Build triggered
- [ ] Build successful (green checkmark)
- [ ] Docker image pushed to Docker Hub

### RunPod Setup
- [ ] Endpoint created
- [ ] Configuration set correctly
- [ ] Deployment successful
- [ ] Status shows "Ready"

### Testing
- [ ] Endpoint ID copied
- [ ] API Key copied
- [ ] Test script run
- [ ] Output image generated
- [ ] No errors in logs

---

## 🆘 Troubleshooting

### "Authentication failed" when pushing
**Solution:** Use Personal Access Token instead of password
- Create token: https://github.com/settings/tokens
- Use token as password

### "GitHub Actions build failed"
**Solution:** Check secrets
- Verify DOCKERHUB_USERNAME is correct
- Verify DOCKERHUB_TOKEN is valid
- Check Actions logs for specific error

### "RunPod deployment failed"
**Solution:** 
- Verify Docker image exists on Docker Hub
- Check image name is correct
- Increase container disk to 25 GB
- Check RunPod logs

---

## 📞 Support

**Documentation:**
- `GITHUB_DEPLOYMENT.md` - Detailed guide
- `README_RUNPOD.md` - API documentation
- `QUICK_REFERENCE.md` - Quick commands

**Links:**
- RunPod Docs: https://docs.runpod.io
- RunPod Discord: https://discord.gg/runpod
- Docker Hub: https://hub.docker.com

---

## 🎊 Current Status

```
✅ Git initialized
✅ Files committed
✅ Remote configured: artemis-interiit/ic-light-runpod
✅ Branch set to main
⏳ Ready to push to GitHub
```

---

## 🚀 Next Action

**अब यह command run करें:**

```powershell
git push -u origin main
```

**पहले GitHub पर repository बना लें:** https://github.com/new

---

**Good luck! 🎉**
