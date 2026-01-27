import streamlit as st
import pandas as pd
import pydeck as pdk

from pixazo_ai import generate_ai_art

st.set_page_config(layout="wide")
st.title("TerraCanvas: AI Environmental Art Generator")

df = pd.read_csv("environment_data_with_coords.csv")

df = df.rename(columns={
    'PM2.5 (µg/m³)': 'PM25',
    'CO (ppm)': 'CO',
    'Temperature (°C)': 'Temperature',
    'Humidity (%)': 'Humidity'
})

def severity_color(aqi):
    if aqi <= 50:
        return [0, 255, 0]
    elif aqi <= 100:
        return [255, 255, 0]
    else:
        return [255, 0, 0]

df['Color'] = df['AQI'].apply(severity_color)

latest_df = df.sort_values('Date').drop_duplicates(subset=['City'], keep='last')

layer = pdk.Layer(
    "ScatterplotLayer",
    data=latest_df,
    get_position='[Longitude, Latitude]',
    get_fill_color='Color',
    get_radius=200000,
    pickable=True
)

st.pydeck_chart(pdk.Deck(layers=[layer]))

st.subheader("Generate AI Artwork")

city = st.selectbox("City", df['City'].unique())
city_data = df[df['City'] == city]
date = st.selectbox("Date", city_data['Date'].unique())

if st.button("Generate Artwork"):
    row = city_data[city_data['Date'] == date].iloc[0]

    with st.spinner("Generating artwork..."):
        image, prompt = generate_ai_art(
            aqi=row['AQI'],
            pm25=row['PM25'],
            co=row['CO'],
            temperature=row['Temperature'],
            humidity=row['Humidity']
        )

    if image:
        st.image(image)
        st.write("Prompt:", prompt)
