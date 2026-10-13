import os
import logging
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import pybreaker

from core.locations import SL_DISTRICTS, get_district_info, find_nearest_district, search_locations
from core.weather_client import resolve_coordinates, fetch_weather_data, fetch_local_dmc_alerts
from core.cache import init_db, get_cached_weather, set_cached_weather, add_community_report, get_community_reports
from core.ai_service import synthesize_weather_context

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("SL-Weather-Backend")

app = Flask(__name__, static_folder="static")

# Enable CORS for all mobile and cross-origin clients
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

# Initialize SQLite database (Weather cache + Community Reports)
init_db()

@app.after_request
def add_mobile_headers(response):
    """Ensure mobile browsers and webviews handle caching and security properly."""
    if request.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

# --- PWA & Static Routes ---

@app.route("/")
def index():
    """Serves the responsive Mobile Generative UI."""
    return render_template("index.html")

@app.route("/manifest.json")
def pwa_manifest():
    """Serves the Web App Manifest for mobile 'Add to Home Screen'."""
    return send_from_directory(app.static_folder, "manifest.json", mimetype="application/manifest+json")

@app.route("/sw.js")
def service_worker():
    """Serves the Service Worker for mobile offline caching."""
    response = send_from_directory(app.static_folder, "sw.js", mimetype="application/javascript")
    response.headers["Service-Worker-Allowed"] = "/"
    return response

@app.route("/api/health")
def api_health():
    """Lightweight health check for mobile connectivity monitoring."""
    return jsonify({
        "status": "healthy",
        "service": "Sri Lanka Climate Precision API",
        "version": "2.0.0",
        "mobile_ready": True
    })

# --- Mobile Weather & Geolocation API ---

@app.route("/api/weather")
def api_weather():
    """
    Mobile-optimized weather endpoint.
    Supports:
      1. Mobile GPS Coordinates: ?lat=6.9271&lon=79.8612
      2. District & Province: ?district=Colombo&province=Western
      3. City Search Query: ?city=Kandy
    """
    lat_str = request.args.get("lat")
    lon_str = request.args.get("lon")
    district = request.args.get("district")
    province = request.args.get("province")
    city = request.args.get("city")

    target_lat = None
    target_lon = None
    target_district = "Colombo"
    target_province = "Western"
    microclimate = "Urban Coastal"
    distance_km = None

    # Case 1: Mobile GPS Coordinates provided
    if lat_str and lon_str:
        try:
            target_lat = float(lat_str)
            target_lon = float(lon_str)
            closest_dist, dist_info = find_nearest_district(target_lat, target_lon)
            target_district = closest_dist
            target_province = dist_info["province"]
            microclimate = dist_info["microclimate"]
            distance_km = dist_info.get("distance_km")
        except ValueError:
            return jsonify({"error": "Invalid latitude or longitude values"}), 400

    # Case 2: District or City name provided
    else:
        location_query = district or city or "Colombo"
        location_query = location_query.strip()
        local_info = get_district_info(location_query)

        if local_info:
            target_district = local_info["district"]
            target_province = province.strip() if province else local_info["province"]
            target_lat = local_info["lat"]
            target_lon = local_info["lon"]
            microclimate = local_info["microclimate"]
        else:
            try:
                geo = resolve_coordinates(location_query)
                target_district = geo.name
                target_province = province.strip() if province else "Western"
                target_lat = geo.latitude
                target_lon = geo.longitude
            except ValueError as e:
                return jsonify({"error": str(e)}), 404

    # Fetch weather data with Circuit Breaker & Offline SQLite Fallback
    weather_data = None
    is_cached = False
    cache_key = f"{target_district.lower()}"

    try:
        raw_weather = fetch_weather_data(target_lat, target_lon)
        weather_data = {
            "city": target_district,
            "province": target_province,
            "latitude": target_lat,
            "longitude": target_lon,
            "current": raw_weather["current"],
            "daily": raw_weather["daily"]
        }
        # Persist to offline cache
        set_cached_weather(cache_key, weather_data)

    except (pybreaker.CircuitBreakerError, Exception) as e:
        logger.warning(f"Live weather fetch failed ({e}). Attempting offline cache for {target_district}")
        weather_data = get_cached_weather(cache_key)
        is_cached = True

    if not weather_data:
        return jsonify({
            "error": "Weather data currently unavailable. No offline cache stored for this location.",
            "suggestion": "Check mobile internet connectivity or try again shortly."
        }), 503

    # Fetch ground-truth DMC disaster warnings & emergency hotlines
    dmc_alert = fetch_local_dmc_alerts(target_province, target_district)

    # Gemini AI Context Synthesis (Monsoon-Aware & Conflict Resolution)
    ai_context = synthesize_weather_context(target_province, target_district, weather_data, dmc_alert)

    # Build mobile-optimized response
    current = weather_data.get("current", {})
    daily = weather_data.get("daily", {})
    uv_max_list = daily.get("uv_index_max", [0])
    uv_val = uv_max_list[0] if uv_max_list else 0

    response_payload = {
        "status": "success",
        "source": "cache" if is_cached else "live",
        "location": {
            "district": target_district,
            "province": target_province,
            "microclimate": microclimate,
            "coordinates": {
                "latitude": target_lat,
                "longitude": target_lon
            },
            "gps_distance_km": distance_km
        },
        "metrics": {
            "temperature": current.get("temperature_2m", 28.0),
            "humidity": current.get("relative_humidity_2m", 80),
            "wind_speed": current.get("wind_speed_10m", 0.0),
            "uv_index": uv_val,
            "weather_code": current.get("weather_code", 0)
        },
        "forecast": {
            "time": daily.get("time", [])[:7],
            "temp_max": daily.get("temperature_2m_max", [])[:7],
            "temp_min": daily.get("temperature_2m_min", [])[:7],
            "precipitation": daily.get("precipitation_sum", [])[:7]
        },
        "dmc_alert": dmc_alert,
        "ai_insights": ai_context
    }

    return jsonify(response_payload)

