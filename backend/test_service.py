import requests
import base64
import json
from PIL import Image
from io import BytesIO

def test_health():
    """Test health endpoint"""
    response = requests.get("http://localhost:8000/health")
    print(f"Health check: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_generation():
    """Test image generation endpoint with proper Qwen-Image parameters"""
    payload = {
        "prompt": "A beautiful sunset over mountains",
        "num_inference_steps": 20,
        "width": 1328,
        "height": 1328,
        "true_cfg_scale": 4.0
    }
    
    response = requests.post("http://localhost:8000/generate", json=payload, timeout=180)
    print(f"Generation test: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        # Decode and save the image
        img_data = base64.b64decode(data["image_base64"])
        img = Image.open(BytesIO(img_data))
        img.save("test_output.png")
        print("Image saved as test_output.png")
        return True
    else:
        print(f"Error: {response.text}")
        return False

if __name__ == "__main__":
    print("Testing Qwen-Image service...")
    
    if test_health():
        print("✓ Health check passed")
        if test_generation():
            print("✓ Image generation test passed")
        else:
            print("✗ Image generation test failed")
    else:
        print("✗ Health check failed")
