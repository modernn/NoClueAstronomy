"""
Configuration module for the NoClueAstronomy API.

This module loads configuration settings from environment variables
and provides them to the rest of the application.
"""

import os
import logging
from pathlib import Path
from typing import List
import json

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Root directory
ROOT_DIR = Path(__file__).parent.parent.absolute()

# API details
API_TITLE = os.getenv("API_TITLE", "NoClueAstronomy API")
API_DESCRIPTION = os.getenv("API_DESCRIPTION", "An API that queries and caches astronomical data from various sources")
API_VERSION = os.getenv("API_VERSION", "1.0.0")
API_DOCS_URL = "/docs"
API_REDOC_URL = "/redoc"

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{ROOT_DIR}/data/astronomy.db")

# External API configuration
ASTRONOMY_API_BASE_URL = os.getenv("ASTRONOMY_API_BASE_URL", "https://api.astronomyapi.com/api/v2")
ASTRONOMY_APP_ID = os.getenv("ASTRONOMY_APP_ID", "")
ASTRONOMY_APP_SECRET = os.getenv("ASTRONOMY_APP_SECRET", "")

NASA_API_BASE_URL = os.getenv("NASA_API_BASE_URL", "https://api.nasa.gov")
NASA_API_KEY = os.getenv("NASA_API_KEY", "")

# Cache configuration
CACHE_EXPIRATION_HOURS = int(os.getenv("CACHE_EXPIRATION_HOURS", "24"))

# Rate limiting configuration
RATE_LIMIT = int(os.getenv("RATE_LIMIT", "60"))  # Default: 60 requests per minute
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # Default: 60 seconds window
RATE_LIMIT_BLOCK_TIME = int(os.getenv("RATE_LIMIT_BLOCK_TIME", "300"))  # Default: 5 minutes block

# CORS configuration
def _parse_list_env(env_value, default):
    """Parse a JSON list from environment variable or return default"""
    if not env_value:
        return default
    try:
        return json.loads(env_value)
    except json.JSONDecodeError:
        logging.warning(f"Failed to parse JSON list from environment variable, using default: {default}")
        return default

CORS_ORIGINS = _parse_list_env(os.getenv("CORS_ORIGINS"), ["*"])
CORS_METHODS = _parse_list_env(os.getenv("CORS_METHODS"), ["*"])
CORS_HEADERS = _parse_list_env(os.getenv("CORS_HEADERS"), ["*"])

# Logging configuration
LOG_LEVEL = os.getenv("API_LOG_LEVEL", "INFO").upper()
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[logging.StreamHandler()]
)

# Create logger for this module
logger = logging.getLogger(__name__)

def validate_config():
    """
    Validate critical configuration settings.
    
    Performs checks on essential configuration values and logs warnings for missing values.
    """
    # Check API keys
    if not ASTRONOMY_APP_ID or not ASTRONOMY_APP_SECRET:
        logger.warning("Astronomy API credentials not set. Astronomy API features will not work.")
    
    if not NASA_API_KEY:
        logger.warning("NASA API key not set. NASA API features will not work.")
    
    # Validate database URL
    if not DATABASE_URL:
        logger.error("DATABASE_URL not set. Application may not function correctly.")
    
    # Log configuration status
    logger.info(f"API initialized with title: {API_TITLE}, version: {API_VERSION}")
    logger.info(f"Cache expiration set to {CACHE_EXPIRATION_HOURS} hours")
    logger.info(f"Rate limiting: {RATE_LIMIT} requests per {RATE_LIMIT_WINDOW} seconds")
    
    return True