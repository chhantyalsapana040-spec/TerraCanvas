import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFilter

def map_environment_to_visual(aqi, pm25, co, temperature, humidity):
    # Normalize values for visual mapping
    aqi_norm = min(aqi / 500, 1.0)
    pm25_norm = min(pm25 / 500, 1.0)
    co_norm = min(co / 10, 1.0)
    
    pollution = (aqi_norm + pm25_norm + co_norm) / 3
    darkness = pollution * 255
    noise_intensity = pollution * 255
    warmth = min(max((temperature - 20) / 20 * 255, 0), 255)
    smoothness = min(max(humidity / 100 * 10, 1), 10)
    return darkness, noise_intensity, smoothness, warmth

def generate_texture(width, height, darkness, noise_intensity, smoothness):
    # Base image
    img = np.zeros((height, width, 3), dtype=np.uint8)

    # Noise layer
    noise = np.random.randint(0, int(noise_intensity)+1, (height, width), dtype=np.uint8)
    img[:, :, 0] = np.clip(darkness + noise, 0, 255)
    img[:, :, 1] = np.clip(darkness + noise // 2, 0, 255)
    img[:, :, 2] = np.clip(darkness, 0, 255)

    # Blur for smoothness
    img = cv2.GaussianBlur(img, (int(smoothness)*2+1, int(smoothness)*2+1), 0)

    # Convert to PIL
    pil_img = Image.fromarray(img)

    # Add procedural shapes for AI-style effect
    draw = ImageDraw.Draw(pil_img)
    for _ in range(15):
        x0, y0 = np.random.randint(0, width), np.random.randint(0, height)
        x1, y1 = x0 + np.random.randint(20, 100), y0 + np.random.randint(20, 100)
        fill = (np.random.randint(0, 255), np.random.randint(0, 255), np.random.randint(0, 255), 100)
        draw.ellipse([x0, y0, x1, y1], fill=None, outline=fill)

    pil_img = pil_img.filter(ImageFilter.DETAIL)
    return pil_img

def compose_artwork(texture, warmth):
    # Adjust colors for warmth
    img = texture.convert("RGB")
    r, g, b = img.split()
    r = r.point(lambda i: min(i + warmth, 255))
    img = Image.merge("RGB", (r, g, b))
    return img
