# imagegen.py

import os
import base64
from io import BytesIO
from PIL import Image
import aiohttp

# Default A1111 API endpoint; adjust via environment variable if needed.
A1111_API_URL = os.getenv("A1111_API_URL", "http://127.0.0.1:7860/sdapi/v1/txt2img")

async def generate_image_async(prompt: str) -> Image.Image:
    """
    Asynchronously generates an image using the Automatic1111 Stable Diffusion webUI API.

    Args:
        prompt (str): The text prompt for generating the image.

    Returns:
        Image.Image: A PIL Image object of the generated image.

    Raises:
        Exception: If the API call fails or no image is returned.
    """
    # Build the payload with some default parameters.
    payload = {
        "prompt": f"{prompt}, <lora:LCM_LoRA_Weights_SD15:1>",
        "negative_prompt": "nsfw",  # You can adjust this or add more negatives.
        "steps": 10,
        "sampler_index": "LCM",  # Adjust to your preferred sampler if needed.
        "cfg_scale": 1,
        "seed": -1,
        "width": 368,
        "height": 512,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(A1111_API_URL, json=payload, timeout=120) as response:
            response.raise_for_status()
            result = await response.json()

            # The API typically returns a list of base64-encoded images in the "images" key.
            if "images" in result and result["images"]:
                # Decode the first image in the list.
                image_b64 = result["images"][0]
                image_bytes = base64.b64decode(image_b64)
                image = Image.open(BytesIO(image_bytes))
                return image
            else:
                raise Exception("No image was returned from the API.")
