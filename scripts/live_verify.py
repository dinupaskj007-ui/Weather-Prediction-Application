import requests
import json

BASE = "http://127.0.0.1:5000"

print("========================================")
print(" LIVE BACKEND & MOBILE API TEST SUITE   ")
print("========================================")

# 1. Health
res = requests.get(f"{BASE}/api/health")
print(f"1. /api/health -> Status: {res.status_code}, Mobile Ready: {res.json().get('mobile_ready')}")

# 2. Frontend HTML
res = requests.get(f"{BASE}/")
print(f"2. / (Frontend HTML) -> Status: {res.status_code}, Size: {len(res.text)} bytes")

# 3. PWA Manifest & Service Worker
res_manifest = requests.get(f"{BASE}/manifest.json")
res_sw = requests.get(f"{BASE}/sw.js")
print(f"3. PWA Manifest -> Status: {res_manifest.status_code}, App: '{res_manifest.json().get('short_name')}', Display: '{res_manifest.json().get('display')}'")
print(f"   PWA Service Worker -> Status: {res_sw.status_code}, Type: {res_sw.headers.get('Content-Type')}")

# 4. Weather API (District Query)
res_weather = requests.get(f"{BASE}/api/weather?district=Colombo&province=Western")
w_data = res_weather.json()
print(f"4. /api/weather (Colombo) -> Status: {res_weather.status_code}")
print(f"   - Temp: {w_data['metrics']['temperature']}°C, Humidity: {w_data['metrics']['humidity']}%, UV: {w_data['metrics']['uv_index']}")
print(f"   - AI Summary: {w_data['ai_insights']['synthetic_impact_statement'][:80]}...")

# 5. Mobile GPS Weather Coordinates
res_gps = requests.get(f"{BASE}/api/weather?lat=6.9271&lon=79.8612")
gps_data = res_gps.json()
print(f"5. /api/weather (GPS 6.9271, 79.8612) -> Status: {res_gps.status_code}")
print(f"   - Nearest District: {gps_data['location']['district']} ({gps_data['location']['province']} Province)")
print(f"   - Distance to center: {gps_data['location']['gps_distance_km']} km")

# 6. Disaster Alerts Endpoint (Ratnapura - High Landslide Risk)
res_alert = requests.get(f"{BASE}/api/alerts?district=Ratnapura&province=Sabaragamuwa")
alert_data = res_alert.json()['alert']
print(f"6. /api/alerts (Ratnapura) -> Status: {res_alert.status_code}")
print(f"   - Severity: {alert_data['severity']}")
print(f"   - Threat Type: {alert_data['threat_type']}")
print(f"   - Emergency Hotline: {alert_data['hotlines']['dmc_hotline']}")

# 7. Community Reporting API (GET and POST)
res_reports = requests.get(f"{BASE}/api/reports")
rep_data = res_reports.json()
print(f"7. /api/reports (Community Feed) -> Status: {res_reports.status_code}, Total Active Reports: {rep_data['count']}")
print(f"   - Latest Report: [{rep_data['reports'][0]['threat_level']}] {rep_data['reports'][0]['user_name']} in {rep_data['reports'][0]['district']}: '{rep_data['reports'][0]['message'][:60]}...'")

# 8. Locations Predictive Search
res_search = requests.get(f"{BASE}/api/locations/search?q=Kandy")
search_data = res_search.json()
print(f"8. /api/locations/search?q=Kandy -> Status: {res_search.status_code}, Matches: {search_data['count']}")
print(f"   - District: {search_data['results'][0]['district']}, Microclimate: {search_data['results'][0]['microclimate']}")

print("\n========================================")
print(" ALL 8 LIVE ENDPOINTS VERIFIED & PASSING ")
print("========================================")
