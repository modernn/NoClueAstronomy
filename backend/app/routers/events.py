from fastapi import APIRouter

router = APIRouter()

@router.get("/events")
def get_events():
    return [{"event": "Meteor Shower", "date": "2025-01-20"}]
