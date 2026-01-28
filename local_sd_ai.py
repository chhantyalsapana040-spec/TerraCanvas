import sys
import os
import random
import numpy as np
from PIL import Image


sys.path.append(os.path.join(os.path.dirname(__file__), "models"))

# Import local SD repo modules
from stable_diffusion_pytorch import pipeline, model_loader

# Prompt generator inside same module
AQI_DESCRIPTIONS = {
    "good": [
        "serene, clean natural landscape",
        "peaceful, lush greenery, soft gradients",
        "tranquil environment, calm, harmonious"
    ],
    "moderate": [
        "slightly polluted cityscape, hazy atmosphere",
        "urban scene with subtle smog, muted colors",
        "tense city skyline, fragmented forms, soft haze"
    ],
    "poor": [
        "chaotic, heavily polluted urban scene",
        "dark, turbulent textures, smoke-filled skyline",
        "dramatic, unsettling industrial city, hazy atmosphere"
    ]
}

TEMPERATURE_DESCRIPTIONS = {
    "hot": ["warm tones, heatwave", "scorching sun, vibrant reds", "sweltering, golden light"],
    "cold": ["cold tones, misty", "frosty, icy environment", "chilly, pale blue atmosphere"],
    "mild": ["pleasant temperature, soft light", "neutral tones, comfortable weather"]
}

HUMIDITY_DESCRIPTIONS = {
    "high": ["misty, humid, cloudy atmosphere", "foggy, damp environment", "dense humidity, soft haze"],
    "low": ["dry, dusty air", "arid landscape"],
    "moderate": ["balanced humidity, clear air"]
}

ART_STYLE_VARIATIONS = [
    "digital art",
    "abstract",
    "cinematic composition",
    "oil painting",
    "watercolor style",
    "fantasy art",
    "concept art"
]


def generate_prompt_from_data(aqi, pm25, co, temperature, humidity):
    # AQI
    if aqi <= 50:
        aqi_desc = random.choice(AQI_DESCRIPTIONS["good"])
    elif aqi <= 100:
        aqi_desc = random.choice(AQI_DESCRIPTIONS["moderate"])
    else:
        aqi_desc = random.choice(AQI_DESCRIPTIONS["poor"])

    # Temperature
    if temperature > 30:
        temp_desc = random.choice(TEMPERATURE_DESCRIPTIONS["hot"])
    elif temperature < 10:
        temp_desc = random.choice(TEMPERATURE_DESCRIPTIONS["cold"])
    else:
        temp_desc = random.choice(TEMPERATURE_DESCRIPTIONS["mild"])

    # Humidity
    if humidity > 80:
        humidity_desc = random.choice(HUMIDITY_DESCRIPTIONS["high"])
    elif humidity < 30:
        humidity_desc = random.choice(HUMIDITY_DESCRIPTIONS["low"])
    else:
        humidity_desc = random.choice(HUMIDITY_DESCRIPTIONS["moderate"])

    # Random style
    style_desc = ", ".join(random.sample(ART_STYLE_VARIATIONS, 3))

    return f"{aqi_desc}, {temp_desc}, {humidity_desc}, {style_desc}"


# Global cache
MODELS = None

def load_models(device="cpu"):
    global MODELS
    if MODELS is None:
        MODELS = model_loader.preload_models(device)
    return MODELS


def generate_ai_art(
    aqi, pm25, co, temperature, humidity,
    width=512, height=512,
    device="cuda",   
    sampler="k_lms",
    n_inference_steps=20,
    cfg_scale=7.5,
    strength=0.8,
    do_cfg=True,
    seed=None
):
    models = load_models(device)

    prompt = generate_prompt_from_data(aqi, pm25, co, temperature, humidity)

    image = pipeline.generate(
        prompts=[prompt],
        uncond_prompts=[""],
        input_images=[],
        strength=strength,
        do_cfg=do_cfg,
        cfg_scale=cfg_scale,
        height=height,
        width=width,
        sampler=sampler,
        n_inference_steps=n_inference_steps,
        seed=seed,
        models=models,
        device=device,
        idle_device="cpu"
    )[0]

    return image, prompt