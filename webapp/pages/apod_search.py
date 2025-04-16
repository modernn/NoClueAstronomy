import streamlit as st
import requests

st.set_page_config(page_title="APOD Search", layout="wide")

API_SEARCH_URL = "http://127.0.0.1:8000/search/"

st.title("🔭 APOD Search")
search_term = st.text_input("Enter a keyword to search APODs (e.g., 'nebula', 'moon')")

def chunk_list(data, chunk_size):
    """Helper: yield successive chunk_size chunks from data."""
    for i in range(0, len(data), chunk_size):
        yield data[i : i + chunk_size]

def text_length(apod):
    """
    Rough measure of 'vertical space' used by title + date + potential thumbnail.
    This doesn't directly map to pixels but helps compare item heights within the row.
    """
    title_len = len(apod.get("title", ""))
    # If there's a thumbnail, assume it adds some vertical space
    thumb_space = 50 if apod.get("thumbnail") else 10
    return title_len + thumb_space

# --- Search Button ---
if st.button("Search"):
    if not search_term:
        st.warning("Please enter a search term.")
    else:
        # Get results from your FastAPI endpoint
        response = requests.get(API_SEARCH_URL, params={"term": search_term})
        if response.status_code == 200:
            results = response.json()
            if not results:
                st.warning("No results found.")
            else:
                st.success(f"Found {len(results)} results for '{search_term}'")

                # Break results into rows of 3
                for row_data in chunk_list(results, 3):
                    # Calculate the "max length" in this row to align bottom
                    row_lengths = [text_length(apod) for apod in row_data]
                    max_len = max(row_lengths) if row_lengths else 0

                    cols = st.columns(len(row_data))
                    for col, apod, item_len in zip(cols, row_data, row_lengths):
                        with col:
                            # 1) Container for top portion (image, title, date)
                            with st.container():
                                thumbnail_b64 = apod.get("thumbnail")
                                if thumbnail_b64:
                                    data_uri = f"data:image/jpeg;base64,{thumbnail_b64}"
                                    st.image(data_uri, use_container_width=True)
                                else:
                                    st.write("No thumbnail available")

                                title = apod.get("title", "No Title")
                                date_str = apod.get("date", "No Date")
                                st.markdown(f"**{title}**")
                                st.write(f"**Date**: {date_str}")

                            # 2) Add empty lines so that shorter cards match the row’s tallest card
                            filler_lines = max_len - item_len
                            for _ in range(filler_lines // 5):
                                st.write("")  # each loop adds ~ one line of vertical space

                            # 3) Container for the bottom portion (expander)
                            with st.container():
                                with st.expander("More details"):
                                    media_type = apod.get("media_type", "")
                                    url = apod.get("url", "")
                                    hd_url = apod.get("hd_url")
                                    explanation = apod.get("explanation", "No explanation.")

                                    if media_type == "image":
                                        st.image(url, use_container_width=True)
                                        if hd_url:
                                            st.markdown(
                                                f"[View HD Image]({hd_url})",
                                                unsafe_allow_html=True
                                            )
                                    elif media_type == "video":
                                        if url.startswith("//"):
                                            url = "https:" + url
                                        st.video(url)
                                    else:
                                        st.write("Unknown media type.")

                                    st.write(explanation)
        else:
            st.error(f"API Error: {response.status_code}")
