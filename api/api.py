# api.py

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from typing import List, Dict
from pathlib import Path
from contextlib import closing
import sqlite3
import base64
import random

# Initialize FastAPI app with metadata
app = FastAPI(
    title="NoClueAstronomy API",
    description="A FastAPI service to query local APOD data (title, description, random images).",
    version="1.0.0",
    contact={
        "name": "NoClueAstronomy Team",
        "url": "https://github.com/modernn/NoClueAstronomy",
        "email": "support@noclueastronomy.com"
    }
)

# Path to the database (../apod-archive/apod_images.db relative to this file)
DB_FILE = Path(__file__).resolve().parent.parent / "apod-archive" / "apod_images.db"

def custom_openapi():
    """
    Generate a custom OpenAPI schema, used for Swagger and Redoc.
    """
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


def search_apod(term: str) -> List[Dict]:
    """
    Searches the APOD database for the given term in title or explanation.
    Returns *all* matching APOD metadata (no pagination) including base64-encoded thumbnail.
    """
    query = """
    SELECT 
        id, date, title, explanation, url, hd_url, media_type, thumbnail
    FROM apod
    WHERE title LIKE ?
       OR explanation LIKE ?
    """

    with closing(sqlite3.connect(DB_FILE)) as conn:
        conn.row_factory = sqlite3.Row  # results as dictionaries
        with closing(conn.cursor()) as cursor:
            cursor.execute(query, (f"%{term}%", f"%{term}%"))
            rows = cursor.fetchall()

    apod_list = []
    for row in rows:
        apod_data = dict(row)
        if apod_data["thumbnail"]:
            # Convert thumbnail bytes to base64 string
            apod_data["thumbnail"] = base64.b64encode(apod_data["thumbnail"]).decode("utf-8")
        apod_list.append(apod_data)
    return apod_list


def get_random_apod() -> Dict:
    """
    Returns a single random APOD entry from the database, including base64-encoded thumbnail.
    """
    query = """
    SELECT 
        id, date, title, explanation, url, hd_url, media_type, thumbnail
    FROM apod
    ORDER BY RANDOM() 
    LIMIT 1
    """
    with closing(sqlite3.connect(DB_FILE)) as conn:
        conn.row_factory = sqlite3.Row
        with closing(conn.cursor()) as cursor:
            cursor.execute(query)
            row = cursor.fetchone()

    if not row:
        return {}
    apod_data = dict(row)
    if apod_data["thumbnail"]:
        apod_data["thumbnail"] = base64.b64encode(apod_data["thumbnail"]).decode("utf-8")
    return apod_data


@app.get("/search/", response_model=List[Dict], tags=["APOD Operations"])
def search_apod_endpoint(term: str = Query(..., description="Search term for APOD title or explanation")):
    """
    Search the local APOD database by keyword, returning all matching results.

    - **term**: Keyword to search for in the APOD title or explanation.

    **Example**:
    `/search/?term=nebula`
    """
    results = search_apod(term)
    if not results:
        return JSONResponse(content={"message": "No results found"}, status_code=404)
    return results


@app.get("/random", response_model=Dict, tags=["APOD Operations"])
def random_apod_endpoint():
    """
    Return a single random APOD entry from the database.
    """
    apod_data = get_random_apod()
    if not apod_data:
        return JSONResponse(content={"message": "No APOD data found"}, status_code=404)
    return apod_data
