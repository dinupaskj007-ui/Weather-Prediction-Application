import pytest
from app import app
from core.locations import find_nearest_district, search_locations, get_city_info

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_index_page(client):
    """Test web root route serves the dashboard HTML with required widgets."""
    res = client.get("/")
    assert res.status_code == 200
    html = res.get_data(as_text=True)
    assert "Today's Weather" in html
    assert "todayHourlyScroll" in html
    assert "btn-ai-prediction" in html
    assert "aiPredictionModal" in html
    assert "openAIPredictionModal" in html
    assert "emergencyBeaconBtn" in html
    assert "communityReportsModal" in html
    assert "openCommunityReportsModal" in html
    assert "loginScreen" in html
    assert "userNameInput" in html
    assert "Nickname" in html
    assert "saveDataAndProceed" in html

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
    assert "hourly" in data
    assert len(data["hourly"]["time"]) >= 24
    assert len(data["hourly"]["temperature"]) >= 24

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


def test_api_weather_7day_prediction(client):
    """Test 7-day AI weather prediction attached to /api/weather."""
    res = client.get("/api/weather?district=Colombo&province=Western")
    assert res.status_code == 200
    data = res.get_json()
    assert "ai_7day_prediction" in data
    pred = data["ai_7day_prediction"]
    assert pred["status"] == "success"
    assert "daily_predictions" in pred
    assert len(pred["daily_predictions"]) == 10
    assert "peak_rain_day" in pred
    assert "best_outdoor_day" in pred
    assert pred["overall_confidence"] >= 80.0
    day0 = pred["daily_predictions"][0]
    assert day0["day_name"] == "Today"
    assert "rain_probability" in day0
    assert "confidence_score" in day0
    assert "ai_advisory" in day0

def test_api_7day_forecast_endpoint(client):
    """Test dedicated /api/forecast/7day endpoint."""
    res = client.get("/api/forecast/7day?district=Kandy&province=Central")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["district"] == "Kandy"
    assert len(data["daily_predictions"]) == 10
    assert data["overall_confidence"] >= 80.0


def test_city_search_and_lookup():
    """Test searching and looking up cities across Sri Lankan districts."""
    # Negombo in Gampaha
    res_negombo = search_locations("Negombo")
    assert len(res_negombo) >= 1
    assert res_negombo[0]["city"] == "Negombo"
    assert res_negombo[0]["district"] == "Gampaha"
    assert res_negombo[0]["province"] == "Western"

    # Direct city lookup
    info = get_city_info("Hikkaduwa")
    assert info is not None
    assert info["district"] == "Galle"
    assert info["province"] == "Southern"

    # Hatton in Nuwara Eliya
    res_hatton = search_locations("Hatton")
    assert len(res_hatton) >= 1
    assert res_hatton[0]["district"] == "Nuwara Eliya"


def test_api_weather_city(client):
    """Test /api/weather with specific city query (Negombo, Gampaha District)."""
    res = client.get("/api/weather?city=Negombo")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["location"]["city"] == "Negombo"
    assert data["location"]["district"] == "Gampaha"
    assert data["location"]["province"] == "Western"
    assert "metrics" in data


def test_api_forecast_7day_city(client):
    """Test /api/forecast/7day with specific city query (Kataragama)."""
    res = client.get("/api/forecast/7day?city=Kataragama")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert len(data["daily_predictions"]) == 10
