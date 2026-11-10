from __future__ import annotations

from typing import Any

import requests

from tools._shared import TIMEOUT, err

ALLOWED_UNITS = {"celsius", "fahrenheit"}

KNOWN_CITIES: dict[str, tuple[float, float, str]] = {
    "hanoi": (21.0285, 105.8542, "Hanoi, Vietnam"),
    "ha noi": (21.0285, 105.8542, "Hanoi, Vietnam"),
    "ho chi minh": (10.8231, 106.6297, "Ho Chi Minh City, Vietnam"),
    "saigon": (10.8231, 106.6297, "Ho Chi Minh City, Vietnam"),
    "da nang": (16.0544, 108.2022, "Da Nang, Vietnam"),
    "danang": (16.0544, 108.2022, "Da Nang, Vietnam"),
    "da lat": (11.9404, 108.4583, "Da Lat, Vietnam"),
    "hue": (16.4637, 107.5909, "Hue, Vietnam"),
    "tokyo": (35.6762, 139.6503, "Tokyo, Japan"),
    "seoul": (37.5665, 126.9780, "Seoul, South Korea"),
    "singapore": (1.3521, 103.8198, "Singapore"),
    "london": (51.5074, -0.1278, "London, United Kingdom"),
    "new york": (40.7128, -74.0060, "New York, United States"),
    "paris": (48.8566, 2.3522, "Paris, France"),
}


def _resolve_coordinates(city: str) -> tuple[float, float, str]:
    key = city.strip().lower()
    if key in KNOWN_CITIES:
        return KNOWN_CITIES[key]

    geo_resp = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": city.strip(), "count": 1, "language": "en", "format": "json"},
        timeout=TIMEOUT,
    )
    geo_resp.raise_for_status()
    results = geo_resp.json().get("results") or []
    if not results:
        raise ValueError(f"City not found: {city!r}")
    top = results[0]
    country = top.get("country") or ""
    label = f"{top.get('name', city)}, {country}".strip(", ")
    return float(top["latitude"]), float(top["longitude"]), label


def get_weather(
    city: str = "",
    days: int = 1,
    unit: str = "celsius",
) -> dict[str, Any]:
    try:
        clean_city = (city or "").strip()
        if not clean_city:
            raise ValueError("city must not be empty")

        forecast_days = int(days or 1)
        if forecast_days < 1 or forecast_days > 7:
            raise ValueError("days must be between 1 and 7")

        clean_unit = (unit or "celsius").strip().lower()
        if clean_unit not in ALLOWED_UNITS:
            raise ValueError(f"Invalid unit {unit!r}; must be one of {sorted(ALLOWED_UNITS)}")

        lat, lon, resolved_name = _resolve_coordinates(clean_city)
        response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,precipitation",
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
                "temperature_unit": clean_unit,
                "forecast_days": forecast_days,
                "timezone": "auto",
            },
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()

        current = data.get("current") or {}
        daily_raw = data.get("daily") or {}
        dates = daily_raw.get("time") or []
        t_max = daily_raw.get("temperature_2m_max") or []
        t_min = daily_raw.get("temperature_2m_min") or []
        precip = daily_raw.get("precipitation_sum") or []

        daily = []
        for idx, day_date in enumerate(dates[:forecast_days]):
            daily.append({
                "date": day_date,
                "temp_max": t_max[idx] if idx < len(t_max) else None,
                "temp_min": t_min[idx] if idx < len(t_min) else None,
                "precipitation_mm": precip[idx] if idx < len(precip) else None,
            })

        return {
            "tool": "get_weather",
            "city": clean_city,
            "location": resolved_name,
            "unit": clean_unit,
            "days": forecast_days,
            "current": {
                "temperature": current.get("temperature_2m"),
                "humidity": current.get("relative_humidity_2m"),
                "precipitation_mm": current.get("precipitation"),
            },
            "daily": daily,
        }
    except Exception as exc:
        return err("get_weather", exc)
