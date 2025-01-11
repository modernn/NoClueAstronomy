import streamlit as st
import streamlit_authenticator as stauth
import requests
import json

# Page title
st.set_page_config(page_title="Astronomical Events Viewer", layout="wide")

# Sidebar: User Authentication
with st.sidebar:
    st.title("Login")

    # Load credentials from a secure location
    credentials = {
        "usernames": {
            "admin": {
                "email": "admin@example.com",
                "name": "Admin",
                "password": stauth.Hasher(["admin_password"]).generate()[0],
            }
        }
    }

    authenticator = stauth.Authenticate(
        credentials,
        "app_dashboard",
        "auth_key",
        cookie_expiry_days=1
    )

    name, authentication_status, username = authenticator.login("Login", "main")

# Main Page Content
if authentication_status:
    st.sidebar.success(f"Welcome, {name}!")
    authenticator.logout("Logout", "sidebar")

    # Navigation
    selected_page = st.sidebar.radio("Navigation", ["View Events", "Create User"])

    # View Events Page
    if selected_page == "View Events":
        st.header("Upcoming Astronomical Events")
        try:
            response = requests.get("http://localhost:8000/events")
            if response.status_code == 200:
                events = response.json()
                for event in events:
                    st.subheader(event["name"])
                    st.write(f"Date: {event['date']}")
                    st.write(f"Description: {event['description']}")
                    st.write("---")
            else:
                st.error("Failed to fetch events.")
        except requests.exceptions.RequestException as e:
            st.error(f"Error: {e}")

    # Create User Page
    elif selected_page == "Create User":
        st.header("Create a New User")
        with st.form("user_form"):
            username = st.text_input("Username")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Create User")

        if submit:
            try:
                response = requests.post("http://localhost:8000/users", json={
                    "username": username,
                    "email": email,
                    "password": password
                })
                if response.status_code == 200:
                    st.success("User created successfully!")
                else:
                    st.error(f"Error: {response.json().get('detail')}")
            except requests.exceptions.RequestException as e:
                st.error(f"Error: {e}")
else:
    st.sidebar.error("Please log in to access the application.")
