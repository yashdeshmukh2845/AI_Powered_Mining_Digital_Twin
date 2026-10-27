import os
from typing import Dict, Any

class Settings:
    PROJECT_NAME: str = "MOIL Manganese Intelligence — AI-Powered Mining Digital Twin"
    VERSION: str = "2.0.0"
    
    # Non-negotiable design rule disclaimers (The Subsurface Trap)
    SUBSURFACE_TRAP_DISCLAIMER: str = (
        "Satellite and remote-sensing data (rainfall, soil moisture, NDVI, LST, SAR) provide surface environmental context "
        "(weather disruption, haul-road friction, pit flooding risks, and exploration drill planning). "
        "Satellite sensors CANNOT directly detect underground manganese ore. "
        "Subsurface reserve estimation is strictly derived from borehole core samples, chemical laboratory assays, and geostatistical block modeling."
    )
    
    SURFACE_MAP_DISCLAIMER: str = (
        "Surface Exploration Priority Map: Guides where to drill next based on structural fault proximity and borehole coverage gaps. "
        "Does not indicate ore at depth."
    )
    
    DEMO_DATA_LABEL: str = (
        "Demo data - replace via the Data Ingestion pipeline with MOIL data"
    )
    
    # Configurable Mine Registry
    MINES: Dict[str, Dict[str, Any]] = {
        "MINE-001": {
            "id": "MINE-001",
            "name": "Dongri Buzurg Manganese Mine",
            "code": "DBM-01",
            "district": "Bhandara District",
            "state": "Maharashtra, India",
            "location": "Bhandara District, Maharashtra, India",
            "latitude": 21.5342,
            "longitude": 79.6915,
            "elevation": 320.0,
            "operational_status": "Active",
            "illustrative_daily_target_tonnes": 2500.0,
            "target_note": "Illustrative benchmark daily target unless calibrated with official MOIL production quota",
            "ore_type": "Manganese Gondite (Pyrolusite, Cryptomelane, Braunite)",
            "bulk_density_default": 3.4
        },
        "MINE-002": {
            "id": "MINE-002",
            "name": "Mansar Manganese Mine",
            "code": "MSM-02",
            "district": "Nagpur District",
            "state": "Maharashtra, India",
            "location": "Nagpur District, Maharashtra, India",
            "latitude": 21.3912,
            "longitude": 79.2568,
            "elevation": 305.0,
            "operational_status": "Active",
            "illustrative_daily_target_tonnes": 1800.0,
            "target_note": "Illustrative benchmark daily target",
            "ore_type": "Manganese Bedded Deposit",
            "bulk_density_default": 3.3
        },
        "MINE-003": {
            "id": "MINE-003",
            "name": "Balaghat Manganese Mine",
            "code": "BGM-03",
            "district": "Balaghat District",
            "state": "Madhya Pradesh, India",
            "location": "Balaghat District, Madhya Pradesh, India",
            "latitude": 21.8134,
            "longitude": 80.1843,
            "elevation": 345.0,
            "operational_status": "Active",
            "illustrative_daily_target_tonnes": 3200.0,
            "target_note": "Illustrative benchmark daily target",
            "ore_type": "Deep Underground & Open Cast Manganese Reef",
            "bulk_density_default": 3.5
        }
    }
    
    # Open-Meteo weather endpoint
    OPEN_METEO_ARCHIVE_URL: str = "https://archive-api.open-meteo.com/v1/archive"
    OPEN_METEO_FORECAST_URL: str = "https://api.open-meteo.com/v1/forecast"
    
    # Physics simulator standard defaults
    EXCAVATOR_TPH: float = 350.0
    TRUCK_TPH: float = 180.0
    TRUCK_TO_EXCAVATOR_RATIO: float = 1.5
    RAIN_SPEED_PENALTY_THRESHOLD_MM: float = 10.0
    RAIN_SPEED_PENALTY_RATE: float = 0.015  # 1.5% speed penalty per mm above threshold

settings = Settings()
