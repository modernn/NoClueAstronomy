import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.title("Astronomical Events Viewer")

# Fetch all events
st.header("Upcoming Events")
response = requests.get(f"{API_URL}/events")
if response.status_code == 200:
    events = response.json()
    for event in events:
        st.subheader(event["name"])
        st.write(f"Date: {event['date']}")
        st.write(f"Description: {event['description']}")
else:
    st.error("Failed to fetch events.")

# Fetch a specific event by ID
st.header("Search Event by ID")
event_id = st.number_input("Enter Event ID", min_value=1, step=1)
if st.button("Search"):
    response = requests.get(f"{API_URL}/events/{event_id}")
    if response.status_code == 200:
        event = response.json()
        if "error" in event:
            st.error(event["error"])
        else:
            st.write(f"Name: {event['name']}")
            st.write(f"Date: {event['date']}")
            st.write(f"Description: {event['description']}")
    else:
        st.error("Failed to fetch event.")
