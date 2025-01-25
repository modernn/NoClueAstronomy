import streamlit as st
from components import sidebar as sb

sb.render_sidebar()

# Main landing page content
st.title("Welcome to NoClueAstronomy 🌌")
st.markdown(
    """
    Explore the wonders of the universe with **NoClueAstronomy**.  
    Use the sidebar to navigate to different sections of the app.

    ### Features:
    - **Astronomical Events**: Stay updated with meteor showers, eclipses, and more.
    - **Glossary/Terms**: Learn the definitions of common astronomy terms.
    - **Interactive Tools**: Use star maps and more (coming soon!).

    *Start exploring the cosmos now!*
    """
)
