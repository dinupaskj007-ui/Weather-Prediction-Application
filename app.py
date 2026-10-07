from flask import Flask, request, jsonify, render_template
from core.weather_client import fetch_coordinates, fetch_weather_data, fetch_local_dmc_alerts
from core.cache import init_db, get_cached_weather, set_cached_weather
from core.ai_service import synthesize_weather_context
import pybreaker
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Initialize the cache DB on startup
init_db()

@app.route("/")
def index():
    """Serves the Generative UI frontend."""
    return render_template("index.html")

@app.route("/api/weather")
def api_weather():
    """
    Core backend pipeline:
    1. Fetch Global Data (Open-Meteo) via Circuit Breaker & Caching
    2. Fetch Local Ground Truth (DMC Alerts)
    3. AI Data Fusion & Synthesis
    """
    province = request.args.get("province", "Western")
    district = request.args.get("district", "Colombo")
    
    district = district.strip()
    province = province.strip()
    
    weather_data = None
    is_cached = False
    
    try:
        # Phase 1: Global API with Resiliency
        geo = fetch_coordinates(district)
        raw_weather = fetch_weather_data(geo.latitude, geo.longitude)
        
        weather_data = {
            "city": geo.name,
            "country": geo.country,
            "latitude": geo.latitude,
            "longitude": geo.longitude,
            "current": raw_weather["current"],
            "daily": raw_weather["daily"]
        }
        
        # Save validated data to offline cache
        set_cached_weather(district, weather_data)
        
    except pybreaker.CircuitBreakerError:
        app.logger.warning(f"Circuit Breaker Open! Attempting to serve cache for {district}")
        weather_data = get_cached_weather(district)
        is_cached = True
    except ValueError as e:
        app.logger.error(f"Validation Error: {e}")
        return jsonify({"error": str(e)}), 422
    except Exception as e:
        app.logger.error(f"Network Error: {e}")
        weather_data = get_cached_weather(district)
        is_cached = True
        
    if not weather_data:
        return jsonify({"error": "Service unavailable and no offline cache exists for this location."}), 503
        
    # Phase 2: Local Ground Truth (DMC)
    dmc_alert = fetch_local_dmc_alerts(province, district)
    
    # Phase 3: AI Data Fusion (Monsoon-Aware)
    ai_context = synthesize_weather_context(province, district, weather_data, dmc_alert)
    
    # Construct final payload
    response_payload = {
        "status": "success",
        "source": "cache" if is_cached else "live",
        "location": {
            "district": district,
            "province": province
        },
        "metrics": {
            "temperature": weather_data["current"]["temperature_2m"],
            "humidity": weather_data["current"]["relative_humidity_2m"],
            "wind_speed": weather_data["current"].get("wind_speed_10m", 0),
            "uv_index": weather_data["daily"].get("uv_index_max", [0])[0] if "uv_index_max" in weather_data["daily"] and weather_data["daily"]["uv_index_max"] else 0,
            "weather_code": weather_data["current"]["weather_code"]
        },
        "dmc_alert": dmc_alert,
        "ai_insights": ai_context
    }
    
    return jsonify(response_payload)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
