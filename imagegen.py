# animategen.py

import os
import base64
from io import BytesIO
import aiohttp

# Default A1111 API endpoint; adjust via environment variable if needed.
A1111_API_URL = os.getenv("A1111_API_URL", "http://127.0.0.1:7860/sdapi/v1/txt2img")

async def generate_animation_gif_async(prompt: str) -> bytes:
    """
    Asynchronously generates an animated GIF using the AnimateDiff extension via the A1111 API.
    
    Args:
        prompt (str): The text prompt for generating the animation.
    
    Returns:
        bytes: The generated GIF as raw bytes (decoded from base64).
    
    Raises:
        Exception: If the API call fails or no GIF is returned.
    """
    payload = {
        "prompt": f"{prompt}, <lora:AnimateLCM_sd15_t2v_lora:0.7>", # Get this LoRA from https://huggingface.co/wangfuyun/AnimateLCM/resolve/main/AnimateLCM_sd15_t2v_lora.safetensors
        "negative_prompt": "nsfw",
        "steps": 10,
        "sampler_index": "LCM",   # Adjust sampler if needed.
        "cfg_scale": 1.5,
        "seed": -1,
        "width": 448,
        "height": 512,
        "alwayson_scripts": {
            "AnimateDiff": {
                "args": [{
                    "model": "improvedHumansMotion_refinedHumanMovement.ckpt",  # Motion module weight.
                    "format": ["GIF"],             # Specify GIF format.
                    "enable": True,
                    "video_length": 16,            # Number of frames.
                    "fps": 8,                      # Frames per second.
                    "loop_number": 0,              # 0 means infinite looping.
                    "closed_loop": "A",            # Set to "A" for aggressive closed loop.
                    "batch_size": 16,              # Context batch size.
                    "stride": 1,                   # Motion stride.
                    "overlap": -1,                 # Use default overlap (batch_size // 4).
                    "interp": "Off",               # Frame interpolation off (or "FILM" if desired).
                    "interp_x": 10                 # Interpolation factor if enabled.
                }]
            }
        }
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(A1111_API_URL, json=payload, timeout=300) as response:
            response.raise_for_status()
            result = await response.json()
            # Expecting the base64-encoded GIF in the "images" key.
            if "images" in result and result["images"]:
                gif_b64 = result["images"][0]
                gif_bytes = base64.b64decode(gif_b64)
                return gif_bytes
            else:
                raise Exception("No GIF was returned from the API. Response keys: " + str(result.keys()))

# Example usage:
# gif_bytes = await generate_animation_gif_async("A vibrant dance scene in a futuristic city")
# with open("animation.gif", "wb") as f:
#     f.write(gif_bytes)
