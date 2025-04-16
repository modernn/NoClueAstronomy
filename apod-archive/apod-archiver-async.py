import os
import argparse
import logging
import sqlite3
import re
import asyncio
import aiohttp
from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path
from PIL import Image

# Configuration
NASA_API_KEY = os.environ.get("NASA_API_KEY", "IkuABPxWolnxE8KbyBqXECfMLWfEmJek10hDSduE")
APOD_URL = "https://api.nasa.gov/planetary/apod"
DB_FILE = "apod_images.db"
THUMBNAIL_SIZE = (200, 200)  # Thumbnail size (width, height)
DEFAULT_THUMBNAIL_PATH = "default_thumbnail.jpg"  # Path to a default thumbnail image

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


def load_default_thumbnail() -> bytes:
    """Load a default thumbnail from disk if available."""
    try:
        with open(DEFAULT_THUMBNAIL_PATH, "rb") as f:
            return f.read()
    except Exception as e:
        logging.error("Error loading default thumbnail: %s", e)
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
        try:
            if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                background = Image.new("RGB", img.size, (255, 255, 255))
                # Attempt to paste using the alpha mask
                background.paste(img, mask=img.split()[-1])
                img = background
            else:
                img = img.convert("RGB")
        except Exception as e:
            # Fallback if transparency handling fails
            if "bad transparency mask" in str(e).lower():
                logging.warning("Bad transparency mask encountered; falling back to simple conversion.")
                img = img.convert("RGB")
            else:
                raise e

        buffer = BytesIO()
        img.save(buffer, format="JPEG")
        return buffer.getvalue()
    except Exception as e:
        logging.error("Error creating thumbnail: %s", e)
    return None


# -----------------------------
# Asynchronous helper functions
# -----------------------------

async def fetch_apod_data_async(apod_date: str, session: aiohttp.ClientSession) -> dict:
    """Fetch APOD data from NASA API for a given date asynchronously."""
    params = {"api_key": NASA_API_KEY, "date": apod_date}
    async with session.get(APOD_URL, params=params) as response:
        if response.status == 200:
            return await response.json()
        logging.error("Error fetching APOD data for %s: %s", apod_date, response.status)
        return None


async def fetch_bytes(url: str, session: aiohttp.ClientSession) -> bytes:
    if url.startswith("//"):
        url = "https:" + url
    try:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.read()
            logging.error("Failed to download image from %s (status: %s)", url, response.status)
    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        logging.error("Error fetching %s: %s", url, e)
    # Return a default thumbnail if the request fails
    return load_default_thumbnail()


async def get_youtube_thumbnail_async(video_url: str, session: aiohttp.ClientSession) -> bytes:
    """Extract the YouTube video ID and download the corresponding thumbnail asynchronously."""
    match = re.search(r"youtube\.com/embed/([^?&]+)", video_url)
    if match:
        video_id = match.group(1)
        thumb_url = f"https://img.youtube.com/vi/{video_id}/0.jpg"
        logging.info("YouTube thumbnail URL: %s", thumb_url)
        image_bytes = await fetch_bytes(thumb_url, session)
        if image_bytes:
            return create_thumbnail_blob_from_image(image_bytes)
        else:
            logging.error("Failed to download YouTube thumbnail from %s", thumb_url)
    else:
        logging.error("Could not extract YouTube video ID from %s", video_url)
    return load_default_thumbnail()


async def get_vimeo_thumbnail_async(video_url: str, session: aiohttp.ClientSession) -> bytes:
    """Use Vimeo's oEmbed API to extract a thumbnail."""
    oembed_url = "https://vimeo.com/api/oembed.json"
    params = {"url": video_url}
    async with session.get(oembed_url, params=params) as response:
        if response.status == 200:
            data = await response.json()
            thumb_url = data.get("thumbnail_url")
            if thumb_url:
                image_bytes = await fetch_bytes(thumb_url, session)
                if image_bytes:
                    return create_thumbnail_blob_from_image(image_bytes)
        logging.error("Error fetching Vimeo thumbnail for %s", video_url)
    return load_default_thumbnail()


