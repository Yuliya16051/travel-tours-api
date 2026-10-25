from fastapi.testclient import TestClient
from app_final import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_version():
    r = client.get("/version")
    assert r.status_code == 200
    assert "version" in r.json()

def test_list_tours():
    r = client.get("/tours")
    assert r.status_code == 200
    assert r.json()["count"] >= 1

def test_filter_by_country():
    r = client.get("/tours?country=Италия")
    assert r.status_code == 200
    assert all(t["country"] == "Италия" for t in r.json()["tours"])

def test_tour_not_found():
    r = client.get("/tours/9999")
    assert r.status_code == 404

def test_create_booking():
    r = client.post("/bookings", json={
        "tour_id": 1, "name": "Иван", "email": "ivan@example.com"
    })
    assert r.status_code == 200
    assert r.json()["status"] == "created"

def test_filter_by_max_days():
    r = client.get("/tours?max_days=6")
    assert r.status_code == 200
    assert all(t["days"] <= 6 for t in r.json()["tours"])