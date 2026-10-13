import math
from typing import Dict, List, Optional, Tuple

SL_DISTRICTS: Dict[str, Dict] = {
    "Colombo": {"province": "Western", "lat": 6.9271, "lon": 79.8612, "microclimate": "Urban Coastal - High Humidity"},
    "Gampaha": {"province": "Western", "lat": 7.0917, "lon": 79.9999, "microclimate": "Coastal Lowland - Heavy Monsoonal Showers"},
    "Kalutara": {"province": "Western", "lat": 6.5854, "lon": 79.9607, "microclimate": "Southwest Coast - Thunderstorms"},
    "Kandy": {"province": "Central", "lat": 7.2906, "lon": 80.6337, "microclimate": "Mid-Elevation Basin - Frequent Mist & Rain"},
    "Matale": {"province": "Central", "lat": 7.4675, "lon": 80.6234, "microclimate": "Foothills - Windward Gusts"},
    "Nuwara Eliya": {"province": "Central", "lat": 6.9497, "lon": 80.7891, "microclimate": "Highland Mountain - Dense Fog, Cold"},
    "Galle": {"province": "Southern", "lat": 6.0535, "lon": 80.2210, "microclimate": "Southern Coast - High Swell & Thundershowers"},
    "Matara": {"province": "Southern", "lat": 5.9549, "lon": 80.5550, "microclimate": "Southern Maritime - Gusty Monsoon Winds"},
    "Hambantota": {"province": "Southern", "lat": 6.1429, "lon": 81.1212, "microclimate": "Semi-Arid Coastal - High Heat Index"},
    "Jaffna": {"province": "Northern", "lat": 9.6615, "lon": 80.0255, "microclimate": "Northern Peninsula - Intense Solar UV"},
    "Kilinochchi": {"province": "Northern", "lat": 9.3803, "lon": 80.3770, "microclimate": "Northern Plains - Dry Zone Heat"},
    "Mannar": {"province": "Northern", "lat": 8.9810, "lon": 79.9044, "microclimate": "Gulf of Mannar - Strong Trade Winds"},
    "Vavuniya": {"province": "Northern", "lat": 8.7542, "lon": 80.4982, "microclimate": "Inland Plains - High Diurnal Range"},
    "Mullaitivu": {"province": "Northern", "lat": 9.2671, "lon": 80.8142, "microclimate": "Northeast Coast - Cyclonic Risk"},
    "Trincomalee": {"province": "Eastern", "lat": 8.5874, "lon": 81.2152, "microclimate": "Deep Natural Harbor - East Monsoon Inflow"},
    "Batticaloa": {"province": "Eastern", "lat": 7.7310, "lon": 81.6747, "microclimate": "Eastern Lagoon - High Coastal Humidity"},
    "Ampara": {"province": "Eastern", "lat": 7.2912, "lon": 81.6724, "microclimate": "Eastern Floodplains - Seasonal Maha Rain"},
    "Kurunegala": {"province": "North Western", "lat": 7.4863, "lon": 80.3623, "microclimate": "Intermediate Valley - Thunderstorm Corridor"},
    "Puttalam": {"province": "North Western", "lat": 8.0408, "lon": 79.8394, "microclimate": "Lagoon Belt - Hot & Strong Sea Breeze"},
    "Anuradhapura": {"province": "North Central", "lat": 8.3114, "lon": 80.4037, "microclimate": "Historic Dry Basin - Peak Heat & Tank Evap"},
    "Polonnaruwa": {"province": "North Central", "lat": 7.9403, "lon": 81.0188, "microclimate": "Dry Lowlands - High Solar Radiation"},
    "Badulla": {"province": "Uva", "lat": 6.9934, "lon": 81.0550, "microclimate": "Eastern Hill Slopes - Valley Mist & Showers"},
    "Moneragala": {"province": "Uva", "lat": 6.8714, "lon": 81.3487, "microclimate": "Lower Uva Basin - Dry Warm Winds"},
    "Ratnapura": {"province": "Sabaragamuwa", "lat": 6.6828, "lon": 80.4037, "microclimate": "Wet Zone Basin - Peak Island Rainfall & Landslides"},
    "Kegalle": {"province": "Sabaragamuwa", "lat": 7.2513, "lon": 80.3464, "microclimate": "Hill Slopes - High Landslide Sensitivity"}
}

def get_district_info(district_name: str) -> Optional[Dict]:
    """Case-insensitive district lookup."""
    for name, data in SL_DISTRICTS.items():
        if name.lower() == district_name.strip().lower():
            return {
                "district": name,
                "province": data["province"],
                "lat": data["lat"],
                "lon": data["lon"],
                "microclimate": data["microclimate"]
            }
    return None

def find_nearest_district(lat: float, lon: float) -> Tuple[str, Dict]:
    """Finds closest Sri Lankan district using Haversine formula from mobile GPS."""
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371.0 # Earth radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    closest_district = "Colombo"
    min_dist = float("inf")
    
    for name, data in SL_DISTRICTS.items():
        d = haversine(lat, lon, data["lat"], data["lon"])
        if d < min_dist:
            min_dist = d
            closest_district = name

    info = SL_DISTRICTS[closest_district].copy()
    info["district"] = closest_district
    info["distance_km"] = round(min_dist, 1)
    return closest_district, info

def search_locations(query: str) -> List[Dict]:
    """Search districts by prefix or partial match for mobile predictive search."""
    q = query.strip().lower()
    matches = []
    for name, data in SL_DISTRICTS.items():
        if q in name.lower() or q in data["province"].lower() or q in data["microclimate"].lower():
            matches.append({
                "district": name,
                "province": data["province"],
                "lat": data["lat"],
                "lon": data["lon"],
                "microclimate": data["microclimate"]
            })
    return matches
