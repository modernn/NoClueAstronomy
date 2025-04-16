from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import sqlite3
from datetime import datetime

app = FastAPI(title="Lunar Eclipse API", description="API to retrieve upcoming and past lunar eclipse events.", version="1.0")

DB_NAME = "eclipse_data.db"

class EclipseEvent(BaseModel):
    cat_num: str
    calendar_date: str
    greatest_eclipse: str
    delta_t: str
    luna_num: str
    saros_num: str
    eclipse_type: str
    qse: str
    gamma: str
    mag1: str
    mag2: str
    pen: str
    par: str
    total: str
    lat: str
    lng: str
    # This field is computed from calendar_date and greatest_eclipse.
    event_datetime: datetime

def fetch_all_events() -> List[EclipseEvent]:
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM eclipses")
    rows = cur.fetchall()
    events = []
    for row in rows:
        # Combine the calendar_date (e.g., "2001 Jan 09") and greatest_eclipse (e.g., "20:21:40")
        # into one datetime. Adjust the format string if necessary.
        dt_str = f"{row['calendar_date']} {row['greatest_eclipse']}"
        try:
            # Format: Year, abbreviated Month, Day, Hour:Minute:Second
            event_dt = datetime.strptime(dt_str, "%Y %b %d %H:%M:%S")
        except Exception as e:
            # If the datetime cannot be parsed, skip the event.
            continue
        event = EclipseEvent(
            cat_num=row["cat_num"],
            calendar_date=row["calendar_date"],
            greatest_eclipse=row["greatest_eclipse"],
            delta_t=row["delta_t"],
            luna_num=row["luna_num"],
            saros_num=row["saros_num"],
            eclipse_type=row["eclipse_type"],
            qse=row["qse"],
            gamma=row["gamma"],
            mag1=row["mag1"],
            mag2=row["mag2"],
            pen=row["pen"],
            par=row["par"],
            total=row["total"],
            lat=row["lat"],
            lng=row["lng"],
            event_datetime=event_dt
        )
        events.append(event)
    conn.close()
    return events

@app.get("/upcoming", response_model=List[EclipseEvent])
def get_upcoming_events():
    """
    Retrieve the next three upcoming lunar eclipse events.
    """
    events = fetch_all_events()
    now = datetime.now()
    # Filter events with an event_datetime greater than or equal to now.
    upcoming = [e for e in events if e.event_datetime >= now]
    upcoming.sort(key=lambda e: e.event_datetime)
    return upcoming[:3]

@app.get("/past", response_model=List[EclipseEvent])
def get_past_events():
    """
    Retrieve the last three lunar eclipse events that have already occurred.
    """
    events = fetch_all_events()
    now = datetime.now()
    past = [e for e in events if e.event_datetime < now]
    past.sort(key=lambda e: e.event_datetime, reverse=True)
    return past[:3]

# To run the API, use a command like:
# uvicorn your_api_module:app --reload
