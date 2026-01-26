from diffusers import StableDiffusionPipeline
import torch
from PIL import Image

pipe = None

def load_model():
    global pipe
    if pipe is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        torch_dtype = torch.float16 if device == "cuda" else torch.float32

   
        pipe = StableDiffusionPipeline.from_pretrained(
            "hakurei/waifu-diffusion",
            torch_dtype=torch_dtype
        )
        pipe = pipe.to(device)
    return pipe

def generate_prompt_from_data(aqi, pm25, co, temperature, humidity):
    prompt = ""
    if aqi <= 50:
        prompt += "serene, clean natural landscape, soft gradients, harmonious, calm, smooth lines"
    elif aqi <= 100:
        prompt += "slightly polluted cityscape, hazy atmosphere, subtle tension, muted colors, fragmented forms"
    else:
        prompt += "chaotic, heavily polluted urban scene, dark, turbulent textures, smoke, dramatic, unsettling"

    if temperature > 30:
        prompt += ", warm tones, heatwave"
    elif temperature < 10:
        prompt += ", cold tones, misty"

    if humidity > 80:
        prompt += ", misty, humid, cloudy atmosphere"
    elif humidity < 30:
        prompt += ", dry, dusty air"

    prompt += ", digital art, abstract, high detail, cinematic composition"
    return prompt

def generate_ai_art(aqi, pm25, co, temperature, humidity, width=512, height=512):
    """Generate AI artwork using Stable Diffusion"""
    pipe = load_model()  
    prompt = generate_prompt_from_data(aqi, pm25, co, temperature, humidity)
    image: Image.Image = pipe(prompt, width=width, height=height).images[0]
    return image, prompt
