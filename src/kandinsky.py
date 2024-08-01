import sys
sys.path.append('Kandinsky-3')

import torch
from kandinsky3 import get_T2I_pipeline
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import base64
from io import BytesIO
from PIL import Image
import uvicorn

import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import base64
import requests

device_map = torch.device('cuda:0')
dtype_map = {
    'unet': torch.float32,
    'text_encoder': torch.float16,
    'movq': torch.float32,
}

# Initialize the FastAPI app
app = FastAPI()

# Define the request model
class GenerateImageRequest(BaseModel):
    prompt: str
    width: Optional[int] = 1024
    height: Optional[int] = 1024

# Define the response model
class GenerateImageResponse(BaseModel):
    image_base64: str

# Define the endpoint
@app.post("/k31/", response_model=GenerateImageResponse)
async def generate_image(request: GenerateImageRequest):
    try:
        # Generate the image using the pipeline
        pil_image = t2i_pipe(request.prompt, width=request.width, height=request.height, steps=50)[0]

        # Resize the image if necessary
        if pil_image.size != (request.width, request.height):
            pil_image = pil_image.resize((request.width, request.height))
        
        # Convert the PIL image to base64
        buffered = BytesIO()
        pil_image.save(buffered, format="PNG")
        image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        # Return the response
        return GenerateImageResponse(image_base64=image_base64)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def api_k31_generate(prompt, width=1024, height=1024, url = "http://0.0.0.0:8188/k31/"):
    # Define the text message and image parameters
    data = {
        "prompt": prompt,
        "width": width,
        "height": height
    }
    
    # Send the POST request
    response = requests.post(url, json=data)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Extract the base64 encoded image from the response
        image_base64 = response.json()["image_base64"]
        
        # You can further process the image here, for example, decode it from base64
        decoded_image = Image.open(BytesIO(base64.b64decode(image_base64)))
        
        return decoded_image
    else:
        print("Error:", response.text)
        
# Run the FastAPI app
if __name__ == "__main__":
    t2i_pipe = get_T2I_pipeline(
        device_map, dtype_map,
    )
    uvicorn.run(app, host="0.0.0.0", port=8188)
