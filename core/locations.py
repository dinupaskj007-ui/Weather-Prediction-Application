import math
from typing import Dict, List, Optional, Tuple

SL_DISTRICTS: Dict[str, Dict] = {
    "Colombo": {
        "province": "Western",
        "lat": 6.9271,
        "lon": 79.8612,
        "microclimate": "Urban Coastal - High Humidity"
    },
    "Gampaha": {
        "province": "Western",
        "lat": 7.0917,
        "lon": 79.9999,
        "microclimate": "Coastal Lowland - Heavy Monsoonal Showers"
    },
    "Kalutara": {
        "province": "Western",
        "lat": 6.5854,
        "lon": 79.9607,
        "microclimate": "Southwest Coast - Thunderstorms"
    },
    "Kandy": {
        "province": "Central",
        "lat": 7.2906,
        "lon": 80.6337,
        "microclimate": "Mid-Elevation Basin - Frequent Mist & Rain"
    },
    "Matale": {
        "province": "Central",
        "lat": 7.4675,
        "lon": 80.6234,
        "microclimate": "Foothills - Windward Gusts"
    },
    "Nuwara Eliya": {
        "province": "Central",
        "lat": 6.9497,
        "lon": 80.7891,
        "microclimate": "Highland Mountain - Dense Fog, Cold"
    },
    "Galle": {
        "province": "Southern",
        "lat": 6.0535,
        "lon": 80.2210,
        "microclimate": "Southern Coast - High Swell & Thundershowers"
    },
    "Matara": {
        "province": "Southern",
        "lat": 5.9549,
        "lon": 80.5550,
        "microclimate": "Southern Maritime - Gusty Monsoon Winds"
    },
    "Hambantota": {
        "province": "Southern",
        "lat": 6.1429,
        "lon": 81.1212,
        "microclimate": "Semi-Arid Coastal - High Heat Index"
    },
    "Jaffna": {
        "province": "Northern",
        "lat": 9.6615,
        "lon": 80.0255,
        "microclimate": "Northern Peninsula - Intense Solar UV"
    },
    "Kilinochchi": {
        "province": "Northern",
        "lat": 9.3803,
        "lon": 80.3770,
        "microclimate": "Northern Plains - Dry Zone Heat"
    },
    "Mannar": {
        "province": "Northern",
        "lat": 8.9810,
        "lon": 79.9044,
        "microclimate": "Gulf of Mannar - Strong Trade Winds"
    },
    "Vavuniya": {
        "province": "Northern",
        "lat": 8.7542,
        "lon": 80.4982,
        "microclimate": "Inland Plains - High Diurnal Range"
    },
    "Mullaitivu": {
        "province": "Northern",
        "lat": 9.2671,
        "lon": 80.8142,
        "microclimate": "Northeast Coast - Cyclonic Risk"
    },
    "Trincomalee": {
        "province": "Eastern",
        "lat": 8.5874,
        "lon": 81.2152,
        "microclimate": "Deep Natural Harbor - East Monsoon Inflow"
    },
    "Batticaloa": {
        "province": "Eastern",
        "lat": 7.7310,
        "lon": 81.6747,
        "microclimate": "Eastern Lagoon - High Coastal Humidity"
    },
    "Ampara": {
        "province": "Eastern",
        "lat": 7.2912,
        "lon": 81.6724,
        "microclimate": "Eastern Floodplains - Seasonal Maha Rain"
    },
    "Kurunegala": {
        "province": "North Western",
        "lat": 7.4863,
        "lon": 80.3623,
        "microclimate": "Intermediate Valley - Thunderstorm Corridor"
    },
    "Puttalam": {
        "province": "North Western",
        "lat": 8.0408,
        "lon": 79.8394,
        "microclimate": "Lagoon Belt - Hot & Strong Sea Breeze"
    },
    "Anuradhapura": {
        "province": "North Central",
        "lat": 8.3114,
        "lon": 80.4037,
        "microclimate": "Historic Dry Basin - Peak Heat & Tank Evap"
    },
    "Polonnaruwa": {
        "province": "North Central",
        "lat": 7.9403,
        "lon": 81.0188,
        "microclimate": "Dry Lowlands - High Solar Radiation"
    },
    "Badulla": {
        "province": "Uva",
        "lat": 6.9934,
        "lon": 81.0550,
        "microclimate": "Eastern Hill Slopes - Valley Mist & Showers"
    },
    "Monaragala": {
        "province": "Uva",
        "lat": 6.8714,
        "lon": 81.3487,
        "microclimate": "Lower Uva Basin - Dry Warm Winds"
    },
    "Ratnapura": {
        "province": "Sabaragamuwa",
        "lat": 6.6828,
        "lon": 80.4037,
        "microclimate": "Wet Zone Basin - Peak Island Rainfall & Landslides"
    },
    "Kegalle": {
        "province": "Sabaragamuwa",
        "lat": 7.2513,
        "lon": 80.3464,
        "microclimate": "Hill Slopes - High Landslide Sensitivity"
    }
}