async def create_thumbnail_blob_async(apod_data: dict, session: aiohttp.ClientSession) -> bytes:
    """Create a thumbnail blob based on the media type asynchronously."""
    media_type = apod_data["media_type"]
    url = apod_data.get("url", "")
    
    if media_type == "image":
        image_bytes = await fetch_bytes(url, session)
        if image_bytes:
            return create_thumbnail_blob_from_image(image_bytes)
    elif media_type == "video":
        if "youtube.com" in url:
            return await get_youtube_thumbnail_async(url, session)
        elif "vimeo.com" in url:
            return await get_vimeo_thumbnail_async(url, session)
        else:
            logging.warning("Video provider not supported for thumbnail extraction: %s", url)
            return load_default_thumbnail()
    else:
        logging.warning("Unsupported media type: %s", media_type)
    
    # Optionally, return a default thumbnail if nothing is found
    return load_default_thumbnail()


async def process_apod_async(apod_data: dict, db: APODDatabase, session: aiohttp.ClientSession):
    """Process and store a single APOD entry (including thumbnail creation) asynchronously."""
    thumbnail_blob = await create_thumbnail_blob_async(apod_data, session)
    # Database operations remain synchronous; for heavy loads consider offloading with run_in_executor
    db.insert_apod(apod_data, thumbnail_blob)
    logging.info("APOD for %s processed and saved.", apod_data["date"])


async def process_single_date(date_str: str, db: APODDatabase, session: aiohttp.ClientSession):
    """Fetch and process APOD data for a single date."""
    apod_data = await fetch_apod_data_async(date_str, session)
    if apod_data:
        await process_apod_async(apod_data, db, session)


async def fetch_and_store_apod_async(start_date: datetime, end_date: datetime, db: APODDatabase):
    """
    Fetch and store APOD data for a given date range asynchronously.
    
    This function checks if an entry for a given day already exists
    in the database. If it does, it skips that day.
    """
    timeout = aiohttp.ClientTimeout(total=30)  # 30-second total timeout for each request
    async with aiohttp.ClientSession(timeout=timeout) as session:
        tasks = []
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            if db.exists_entry(date_str):
                logging.info("Entry for %s already exists. Skipping...", date_str)
            else:
                tasks.append(process_single_date(date_str, db, session))
            current_date += timedelta(days=1)
        await asyncio.gather(*tasks)


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


async def main_async():
    """Asynchronous main entry point of the script."""
    start_date, end_date = parse_arguments()
    db = APODDatabase(DB_FILE)
    try:
        await fetch_and_store_apod_async(start_date, end_date, db)
    finally:
        missing = find_missing_dates(db, start_date, end_date)
        db.close()

def find_missing_dates(db: APODDatabase, start_date: datetime, end_date: datetime) -> list:
    """
    Identify which dates between start_date and end_date are missing from the database.
    
    Args:
        db (APODDatabase): The database instance.
        start_date (datetime): The start date of the expected range.
        end_date (datetime): The end date of the expected range.
        
    Returns:
        list: A sorted list of missing date strings (formatted as 'YYYY-MM-DD').
    """
    # Build the set of expected dates as strings.
    expected_dates = set()
    current_date = start_date
    while current_date <= end_date:
        expected_dates.add(current_date.strftime("%Y-%m-%d"))
        current_date += timedelta(days=1)
    
    # Retrieve all stored dates from the database.
    cursor = db.conn.cursor()
    cursor.execute("SELECT date FROM apod")
    stored_dates = {row[0] for row in cursor.fetchall()}
    cursor.close()
    
    # Determine missing dates.
    missing_dates = sorted(expected_dates - stored_dates)
    
    if missing_dates:
        logging.info("Missing dates from database: %s", ", ".join(missing_dates))
    else:
        logging.info("All dates between %s and %s are accounted for.", 
                     start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
    
    return missing_dates


def main():
    """Synchronous wrapper for launching the asynchronous main."""
    asyncio.run(main_async())
    

if __name__ == "__main__":
    main()
