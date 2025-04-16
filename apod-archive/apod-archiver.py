import os
import argparse
import logging
import requests
import sqlite3
import re
from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path
from PIL import Image

# Configuration
NASA_API_KEY = os.environ.get("NASA_API_KEY", "IkuABPxWolnxE8KbyBqXECfMLWfEmJek10hDSduE")
APOD_URL = "https://api.nasa.gov/planetary/apod"
DB_FILE = "apod_images.db"
THUMBNAIL_SIZE = (200, 200)  # Thumbnail size (width, height)

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class APODDatabase:
    """Handles SQLite database operations for storing APOD metadata including thumbnails."""
    
    def __init__(self, db_file: str):
        self.db_file = db_file
        self.conn = sqlite3.connect(self.db_file)
        self.create_table()

    def create_table(self):
        """Create the APOD table if it doesn't exist."""
        query = '''
            CREATE TABLE IF NOT EXISTS apod (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT UNIQUE,
                title TEXT,
                explanation TEXT,
                url TEXT,
                hd_url TEXT,
                media_type TEXT,
                thumbnail BLOB
            )
        '''
        self.conn.execute(query)
        self.conn.commit()

    def exists_entry(self, date_str: str) -> bool:
        """Check if there is already an entry for the given date.
        
        Args:
            date_str (str): The date in 'YYYY-MM-DD' format.
        
        Returns:
            bool: True if an entry exists, False otherwise.
        """
        cursor = self.conn.cursor()
        query = "SELECT 1 FROM apod WHERE date = ? LIMIT 1"
        cursor.execute(query, (date_str,))
        exists = cursor.fetchone() is not None
        cursor.close()
        return exists

    def insert_apod(self, apod_data: dict, thumbnail_blob: bytes = None):
        """Insert APOD metadata along with the thumbnail blob into the database."""
        query = '''
            INSERT OR IGNORE INTO apod (date, title, explanation, url, hd_url, media_type, thumbnail)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        '''
        values = (
            apod_data["date"],
            apod_data["title"],
            apod_data["explanation"],
            apod_data.get("url", ""),
            apod_data.get("hdurl", ""),
            apod_data["media_type"],
            thumbnail_blob,
        )
        self.conn.execute(query, values)
        self.conn.commit()

    def close(self):
        """Close the database connection."""
        self.conn.close()


def fetch_apod_data(apod_date: str) -> dict:
    """Fetch APOD data from NASA API for a given date."""
    params = {"api_key": NASA_API_KEY, "date": apod_date}
    response = requests.get(APOD_URL, params=params)
    if response.ok:
        return response.json()
    logging.error("Error fetching APOD data for %s: %s", apod_date, response.status_code)
    return None


def create_thumbnail_blob_from_image(image_bytes: bytes, size: tuple = THUMBNAIL_SIZE) -> bytes:
    """
    Create a thumbnail from image bytes and return its binary data as JPEG.
    
    This function converts images with an alpha channel (e.g., PNGs)
    to a JPEG with a white background for consistency.
    """
    try:
        img = Image.open(BytesIO(image_bytes))
        img.thumbnail(size)

        # Convert images with transparency (e.g., PNG) to RGB with white background
        if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
            background = Image.new("RGB", img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1])
            img = background
        else:
            img = img.convert("RGB")

        buffer = BytesIO()
        img.save(buffer, format="JPEG")
        return buffer.getvalue()
    except Exception as e:
        logging.error("Error creating thumbnail: %s", e)
    return None


def get_youtube_thumbnail(video_url: str) -> bytes:
    """Extract the YouTube video ID and download the corresponding thumbnail."""
    match = re.search(r"youtube\.com/embed/([^?&]+)", video_url)
    if match:
        video_id = match.group(1)
        thumb_url = f"https://img.youtube.com/vi/{video_id}/0.jpg"
        logging.info("YouTube thumbnail URL: %s", thumb_url)
        response = requests.get(thumb_url)
        if response.ok:
            return create_thumbnail_blob_from_image(response.content)
        else:
            logging.error("Failed to download YouTube thumbnail from %s", thumb_url)
    else:
        logging.error("Could not extract YouTube video ID from %s", video_url)
    return None


def create_thumbnail_blob(apod_data: dict) -> bytes:
    """Create a thumbnail blob based on the media type."""
    media_type = apod_data["media_type"]
    url = apod_data.get("url", "")
    
    if media_type == "image":
        response = requests.get(url)
        if response.ok:
            return create_thumbnail_blob_from_image(response.content)
        else:
            logging.error("Failed to download image from %s", url)
    elif media_type == "video":
        if "youtube.com" in url:
            return get_youtube_thumbnail(url)
        else:
            logging.warning("Video provider not supported for thumbnail extraction: %s", url)
    else:
        logging.warning("Unsupported media type: %s", media_type)
    
    return None


def process_apod(apod_data: dict, db: APODDatabase):
    """Process and store a single APOD entry, including thumbnail creation."""
    thumbnail_blob = create_thumbnail_blob(apod_data)
    db.insert_apod(apod_data, thumbnail_blob)
    logging.info("APOD for %s processed and saved.", apod_data["date"])


def fetch_and_store_apod(start_date: datetime, end_date: datetime, db: APODDatabase):
    """Fetch and store APOD data for a given date range.
    
    This function checks if an entry for a given day already exists
    in the database. If it does, it skips that day.
    """
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        if db.exists_entry(date_str):
            logging.info("Entry for %s already exists. Skipping...", date_str)
        else:
            apod_data = fetch_apod_data(date_str)
            if apod_data:
                process_apod(apod_data, db)
        current_date += timedelta(days=1)


def parse_arguments():
    """Parse and validate command-line arguments for the date range."""
    parser = argparse.ArgumentParser(
        description="Fetch and store NASA APOD data for a date range (thumbnails stored in DB as JPEG)."
    )
    parser.add_argument("--start_date", type=str, required=True, help="Start date in YYYY-MM-DD format")
    parser.add_argument("--end_date", type=str, required=True, help="End date in YYYY-MM-DD format")
    args = parser.parse_args()

    try:
        start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
        end_date = datetime.strptime(args.end_date, "%Y-%m-%d")
        if start_date > end_date:
            parser.error("Start date must be before or equal to end date.")
    except ValueError as e:
        parser.error(str(e))

    return start_date, end_date


def main():
    """Main entry point of the script."""
    start_date, end_date = parse_arguments()
    db = APODDatabase(DB_FILE)
    try:
        fetch_and_store_apod(start_date, end_date, db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