# Alias Moneragala spelling to Monaragala
SL_DISTRICTS["Moneragala"] = SL_DISTRICTS["Monaragala"]

SL_DISTRICT_CITIES: Dict[str, List[str]] = {
    "Ampara": [
        "Ampara", "Kalmunai", "Akkaraipattu", "Sammanthurai", "Pottuvil"
    ],
    "Anuradhapura": [
        "Anuradhapura", "Kekirawa", "Tambuttegama", "Medawachchiya", "Eppawala"
    ],
    "Badulla": [
        "Badulla", "Bandarawela", "Haputale", "Mahiyanganaya", "Welimada"
    ],
    "Batticaloa": [
        "Batticaloa", "Kattankudy", "Eravur", "Valachchenai", "Kalkudah"
    ],
    "Colombo": [
        "Colombo", "Dehiwala-Mount Lavinia", "Moratuwa",
        "Sri Jayawardenepura Kotte", "Maharagama", "Nugegoda"
    ],
    "Galle": [
        "Galle", "Ambalangoda", "Hikkaduwa", "Elpitiya", "Karapitiya"
    ],
    "Gampaha": [
        "Gampaha", "Negombo", "Kelaniya", "Wattala",
        "Ja-Ela", "Minuwangoda", "Katunayake"
    ],
    "Hambantota": [
        "Hambantota", "Tangalle", "Tissamaharama", "Ambalantota", "Beliatta"
    ],
    "Jaffna": [
        "Jaffna", "Point Pedro", "Chavakachcheri", "Kankesanthurai", "Nallur"
    ],
    "Kalutara": [
        "Kalutara", "Panadura", "Horana", "Beruwala", "Aluthgama", "Matugama"
    ],
    "Kandy": [
        "Kandy", "Peradeniya", "Gampola",
        "Nawalapitiya", "Kadugannawa", "Katugastota"
    ],
    "Kegalle": [
        "Kegalle", "Mawanella", "Warakapola", "Rambukkana", "Ruwanwella"
    ],
    "Kilinochchi": [
        "Kilinochchi", "Pallai", "Paranthan", "Pooneryn"
    ],
    "Kurunegala": [
        "Kurunegala", "Kuliyapitiya", "Pannala", "Narammala", "Wariyapola"
    ],
    "Mannar": [
        "Mannar", "Pesalai", "Murunkan", "Silavathurai"
    ],
    "Matale": [
        "Matale", "Dambulla", "Galewela", "Rattota", "Ukuwela"
    ],
    "Matara": [
        "Matara", "Weligama", "Akuressa", "Dikwella", "Hakmana"
    ],
    "Monaragala": [
        "Monaragala", "Wellawaya", "Bibile", "Kataragama", "Buttala"
    ],
    "Mullaitivu": [
        "Mullaitivu", "Puthukkudiyiruppu", "Mankulam", "Oddusuddan"
    ],
    "Nuwara Eliya": [
        "Nuwara Eliya", "Hatton", "Talawakelle", "Nanu Oya", "Norwood"
    ],
    "Polonnaruwa": [
        "Polonnaruwa", "Kaduruwela", "Hingurakgoda", "Medirigiriya"
    ],
    "Puttalam": [
        "Puttalam", "Chilaw", "Wennappuwa", "Nattandiya", "Kalpitiya"
    ],
    "Ratnapura": [
        "Ratnapura", "Balangoda", "Embilipitiya", "Pelmadulla", "Eheliyagoda"
    ],
    "Trincomalee": [
        "Trincomalee", "Kinniya", "Mutur", "Kantalai", "Nilaveli"
    ],
    "Vavuniya": [
        "Vavuniya", "Cheddikulam", "Nedunkeni", "Pampaimadu"
    ]
}

