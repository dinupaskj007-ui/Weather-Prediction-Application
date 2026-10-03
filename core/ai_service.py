import os
import json
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

class AIAnalysis(BaseModel):
    synthetic_impact_statement: str = Field(description="A hyper-local impact statement synthesizing the current weather conditions. Max 2 sentences.")
    anomaly_level: str = Field(description="Anomaly level based on 5-day forecast. Either 'NORMAL', 'WARNING', or 'SEVERE'.")
    anomaly_reason: str = Field(description="Short reason for the anomaly level. If NORMAL, write 'Typical conditions'.")

def synthesize_weather_context(city_name: str, weather_data: dict) -> dict:
    """Uses Gemini to synthesize context and detect anomalies via structured output."""
    # Note: Requires GEMINI_API_KEY environment variable
    try:
        client = genai.Client()
    except Exception:
        # Fallback if no API key is configured locally during testing
        return {
            "synthetic_impact_statement": f"Current data for {city_name} retrieved successfully.",
            "anomaly_level": "NORMAL",
            "anomaly_reason": "AI client not initialized (check API key)."
        }
    
    prompt = f"""
    Analyze the following validated weather data for {city_name}.
    Current weather: {json.dumps(weather_data.get('current'))}
    5-day forecast: {json.dumps(weather_data.get('daily'))}
    
    Tasks:
    1. Create a natural, hyper-local impact statement about the current weather. Do not use raw numbers like 'weather code 3'. Translate to human experience.
    2. Review the 5-day forecast (max/min temps, precipitation) and flag any severe anomalies (e.g. extreme heat, high flood risk).
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=AIAnalysis,
            ),
        )
        return json.loads(response.text)
    except Exception as e:
        # Graceful fallback if AI fails
        print(f"AI Service Error: {e}")
        return {
            "synthetic_impact_statement": "Unable to generate AI insights at this time.",
            "anomaly_level": "NORMAL",
            "anomaly_reason": "AI Service unavailable."
        }
