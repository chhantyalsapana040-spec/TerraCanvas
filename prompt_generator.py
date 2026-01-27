import random

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
    "high": ["misty, humid, cloudy atmosphere", "foggy, damp environment"],
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

    style_desc = ", ".join(random.sample(ART_STYLE_VARIATIONS, 3))

    return f"{aqi_desc}, {temp_desc}, {humidity_desc}, {style_desc}"