SL_DISTRICT_CITIES["Moneragala"] = SL_DISTRICT_CITIES["Monaragala"]

# Compact tuple dataset: (city, district, province, lat, lon, microclimate)
_RAW_CITIES: List[Tuple[str, str, str, float, float, str]] = [
    # Ampara
    ("Ampara", "Ampara", "Eastern", 7.2912, 81.6724,
     "Eastern Floodplains - Seasonal Maha Rain"),
    ("Kalmunai", "Ampara", "Eastern", 7.4167, 81.8333,
     "Eastern Coast - Maritime Humidity"),
    ("Akkaraipattu", "Ampara", "Eastern", 7.2167, 81.8500,
     "Eastern Coast - Coastal Showers"),
    ("Sammanthurai", "Ampara", "Eastern", 7.3667, 81.8000,
     "Eastern Lowlands - Agricultural Zone"),
    ("Pottuvil", "Ampara", "Eastern", 6.8667, 81.8333,
     "Southeast Coast - High Swell & Arid Breeze"),

    # Anuradhapura
    ("Anuradhapura", "Anuradhapura", "North Central", 8.3114, 80.4037,
     "Historic Dry Basin - Peak Heat & Tank Evap"),
    ("Kekirawa", "Anuradhapura", "North Central", 8.0333, 80.6000,
     "Dry Inland Plain - Intermittent Heat"),
    ("Tambuttegama", "Anuradhapura", "North Central", 8.1667, 80.3000,
     "Agricultural Lowlands - Tank Breeze"),
    ("Medawachchiya", "Anuradhapura", "North Central", 8.5333, 80.5000,
     "Northern Junction Plain - High Solar Index"),
    ("Eppawala", "Anuradhapura", "North Central", 8.1500, 80.4167,
     "Central Dry Plains - Tropical Heat"),

    # Badulla
    ("Badulla", "Badulla", "Uva", 6.9934, 81.0550,
     "Eastern Hill Slopes - Valley Mist & Showers"),
    ("Bandarawela", "Badulla", "Uva", 6.8333, 80.9833,
     "Upcountry Basin - Cool Mountain Air & Breeze"),
    ("Haputale", "Badulla", "Uva", 6.7667, 80.9500,
     "Southern Ridge - Dense Cloud Gap & Chill"),
    ("Mahiyanganaya", "Badulla", "Uva", 7.3167, 81.0000,
     "Mahaweli Valley - Warm Intermediate Climate"),
    ("Welimada", "Badulla", "Uva", 6.9000, 80.9000,
     "Highland Valley - Mild Temperate Showers"),

    # Batticaloa
    ("Batticaloa", "Batticaloa", "Eastern", 7.7310, 81.6747,
     "Eastern Lagoon - High Coastal Humidity"),
    ("Kattankudy", "Batticaloa", "Eastern", 7.6833, 81.7167,
     "Maritime Coast - High Heat & Sea Breeze"),
    ("Eravur", "Batticaloa", "Eastern", 7.7833, 81.6000,
     "Lagoon Edge - High Humidity"),
    ("Valachchenai", "Batticaloa", "Eastern", 7.9167, 81.5333,
     "Estuary Lowlands - Seasonal Rains"),
    ("Kalkudah", "Batticaloa", "Eastern", 7.9167, 81.5667,
     "Bay Coast - Tropical Sun & Coastal Showers"),

    # Colombo
    ("Colombo", "Colombo", "Western", 6.9271, 79.8612,
     "Urban Coastal - High Humidity"),
    ("Dehiwala-Mount Lavinia", "Colombo", "Western", 6.8333, 79.8667,
     "Southern Metro Coast - Oceanic Winds"),
    ("Moratuwa", "Colombo", "Western", 6.7730, 79.8816,
     "Coastal Lagoon Fringe - Maritime Air"),
    ("Sri Jayawardenepura Kotte", "Colombo", "Western", 6.8906, 79.9042,
     "Capital Wet Zone - Urban Wet Climate"),
    ("Maharagama", "Colombo", "Western", 6.8500, 79.9333,
     "Inland Suburban - Afternoon Heat & Showers"),
    ("Nugegoda", "Colombo", "Western", 6.8667, 79.8997,
     "Metro Basin - Dense Urban Microclimate"),

    # Galle
    ("Galle", "Galle", "Southern", 6.0535, 80.2210,
     "Southern Coast - High Swell & Thundershowers"),
    ("Ambalangoda", "Galle", "Southern", 6.2333, 80.0500,
     "Southwest Coastline - Maritime Showers"),
    ("Hikkaduwa", "Galle", "Southern", 6.1333, 80.1000,
     "Reef Coast - Tropical Breezes & Coastal Rain"),
    ("Elpitiya", "Galle", "Southern", 6.2667, 80.1500,
     "Inland Foothills - Heavy Tropical Downpours"),
    ("Karapitiya", "Galle", "Southern", 6.0667, 80.2333,
     "Coastal Ridge - High Relative Humidity"),

    # Gampaha
    ("Gampaha", "Gampaha", "Western", 7.0917, 79.9999,
     "Coastal Lowland - Heavy Monsoonal Showers"),
    ("Negombo", "Gampaha", "Western", 7.2083, 79.8358,
     "Lagoon City - Ocean Swells & High Humidity"),
    ("Kelaniya", "Gampaha", "Western", 6.9550, 79.9189,
     "Kelani River Valley - Heavy Riverine Showers"),
    ("Wattala", "Gampaha", "Western", 6.9897, 79.8917,
     "Coastal Belt - Tropical Maritime Air"),
    ("Ja-Ela", "Gampaha", "Western", 7.0750, 79.8917,
     "Estuary Plain - Monsoonal Thunderstorms"),
    ("Minuwangoda", "Gampaha", "Western", 7.1667, 79.9500,
     "Inland Lowland - Convective Showers"),
    ("Katunayake", "Gampaha", "Western", 7.1694, 79.8897,
     "Airport Corridor - Coastal Thermal Currents"),

    # Hambantota
    ("Hambantota", "Hambantota", "Southern", 6.1429, 81.1212,
     "Semi-Arid Coastal - High Heat Index"),
    ("Tangalle", "Hambantota", "Southern", 6.0242, 80.7942,
     "Southern Bay - Strong Ocean Winds"),
    ("Tissamaharama", "Hambantota", "Southern", 6.2833, 81.2833,
     "Dry Tank Zone - Sunny High UV Exposure"),
    ("Ambalantota", "Hambantota", "Southern", 6.1167, 81.0167,
     "Walawe River Basin - Warm Maritime Breeze"),
    ("Beliatta", "Hambantota", "Southern", 6.0500, 80.7167,
     "Intermediate Foothills - Afternoon Cloud Cover"),

    # Jaffna
    ("Jaffna", "Jaffna", "Northern", 9.6615, 80.0255,
     "Northern Peninsula - Intense Solar UV"),
    ("Point Pedro", "Jaffna", "Northern", 9.8167, 80.2333,
     "Northernmost Tip - Strong Coastal Wind Inflow"),
    ("Chavakachcheri", "Jaffna", "Northern", 9.6500, 80.1500,
     "Peninsula Core - Warm Dry Breezes"),
    ("Kankesanthurai", "Jaffna", "Northern", 9.8000, 80.0333,
     "Northern Port - Intense Solar Index & Sea Gusts"),
    ("Nallur", "Jaffna", "Northern", 9.6700, 80.0300,
     "Peninsula Plain - High Temperature & Dry Soil"),

    # Kalutara
    ("Kalutara", "Kalutara", "Western", 6.5854, 79.9607,
     "Southwest Coast - Thunderstorms"),
    ("Panadura", "Kalutara", "Western", 6.7131, 79.9074,
     "Coastal Strip - Strong Southwest Monsoons"),
    ("Horana", "Kalutara", "Western", 6.7167, 80.0667,
     "Wet Zone Inland - Frequent Heavy Rains"),
    ("Beruwala", "Kalutara", "Western", 6.4789, 79.9828,
     "Fishery Coast - High Maritime Swell"),
    ("Aluthgama", "Kalutara", "Western", 6.4333, 80.0000,
     "Bentota Estuary - Tropical Humid Breeze"),
    ("Matugama", "Kalutara", "Western", 6.5167, 80.1167,
     "Lowland Foothills - Dense Rubber Belt Rainfall"),

    # Kandy
    ("Kandy", "Kandy", "Central", 7.2906, 80.6337,
     "Mid-Elevation Basin - Frequent Mist & Rain"),
    ("Peradeniya", "Kandy", "Central", 7.2667, 80.6000,
     "River Basin - Morning Mist & Cool Breezes"),
    ("Gampola", "Kandy", "Central", 7.1667, 80.5667,
     "Mountain Valley - High Annual Rainfall"),
    ("Nawalapitiya", "Kandy", "Central", 7.0500, 80.5333,
     "Central Foothills - Intense Monsoonal Showers"),
    ("Kadugannawa", "Kandy", "Central", 7.2500, 80.5167,
     "Mountain Pass - Sudden Mist & Gusts"),
    ("Katugastota", "Kandy", "Central", 7.3167, 80.6167,
     "Mahaweli Valley - Humid River Basin"),

    # Kegalle
    ("Kegalle", "Kegalle", "Sabaragamuwa", 7.2513, 80.3464,
     "Hill Slopes - High Landslide Sensitivity"),
    ("Mawanella", "Kegalle", "Sabaragamuwa", 7.2500, 80.4500,
     "Rock Foothills - Heavy Convective Thunderstorms"),
    ("Warakapola", "Kegalle", "Sabaragamuwa", 7.2167, 80.2000,
     "Intermediate Valley - Humid Tropical Showers"),
    ("Rambukkana", "Kegalle", "Sabaragamuwa", 7.3167, 80.4000,
     "North Slope - Moderate Rainfall & Warmth"),
    ("Ruwanwella", "Kegalle", "Sabaragamuwa", 7.0500, 80.2500,
     "Kelani Catchment - Frequent Riverine Flooding"),

    # Kilinochchi
    ("Kilinochchi", "Kilinochchi", "Northern", 9.3803, 80.3770,
     "Northern Plains - Dry Zone Heat"),
    ("Pallai", "Kilinochchi", "Northern", 9.5833, 80.3000,
     "Elephant Pass Corridor - Dry Wind Channel"),
    ("Paranthan", "Kilinochchi", "Northern", 9.4333, 80.4000,
     "Agricultural Plain - High Ambient Solar Exposure"),
    ("Pooneryn", "Kilinochchi", "Northern", 9.5000, 80.2000,
     "Jaffna Lagoon Shore - Heavy Trade Winds"),

    # Kurunegala
    ("Kurunegala", "Kurunegala", "North Western", 7.4863, 80.3623,
     "Intermediate Valley - Thunderstorm Corridor"),
    ("Kuliyapitiya", "Kurunegala", "North Western", 7.4667, 80.0500,
     "Coconut Triangle - Warm Humid Climate"),
    ("Pannala", "Kurunegala", "North Western", 7.3333, 79.9833,
     "Southern Border Plains - Tropical Moisture"),
    ("Narammala", "Kurunegala", "North Western", 7.4333, 80.2167,
     "Intermediate Basin - Evening Thunderstorms"),
    ("Wariyapola", "Kurunegala", "North Western", 7.6167, 80.2333,
     "Dry Plain Transition - High Heat Index"),

    # Mannar
    ("Mannar", "Mannar", "Northern", 8.9810, 79.9044,
     "Gulf of Mannar - Strong Trade Winds"),
    ("Pesalai", "Mannar", "Northern", 9.0833, 79.8167,
     "Mannar Island Coast - Arid Sea Winds"),
    ("Murunkan", "Mannar", "Northern", 8.8500, 80.0167,
     "Giant Tank Basin - Hot Dry Zone"),
    ("Silavathurai", "Mannar", "Northern", 8.7000, 79.9167,
     "Gulf Shore - Salt Winds & High UV"),

    # Matale
    ("Matale", "Matale", "Central", 7.4675, 80.6234,
     "Foothills - Windward Gusts"),
    ("Dambulla", "Matale", "Central", 7.8600, 80.6517,
     "Dry Zone Threshold - High Solar Radiation"),
    ("Galewela", "Matale", "Central", 7.7500, 80.5667,
     "North Central Plain Fringe - Warm Breeze"),
    ("Rattota", "Matale", "Central", 7.5167, 80.6667,
     "Knuckles Range Foothills - Mist & Cold Nights"),
    ("Ukuwela", "Matale", "Central", 7.4167, 80.6333,
     "Upper Mahaweli Basin - Cool Moderate Climate"),

    # Matara
    ("Matara", "Matara", "Southern", 5.9549, 80.5550,
     "Southern Maritime - Gusty Monsoon Winds"),
    ("Weligama", "Matara", "Southern", 5.9722, 80.4289,
     "Southern Bay - Swells & Coastal Humidity"),
    ("Akuressa", "Matara", "Southern", 6.1000, 80.4833,
     "Nilwala Valley - High Landslide Risk"),
    ("Dikwella", "Matara", "Southern", 5.9667, 80.7000,
     "South Coast - Strong Ocean Currents & Sun"),
    ("Hakmana", "Matara", "Southern", 6.0833, 80.6500,
     "Inland Hills - Humid Intermittent Rain"),

    # Monaragala
    ("Monaragala", "Monaragala", "Uva", 6.8714, 81.3487,
     "Lower Uva Basin - Dry Warm Winds"),
    ("Wellawaya", "Monaragala", "Uva", 6.7333, 81.1000,
     "Southern Pass Foot - Hot Days & Mountain Breeze"),
    ("Bibile", "Monaragala", "Uva", 7.1667, 81.2167,
     "Eastern Slopes - Maha Season Showers"),
    ("Kataragama", "Monaragala", "Uva", 6.4167, 81.3333,
     "Menik River Arid Zone - Intense Heat & Dry Sun"),
    ("Buttala", "Monaragala", "Uva", 6.7500, 81.2500,
     "Eastern Lowlands - High Solar Index"),

    # Mullaitivu
    ("Mullaitivu", "Mullaitivu", "Northern", 9.2671, 80.8142,
     "Northeast Coast - Cyclonic Risk"),
    ("Puthukkudiyiruppu", "Mullaitivu", "Northern", 9.3000, 80.7000,
     "Coastal Forest Margin - High Heat"),
    ("Mankulam", "Mullaitivu", "Northern", 9.1333, 80.4500,
     "Central Vanni Plain - Intense Dry Heat"),
    ("Oddusuddan", "Mullaitivu", "Northern", 9.1500, 80.6500,
     "Inland Forest Basin - Tropical Warmth"),

    # Nuwara Eliya
    ("Nuwara Eliya", "Nuwara Eliya", "Central", 6.9497, 80.7891,
     "Highland Mountain - Dense Fog, Cold"),
    ("Hatton", "Nuwara Eliya", "Central", 6.8833, 80.6000,
     "Maskeliya Valley - Heavy Monsoon & Mist"),
    ("Talawakelle", "Nuwara Eliya", "Central", 6.9333, 80.6500,
     "Upper Kotmale Basin - Cool High Humidity"),
    ("Nanu Oya", "Nuwara Eliya", "Central", 6.9333, 80.7333,
     "High Peak Foothills - Chilly Mountain Showers"),
    ("Norwood", "Nuwara Eliya", "Central", 6.8333, 80.6167,
     "Castlereagh Basin - Cold Heavy Rainfall"),

    # Polonnaruwa
    ("Polonnaruwa", "Polonnaruwa", "North Central", 7.9403, 81.0188,
     "Dry Lowlands - High Solar Radiation"),
    ("Kaduruwela", "Polonnaruwa", "North Central", 7.9333, 81.0333,
     "Commercial Basin - Hot Dry Climate"),
    ("Hingurakgoda", "Polonnaruwa", "North Central", 8.0500, 80.9833,
     "Minneriya Plain - High Diurnal Heat"),
    ("Medirigiriya", "Polonnaruwa", "North Central", 8.1500, 81.0167,
     "North Plain Dry Forest - Extreme Sun Index"),

    # Puttalam
    ("Puttalam", "Puttalam", "North Western", 8.0408, 79.8394,
     "Lagoon Belt - Hot & Strong Sea Breeze"),
    ("Chilaw", "Puttalam", "North Western", 7.5758, 79.7953,
     "West Coast Lowland - Maritime Gusts"),
    ("Wennappuwa", "Puttalam", "North Western", 7.3667, 79.8333,
     "Southern Border Coast - Humid Breezes"),
    ("Nattandiya", "Puttalam", "North Western", 7.4167, 79.8667,
     "Intermediate Coconut Plain - Warm Days"),
    ("Kalpitiya", "Puttalam", "North Western", 8.2333, 79.7667,
     "Peninsula Lagoon - Very High Wind & Arid Sun"),

    # Ratnapura
    ("Ratnapura", "Ratnapura", "Sabaragamuwa", 6.6828, 80.4037,
     "Wet Zone Basin - Peak Island Rainfall & Landslides"),
    ("Balangoda", "Ratnapura", "Sabaragamuwa", 6.6500, 80.7000,
     "Upper Sabaragamuwa Ridge - Mist & Flash Floods"),
    ("Embilipitiya", "Ratnapura", "Sabaragamuwa", 6.3000, 80.8500,
     "Dry Transition Lowlands - Sunny Warm Days"),
    ("Pelmadulla", "Ratnapura", "Sabaragamuwa", 6.6167, 80.5500,
     "Giri Mountain Valley - High Precipitation"),
    ("Eheliyagoda", "Ratnapura", "Sabaragamuwa", 6.8500, 80.2667,
     "Northern Wet Fringe - Intense Afternoon Rain"),

    # Trincomalee
    ("Trincomalee", "Trincomalee", "Eastern", 8.5874, 81.2152,
     "Deep Natural Harbor - East Monsoon Inflow"),
    ("Kinniya", "Trincomalee", "Eastern", 8.5000, 81.1833,
     "Koddiyar Bay Edge - Humid Coastal Breeze"),
    ("Mutur", "Trincomalee", "Eastern", 8.4500, 81.2667,
     "Southern Bay Shore - Warm Ocean Current"),
    ("Kantalai", "Trincomalee", "Eastern", 8.3667, 81.0000,
     "Tank Reservoir Basin - High Solar Intensity"),
    ("Nilaveli", "Trincomalee", "Eastern", 8.6833, 81.1833,
     "Northern Beach Coast - Tropical Sun & Clear Skies"),

    # Vavuniya
    ("Vavuniya", "Vavuniya", "Northern", 8.7542, 80.4982,
     "Inland Plains - High Diurnal Range"),
    ("Cheddikulam", "Vavuniya", "Northern", 8.6667, 80.3167,
     "Southern Vanni Plains - High Temperature"),
    ("Nedunkeni", "Vavuniya", "Northern", 8.9833, 80.6500,
     "East Inland Forest - Hot Dry Winds"),
    ("Pampaimadu", "Vavuniya", "Northern", 8.7667, 80.4333,
     "Agricultural Basin - Strong Sun & Low Moisture")
]

