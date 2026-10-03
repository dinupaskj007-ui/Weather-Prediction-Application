import requests
import pybreaker
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from pydantic import BaseModel, ValidationError
import logging
from typing import List

# Setup circuit breaker: trip after 3 failures, reset after 60 seconds
weather_breaker = pybreaker.CircuitBreaker(fail_max=3, reset_timeout=60)
logger = logging.getLogger(__name__)

# Pydantic Schemas for Strict Validation (Security Boundary)
class CurrentWeather(BaseModel):
    temperature_2m: float
    relative_humidity_2m: int
    weather_code: int

class DailyForecast(BaseModel):
    time: List[str]
    temperature_2m_max: List[float]
    temperature_2m_min: List[float]
    precipitation_sum: List[float]

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

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((requests.exceptions.RequestException, requests.exceptions.Timeout))
)
@weather_breaker
def fetch_coordinates(city: str) -> CityGeo:
    """Fetch coordinates with exponential backoff and circuit breaker."""
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    
    data = response.json()
    if "results" not in data or not data["results"]:
        raise ValueError(f"City '{city}' not found.")
        
    try:
        # Strict validation
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
    """Fetch weather data with strict Pydantic validation."""
    url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
        "&current=temperature_2m,relative_humidity_2m,weather_code"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
        "&timezone=auto"
    )
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    
    try:
        # Strict schema validation boundary
        validated_weather = WeatherResponseSchema(**response.json())
        return validated_weather.model_dump()
    except ValidationError as e:
        logger.error(f"Weather API changed schema! {e}")
        raise ValueError("Invalid weather response format.")
