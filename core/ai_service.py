import os
import json
import logging
from datetime import datetime
from pydantic import BaseModel, Field

logger = logging.getLogger("SL-Weather-AI")

class AIAnalysis(BaseModel):
    synthetic_impact_statement: str = Field(description="A hyper-local impact statement synthesizing the current weather and local alerts. Max 2 sentences.")
    anomaly_level: str = Field(description="Anomaly level based on 5-day forecast or active local DMC alerts. Either 'NORMAL', 'WARNING', or 'SEVERE'.")
    anomaly_reason: str = Field(description="Short reason for the anomaly level. If NORMAL, write 'Typical conditions'.")
    is_emergency: bool = Field(description="True if the anomaly_level is SEVERE or there is an active local disaster alert (e.g. landslides, rough seas).")

def get_monsoon_context(month: int) -> str:
    """Determine the active monsoon season for Sri Lanka."""
    if 5 <= month <= 9:
        return "Yala Monsoon (Southwest). Heavy rain in Western, Southern, Central, and Sabaragamuwa provinces. Mountain landslide vigilance."
    elif 12 <= month or month <= 2:
        return "Maha Monsoon (Northeast). Rains across Northern, North Central, Eastern, and Uva provinces. Lowland flooding watch."
    elif month in [3, 4, 10, 11]:
        return "Inter-monsoon period. Frequent afternoon convective thunderstorms with intense lightning strikes across the island."
    return "Tropical maritime climate."

def generate_deterministic_meteorological_insight(province: str, district: str, weather_data: dict, dmc_alert: dict) -> dict:
    """
    Authoritative local Sri Lankan meteorological engine.
    Executes in < 1ms without blocking the client on third-party cloud LLM outages.
    """
    curr = weather_data.get("current", {})
    temp = round(curr.get("temperature_2m", 28.0), 1)
    humidity = curr.get("relative_humidity_2m", 78)
    code = curr.get("weather_code", 0)
    wind = round(curr.get("wind_speed_10m", 10.0), 1)

    daily = weather_data.get("daily", {})
    uv_list = daily.get("uv_index_max", [0])
    uv = uv_list[0] if uv_list else 0

    dmc_msg = dmc_alert.get("message", "")
    severity = dmc_alert.get("severity", "NORMAL")
    threat = dmc_alert.get("threat_type", "Standard Conditions")
    is_emergency = severity in ["SEVERE", "RED ALERT"]

    # 1. Critical Disaster Mode Override
    if is_emergency:
        statement = f"CRITICAL DMC ADVISORY for {district}: {dmc_msg} High caution advised along waterways and slopes."
        return {
            "synthetic_impact_statement": statement,
            "anomaly_level": "SEVERE",
            "anomaly_reason": threat,
            "is_emergency": True
        }

    # 2. Thunderstorm / Storm codes (WMO 95, 96, 99)
    if code >= 95:
        statement = f"Convective thunderstorm activity active in {district} ({temp}°C, {humidity}% humidity). Stay indoors during lightning discharge and avoid open fields."
        return {
            "synthetic_impact_statement": statement,
            "anomaly_level": "WARNING",
            "anomaly_reason": "Severe Lightning & Thunderstorm",
            "is_emergency": False
        }

    # 3. Rain & Shower codes (WMO 51-67, 80-82)
    if code in [61, 63, 65, 80, 81, 82]:
        statement = f"Precipitation bands crossing {district} with {temp}°C and {humidity}% humidity. Reduced driving visibility and slippery surfaces expected."
        return {
            "synthetic_impact_statement": statement,
            "anomaly_level": "WARNING" if severity == "WARNING" else "NORMAL",
            "anomaly_reason": "Active Monsoonal Showers",
            "is_emergency": False
        }

    # 4. High UV Warning (Tropical Heat Index)
    if uv >= 8.5:
        statement = f"Elevated solar UV Index ({uv}) in {district} at {temp}°C. Hydrate regularly and limit prolonged unshielded midday sun exposure."
        return {
            "synthetic_impact_statement": statement,
            "anomaly_level": "WARNING" if severity == "ADVISORY" else "NORMAL",
            "anomaly_reason": "High Tropical UV Index",
            "is_emergency": False
        }

    # 5. Coastal / High Wind Warning
    if wind >= 35.0:
        statement = f"Breezy coastal conditions in {district} with wind gusts reaching {wind} km/h at {temp}°C. {dmc_msg}"
        return {
            "synthetic_impact_statement": statement,
            "anomaly_level": "NORMAL",
            "anomaly_reason": "Elevated Wind Speeds",
            "is_emergency": False
        }

    # 6. Standard Nominal Microclimate
    statement = f"Favorable meteorological conditions in {district} ({temp}°C, {humidity}% humidity, {wind} km/h wind). {dmc_msg}"
    return {
        "synthetic_impact_statement": statement,
        "anomaly_level": "NORMAL",
        "anomaly_reason": "Typical conditions",
        "is_emergency": False
    }

# In-memory LRU cache for synthesized insights
_ai_cache = {}

def synthesize_weather_context(province: str, district: str, weather_data: dict, dmc_alert: dict) -> dict:
    """
    Synthesizes meteorological context with sub-second performance.
    Guarantees the meteorological API responds in under 1 second under any network condition.
    """
    cache_key = f"{district.lower()}_{datetime.now().hour}"
    if cache_key in _ai_cache:
        return _ai_cache[cache_key]

    # Always generate authoritative deterministic insight instantly
    insight = generate_deterministic_meteorological_insight(province, district, weather_data, dmc_alert)
    _ai_cache[cache_key] = insight
    return insight
