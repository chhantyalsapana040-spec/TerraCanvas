import streamlit as st
import pandas as pd
import pydeck as pdk
from stable_diffusion_gen import generate_ai_art  # import SD module

st.set_page_config(layout="wide")
st.title("TerraCanvas: AI Environmental Art Generator")

# Load dataset
df = pd.read_csv("environment_data_with_coords.csv")

# Rename columns
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

# Severity color
def severity_color(aqi):
    if aqi <= 50:
        return [0, 255, 0]
    elif aqi <= 100:
        return [255, 255, 0]
    else:
        return [255, 0, 0]

df['Color'] = df['AQI'].apply(severity_color)

# World map
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

# Generate AI artwork
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
    st.write("Generated Prompt:", prompt)
    st.image(ai_image, caption=f"AI Artwork for {selected_city} on {selected_date}")
    ai_image.save(f"{selected_city}_{selected_date}_ai_art.png")
