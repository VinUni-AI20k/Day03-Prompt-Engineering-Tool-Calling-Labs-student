from __future__ import annotations

import re
from typing import Any

import requests

from tools._shared import TIMEOUT, err, fold_text


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
WEATHER_LABELS = {
    0: "Trời quang", 1: "Ít mây", 2: "Mây rải rác", 3: "Nhiều mây",
    45: "Sương mù", 48: "Sương mù đóng băng",
    51: "Mưa phùn nhẹ", 53: "Mưa phùn vừa", 55: "Mưa phùn dày",
    56: "Mưa phùn băng nhẹ", 57: "Mưa phùn băng dày",
    61: "Mưa nhẹ", 63: "Mưa vừa", 65: "Mưa to",
    66: "Mưa băng nhẹ", 67: "Mưa băng to",
    71: "Tuyết nhẹ", 73: "Tuyết vừa", 75: "Tuyết dày", 77: "Hạt tuyết",
    80: "Mưa rào nhẹ", 81: "Mưa rào vừa", 82: "Mưa rào mạnh",
    85: "Tuyết rào nhẹ", 86: "Tuyết rào mạnh",
    95: "Dông", 96: "Dông kèm mưa đá nhẹ", 99: "Dông kèm mưa đá mạnh",
}


def _place(item: dict[str, Any]) -> dict[str, Any]:
    return {key: item.get(key) for key in (
        "name", "admin1", "country", "country_code", "latitude", "longitude", "feature_code",
    )}


def get_weather(location: str = "", country_code: str = "", units: str = "celsius") -> dict[str, Any]:
    """Resolve a city and retrieve current model-based weather from Open-Meteo."""
    try:
        if not isinstance(location, str) or not 2 <= len(location.strip()) <= 200:
            raise ValueError("location must be a city/place name of 2 to 200 characters")
        if not isinstance(country_code, str):
            raise ValueError("country_code must be an ISO two-letter string or empty")
        country_code = country_code.strip().upper()
        if country_code and not re.fullmatch(r"[A-Z]{2}", country_code):
            raise ValueError("country_code must contain two letters, e.g. VN or US")
        if not isinstance(units, str) or units not in {"celsius", "fahrenheit"}:
            raise ValueError("units must be celsius or fahrenheit")

        location = location.strip()
        params: dict[str, Any] = {"name": location, "count": 5, "language": "en", "format": "json"}
        if country_code:
            params["countryCode"] = country_code
        response = requests.get(GEOCODING_URL, params=params, timeout=TIMEOUT)
        response.raise_for_status()
        places = response.json().get("results") or []
        if not places:
            return {"tool": "weather", "error": "location_not_found", "message": "No matching location; ask for a city and country.", "items": []}

        # The geocoder also returns partial matches and airports. Prefer exact
        # names, then a unique national capital explicitly identified by the API.
        normalize_name = lambda value: re.sub(r"\W", "", fold_text(value))
        requested_name = normalize_name(location.split(",", 1)[0])
        exact = [item for item in places if normalize_name(item.get("name", "")) == requested_name]
        if exact:
            places = exact
            capitals = [item for item in places if item.get("feature_code") == "PPLC"]
            if len(capitals) == 1:
                places = capitals
        # Remaining distinct matches require the user's choice.
        candidates = list({(item["latitude"], item["longitude"]): _place(item) for item in places}.values())
        if len(candidates) > 1:
            return {
                "tool": "weather", "error": "ambiguous_location",
                "message": "Ask the user to specify the city, region and country, then retry.",
                "candidates": candidates, "items": [],
            }
        place = candidates[0]
        forecast_params = {
            "latitude": place["latitude"], "longitude": place["longitude"],
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
            "temperature_unit": units, "wind_speed_unit": "kmh", "timezone": "auto",
        }
        response = requests.get(FORECAST_URL, params=forecast_params, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
        current = data.get("current")
        if not isinstance(current, dict) or not current.get("time") or any(
            current.get(key) is None for key in (
                "temperature_2m", "relative_humidity_2m", "apparent_temperature", "weather_code", "wind_speed_10m",
            )
        ):
            raise ValueError("Open-Meteo returned incomplete current weather data")
        current_units = data.get("current_units") or {}
        temperature_unit = current_units.get("temperature_2m", "°C" if units == "celsius" else "°F")
        condition = WEATHER_LABELS.get(current["weather_code"], f"WMO {current['weather_code']}")
        label = ", ".join(str(place[key]) for key in ("name", "admin1", "country") if place.get(key))
        summary = (
            f"{condition}; nhiệt độ {current['temperature_2m']} {temperature_unit}; "
            f"cảm nhận {current['apparent_temperature']} {temperature_unit}; "
            f"độ ẩm {current['relative_humidity_2m']}%; gió {current['wind_speed_10m']} km/h. "
            f"Thời điểm: {current['time']} ({data.get('timezone', 'local')}). "
            "Điều kiện hiện tại từ mô hình thời tiết Open-Meteo."
        )
        source_url = requests.Request("GET", FORECAST_URL, params=forecast_params).prepare().url
        return {
            "tool": "weather", "location": place, "timezone": data.get("timezone"),
            "units": units, "current": current, "current_units": current_units,
            "condition": condition,
            "items": [{"title": f"Thời tiết hiện tại: {label}", "summary": summary,
                       "url": source_url, "source": "Open-Meteo", "date": current["time"]}],
        }
    except Exception as exc:
        return {**err("weather", exc), "items": []}
