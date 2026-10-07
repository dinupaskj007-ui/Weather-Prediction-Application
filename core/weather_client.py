import requests
import pybreaker
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from pydantic import BaseModel, ValidationError
import logging
from typing import List, Optional

weather_breaker = pybreaker.CircuitBreaker(fail_max=3, reset_timeout=60)
logger = logging.getLogger(__name__)

# --- Pydantic Schemas ---
class CurrentWeather(BaseModel):
    temperature_2m: float
    relative_humidity_2m: int
    weather_code: int
    wind_speed_10m: Optional[float] = None

class DailyForecast(BaseModel):
    time: List[str]
    temperature_2m_max: List[float]
    temperature_2m_min: List[float]
    precipitation_sum: List[float]
    uv_index_max: Optional[List[float]] = None

class WeatherResponseSchema(BaseModel):
    current: CurrentWeather
    daily: DailyForecast
    timezone: str

class CityGeo(BaseModel):
    name: str
    latitude: float
    longitude: float
    country: str = ""

class GeoResponseSchema(BaseModel):
    results: List[CityGeo]

# --- SL Specific Mocks ---
def fetch_local_dmc_alerts(province: str, district: str) -> dict:
    """
    Simulates fetching active ground-truth alerts from the SL Disaster Management Centre.
    In a real app, this would scrape DMC RSS feeds or query was.meteo.gov.lk.
    """
    province = province.lower()
    district = district.lower()
    
    # Simulated Local Threat Modeling
    if province in ["central", "sabaragamuwa"] or district in ["ratnapura", "nuwara eliya", "kandy"]:
        return {
            "source": "DMC Sri Lanka",
            "severity": "RED ALERT",
            "threat_type": "Landslide & Flash Flood",
            "message": f"Continuous heavy rainfall detected in {district.capitalize()}. Level 2 Landslide warning issued by NBRO. Evacuate unstable slopes immediately."
        }
    elif province in ["southern", "eastern", "western"]:
        if district in ["galle", "matara", "colombo"]:
            return {
                "source": "Met Dept SL",
                "severity": "WARNING",
                "threat_type": "Rough Seas & High Winds",
                "message": "High waves and strong gusty winds expected. Multiday fishing boats and small craft are advised not to venture out to sea."
            }
            
    return {
        "source": "DMC Sri Lanka",
        "severity": "NORMAL",
        "threat_type": "None",
        "message": "No active emergency alerts for this district."
    }

# --- Global API Connectors ---
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((requests.exceptions.RequestException, requests.exceptions.Timeout))
)
@weather_breaker
def fetch_coordinates(city: str) -> CityGeo:
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    
    data = response.json()
    if "results" not in data or not data["results"]:
        raise ValueError(f"City '{city}' not found.")
        
    try:
        validated_geo = GeoResponseSchema(**data)
        return validated_geo.results[0]
    except ValidationError as e:
        logger.error(f"Geocoding API changed schema! {e}")
        raise ValueError("Invalid geocoding response format.")

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((requests.exceptions.RequestException, requests.exceptions.Timeout))
)
@weather_breaker
def fetch_weather_data(lat: float, lon: float) -> dict:
    url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
        "&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,uv_index_max"
        "&timezone=auto"
    )
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    
    try:
        validated_weather = WeatherResponseSchema(**response.json())
        return validated_weather.model_dump()
    except ValidationError as e:
        logger.error(f"Weather API changed schema! {e}")
        raise ValueError("Invalid weather response format.")