SL_CITIES: Dict[str, Dict] = {
    city: {
        "province": prov,
        "district": dist,
        "lat": lat,
        "lon": lon,
        "microclimate": micro
    }
    for city, dist, prov, lat, lon, micro in _RAW_CITIES
}


def get_city_info(city_name: str) -> Optional[Dict]:
    """Case-insensitive city lookup returning district and coordinates."""
    c_lower = city_name.strip().lower()
    for name, data in SL_CITIES.items():
        if name.lower() == c_lower:
            return {
                "city": name,
                "district": data["district"],
                "province": data["province"],
                "lat": data["lat"],
                "lon": data["lon"],
                "microclimate": data["microclimate"]
            }
    return None


def get_district_info(district_name: str) -> Optional[Dict]:
    """Case-insensitive district lookup (falls back to city match)."""
    d_clean = district_name.strip()
    d_lower = d_clean.lower()
    for name, data in SL_DISTRICTS.items():
        if name.lower() == d_lower:
            return {
                "district": name,
                "province": data["province"],
                "lat": data["lat"],
                "lon": data["lon"],
                "microclimate": data["microclimate"]
            }

    # If queried with a city name, resolve to parent district & city coords
    city_match = get_city_info(d_clean)
    if city_match:
        return {
            "city": city_match["city"],
            "district": city_match["district"],
            "province": city_match["province"],
            "lat": city_match["lat"],
            "lon": city_match["lon"],
            "microclimate": city_match["microclimate"]
        }
    return None


