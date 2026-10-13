import pytest
import json
from app import app
from core.locations import find_nearest_district, search_locations, get_district_info

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    """Test mobile health check endpoint."""
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "healthy"
    assert data["mobile_ready"] is True

def test_pwa_manifest(client):
    """Test Web App Manifest route for mobile Add to Home Screen."""
    res = client.get("/manifest.json")
    assert res.status_code == 200
    data = res.get_json()
    assert data["short_name"] == "SL Weather"
    assert data["display"] == "standalone"

def test_service_worker(client):
    """Test Service Worker for mobile offline caching."""
    res = client.get("/sw.js")
    assert res.status_code == 200
    assert "application/javascript" in res.content_type

def test_nearest_district_gps():
    """Test Haversine mobile GPS nearest district resolver."""
    # Coordinates near Colombo Fort
    district, info = find_nearest_district(6.9344, 79.8428)
    assert district == "Colombo"
    assert info["province"] == "Western"

    # Coordinates near Kandy Lake
    district, info = find_nearest_district(7.2936, 80.6413)
    assert district == "Kandy"
    assert info["province"] == "Central"

def test_locations_search_logic():
    """Test location autocomplete search for Screen 4."""
    results = search_locations("nuwara")
    assert len(results) >= 1
    assert results[0]["district"] == "Nuwara Eliya"

def test_api_locations_endpoint(client):
    """Test /api/locations returns all 25 Sri Lankan districts."""
    res = client.get("/api/locations")
    assert res.status_code == 200
    data = res.get_json()
    assert data["count"] == 25
    assert len(data["locations"]) == 25

def test_api_locations_search_endpoint(client):
    """Test /api/locations/search endpoint."""
    res = client.get("/api/locations/search?q=Galle")
    assert res.status_code == 200
    data = res.get_json()
    assert data["count"] >= 1
    assert data["results"][0]["district"] == "Galle"

def test_api_weather_district(client):
    """Test /api/weather with district parameter."""
    res = client.get("/api/weather?district=Colombo&province=Western")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["location"]["district"] == "Colombo"
    assert "metrics" in data
    assert "temperature" in data["metrics"]
    assert "dmc_alert" in data
    assert "ai_insights" in data

def test_api_weather_gps_coordinates(client):
    """Test /api/weather with mobile GPS coordinates."""
    res = client.get("/api/weather?lat=6.9271&lon=79.8612")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["location"]["district"] == "Colombo"
    assert "gps_distance_km" in data["location"]

def test_api_weather_disaster_alert(client):
    """Test /api/weather for high-risk district (Ratnapura - landslide warning)."""
    res = client.get("/api/weather?district=Ratnapura&province=Sabaragamuwa")
    assert res.status_code == 200
    data = res.get_json()
    assert data["dmc_alert"]["severity"] in ["RED ALERT", "WARNING"]
    assert "Landslide" in data["dmc_alert"]["threat_type"]
    assert data["dmc_alert"]["hotlines"]["dmc_hotline"] == "117"

def test_api_alerts_endpoint(client):
    """Test lightweight disaster alerts check for mobile push/widgets."""
    res = client.get("/api/alerts?district=Galle")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert "hotlines" in data["alert"]

def test_community_reports_get_and_post(client):
    """Test crowdsourced mobile community reporting (GET and POST)."""
    # 1. GET existing reports
    res = client.get("/api/reports")
    assert res.status_code == 200
    initial_data = res.get_json()
    assert initial_data["count"] >= 1

    # 2. POST a new mobile report
    new_report = {
        "user_name": "Kasun Perera",
        "district": "Colombo",
        "province": "Western",
        "message": "Water receding on Baseline Road, traffic moving smoothly now.",
        "threat_level": "LOW"
    }
    post_res = client.post("/api/reports", json=new_report)
    assert post_res.status_code == 201
    post_data = post_res.get_json()
    assert post_data["report"]["user_name"] == "Kasun Perera"
    assert post_data["report"]["threat_level"] == "LOW"

    # 3. GET filtered by district
    res_filtered = client.get("/api/reports?district=Colombo")
    filtered_data = res_filtered.get_json()
    user_names = [r["user_name"] for r in filtered_data["reports"]]
    assert "Kasun Perera" in user_names
