import streamlit as st

# Glossary page content
st.title("Astronomy Glossary 🌟")

st.markdown(
    """
    ### Terms & Definitions
    - **Altitude and Azimuth**: The visual description of a celestial body’s location.  It is specific to the observer at the time and location from which he or she is observing.
        - Altitude – The angular distance measured in degrees of the distance of the object above the horizon.  Horizon = 0&deg.  Zenith (point directly overhead) = 90&deg.
        - Azimuth – The compass points.  North = 0&deg, East = 90&deg, South = 180&deg, West = 270&deg.
    - **Astronomy**: The study of celestial objects, space, and the universe as a whole.
    - **Eclipse**: An event where one celestial body moves into the shadow of another.
    - **Julian Calendar**: A calendar  expresses any date in only one number.  The Julian Calendar begins on January 1, 4713 BCE as day 1.  The Julian date for Jan 1, 2025 was 2460676.  
    - **Magnitude**: A scale used for ranking the brightness of celestial objects.  It is a bit counter intuitive.  The brighter a star is, the smaller its magnitude.  
    - **Meteor Shower**: A celestial event where multiple meteors are observed to radiate from one point in the night sky.
    - **Nebula**: A giant cloud of dust and gas in space.
    - **Right Ascension and Declination**: The coordinate system that marks a celestial body’s location.  The right ascension and declination coordinate grid is permanently “imprinted” on the sky.  It is independent of the observer’s location.  
        - Right Ascension is expressed in hours:minutes:seconds
        - Declination is expressed in degrees:minutes:seconds; positive for degrees north, negative for degrees south.
        - Example:  Sirius is the brightest star in the sky.  Its coordinates are:
            RA  06h 45m 08.9s
            Dec  -16&deg 42’ 58”
    - **Supernova**: A powerful and luminous explosion of a star.
    - **Universal Time**: Universal Time (UT) is time independent of time zones.  It is essentialy the same as Greenwich Mean Time (GMT).  Sometimes it is called Universal Time Coordinated (UTC).

    ### Expand Your Knowledge
    This glossary will grow as we continue to expand NoClueAstronomy. Check back for more terms!
    """
)
