import streamlit as st
import pandas as pd
import pydeck as pdk
import os
from pymongo import MongoClient
from seeder import AOR_CONFIG

# -----------------
# 1. Page Config (must be first)
st.set_page_config(page_title="Global Intel Dashboard", layout="wide")


# -----------------
# MONGODB CONNECTION (cached)
@st.cache_resource
def init_connection():
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017/")
    return MongoClient(mongo_url)


client = init_connection()
db = client.intel_db


# -----------------
# FETCH DATA
def get_intel_data(aor_name):
    items = list(db.reports.find({"ccom": aor_name}))
    if not items:
        return pd.DataFrame()

    df = pd.DataFrame(items)

    # 1. DROP MONGODB _id (PyDeck can't serialize BSON ObjectIds)
    if '_id' in df.columns:
        df = df.drop(columns=['_id'])

    # 2. FORCE NUMERIC (Essential for mapping)
    df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
    df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
    df['intensity'] = pd.to_numeric(df['intensity'], errors='coerce')

    # 3. CLEANUP
    df = df.dropna(subset=['lat', 'lon', 'intensity'])

    # 4. DATETIME FORMATTING
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')

    return df


# -----------------
# APP HEADER
st.title("🌍 Geospatial News Ranker")

# Sidebar filters
st.sidebar.header("Mission Parameters")
region = st.sidebar.selectbox("Select AOR", list(AOR_CONFIG.keys()))
config = AOR_CONFIG[region]

# Fetch data
df = get_intel_data(region)

if not df.empty:
    # -----------------
    # 3D MAP (PyDeck)
    st.subheader(f"📍 Intelligence Distribution: {region}")

    layer = pdk.Layer(
        "ColumnLayer",
        data=df,
        # Use column names as strings, not lambdas
        get_position='[lon, lat]',
        get_elevation='intensity',
        elevation_scale=1000,
        radius=50000,
        # For colors, pass a fixed list or a column name
        get_fill_color="[200, 30, 0, 160]",
        pickable=True,
        auto_highlight=True,
    )

    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=pdk.ViewState(
            latitude=config["lat"],
            longitude=config["lon"],
            zoom=config["zoom"],
            pitch=45
        ),
        map_style=pdk.map_styles.LIGHT,
        tooltip={
            "html": "<b>AOR:</b> {ccom}<br/><b>Summary:</b> {summary}",
            "style": {"backgroundColor": "steelblue", "color": "white"}
        }
    )

    st.pydeck_chart(deck)

    # -----------------
    # Raw data preview
    st.markdown("---")
    st.subheader("📑 Raw Intelligence Feed")

    available_cols = [col for col in ['timestamp', 'country', 'category', 'summary', 'intensity'] if col in df.columns]
    st.dataframe(df[available_cols], use_container_width=True, hide_index=True)

else:
    # -----------------
    # Fallback UI if DB empty
    st.info("📡 No intelligence reports found. Run 'python seeder.py' to populate the database.")

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
