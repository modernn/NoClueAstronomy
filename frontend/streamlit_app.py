import streamlit as st
import streamlit_authenticator as stauth
import requests

st.title("Astronomical Events Viewer")

# Authentication
authenticator = stauth.Authenticate(
    {"usernames": {"user1": {"name": "User One", "password": "password123"}}},
    "cookie_name",
    "cookie_key",
    30
)

name, authentication_status, username = authenticator.login("Login")

if authentication_status:
    st.success(f"Welcome, {name}!")
    
    # Fetch and display events
    token = "your_generated_jwt_token"  # Replace with your token logic
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get("http://localhost:8000/events", headers=headers)
    
    if response.status_code == 200:
        events = response.json()
        st.write("Upcoming Events:")
        for event in events:
            st.write(event)
    else:
        st.error("Failed to fetch events")

elif authentication_status == False:
    st.error("Username/password is incorrect")
else:
    st.warning("Please enter your credentials")
