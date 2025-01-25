import streamlit as st
import requests
from datetime import date
from components import sidebar as sb

sb.render_sidebar()

# Set up the APOD page
st.title("NASA Astronomy Picture of the Day 🌌")

# Input for selecting a date
selected_date = st.date_input("Select a date for the APOD", value=date.today())

# Fetch the APOD data from NASA API
@st.cache_data
def fetch_apod(api_key, apod_date):
    url = "https://api.nasa.gov/planetary/apod"
    params = {
        "api_key": api_key,
        "date": apod_date,
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Failed to fetch APOD: {response.status_code}"}

# NASA API Key (replace with your actual key)
API_KEY = "IkuABPxWolnxE8KbyBqXECfMLWfEmJek10hDSduE"

# Fetch and display the APOD
if st.button("Fetch APOD"):
    apod_data = fetch_apod(API_KEY, selected_date.strftime("%Y-%m-%d"))
    
    if "error" in apod_data:
        st.error(apod_data["error"])
    else:
        st.image(apod_data["url"], caption=apod_data["title"], use_container_width=True)
        st.write(apod_data["explanation"])
