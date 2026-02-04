import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
from datetime import datetime
import os
from pymongo import MongoClient
from seeder import AOR_CONFIG

# 1. Page Config MUST be the absolute first Streamlit command
st.set_page_config(page_title="Global Intel Dashboard", layout="wide")


# ----------------- MONGODB CONNECTION LOGIC -----------------
@st.cache_resource
def init_connection():
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017/")
    return MongoClient(mongo_url)


client = init_connection()
db = client.intel_db


def get_intel_data(aor_name):
    """Fetch intelligence data from MongoDB for the selected AOR."""
    items = db.reports.find({"ccom": aor_name})
    df = pd.DataFrame(list(items))

    if not df.empty:
        # Ensure coordinates and intensity are numeric
        df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
        df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
        df['intensity'] = pd.to_numeric(df['intensity'], errors='coerce')

    return df


# -----------------END OF CONNECTION LOGIC -----------------



st.title("🌍 Geospatial News Ranker")

# Sidebar for filters
st.sidebar.header("Mission Parameters")
region = st.sidebar.selectbox("Select AOR", list(AOR_CONFIG.keys()))

# Get configuration for selected AOR
config = AOR_CONFIG[region]

# Fetch data from MongoDB
df = get_intel_data(region)

if not df.empty:
    # 2. RENDER THE 3D MAP (PyDeck Layer)
    st.subheader(f"📍 Intelligence Distribution: {region}")

    st.pydeck_chart(pdk.Deck(
        map_style=None,
        initial_view_state=pdk.ViewState(
            latitude=config["lat"], longitude=config["lon"],
            zoom=config["zoom"], pitch=45
        ),
        layers=[
            pdk.Layer(
                "ColumnLayer",
                data=df,
                get_position='[lon, lat]',
                get_elevation='intensity',
                elevation_scale=1000,
                radius=50000,
                get_fill_color="[200, 30, 0, 160]",
                pickable=True,
                auto_highlight=True,
            ),
        ],
        tooltip={
            "html": "<b>AOR:</b> {ccom}<br/><b>Summary:</b> {summary}",
            "style": {"backgroundColor": "steelblue", "color": "white"}
        }
    ))

    # 3. RENDER THE DATA PREVIEW (Tabular Data)
    st.markdown("---")
    st.subheader("📑 Raw Intelligence Feed")

    # Filter available columns to avoid errors
    available_cols = [col for col in ['timestamp', 'country', 'category', 'summary', 'intensity'] if col in df.columns]
    st.dataframe(
        df[available_cols],
        use_container_width=True,
        hide_index=True
    )
else:
    # Fallback if MongoDB is empty: Display the UI with a message
    st.info("📡 No intelligence reports found. Run 'python seeder.py' to populate the database.")

    # Display the AOR briefing
    col1, col2 = st.columns([3, 1])

    with col1:
        st.subheader(f"Strategic View: {region} (Awaiting Data)")
        st.map(pd.DataFrame({"lat": [config["lat"]], "lon": [config["lon"]]}))

    with col2:
        st.subheader("Regional Briefing")
        st.write(f"**AOR Scope:** {config['desc']}")
        st.metric("Expected Intel Points", "100+")

        if region == "USINDOPACOM":
            st.error("⚠️ Conflict Flashpoint: South China Sea")
            st.info("ℹ️ Monitoring Freedom of Navigation (FONOP) routes.")
        elif region == "USEUCOM":
            st.warning("⚠️ Border Activity: Suwalki Gap")