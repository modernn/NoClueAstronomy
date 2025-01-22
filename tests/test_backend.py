from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_get_all_events():
    response = client.get("/events/")
    assert response.status_code == 200

def test_get_event_by_id():
    response = client.get("/events/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1

def test_get_event_not_found():
    response = client.get("/events/99")
    assert response.status_code == 404
