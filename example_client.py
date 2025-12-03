"""
Example client code for calling IC-Light RunPod Serverless API
"""

import runpod
import base64
import json
from PIL import Image
import io
import time

class ICLightClient:
    def __init__(self, api_key, endpoint_id):
        """
        Initialize IC-Light client
        
        Args:
            api_key: Your RunPod API key
            endpoint_id: Your RunPod endpoint ID
        """
        runpod.api_key = api_key
        self.endpoint = runpod.Endpoint(endpoint_id)
    
    @staticmethod
    def image_to_base64(image_path):
        """Convert image file to base64 string"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    
    @staticmethod
    def pil_to_base64(pil_image):
        """Convert PIL Image to base64 string"""
        buffered = io.BytesIO()
        pil_image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()
    
    @staticmethod
    def base64_to_pil(base64_string):
        """Convert base64 string to PIL Image"""
        img_data = base64.b64decode(base64_string)
        return Image.open(io.BytesIO(img_data))
    
    def relight(self, 
                foreground_image,
                prompt,
                background_image=None,
                bg_source="grey",
                image_width=512,
                image_height=640,
                num_samples=1,
                seed=12345,
                steps=20,
                cfg_scale=7.0,
                highres_scale=1.5,
                highres_denoise=0.5,
                added_prompt="best quality",
                negative_prompt="lowres, bad anatomy, bad hands, cropped, worst quality",
                wait_for_result=True):
        """
        Relight an image using IC-Light
        
        Args:
            foreground_image: Path to foreground image or PIL Image
            prompt: Text prompt for relighting
            background_image: Optional background image path or PIL Image
            bg_source: Background source (grey, left, right, top, bottom, upload)
            image_width: Output width
            image_height: Output height
            num_samples: Number of images to generate
            seed: Random seed
            steps: Number of inference steps
            cfg_scale: Classifier-free guidance scale
            highres_scale: Highres upscaling factor
            highres_denoise: Highres denoising strength
            added_prompt: Additional positive prompt
            negative_prompt: Negative prompt
            wait_for_result: Wait for result or return job ID
        
        Returns:
            List of PIL Images if wait_for_result=True, else job ID
        """
        # Convert images to base64
        if isinstance(foreground_image, str):
            fg_base64 = self.image_to_base64(foreground_image)
        elif isinstance(foreground_image, Image.Image):
            fg_base64 = self.pil_to_base64(foreground_image)
        else:
            raise ValueError("foreground_image must be file path or PIL Image")
        
        # Prepare request
        request_data = {
            "input": {
                "foreground_image": fg_base64,
                "prompt": prompt,
                "bg_source": bg_source,
                "image_width": image_width,
                "image_height": image_height,
                "num_samples": num_samples,
                "seed": seed,
                "steps": steps,
                "cfg_scale": cfg_scale,
                "highres_scale": highres_scale,
                "highres_denoise": highres_denoise,
                "added_prompt": added_prompt,
                "negative_prompt": negative_prompt
            }
        }
        
        # Add background if provided
        if bg_source == "upload" and background_image is not None:
            if isinstance(background_image, str):
                bg_base64 = self.image_to_base64(background_image)
            elif isinstance(background_image, Image.Image):
                bg_base64 = self.pil_to_base64(background_image)
            else:
                raise ValueError("background_image must be file path or PIL Image")
            request_data["input"]["background_image"] = bg_base64
        
        # Run request
        print("Sending request to RunPod...")
        run_request = self.endpoint.run(request_data)
        
        if not wait_for_result:
            return run_request.job_id
        
        # Wait for result
        print("Waiting for result...")
        start_time = time.time()
        
        while True:
            status = run_request.status()
            
            if status == "COMPLETED":
                result = run_request.output()
                elapsed = time.time() - start_time
                print(f"Completed in {elapsed:.2f} seconds")
                
                if result["status"] == "success":
                    images = [self.base64_to_pil(img) for img in result["images"]]
                    return images
                else:
                    raise Exception(f"Error: {result.get('message', 'Unknown error')}")
            
            elif status in ["FAILED", "CANCELLED"]:
                raise Exception(f"Job {status}")
            
            time.sleep(1)
    
    def get_result(self, job_id):
        """Get result for a previously submitted job"""
        run_request = self.endpoint.run_request(job_id)
        result = run_request.output()
        
        if result["status"] == "success":
            return [self.base64_to_pil(img) for img in result["images"]]
        else:
            raise Exception(f"Error: {result.get('message', 'Unknown error')}")


# Example usage
if __name__ == "__main__":
    # Configuration
    API_KEY = "your-runpod-api-key"
    ENDPOINT_ID = "your-endpoint-id"
    
    # Initialize client
    client = ICLightClient(API_KEY, ENDPOINT_ID)
    
    # Example 1: Simple relighting with grey background
    print("\n=== Example 1: Grey Background ===")
    images = client.relight(
        foreground_image="input.jpg",
        prompt="beautiful woman, cinematic lighting",
        bg_source="grey"
    )
    images[0].save("output_grey.png")
    print("Saved: output_grey.png")
    
    # Example 2: Left lighting
    print("\n=== Example 2: Left Lighting ===")
    images = client.relight(
        foreground_image="input.jpg",
        prompt="professional portrait, studio lighting",
        bg_source="left",
        steps=25,
        cfg_scale=7.5
    )
    images[0].save("output_left.png")
    print("Saved: output_left.png")
    
    # Example 3: Custom background
    print("\n=== Example 3: Custom Background ===")
    images = client.relight(
        foreground_image="person.jpg",
        background_image="background.jpg",
        prompt="person in beautiful environment",
        bg_source="upload",
        image_width=768,
        image_height=768
    )
    images[0].save("output_custom.png")
    print("Saved: output_custom.png")
    
    # Example 4: Multiple samples
    print("\n=== Example 4: Multiple Samples ===")
    images = client.relight(
        foreground_image="input.jpg",
        prompt="artistic portrait, dramatic lighting",
        bg_source="right",
        num_samples=3,
        seed=42
    )
    for idx, img in enumerate(images):
        img.save(f"output_sample_{idx}.png")
        print(f"Saved: output_sample_{idx}.png")
    
    # Example 5: Async (non-blocking)
    print("\n=== Example 5: Async Request ===")
    job_id = client.relight(
        foreground_image="input.jpg",
        prompt="beautiful lighting",
        wait_for_result=False
    )
    print(f"Job submitted: {job_id}")
    
    # Do other work...
    time.sleep(10)
    
    # Get result later
    images = client.get_result(job_id)
    images[0].save("output_async.png")
    print("Saved: output_async.png")
