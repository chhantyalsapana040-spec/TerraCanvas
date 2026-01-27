import urllib.request
import json
from PIL import Image
from io import BytesIO
from prompt_generator import generate_prompt_from_data

PIXAZO_API_KEY = "2ae421faca384fcaa93f5586fb5e3f1c"
PIXAZO_URL = "https://gateway.pixazo.ai/getImage/v1/getSDXLImage"


def generate_ai_art(aqi, pm25, co, temperature, humidity, width=512, height=512):
    prompt = generate_prompt_from_data(
        aqi=aqi,
        pm25=pm25,
        co=co,
        temperature=temperature,
        humidity=humidity
    )

    headers = {
        "Content-Type": "application/json",
        "Ocp-Apim-Subscription-Key": PIXAZO_API_KEY
    }

    body = {
        "prompt": prompt,
        "width": width,
        "height": height,
        "num_inference_steps": 25,
        "guidance_scale": 7.5
    }

    try:
        req = urllib.request.Request(
            PIXAZO_URL,
            headers=headers,
            data=json.dumps(body).encode("utf-8"),
            method="POST"
        )

        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode("utf-8"))

        image_url = result.get("imageUrl")
        if not image_url:
            raise Exception("No image URL returned")

        with urllib.request.urlopen(image_url) as img_resp:
            image = Image.open(BytesIO(img_resp.read())).convert("RGB")

        return image, prompt

    except Exception as e:
        print("Error generating image:", e)
        return None, prompt
