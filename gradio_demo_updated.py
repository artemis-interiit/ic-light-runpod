FROM python:3.10-slim

WORKDIR /app

# Dependencies install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code copy
COPY . .

# Run handler
CMD ["python", "rp_handler.py"]
```

**3. requirements.txt banao:**
```
runpod
# Aapke model ki requirements yahan add karo
# torch
# transformers
# etc.