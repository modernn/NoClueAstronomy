import streamlit as st
from streamlit_extras.switch_page_button import switch_page

def render_sidebar():
    st.sidebar.title("Navigation")
    if st.sidebar.button("Home"):
        switch_page("app")  # Navigates to the main app page
    if st.sidebar.button("Glossary"):
        switch_page("glossary")  # Navigates to the Glossary page
    if st.sidebar.button("APOD"):
        switch_page("apod")  # Navigates to the APOD page
