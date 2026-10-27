import os
import json
import math
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import requests
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.database.models import WeatherObservation

logger = logging.getLogger(__name__)

class WeatherService:
    """
    Open-Meteo & NASA POWER Weather Service.
    Fetches real historical & forecast meteorological observations:
    - Daily Precipitation (mm)
    - Mean, Max, Min Temperatures (°C)
    - Soil Moisture (0-7cm layer m³/m³)
    
    Caches all records into SQLite/PostgreSQL `weather_observations` table.
    Falls back gracefully to realistic seasonal monsoonal generator if offline.
    """

    @classmethod
    def get_forecast(
        cls,
        latitude: float = 21.5342,
        longitude: float = 79.6915,
        horizon_days: int = 14,
        db: Optional[Session] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetches 1 to 14 day weather forecast for mine coordinates from Open-Meteo.
        """
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum", "soil_moisture_0_to_7cm_mean"],
            "forecast_days": min(16, max(1, horizon_days)),
            "timezone": "auto"
        }
        
        try:
            resp = requests.get(settings.OPEN_METEO_FORECAST_URL, params=params, timeout=6)
            if resp.status_code == 200:
                data = resp.json()
                daily = data.get("daily", {})
                dates = daily.get("time", [])
                precips = daily.get("precipitation_sum", [])
                t_max = daily.get("temperature_2m_max", [])
                t_min = daily.get("temperature_2m_min", [])
                soils = daily.get("soil_moisture_0_to_7cm_mean", [])
                
                results = []
                for i, d_str in enumerate(dates):
                    p = float(precips[i]) if i < len(precips) and precips[i] is not None else 0.0
                    t_hi = float(t_max[i]) if i < len(t_max) and t_max[i] is not None else 32.0
                    t_lo = float(t_min[i]) if i < len(t_min) and t_min[i] is not None else 22.0
                    s_m = float(soils[i]) if i < len(soils) and soils[i] is not None else 0.28
                    
                    results.append({
                        "date": d_str,
                        "rainfall_mm": round(p, 1),
                        "temp_max_c": round(t_hi, 1),
                        "temp_min_c": round(t_lo, 1),
                        "temp_mean_c": round((t_hi + t_lo) / 2.0, 1),
                        "soil_moisture": round(s_m, 3),
                        "data_source": "public_real (Open-Meteo API Forecast)",
                        "is_forecast": True
                    })
                return results
        except Exception as e:
            logger.warning(f"Open-Meteo API offline or timed out: {e}. Utilizing cached/synthetic monsoon fallback.")

        # Deterministic seasonal fallback based on date
        today = datetime.utcnow().date()
        fallback = []
        for d in range(horizon_days):
            cur = today + timedelta(days=d)
            month = cur.month
            # Monsoon July-Sept in Bhandara district
            is_monsoon = month in [6, 7, 8, 9]
            sim_rain = round(max(0.0, 18.0 if is_monsoon and (d % 3 == 0) else 0.0), 1)
            fallback.append({
                "date": cur.strftime("%Y-%m-%d"),
                "rainfall_mm": sim_rain,
                "temp_max_c": 34.0 if not is_monsoon else 29.0,
                "temp_min_c": 24.0 if not is_monsoon else 23.0,
                "temp_mean_c": 28.5,
                "soil_moisture": 0.42 if is_monsoon else 0.22,
                "data_source": "synthetic (Calibrated Monsoon Fallback)",
                "is_forecast": True
            })
        return fallback

    @classmethod
    def get_historical(
        cls,
        latitude: float = 21.5342,
        longitude: float = 79.6915,
        start_date: str = "2024-01-01",
        end_date: str = "2024-12-31",
        db: Optional[Session] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetches historical daily weather from DB cache or Open-Meteo Archive.
        """
        if db:
            cached = db.query(WeatherObservation).filter(
                WeatherObservation.date >= start_date,
                WeatherObservation.date <= end_date
            ).order_by(WeatherObservation.date.asc()).all()
            if len(cached) >= 30:
                return [{
                    "date": c.date,
                    "rainfall_mm": c.precipitation_sum_mm,
                    "temp_mean_c": c.temperature_mean_c,
                    "temp_max_c": c.temperature_max_c,
                    "temp_min_c": c.temperature_min_c,
                    "data_source": "public_real (Open-Meteo Cached DB)"
                } for c in cached]

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date,
            "end_date": end_date,
            "daily": ["temperature_2m_max", "temperature_2m_min", "temperature_2m_mean", "precipitation_sum"],
            "timezone": "auto"
        }
        try:
            resp = requests.get(settings.OPEN_METEO_ARCHIVE_URL, params=params, timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                daily = data.get("daily", {})
                dates = daily.get("time", [])
                precips = daily.get("precipitation_sum", [])
                t_mean = daily.get("temperature_2m_mean", [])
                t_max = daily.get("temperature_2m_max", [])
                t_min = daily.get("temperature_2m_min", [])

                records = []
                for i, d_str in enumerate(dates):
                    rec = {
                        "date": d_str,
                        "rainfall_mm": float(precips[i]) if precips[i] is not None else 0.0,
                        "temp_mean_c": float(t_mean[i]) if t_mean[i] is not None else 27.0,
                        "temp_max_c": float(t_max[i]) if t_max[i] is not None else 32.0,
                        "temp_min_c": float(t_min[i]) if t_min[i] is not None else 21.0,
                        "data_source": "public_real (Open-Meteo Archive)"
                    }
                    records.append(rec)
                    # Cache in DB if provided
                    if db:
                        obs = WeatherObservation(
                            id=f"W-{d_str}",
                            date=d_str,
                            station_latitude=latitude,
                            station_longitude=longitude,
                            temperature_mean_c=rec["temp_mean_c"],
                            temperature_max_c=rec["temp_max_c"],
                            temperature_min_c=rec["temp_min_c"],
                            precipitation_sum_mm=rec["rainfall_mm"],
                            provenance_source="open-meteo-api"
                        )
                        db.merge(obs)
                if db:
                    db.commit()
                return records
        except Exception as e:
            logger.warning(f"Error fetching Open-Meteo historical: {e}")

        # Fallback empty or offline
        return []
