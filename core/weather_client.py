import requests
import pybreaker
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from pydantic import BaseModel, ValidationError
import logging
from typing import List, Optional
from core.locations import get_district_info

weather_breaker = pybreaker.CircuitBreaker(fail_max=3, reset_timeout=60)
logger = logging.getLogger(__name__)

# --- Pydantic Schemas ---
class CurrentWeather(BaseModel):
    temperature_2m: float
    relative_humidity_2m: int
    weather_code: int
    wind_speed_10m: Optional[float] = 0.0

class DailyForecast(BaseModel):
    time: List[str]
    temperature_2m_max: List[float]
    temperature_2m_min: List[float]
    precipitation_sum: List[float]
    precipitation_probability_max: Optional[List[int]] = None
    weather_code: Optional[List[int]] = None
    uv_index_max: Optional[List[float]] = None
    wind_speed_10m_max: Optional[List[float]] = None

class WeatherResponseSchema(BaseModel):
    current: CurrentWeather
    daily: DailyForecast
    timezone: str

class CityGeo(BaseModel):
    name: str
    latitude: float
    longitude: float
    country: str = "Sri Lanka"

class GeoResponseSchema(BaseModel):
    results: List[CityGeo]

# --- SL Specific Disaster Management Center (DMC) & Met Dept Alerts ---
def fetch_local_dmc_alerts(province: str, district: str) -> dict:
    """
    Simulates fetching authoritative ground-truth alerts from the SL Disaster Management Centre.
    Includes emergency hotlines for mobile users.
    """
    prov = province.strip().lower() if province else ""
    dist = district.strip().lower() if district else ""
    
    hotlines = {
        "dmc_hotline": "117",
        "ambulance_suwaseriya": "1990",
        "police_emergency": "119",
        "met_dept": "011-2686499"
    }

    # Microclimate threat modeling by province/district
    if prov in ["central", "sabaragamuwa"] or dist in ["ratnapura", "kandy", "nuwara eliya", "kegalle"]:
        return {
            "source": "DMC Sri Lanka / NBRO",
            "severity": "RED ALERT",
            "threat_type": "Landslide & Torrential Rain",
            "hotlines": hotlines,
            "evacuation_status": "Active Warning - Level 2",
            "message": f"Continuous rainfall over 150mm recorded in {district.capitalize()}. NBRO Level 2 Amber warning for mountainous slopes. Avoid hillside roads and water basins."
        }
    elif prov in ["southern", "western"] and dist in ["galle", "matara", "colombo"]:
        return {
            "source": "Met Dept Sri Lanka",
            "severity": "WARNING",
            "threat_type": "Severe Lightning & Rough Swells",
            "hotlines": hotlines,
            "evacuation_status": "Advisory",
            "message": f"Gusty winds up to 60 km/h with severe lightning expected across {district.capitalize()} coastal areas. Naval and fishing communities advised not to navigate small craft."
        }
    elif prov in ["northern", "north central"] and dist in ["jaffna", "anuradhapura", "mannar"]:
        return {
            "source": "DMC Sri Lanka",
            "severity": "ADVISORY",
            "threat_type": "High Solar UV Index & Heat Advisory",
            "hotlines": hotlines,
            "evacuation_status": "Normal",
            "message": f"Peak diurnal temperatures with Extreme UV index (Level 9+). Limit prolonged outdoor exposure between 11 AM and 3 PM."
        }
            
    return {
        "source": "DMC Sri Lanka",
        "severity": "NORMAL",
        "threat_type": "Monsoon Routine",
        "hotlines": hotlines,
        "evacuation_status": "None",
        "message": f"Normal seasonal conditions in {district.capitalize()}. No active disaster evacuation orders."
    }

# --- Coordinates & Weather Fetching ---
def resolve_coordinates(district_or_city: str) -> CityGeo:
    """
    Resolves coordinates using high-speed local Sri Lankan district table first.
    Falls back to Open-Meteo Geocoding API if not found.
    """
    local = get_district_info(district_or_city)
    if local:
        return CityGeo(
            name=local["district"],
            latitude=local["lat"],
            longitude=local["lon"],
            country="Sri Lanka"
        )
    return fetch_coordinates_from_api(district_or_city)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((requests.exceptions.RequestException, requests.exceptions.Timeout))
)
@weather_breaker
def fetch_coordinates_from_api(city: str) -> CityGeo:
    """Remote geocoding fallback."""
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    
    data = response.json()
    if "results" not in data or not data["results"]:
        raise ValueError(f"Location '{city}' could not be resolved.")
        
    try:
        validated_geo = GeoResponseSchema(**data)
        return validated_geo.results[0]
    except ValidationError as e:
        logger.error(f"Geocoding API schema error: {e}")
        raise ValueError("Invalid geocoding response format.")

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((requests.exceptions.RequestException, requests.exceptions.Timeout))
)
@weather_breaker
def fetch_weather_data(lat: float, lon: float) -> dict:
    """Fetch high-precision weather metrics via Open-Meteo."""
    url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
        "&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,weather_code,uv_index_max,wind_speed_10m_max"
        "&timezone=Asia/Colombo"
    )
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    
    try:
        validated_weather = WeatherResponseSchema(**response.json())
        return validated_weather.model_dump()
    except ValidationError as e:
        logger.error(f"Weather API schema error: {e}")
        raise ValueError("Invalid weather response format.")
