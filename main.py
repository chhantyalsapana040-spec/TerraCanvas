import streamlit as st
import pandas as pd
import pydeck as pdk
from geopy.geocoders import Nominatim
import time
from utils import map_environment_to_visual, generate_texture, compose_artwork

st.set_page_config(layout="wide")
st.title("TerraCanvas: Environmental Art Generator")


# Load dataset

df = pd.read_csv("environment_data.csv")

# Rename columns for simpler access
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


# Geocode cities to get latitude & longitude
-
geolocator = Nominatim(user_agent="terracanvas_app")

def get_lat_lon(city, country):
    try:
        location = geolocator.geocode(f"{city}, {country}")
        if location:
            return location.latitude, location.longitude
    except:
        pass
    return None, None

# Only geocode if Latitude/Longitude not already present
if 'Latitude' not in df.columns or 'Longitude' not in df.columns:
    latitudes, longitudes = [], []
    for i, row in df.iterrows():
        lat, lon = get_lat_lon(row['City'], row['Country'])
        latitudes.append(lat if lat else 0)
        longitudes.append(lon if lon else 0)
        time.sleep(1)  # polite pause to avoid API rate limit
    df['Latitude'] = latitudes
    df['Longitude'] = longitudes

# Color based on AQI severity

def severity_color(aqi):
    if aqi <= 50:
        return [0, 255, 0]      # Green: Good
    elif aqi <= 100:
        return [255, 255, 0]    # Yellow: Moderate
    else:
        return [255, 0, 0]      # Red: Unhealthy

df['Color'] = df['AQI'].apply(severity_color)


# World map with points

st.subheader(" World Map of Pollution Severity")
layer = pdk.Layer(
    "ScatterplotLayer",
    data=df,
    get_position='[Longitude, Latitude]',
    get_fill_color='Color',
    get_radius=200000,
    pickable=True
)
view_state = pdk.ViewState(latitude=0, longitude=0, zoom=1)
r = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={"text": "{City}\nAQI: {AQI}\nPM2.5: {PM25}\nCO: {CO}"}
)
st.pydeck_chart(r)


# Generate artwork for selected city

st.subheader("Generate Artwork for a City")
selected_city = st.selectbox("Select City", df['City'].unique())

if st.button("Generate Artwork"):
    row = df[df['City'] == selected_city].iloc[0]
    darkness, noise_intensity, smoothness, warmth = map_environment_to_visual(
        aqi=row['AQI'],
        pm25=row['PM25'],
        co=row['CO'],
        temperature=row['Temperature'],
        humidity=row['Humidity']
    )
    texture = generate_texture(800, 600, darkness, noise_intensity, smoothness)
    artwork = compose_artwork(texture, warmth)
    artwork.save(f"{selected_city}_art.png")
    st.image(artwork, caption=f"Artwork for {selected_city}")