def get_location_info(location_query: str) -> Optional[Dict]:
    """Resolve location by city first, then district."""
    city_info = get_city_info(location_query)
    if city_info:
        return city_info
    return get_district_info(location_query)


def find_nearest_district(lat: float, lon: float) -> Tuple[str, Dict]:
    """Find closest Sri Lankan district using Haversine formula from GPS."""
    def haversine(lat1, lon1, lat2, lon2):
        r = 6371.0  # Earth radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2))
            * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return r * c

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
    """
    Search both cities and districts by prefix or partial match.
    Prioritizes exact and starts-with matches for fast predictive search.
    """
    q = query.strip().lower()
    if not q:
        return []

    exact_matches: List[Dict] = []
    prefix_matches: List[Dict] = []
    substring_matches: List[Dict] = []
    seen = set()

    # 1. Search Cities
    for name, data in SL_CITIES.items():
        name_lower = name.lower()
        dist_lower = data["district"].lower()
        prov_lower = data["province"].lower()

        if q in name_lower or q in dist_lower or q in prov_lower:
            key = f"city:{name}"
            if key in seen:
                continue
            seen.add(key)

            entry = {
                "name": name,
                "city": name,
                "district": data["district"],
                "province": data["province"],
                "lat": data["lat"],
                "lon": data["lon"],
                "microclimate": data["microclimate"],
                "type": "city"
            }

            if name_lower == q:
                exact_matches.append(entry)
            elif name_lower.startswith(q):
                prefix_matches.append(entry)
            else:
                substring_matches.append(entry)

    # 2. Search Districts (when user searches district names)
    for name, data in SL_DISTRICTS.items():
        name_lower = name.lower()
        prov_lower = data["province"].lower()

        if q in name_lower or q in prov_lower:
            key = f"district:{name}"
            if key in seen:
                continue
            seen.add(key)

            entry = {
                "name": name,
                "city": name,
                "district": name,
                "province": data["province"],
                "lat": data["lat"],
                "lon": data["lon"],
                "microclimate": data["microclimate"],
                "type": "district"
            }

            if name_lower == q:
                exact_matches.append(entry)
            elif name_lower.startswith(q):
                prefix_matches.append(entry)
            else:
                substring_matches.append(entry)

    # Return ordered matches, capped at 30
    combined = exact_matches + prefix_matches + substring_matches
    return combined[:30]
