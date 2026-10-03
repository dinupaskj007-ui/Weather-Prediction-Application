from flask import Flask, request, jsonify, render_template
from core.weather_client import fetch_coordinates, fetch_weather_data
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
    """Weather endpoint enforcing circuit breaking, caching, and AI synthesis."""
    city = request.args.get("city")
    if not city:
        return jsonify({"error": "City parameter is required"}), 400
    
    city = city.strip()
    weather_data = None
    is_cached = False
    
    try:
        # Try fetching fresh data via Circuit Breaker
        geo = fetch_coordinates(city)
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
        set_cached_weather(city, weather_data)
        
    except pybreaker.CircuitBreakerError:
        app.logger.warning(f"Circuit Breaker Open! Attempting to serve cache for {city}")
        weather_data = get_cached_weather(city)
        is_cached = True
    except ValueError as e:
        app.logger.error(f"Validation Error: {e}")
        return jsonify({"error": str(e)}), 422
    except Exception as e:
        app.logger.error(f"Network Error: {e}")
        weather_data = get_cached_weather(city)
        is_cached = True
        
    if not weather_data:
        return jsonify({"error": "Service unavailable and no offline cache exists for this location."}), 503
        
    # Inject AI Context & Anomaly Detection
    ai_context = synthesize_weather_context(city, weather_data)
    
    return jsonify({
        "status": "success",
        "source": "cache" if is_cached else "live",
        "data": weather_data,
        "ai_context": ai_context
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)
