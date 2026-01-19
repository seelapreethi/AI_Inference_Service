import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_predict_sync():
    payload = {"text": "I love this movie"}
    response = client.post("/predict_sync", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert "confidence" in data
    assert 0 <= data["confidence"] <= 1

# Optional: if /predict_async is enabled
def test_predict_async():
    payload = {"text": "This is amazing"}
    response = client.post("/predict_async", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    assert "status" in data
