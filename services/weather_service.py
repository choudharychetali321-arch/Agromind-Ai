"""Open-Meteo weather client using Python's standard-library HTTP support."""

import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from utils.constants import CLIMATE_RULES_NOTE
from utils.validators import validate_coordinates

API_URL = "https://api.open-meteo.com/v1/forecast"


def get_weather(latitude: float, longitude: float) -> dict:
    latitude, longitude = validate_coordinates(latitude, longitude)
    params = urlencode(
        {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m",
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
            "forecast_days": 7,
            "timezone": "auto",
        }
    )
    request = Request(f"{API_URL}?{params}", headers={"User-Agent": "AgroMind-AI/1.0"})
    try:
        with urlopen(request, timeout=15) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Weather service is unavailable: {exc}") from exc

    current = payload.get("current")
    daily = payload.get("daily")
    if not isinstance(current, dict) or not isinstance(daily, dict):
        raise RuntimeError("Weather service returned an incomplete response.")
    try:
        temperatures = daily["temperature_2m_max"]
        rain = daily["precipitation_sum"]
        return {
            "latitude": payload.get("latitude", latitude),
            "longitude": payload.get("longitude", longitude),
            "timezone": payload.get("timezone", "unknown"),
            "observed_at": current["time"],
            "temperature_c": float(current["temperature_2m"]),
            "humidity_percent": float(current["relative_humidity_2m"]),
            "current_precipitation_mm": float(current["precipitation"]),
            "wind_speed_kmh": float(current["wind_speed_10m"]),
            "forecast": [
                {
                    "date": daily["time"][i],
                    "temperature_max_c": float(temperatures[i]),
                    "temperature_min_c": float(daily["temperature_2m_min"][i]),
                    "precipitation_mm": float(rain[i]),
                }
                for i in range(len(daily["time"]))
            ],
            "rain_next_7d_mm": sum(float(amount) for amount in rain),
            "max_forecast_temperature_c": max(float(value) for value in temperatures),
            "risk_note": CLIMATE_RULES_NOTE,
        }
    except (KeyError, TypeError, ValueError, IndexError) as exc:
        raise RuntimeError("Weather service returned data in an unexpected format.") from exc


def assess_climate_risks(weather: dict) -> list[dict]:
    risks = []
    maximum = weather["max_forecast_temperature_c"]
    rainfall = weather["rain_next_7d_mm"]
    if maximum >= 35:
        risks.append({"risk": "Heat stress", "level": "high", "reason": f"Forecast maximum is {maximum:.1f}°C."})
    elif maximum >= 30:
        risks.append({"risk": "Heat stress", "level": "moderate", "reason": f"Forecast maximum is {maximum:.1f}°C."})
    if rainfall < 10:
        risks.append({"risk": "Low rainfall / drought watch", "level": "high", "reason": f"Forecast total is {rainfall:.1f} mm over 7 days."})
    elif rainfall < 25:
        risks.append({"risk": "Low rainfall / drought watch", "level": "moderate", "reason": f"Forecast total is {rainfall:.1f} mm over 7 days."})
    if rainfall > 150:
        risks.append({"risk": "Excess rainfall", "level": "high", "reason": f"Forecast total is {rainfall:.1f} mm over 7 days."})
    elif rainfall > 100:
        risks.append({"risk": "Excess rainfall", "level": "moderate", "reason": f"Forecast total is {rainfall:.1f} mm over 7 days."})
    return risks
