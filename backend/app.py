from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from diffusers import DiffusionPipeline
import torch
import base64
from io import BytesIO
import logging
import os
import random
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GenerationRequest(BaseModel):
    prompt: str
    negative_prompt: str = " "
    num_inference_steps: int = 50
    width: int = 1328
    height: int = 1328
    true_cfg_scale: float = 4.0
    seed: int = -1  # -1 means random seed

class GenerationResponse(BaseModel):
    image_base64: str
    seed_used: int

# Global model variable
pipeline = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global pipeline
    try:
        logger.info("Loading Qwen-Image model...")
        
        # Check available GPUs
        gpu_count = torch.cuda.device_count()
        logger.info(f"Found {gpu_count} GPUs")
        
        # Set memory management
        os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
        
        if gpu_count > 1:
            device_map = "balanced"
            torch_dtype = torch.bfloat16
        else:
            device_map = "cuda:0"
            torch_dtype = torch.bfloat16
        
        pipeline = DiffusionPipeline.from_pretrained(
            "Qwen/Qwen-Image",
            torch_dtype=torch_dtype,
            trust_remote_code=True,
            device_map=device_map
        )
        
        logger.info(f"Model loaded across {gpu_count} GPU(s)")
            
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise
    
    yield
    
    # Shutdown (cleanup if needed)
    logger.info("Shutting down...")

app = FastAPI(title="Qwen-Image Generation Service", lifespan=lifespan)

@app.post("/generate", response_model=GenerationResponse)
async def generate_image(request: GenerationRequest):
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Handle seed generation
        if request.seed == -1:
            # Generate random seed
            import random
            seed_used = random.randint(0, 2147483647)
        else:
            seed_used = request.seed
        
        logger.info(f"Generating image with seed: {seed_used}")
        logger.info(f"Prompt: {request.prompt[:100]}...")
        logger.info(f"Negative prompt: {request.negative_prompt[:50]}...")
        
        # Create generator with seed
        generator = torch.Generator(device="cuda").manual_seed(seed_used)
        
        # Generate image using proper Qwen-Image parameters
        with torch.no_grad():
            result = pipeline(
                prompt=request.prompt,
                negative_prompt=request.negative_prompt,
                width=request.width,
                height=request.height,
                num_inference_steps=request.num_inference_steps,
                true_cfg_scale=request.true_cfg_scale,
                generator=generator
            )
        
        image = result.images[0]
        
        # Convert to base64
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        logger.info(f"Image generated successfully with seed: {seed_used}")
        
        return GenerationResponse(image_base64=img_base64, seed_used=seed_used)
    
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    gpu_info = {
        "gpu_count": torch.cuda.device_count(),
        "gpu_available": torch.cuda.is_available(),
        "gpu_memory": [f"{torch.cuda.get_device_properties(i).total_memory / 1e9:.1f}GB" 
                      for i in range(torch.cuda.device_count())]
    }
    return {
        "status": "healthy", 
        "model_loaded": pipeline is not None,
        "model_name": "Qwen/Qwen-Image",
        "gpu_info": gpu_info
    }

@app.get("/model-info")
async def get_model_info():
    """Get information about the loaded model and supported parameters"""
    return {
        "model_name": "Qwen/Qwen-Image",
        "model_type": "Text-to-Image Diffusion Model",
        "capabilities": [
            "High-quality image generation",
            "Complex text rendering (English & Chinese)",
            "Multiple aspect ratios",
            "Precise image editing",
            "Style transfer"
        ],
        "supported_parameters": {
            "prompt": "Text description of the image to generate",
            "negative_prompt": "Text description of what to avoid in the image",
            "num_inference_steps": "Number of denoising steps (10-100, default: 50)",
            "width": "Image width in pixels",
            "height": "Image height in pixels", 
            "true_cfg_scale": "Classifier-free guidance scale (1.0-10.0, default: 4.0)",
            "seed": "Random seed for reproducible results (-1 for random)"
        },
        "recommended_aspect_ratios": {
            "1:1": [1328, 1328],
            "16:9": [1664, 928],
            "9:16": [928, 1664],
            "4:3": [1472, 1140],
            "3:4": [1140, 1472],
            "3:2": [1584, 1056],
            "2:3": [1056, 1584]
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
