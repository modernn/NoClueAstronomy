import streamlit as st
import pandas as pd
import requests
import pydeck as pdk
from datetime import datetime

# ----------------------------------------------------------------------------
# Helper functions for parsing latitude and longitude strings
# ----------------------------------------------------------------------------
def parse_lat(lat_str: str) -> float:
    """Converts a string like '3N' or '6S' to numeric latitude."""
    num = float(lat_str[:-1])
    if lat_str[-1].upper() == 'S':
        num = -num
    return num

def parse_lng(lng_str: str) -> float:
    """Converts a string like '102W' or '87E' to numeric longitude."""
    num = float(lng_str[:-1])
    if lng_str[-1].upper() == 'W':
        num = -num
    return num

def color_from_type(eclipse_type: str) -> list:
    """
    Returns a color (RGBA list) based on the eclipse type.
    For example, total eclipses are red, partial are yellow, and penumbral are gray.
    """
    try:
        et = eclipse_type.lower()
    except Exception:
        et = ""
    if et == "total":
        return [255, 0, 0, 160]      # Red for totality
    elif et == "partial":
        return [255, 255, 0, 160]    # Yellow for partial
    elif et == "penumbral":
        return [150, 150, 150, 160]  # Gray for penumbral
    else:
        return [200, 30, 0, 160]     # Default color

# ----------------------------------------------------------------------------
# Fetch data from the FastAPI endpoints
# ----------------------------------------------------------------------------
BASE_URL = "http://127.0.0.1:8000"  # Adjust if needed

def fetch_eclipse_data(endpoint: str) -> pd.DataFrame:
    """
    Fetches eclipse events data from the given API endpoint and returns it as a pandas DataFrame.
    """
    url = f"{BASE_URL}{endpoint}"
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()  # List of eclipse events

    df = pd.DataFrame(data)
    df["event_datetime"] = pd.to_datetime(df["event_datetime"])

    # Parse lat/lng into numeric values
    df["lat_num"] = df["lat"].apply(parse_lat)
    df["lng_num"] = df["lng"].apply(parse_lng)
    
    # Add a dynamic color based on eclipse type
    df["color"] = df["eclipse_type"].apply(color_from_type)

    return df

# ----------------------------------------------------------------------------
# PyDeck map creation function with enhanced tooltips
# ----------------------------------------------------------------------------
def create_pydeck_chart(df: pd.DataFrame, initial_lat=0, initial_lon=0, zoom=1):
    """
    Create a PyDeck chart from a DataFrame with 'lat_num' and 'lng_num' columns,
    using dynamic colors and enhanced tooltips.
    """
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position='[lng_num, lat_num]',
        get_color='color',  # Use dynamic color from the "color" column
        get_radius=50000,   # Adjust radius as needed
        pickable=True,
    )
    
    view_state = pdk.ViewState(
        latitude=initial_lat,
        longitude=initial_lon,
        zoom=zoom,
        pitch=0,
    )
    
    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={
            "html": "<b>Date:</b> {calendar_date}<br>"
                    "<b>Eclipse Type:</b> {eclipse_type}<br>"
                    "<b>Greatest Eclipse:</b> {greatest_eclipse}<br>"
                    "<b>Lat:</b> {lat_num}<br>"
                    "<b>Lng:</b> {lng_num}",
            "style": {"backgroundColor": "steelblue", "color": "white", "fontSize": "12px"}
        }
    )
    
    return deck

# ----------------------------------------------------------------------------
# Main Streamlit layout
# ----------------------------------------------------------------------------
st.set_page_config(page_title="Lunar Eclipse Events", layout="wide")
st.title("Lunar Eclipse Events Dashboard")

st.markdown(
    """
    This **Streamlit** app retrieves lunar eclipse events data from a FastAPI and visualizes both upcoming and past events.
    
    The maps below use **PyDeck** for rendering eclipse event locations. Enhanced tooltips now show additional details (eclipse type, greatest eclipse time, etc.), and marker colors are dynamically set based on eclipse visibility.
    """
)

# ----------------------------------------------------------------------------
# Fetch Upcoming and Past Data
# ----------------------------------------------------------------------------
try:
    df_upcoming = fetch_eclipse_data("/upcoming")
    df_past = fetch_eclipse_data("/past")
