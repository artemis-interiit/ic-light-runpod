"""
Test script for IC-Light RunPod Handler
Run this locally to test the handler before deploying
"""

import base64
import json
from PIL import Image
import io
import numpy as np

def image_to_base64(image_path):
    """Convert image file to base64 string"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

def create_test_image(width=512, height=640):
    """Create a test image"""
    # Create a simple gradient image
    img = np.zeros((height, width, 3), dtype=np.uint8)
    for i in range(height):
        img[i, :, :] = [int(255 * i / height), 128, 255 - int(255 * i / height)]
    return Image.fromarray(img)

def save_base64_image(base64_string, output_path):
    """Save base64 string as image"""
    img_data = base64.b64decode(base64_string)
    img = Image.open(io.BytesIO(img_data))
    img.save(output_path)
    print(f"Saved: {output_path}")

def test_handler_locally():
    """Test the handler locally"""
    print("Testing IC-Light Handler Locally...")
    
    # Import handler
    from rp_handler import handler, initialize_models
    
    # Initialize models
    print("\nInitializing models...")
    initialize_models()
    print("Models initialized!")
    
    # Create test image
    print("\nCreating test image...")
    test_img = create_test_image()
    buffered = io.BytesIO()
    test_img.save(buffered, format="PNG")
    test_img_base64 = base64.b64encode(buffered.getvalue()).decode()
    
    # Create test event
    event = {
        "input": {
            "foreground_image": test_img_base64,
            "prompt": "beautiful woman, cinematic lighting",
            "bg_source": "grey",
            "image_width": 512,
            "image_height": 640,
            "num_samples": 1,
            "seed": 12345,
            "steps": 20,
            "cfg_scale": 7.0,
            "highres_scale": 1.5,
            "highres_denoise": 0.5
        }
    }
    
    print("\nProcessing request...")
    result = handler(event)
    
    print("\nResult:")
    print(json.dumps({k: v for k, v in result.items() if k != 'images'}, indent=2))
    
    if result["status"] == "success":
        print(f"\nGenerated {len(result['images'])} image(s)")
        for idx, img_base64 in enumerate(result["images"]):
            output_path = f"test_output_{idx}.png"
            save_base64_image(img_base64, output_path)
    else:
        print(f"\nError: {result.get('message', 'Unknown error')}")

def test_with_real_image(image_path):
    """Test with a real image"""
    print(f"Testing with real image: {image_path}")
    
    from rp_handler import handler, initialize_models
    
    # Initialize models
    print("\nInitializing models...")
    initialize_models()
    
    # Load image
    img_base64 = image_to_base64(image_path)
    
    # Create event
    event = {
        "input": {
            "foreground_image": img_base64,
            "prompt": "beautiful lighting, professional photography",
            "bg_source": "left",
            "image_width": 512,
            "image_height": 640,
            "num_samples": 1,
            "seed": 42,
            "steps": 25,
            "cfg_scale": 7.5
        }
    }
    
    print("\nProcessing...")
    result = handler(event)
    
    if result["status"] == "success":
        for idx, img_base64 in enumerate(result["images"]):
            save_base64_image(img_base64, f"real_output_{idx}.png")
    else:
        print(f"Error: {result.get('message')}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Test with provided image
        test_with_real_image(sys.argv[1])
    else:
        # Test with generated image
        test_handler_locally()
