# External NASA API configuration
NASA_API_KEY = os.getenv("NASA_API_KEY", "")
NASA_API_BASE_URL = "https://api.nasa.gov"
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Root directory
ROOT_DIR = Path(__file__).parent.parent.absolute()

# API details
API_TITLE = "NoClueAstronomy API"
API_DESCRIPTION = "An API that queries and caches astronomical data from astronomyapi.com"
API_VERSION = "1.0.0"
API_DOCS_URL = "/docs"
API_REDOC_URL = "/redoc"

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{ROOT_DIR}/data/astronomy.db")

# External Astronomy API configuration
ASTRONOMY_API_BASE_URL = "https://api.astronomyapi.com/api/v2"
ASTRONOMY_APP_ID = os.getenv("ASTRONOMY_APP_ID", "your_app_id")
ASTRONOMY_APP_SECRET = os.getenv("ASTRONOMY_APP_SECRET", "your_app_secret")

# Cache configuration
CACHE_EXPIRATION_HOURS = int(os.getenv("CACHE_EXPIRATION_HOURS", "24"))

# Rate limiting configuration
RATE_LIMIT = int(os.getenv("RATE_LIMIT", "60"))  # Default: 60 requests per minute
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # Default: 60 seconds window
RATE_LIMIT_BLOCK_TIME = int(os.getenv("RATE_LIMIT_BLOCK_TIME", "300"))  # Default: 5 minutes block

# Logging configuration
LOG_LEVEL = os.getenv("API_LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

# CORS configuration
CORS_ORIGINS = ["*"]  # Allow all origins
CORS_METHODS = ["*"]  # Allow all methods
CORS_HEADERS = ["*"]  # Allow all headers