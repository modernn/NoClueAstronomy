from fastapi import APIRouter, HTTPException
from models.event_model import Event
from utils.jwt_handler import verify_jwt
import json

router = APIRouter()

with open("data/data.json") as f:
    events_data = json.load(f)

@router.get("/", response_model=list[Event])
def get_all_events():
    return events_data

@router.get("/{event_id}", response_model=Event)
def get_event(event_id: int):
    for event in events_data:
        if event["id"] == event_id:
            return event
    raise HTTPException(status_code=404, detail="Event not found")
