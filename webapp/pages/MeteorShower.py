# pages/MeteorShower.py
import streamlit as st
import requests
import datetime
import base64

# =============================================================================
# Configuration and API Key Setup
# =============================================================================
try:
    API_KEY = st.secrets["ASTRONOMY_API"]["API_KEY"]
    API_SECRET = st.secrets["ASTRONOMY_API"]["API_SECRET"]
except KeyError:
    st.error("API credentials not found in st.secrets. Please add API_KEY and API_SECRET to your secrets.toml.")
    st.stop()

BASE_URL = "https://api.astronomyapi.com/api/v2"

# Construct the Basic Auth header manually.
credentials = f"{API_KEY}:{API_SECRET}"
encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
HEADERS = {"Authorization": f"Basic {encoded_credentials}"}

# =============================================================================
# Helper Functions
# =============================================================================
def get_meteor_shower_events(date: datetime.date):
    """
    Retrieve meteor shower events for the given date.
    """
    endpoint = f"{BASE_URL}/astronomy/events"
    params = {
        "date": date.isoformat(),
        "event_type": "meteor_shower"  # assuming the API supports this filter
    }
    response = requests.get(endpoint, params=params, headers=HEADERS)

    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error fetching events: {response.status_code} - {response.text}")
        return None

def get_object_position(lat: float, lon: float, date_time: datetime.datetime, ra, dec):
    """
    Retrieve the position (altitude and azimuth) of an object with given
    right ascension (ra) and declination (dec) for the observer's location and time.
    """
    endpoint = f"{BASE_URL}/astronomy/positions"
    params = {
        "latitude": lat,
        "longitude": lon,
        "date_time": date_time.isoformat(),
        "object_ra": ra,
        "object_dec": dec,
    }
    response = requests.get(endpoint, params=params, headers=HEADERS)

    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error fetching object position: {response.status_code} - {response.text}")
        return None

def get_sun_info(lat: float, lon: float, date: datetime.date):
    """
    Retrieve sunrise, sunset, and twilight information for the given location and date.
    """
    endpoint = f"{BASE_URL}/astronomy/sun"
    params = {
        "latitude": lat,
        "longitude": lon,
        "date": date.isoformat()
    }
    response = requests.get(endpoint, params=params, headers=HEADERS)

    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error fetching sun info: {response.status_code} - {response.text}")
        return None

def get_moon_info(lat: float, lon: float, date: datetime.date):
    """
    Retrieve moonrise, moonset, and illumination data for the given location and date.
    """
    endpoint = f"{BASE_URL}/astronomy/moon"
    params = {
        "latitude": lat,
        "longitude": lon,
        "date": date.isoformat()
    }
    response = requests.get(endpoint, params=params, headers=HEADERS)

    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error fetching moon info: {response.status_code} - {response.text}")
        return None

# =============================================================================
# Application Page: Meteor Shower Visibility Checker
# =============================================================================
def app():
    st.title("Meteor Shower Visibility Checker")
    st.markdown(
        """
        This page uses AstronomyAPI data to identify upcoming meteor shower events and
        determine if they will be visible from a specified location and time.
        """
    )

    # Sidebar for observer input
    st.sidebar.header("Observer Details")
    latitude = st.sidebar.number_input("Latitude", value=40.0, format="%.6f")
    longitude = st.sidebar.number_input("Longitude", value=-74.0, format="%.6f")
    date = st.sidebar.date_input("Observation Date", datetime.date.today())

    if st.sidebar.button("Check Meteor Shower"):
        st.subheader(f"Results for {date} at ({latitude}, {longitude})")

        # 1. Retrieve meteor shower events for the date
        events_data = get_meteor_shower_events(date)
        if events_data and "data" in events_data:
            events = events_data["data"].get("events", [])
            if not events:
                st.info("No meteor shower events found for this date.")
            else:
                for event in events:
                    st.markdown(f"### {event.get('name', 'Unnamed Meteor Shower')}")
                    st.write(f"**Start Time:** {event.get('start')}")
                    st.write(f"**Peak Time:** {event.get('peak')}")
                    
                    # Retrieve radiant information (assumes the API returns a 'radiant' field)
                    radiant = event.get("radiant")
                    if radiant:
                        ra = radiant.get("ra")
                        dec = radiant.get("dec")
                        st.write(f"**Radiant Coordinates:** RA: {ra}, Dec: {dec}")
                        
                        # 2. Determine the position of the radiant at the peak time
                        try:
                            event_peak = datetime.datetime.fromisoformat(event.get("peak"))
                        except Exception as e:
                            st.error(f"Error parsing event peak time: {e}")
                            event_peak = datetime.datetime.now()
                        
                        pos_data = get_object_position(latitude, longitude, event_peak, ra, dec)
                        if pos_data and "data" in pos_data:
                            position = pos_data["data"].get("position", {})
                            altitude = position.get("altitude")
                            azimuth = position.get("azimuth")
                            st.write(
                                f"At peak time, the radiant is at **altitude**: {altitude}° and **azimuth**: {azimuth}°."
                            )
                        else:
                            st.warning("Could not retrieve the radiant's position data.")
                    else:
                        st.warning("No radiant data available for this event.")

                    # 3. Retrieve and display local sun info for darkness conditions
                    sun_data = get_sun_info(latitude, longitude, date)
                    if sun_data and "data" in sun_data:
                        sun = sun_data["data"]
                        st.write("**Sun Information:**")
                        st.write(f"Sunrise: {sun.get('sunrise')}")
                        st.write(f"Sunset: {sun.get('sunset')}")
                        st.write(f"Astronomical Twilight Start: {sun.get('astronomical_twilight_start')}")
                        st.write(f"Astronomical Twilight End: {sun.get('astronomical_twilight_end')}")
                    else:
                        st.warning("Sun information is not available.")

                    # 4. Retrieve and display local moon info to assess brightness
                    moon_data = get_moon_info(latitude, longitude, date)
                    if moon_data and "data" in moon_data:
                        moon = moon_data["data"]
                        st.write("**Moon Information:**")
                        st.write(f"Moonrise: {moon.get('moonrise')}")
                        st.write(f"Moonset: {moon.get('moonset')}")
                        st.write(f"Illumination: {moon.get('illumination')}%")
                    else:
                        st.warning("Moon information is not available.")
        else:
            st.error("Failed to retrieve meteor shower events data.")

if __name__ == "__main__":
    app()