except Exception as e:
    st.error(f"Failed to retrieve data from the API: {e}")
    st.stop()

# ----------------------------------------------------------------------------
# Upcoming Eclipses Section
# ----------------------------------------------------------------------------
st.header("Upcoming Eclipses")
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Upcoming Eclipses Table")
    display_cols = [
        "calendar_date", "greatest_eclipse", "eclipse_type",
        "gamma", "mag1", "mag2", "lat", "lng"
    ]
    st.dataframe(df_upcoming[display_cols])
    
    st.subheader("Upcoming Eclipse Details")
    for _, row in df_upcoming.iterrows():
        with st.expander(f"Details for {row['calendar_date']} (Cat #{row['cat_num']})"):
            st.write(f"**Date/Time:** {row['event_datetime']} UTC")
            st.write(f"**Eclipse Type:** {row['eclipse_type']}")
            st.write(f"**Gamma:** {row['gamma']}")
            st.write(f"**Magnitude (mag1):** {row['mag1']}")
            st.write(f"**Magnitude (mag2):** {row['mag2']}")
            st.write(f"**Penumbra:** {row['pen']}")
            st.write(f"**Partial:** {row['par']}")
            st.write(f"**Total:** {row['total']}")
            st.write(f"**Saros Series:** {row['saros_num']}")
            st.write(f"**Lat/Lng:** {row['lat']} / {row['lng']}")

with col2:
    st.subheader("Upcoming Eclipse Map")
    if not df_upcoming.empty:
        init_lat = df_upcoming["lat_num"].mean()
        init_lon = df_upcoming["lng_num"].mean()
    else:
        init_lat, init_lon = 0, 0
    deck_chart_upcoming = create_pydeck_chart(df_upcoming, initial_lat=init_lat, initial_lon=init_lon, zoom=1)
    st.pydeck_chart(deck_chart_upcoming)
    
    st.subheader("Eclipse Geometry Schematic")
    st.markdown(
        """
        ```
            (Sun)
             \\
              \\
        Penumbra \\    (Moon)
                  \\  /
                  Umbra
        (Earth) <--------O
        ```
        """
    )

st.write("---")

# ----------------------------------------------------------------------------
# Past Eclipses Section
# ----------------------------------------------------------------------------
st.header("Past Eclipses")
col3, col4 = st.columns([2, 1])

with col3:
    st.subheader("Past Eclipses Table")
    st.dataframe(df_past[display_cols])
    
    st.subheader("Past Eclipse Details")
    for _, row in df_past.iterrows():
        with st.expander(f"Details for {row['calendar_date']} (Cat #{row['cat_num']})"):
            st.write(f"**Date/Time:** {row['event_datetime']} UTC")
            st.write(f"**Eclipse Type:** {row['eclipse_type']}")
            st.write(f"**Gamma:** {row['gamma']}")
            st.write(f"**Magnitude (mag1):** {row['mag1']}")
            st.write(f"**Magnitude (mag2):** {row['mag2']}")
            st.write(f"**Penumbra:** {row['pen']}")
            st.write(f"**Partial:** {row['par']}")
            st.write(f"**Total:** {row['total']}")
            st.write(f"**Saros Series:** {row['saros_num']}")
            st.write(f"**Lat/Lng:** {row['lat']} / {row['lng']}")

with col4:
    st.subheader("Past Eclipse Map")
    if not df_past.empty:
        init_lat_past = df_past["lat_num"].mean()
        init_lon_past = df_past["lng_num"].mean()
    else:
        init_lat_past, init_lon_past = 0, 0
    deck_chart_past = create_pydeck_chart(df_past, initial_lat=init_lat_past, initial_lon=init_lon_past, zoom=1)
    st.pydeck_chart(deck_chart_past)
    
    st.subheader("Eclipse Geometry Schematic")
    st.markdown(
        """
        ```
        (Earth) <--------O
                  Umbra
                  /  \\
        Penumbra /    (Moon)
                /
               /
            (Sun)
        ```
        """
    )

st.write("---")
st.caption("Data retrieved from the FastAPI endpoints `/upcoming` and `/past`.")