# --- Mobile Disaster Alerts Endpoint ---

@app.route("/api/alerts")
def api_alerts():
    """
    Lightweight disaster alert check for mobile background push and widgets.
    """
    district = request.args.get("district", "Colombo").strip()
    province = request.args.get("province", "Western").strip()

    info = get_district_info(district)
    if info:
        province = info["province"]

    alert = fetch_local_dmc_alerts(province, district)
    return jsonify({
        "status": "success",
        "district": district,
        "province": province,
        "alert": alert
    })

# --- Mobile Community Reporting API ---

@app.route("/api/reports", methods=["GET", "POST"])
def api_reports():
    """
    Crowdsourced mobile emergency incident reporting and feed.
    GET: List recent community reports (filtered by ?district=... or all).
    POST: Submit a new mobile incident report.
    """
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        user_name = data.get("user_name", "").strip()
        district = data.get("district", "").strip()
        province = data.get("province", "").strip()
        message = data.get("message", "").strip()
        threat_level = data.get("threat_level", "MODERATE").strip()

        if not user_name:
            return jsonify({"error": "User name is required"}), 400
        if not district:
            return jsonify({"error": "District is required"}), 400
        if not message:
            return jsonify({"error": "Report message cannot be empty"}), 400
        if len(message) > 500:
            return jsonify({"error": "Message exceeds maximum length of 500 characters"}), 400

        # Auto-resolve province if omitted
        if not province:
            dist_info = get_district_info(district)
            if dist_info:
                province = dist_info["province"]

        saved_report = add_community_report(user_name, district, province, message, threat_level)
        return jsonify({
            "status": "success",
            "message": "Community report submitted successfully.",
            "report": saved_report
        }), 201

    # GET request
    district_filter = request.args.get("district")
    limit = int(request.args.get("limit", 20))
    reports = get_community_reports(district=district_filter, limit=limit)
    return jsonify({
        "status": "success",
        "count": len(reports),
        "reports": reports
    })

# --- Mobile Locations & Microclimate Search API ---

@app.route("/api/locations")
def api_locations():
    """Returns all 25 Sri Lankan districts and microclimate descriptions for mobile caching."""
    locations_list = []
    for name, data in SL_DISTRICTS.items():
        locations_list.append({
            "district": name,
            "province": data["province"],
            "lat": data["lat"],
            "lon": data["lon"],
            "microclimate": data["microclimate"]
        })
    return jsonify({
        "status": "success",
        "count": len(locations_list),
        "locations": locations_list
    })

@app.route("/api/locations/search")
def api_search_locations():
    """Predictive autocomplete search for Screen 4."""
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"status": "success", "results": []})

    results = search_locations(query)
    return jsonify({
        "status": "success",
        "query": query,
        "count": len(results),
        "results": results
    })

if __name__ == "__main__":
    # Host on 0.0.0.0 so all mobile devices on the network can connect
    app.run(debug=True, host="0.0.0.0", port=5000)
