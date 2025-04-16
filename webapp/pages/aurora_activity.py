import streamlit as st
import pandas as pd
import requests
import hashlib
import base64

def generate_auth_key(raw_key: str) -> str:
    """
    Generate an API key that is hashed with SHA-256 and encoded with Base64.
    
    Args:
        raw_key (str): The original API key.
    
    Returns:
        str: The hashed and Base64-encoded key.
    """
    # Compute the SHA-256 hash of the raw key (as bytes)
    sha256_hash = hashlib.sha256(raw_key.encode('utf-8')).digest()
    # Encode the hash using Base64 and convert to a UTF-8 string
    encoded_key = base64.b64encode(sha256_hash).decode('utf-8')
    return encoded_key

# Replace 'YOUR_RAW_API_KEY' with your actual API key (unhashed)
raw_key = "YOUR_RAW_API_KEY"
hashed_key = generate_auth_key(raw_key)

# Format the Authorization header. Adjust the prefix if required by the API docs.
headers = {
    "Authorization": f"key={hashed_key}"
}

# ------------------------------------------------------------------
# Aurora Activity Dashboard Page for NoClueAstronomy
# ------------------------------------------------------------------
st.title("Aurora Activity Dashboard")
st.markdown(
    """
    Welcome to the Aurora Activity Dashboard!  
    This page displays near–real–time auroral measurements from several high–latitude stations across northern Europe.
    
    **What is an Aurora?**  
    Auroras (the Northern or Southern Lights) occur when charged particles from the sun interact with Earth's magnetic field,
    resulting in beautiful light displays in the sky—especially in high–latitude regions. This dashboard uses the KP Index and 
    other metrics to help indicate when auroras might be visible.
    """
)

# Display an image of an aurora to help beginners visualize the phenomenon.
st.image(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e8/Aurora_Borealis_from_the_Slopes_of_Alyeska_Mountain_2017.jpg/640px-Aurora_Borealis_from_the_Slopes_of_Alyeska_Mountain_2017.jpg",
    caption="Aurora Borealis",
    use_column_width=True
)

# --- Data Fetching ---
data_url = "https://aurora.hendrikpeter.net/api/aurora_data.json"
try:
    response = requests.get(data_url, headers=headers)
    response.raise_for_status()  # Raises an error for bad responses
    data = response.json()
except Exception as e:
    st.error("Error fetching events: " + str(e))
    st.stop()

# Display last updated time
st.subheader("Last Updated")
st.write(data.get("last_update_at", "Unknown"))

# --- Process Station Data ---
locations = data.get("locations", {})

# Build a list of dictionaries for each station
stations = []
for key, station in locations.items():
    stations.append({
        "Station": station.get("human_readable_name", key),
        "KP": station.get("kp", 0),
        "Average Deviation": station.get("average_deviation", 0),
        "Average Total": station.get("average_total", 0),
        "Quiet Mean": station.get("quiet_mean_tot", 0),
        "Latitude": station.get("lat", None),
        "Longitude": station.get("long", None),
        "Data Source": station.get("data_source", "Unknown")
    })

# Convert to a pandas DataFrame for display and filtering
df = pd.DataFrame(stations)

# --- Sidebar for Filtering ---
st.sidebar.header("Filter Options")
# For example, filter by KP index
kp_values = sorted(df["KP"].unique())
selected_kps = st.sidebar.multiselect("Select KP values:", kp_values, default=kp_values)
filtered_df = df[df["KP"].isin(selected_kps)]

# --- Map View ---
st.subheader("Map View")
# Streamlit's st.map expects columns named "lat" and "lon"
map_data = filtered_df.rename(columns={"Latitude": "lat", "Longitude": "lon"})
st.map(map_data[["lat", "lon"]])

# --- Detailed Table ---
st.subheader("Station Details")
st.dataframe(filtered_df)

# --- Station Detailed Information ---
st.subheader("More Information")
station_list = filtered_df["Station"].tolist()
selected_station = st.selectbox("Select a station to view details:", station_list)

if selected_station:
    station_info = filtered_df[filtered_df["Station"] == selected_station].iloc[0]
    st.markdown("#### Detailed Information")
    st.write(f"**Station:** {station_info['Station']}")
    st.write(f"**KP Index:** {station_info['KP']}")
    st.write(f"**Average Deviation:** {station_info['Average Deviation']}")
    st.write(f"**Average Total:** {station_info['Average Total']}")
    st.write(f"**Quiet Mean:** {station_info['Quiet Mean']}")
    st.write(f"**Location:** ({station_info['Latitude']}, {station_info['Longitude']})")
    st.write(f"**Data Source:** {station_info['Data Source']}")

    # Expandable sections to explain metrics
    with st.expander("What does KP Index mean?"):
        st.markdown(
            """
            **KP Index** is a scale (typically from 0 to 9) that measures the level of geomagnetic activity.
            Higher values indicate a greater chance of auroral activity. For example, a KP index above 5 often means that
            the conditions are favorable for viewing auroras.
            """
        )
    with st.expander("More about the other metrics"):
        st.markdown(
            """
            - **Average Deviation:** Represents how much the measurements vary from station to station.
            - **Average Total:** Indicates the overall level of geomagnetic measurements at the station.
            - **Quiet Mean:** Shows the baseline level of geomagnetic activity during calm conditions.
            """
        )

# --- Footer / Additional Info ---
st.markdown(
    """
    ---
    Data provided by [Hendrik Peter Aurora API](https://aurora.hendrikpeter.net/api/aurora_data.json).  
    For more details about auroras and how to interpret this data, refer to the explanations above.
    """
)
