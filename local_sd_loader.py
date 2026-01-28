import torch
from diffusers import StableDiffusionPipeline

MODEL_PATH = "/models/stable_diffusion_pytorch"  
pipe = None  # global cache

def load_model():
    global pipe
    if pipe is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        torch_dtype = torch.float16 if device == "cuda" else torch.float32

        pipe = StableDiffusionPipeline.from_pretrained(
            MODEL_PATH,
            torch_dtype=torch_dtype
        )
        pipe = pipe.to(device)
    return pipe
