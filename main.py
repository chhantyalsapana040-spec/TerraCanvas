import streamlit as st
import pandas as pd
import pydeck as pdk

from local_sd_ai import generate_ai_art

# -------------------- PAGE SETUP --------------------
st.set_page_config(layout="wide")
st.title("TerraCanvas: AI Environmental Art Generator")

# -------------------- LOAD DATA --------------------
df = pd.read_csv("environment_data_with_coords.csv")

df = df.rename(columns={
    'PM2.5 (µg/m³)': 'PM25',
    'CO (ppm)': 'CO',
    'Temperature (°C)': 'Temperature',
    'Humidity (%)': 'Humidity'
})

# -------------------- COLOR LOGIC --------------------
def severity_color(aqi):
    if aqi <= 50:
        return [0, 255, 0]
    elif aqi <= 100:
        return [255, 255, 0]
    else:
        return [255, 0, 0]

df["Color"] = df["AQI"].apply(severity_color)

# Latest record per city
latest_df = df.sort_values("Date").drop_duplicates(
    subset=["City"], keep="last"
)

# -------------------- PYDECK LAYER --------------------
layer = pdk.Layer(
    "ScatterplotLayer",
    data=latest_df,
    get_position="[Longitude, Latitude]",
    get_fill_color="Color",
    get_radius=300000,
    radius_min_pixels=5,
    radius_max_pixels=15,
    pickable=True
)

# -------------------- TOOLTIP (HOVER DATA) --------------------
tooltip = {
    "html": """
    <b>City:</b> {City}<br/>
    <b>Date:</b> {Date}<br/>
    <b>AQI:</b> {AQI}<br/>
    <b>PM2.5:</b> {PM25} µg/m³<br/>
    <b>CO:</b> {CO} ppm<br/>
    <b>Temperature:</b> {Temperature} °C<br/>
    <b>Humidity:</b> {Humidity} %
    """,
    "style": {
        "backgroundColor": "rgba(0, 0, 0, 0.8)",
        "color": "white",
        "fontSize": "12px"
    }
}

# -------------------- MAP --------------------
deck = pdk.Deck(
    layers=[layer],
    tooltip=tooltip,
    initial_view_state=pdk.ViewState(
        latitude=latest_df["Latitude"].mean(),
        longitude=latest_df["Longitude"].mean(),
        zoom=3,
        pitch=0
    )
)

st.pydeck_chart(deck)

# -------------------- ART GENERATION UI --------------------
st.subheader("Generate AI Artwork")

city = st.selectbox("City", df["City"].unique())
city_data = df[df["City"] == city]
date = st.selectbox("Date", city_data["Date"].unique())

if st.button("Generate Artwork"):
    row = city_data[city_data["Date"] == date].iloc[0]

    with st.spinner("Generating artwork..."):
        image, prompt = generate_ai_art(
            aqi=row["AQI"],
            pm25=row["PM25"],
            co=row["CO"],
            temperature=row["Temperature"],
            humidity=row["Humidity"]
        )

    if image is not None:
        st.image(image, width=512)
        st.markdown(f"**Prompt:** {prompt}")
    else:
        st.error("Failed to generate artwork.")
