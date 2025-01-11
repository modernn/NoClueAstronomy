from fastapi import FastAPI
from typing import List, Dict
import json

app = FastAPI()

# Load sample data
with open("data.json", "r") as f:
    events = json.load(f)

@app.get("/events", response_model=List[Dict])
def get_events():
    """Fetch all astronomical events."""
    return events

@app.get("/events/{event_id}")
def get_event(event_id: int):
    """Fetch a specific event by ID."""
    for event in events:
        if event["id"] == event_id:
            return event
    return {"error": "Event not found"}
