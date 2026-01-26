import streamlit as st
import pandas as pd
import pydeck as pdk
from PIL import Image
import urllib.request
import json
from io import BytesIO
import requests

st.set_page_config(layout="wide")
st.title("TerraCanvas: AI Environmental Art Generator")


# 1. Load dataset
df = pd.read_csv("environment_data_with_coords.csv")

# Rename columns for convenience
df = df.rename(columns={
    'PM2.5 (µg/m³)': 'PM25',
    'PM10 (µg/m³)': 'PM10',
    'NO2 (ppb)': 'NO2',
    'SO2 (ppb)': 'SO2',
    'CO (ppm)': 'CO',
    'O3 (ppb)': 'O3',
    'Temperature (°C)': 'Temperature',
    'Humidity (%)': 'Humidity',
    'Wind Speed (m/s)': 'Wind'
})


# 2. Severity color
def severity_color(aqi):
    if aqi <= 50:
        return [0, 255, 0]
    elif aqi <= 100:
        return [255, 255, 0]
    else:
        return [255, 0, 0]

df['Color'] = df['AQI'].apply(severity_color)


# 3. World map
latest_df = df.sort_values('Date').drop_duplicates(subset=['City'], keep='last')
st.subheader("World Map of Pollution Severity")
layer = pdk.Layer(
    "ScatterplotLayer",
    data=latest_df,
    get_position='[Longitude, Latitude]',
    get_fill_color='Color',
    get_radius=200000,
    pickable=True
)
view_state = pdk.ViewState(latitude=0, longitude=0, zoom=1)
r = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={"text": "{City}\nLatest AQI: {AQI}\nPM2.5: {PM25}\nCO: {CO}\nDate: {Date}"}
)
st.pydeck_chart(r)


# 4. AI Art Functions
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
    """
    Uses Pixazo SDXL API to generate AI art.
    Returns PIL.Image and the prompt used.
    """
    url = "https://gateway.pixazo.ai/getImage/v1/getSDXLImage"
    api_key = "eb9d028bb1884df882ec9aae5075b5ae"

    prompt = generate_prompt_from_data(aqi, pm25, co, temperature, humidity)

    headers = {
        'Content-Type': 'application/json',
        'Ocp-Apim-Subscription-Key': api_key
    }

    body = {
        "prompt": prompt,
        "width": width,
        "height": height,
        "num_inference_steps": 25,
        "guidance_scale": 7.5,
        "seed": None
    }

    try:
        # Send POST request
        req = urllib.request.Request(url, headers=headers, data=json.dumps(body).encode("utf-8"), method="POST")
        response = urllib.request.urlopen(req)
        result_json = json.loads(response.read().decode("utf-8"))

        image_url = result_json.get("imageUrl")
        if not image_url:
            st.error("API returned no image URL")
            return None, prompt

        # Fetch image from URL
        img_response = requests.get(image_url)
        img = Image.open(BytesIO(img_response.content))
        return img, prompt

    except Exception as e:
        st.error(f"Error generating image: {e}")
        return None, prompt


# 5. Streamlit UI for AI Art
st.subheader("Generate AI Artwork for a City & Date")

selected_city = st.selectbox("Select City", df['City'].unique())
city_data = df[df['City'] == selected_city].sort_values('Date')
selected_date = st.selectbox("Select Date", city_data['Date'].unique())

if st.button("Generate Artwork"):
    row = city_data[city_data['Date'] == selected_date].iloc[0]
    with st.spinner("Generating AI artwork..."):
        ai_image, prompt = generate_ai_art(
            aqi=row['AQI'],
            pm25=row['PM25'],
            co=row['CO'],
            temperature=row['Temperature'],
            humidity=row['Humidity'],
            width=512,
            height=512
        )
    if ai_image:
        st.write("Generated Prompt:", prompt)
        st.image(ai_image, caption=f"AI Artwork for {selected_city} on {selected_date}")
        ai_image.save(f"{selected_city}_{selected_date}_ai_art.png")
    else:
        st.error("Failed to generate image")
