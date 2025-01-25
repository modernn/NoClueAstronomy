import streamlit as st
from components import sidebar as sb

sb.render_sidebar()

# Glossary page content
st.title("Astronomy Glossary 🌟")

st.markdown(
    """
    ### Terms & Definitions
    - **Astronomy**: The study of celestial objects, space, and the universe as a whole.
    - **Eclipse**: An event where one celestial body moves into the shadow of another.
    - **Meteor Shower**: A celestial event where multiple meteors are observed to radiate from one point in the night sky.
    - **Nebula**: A giant cloud of dust and gas in space.
    - **Supernova**: A powerful and luminous explosion of a star.
    
    Cool new things to think about!!!!

    ### Expand Your Knowledge
    This glossary will grow as we continue to expand NoClueAstronomy. Check back for more terms!
    """
)
