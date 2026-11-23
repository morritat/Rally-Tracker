"""Интеграция с OpenWeatherMap API: текущая погода и прогноз для этапов."""
import os
import time
from datetime import datetime, timezone
from typing import Optional

import requests
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
load_dotenv(os.path.join(BASE_DIR, ".env"))


class WeatherService:
    API_KEY = os.environ.get("OPENWEATHER_API_KEY", "").strip()
    UNITS = os.environ.get("OPENWEATHER_UNITS", "metric")
    BASE_URL = "https://api.openweathermap.org/data/2.5"
    CACHE_TTL = 300  # 5 минут
    REQUEST_TIMEOUT = 10
    _cache = {}

    SURFACE_MAP = {
        "rain": "wet", "drizzle": "wet", "thunderstorm": "wet",
        "snow": "snow", "sleet": "snow",
        "clear": "dry", "mist": "dry", "fog": "dry", "haze": "dry",
        "clouds": "dry",
    }

    @classmethod
    def _request(cls, endpoint: str, lat: float, lon: float) -> Optional[dict]:
        if not cls.API_KEY:
            print("⚠️ OPENWEATHER_API_KEY не задан")
            return None
        try:
            response = requests.get(
                f"{cls.BASE_URL}/{endpoint}",
                params={
                    "lat": lat, "lon": lon, "appid": cls.API_KEY,
                    "units": cls.UNITS, "lang": "ru",
                },
                timeout=cls.REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            print(f"⚠️ Ошибка OpenWeatherMap [{endpoint}]: {exc}")
            return None
        except ValueError as exc:
            print(f"⚠️ OpenWeatherMap вернул не JSON: {exc}")
            return None

    @classmethod
    def _normalize(cls, item: dict) -> dict:
        weather = item.get("weather", [{}])[0]
        main = item.get("main", {})
        return {
            "temp": round(float(main.get("temp", 0))),
            "desc": weather.get("description", ""),
            "wind_speed": round(float(item.get("wind", {}).get("speed", 0))),
            "surface_type": cls.SURFACE_MAP.get(weather.get("main", "").lower(), "dry"),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

    @classmethod
    def _cache_get(cls, key):
        cached = cls._cache.get(key)
        if cached and time.monotonic() - cached[0] < cls.CACHE_TTL:
            return cached[1]
        return None

    @classmethod
    def _cache_set(cls, key, value):
        cls._cache[key] = (time.monotonic(), value)

    @classmethod
    def _forecast_for_local_time(cls, forecast: dict, target_date: str) -> Optional[dict]:
        """Выбирает ближайший 3-часовой прогноз с учётом локального времени города."""
        target = datetime.fromisoformat(str(target_date).replace("Z", "+00:00"))
        if target.tzinfo is not None:
            target = target.astimezone(timezone.utc).replace(tzinfo=None)

        tz_offset = int(forecast.get("city", {}).get("timezone", 0))
        candidates = []
        for item in forecast.get("list", []):
            dt_local = datetime.fromtimestamp(item["dt"], timezone.utc).replace(tzinfo=None)
            dt_local = dt_local + __import__("datetime").timedelta(seconds=tz_offset)
            candidates.append((abs((dt_local - target).total_seconds()), item))
        if not candidates:
            return None
        return cls._normalize(min(candidates, key=lambda x: x[0])[1])

    @classmethod
    def get_weather(cls, lat: float, lon: float, target_date: str = None) -> Optional[dict]:
        if lat is None or lon is None or not cls.API_KEY:
            return None

        cache_key = (round(float(lat), 4), round(float(lon), 4), target_date or "current")
        cached = cls._cache_get(cache_key)
        if cached:
            return cached

        # Для этапа в ближайшие 5 суток обязательно используем прогноз,
        # а не старое значение из БД. Это устраняет «зависшую» погоду.
        if target_date:
            try:
                target = datetime.fromisoformat(str(target_date).replace("Z", "+00:00"))
                now = datetime.now(timezone.utc)
                if target.tzinfo is None:
                    target = target.replace(tzinfo=timezone.utc)
                hours = (target - now).total_seconds() / 3600
                if 0 <= hours <= 120:
                    forecast = cls._request("forecast", lat, lon)
                    result = cls._forecast_for_local_time(forecast, target_date) if forecast else None
                    if result:
                        cls._cache_set(cache_key, result)
                    return result
                if hours > 120:
                    return None
            except (ValueError, TypeError, OverflowError):
                pass

        current = cls._request("weather", lat, lon)
        if not current:
            return None
        result = cls._normalize(current)
        cls._cache_set(cache_key, result)
        return result
