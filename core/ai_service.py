import os
import json
from datetime import datetime
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

class AIAnalysis(BaseModel):
    synthetic_impact_statement: str = Field(description="A hyper-local impact statement synthesizing the current weather and local alerts. Max 2 sentences.")
    anomaly_level: str = Field(description="Anomaly level based on 5-day forecast or active local DMC alerts. Either 'NORMAL', 'WARNING', or 'SEVERE'.")
    anomaly_reason: str = Field(description="Short reason for the anomaly level. If NORMAL, write 'Typical conditions'.")
    is_emergency: bool = Field(description="True if the anomaly_level is SEVERE or there is an active local disaster alert (e.g. landslides, rough seas).")

def get_monsoon_context(month: int) -> str:
    """Determine the monsoon season based on the month."""
    if 5 <= month <= 9:
        return "Yala Monsoon (Southwest). Characterized by heavy rains in Western, Southern, Central, and Sabaragamuwa provinces. High risk of landslides in central highlands."
    elif 12 <= month or month <= 2:
        return "Maha Monsoon (Northeast). Characterized by rains in Northern, North Central, Eastern, and Uva provinces. Risk of flooding."
    elif month in [3, 4, 10, 11]:
        return "Inter-monsoon period. Characterized by afternoon thunderstorms and severe lightning strikes across the island."
    return "Typical tropical climate."

def synthesize_weather_context(province: str, district: str, weather_data: dict, dmc_alert: dict) -> dict:
    """Uses Gemini to synthesize context, applying Monsoon-Aware Prompting and Local Conflict Resolution."""
    try:
        client = genai.Client()
    except Exception:
        # Fallback if no API key is configured
        is_emerg = dmc_alert.get("severity") in ["SEVERE", "RED ALERT"]
        return {
            "synthetic_impact_statement": f"Current data for {district} retrieved. {dmc_alert.get('message', '')}",
            "anomaly_level": "SEVERE" if is_emerg else "NORMAL",
            "anomaly_reason": "AI client not initialized.",
            "is_emergency": is_emerg
        }
    
    current_month = datetime.now().month
    monsoon_context = get_monsoon_context(current_month)
    
    prompt = f"""
    You are an authoritative Sri Lankan Meteorology AI Assistant.
    Analyze the weather for {district}, {province} Province, Sri Lanka.
    
    Temporal/Geospatial Context:
    Current Month: {current_month}
    Monsoon Season: {monsoon_context}
    
    Global Weather API Data (may lag or hallucinate microclimates):
    {json.dumps(weather_data.get('current'))}
    5-day forecast: {json.dumps(weather_data.get('daily'))}
    
    Local Ground Truth (Disaster Management Centre - HIGHEST PRIORITY):
    {json.dumps(dmc_alert)}
    
    Tasks:
    1. Conflict Resolution: If the DMC Ground Truth shows a severe alert (e.g., Landslide, Rough Seas), you MUST prioritize it over the Global API data. 
    2. Lightning Risk: If it is an inter-monsoon period, strongly emphasize severe lightning advisories for outdoor workers.
    3. Create a natural, hyper-local impact statement synthesizing this data into actionable safety advice. Ensure the language implies authoritative knowledge of Sri Lankan geography.
    4. Determine the anomaly level and emergency flag accurately based on the DMC alert and forecast.
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=AIAnalysis,
                temperature=0.2, # Keep it authoritative and deterministic
            ),
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"AI Service Error: {e}")
        return {
            "synthetic_impact_statement": "Unable to generate AI insights. Please refer to DMC alerts directly.",
            "anomaly_level": "WARNING",
            "anomaly_reason": "AI Service unavailable.",
            "is_emergency": dmc_alert.get("severity") in ["SEVERE", "RED ALERT"]
        }
