import os
import requests
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
BASE_URL = "https://api.openweathermap.org/data/2.5"


def _weather_icon_emoji(icon_code: str) -> str:
    """Map OpenWeatherMap icon codes to emoji."""
    mapping = {
        "01d": "☀️", "01n": "🌙",
        "02d": "⛅", "02n": "🌥️",
        "03d": "🌥️", "03n": "🌥️",
        "04d": "☁️", "04n": "☁️",
        "09d": "🌧️", "09n": "🌧️",
        "10d": "🌦️", "10n": "🌧️",
        "11d": "⛈️", "11n": "⛈️",
        "13d": "❄️", "13n": "❄️",
        "50d": "🌫️", "50n": "🌫️",
    }
    return mapping.get(icon_code, "🌤️")


def get_current_weather(city: str) -> Optional[Dict[str, Any]]:
    """Fetch current weather for a city from OpenWeatherMap."""
    if not OPENWEATHER_API_KEY:
        return _mock_weather(city)

    try:
        url = f"{BASE_URL}/weather"
        params = {
            "q": city,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric",
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        icon_code = data["weather"][0]["icon"]
        return {
            "temperature": round(data["main"]["temp"], 1),
            "feels_like": round(data["main"]["feels_like"], 1),
            "description": data["weather"][0]["description"].capitalize(),
            "humidity": data["main"]["humidity"],
            "wind_speed": round(data["wind"]["speed"] * 3.6, 1),  # m/s → km/h
            "icon": _weather_icon_emoji(icon_code),
            "icon_code": icon_code,
            "forecast": [],
        }
    except requests.exceptions.RequestException as e:
        print(f"[WeatherService] Current weather fetch failed: {e}")
        return _mock_weather(city)


def get_forecast(city: str, days: int = 5) -> list:
    """Fetch 5-day / 3-hour forecast and collapse to daily summaries."""
    if not OPENWEATHER_API_KEY:
        return _mock_forecast(days)

    try:
        url = f"{BASE_URL}/forecast"
        params = {
            "q": city,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric",
            "cnt": min(days * 8, 40),  # 8 readings per day
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Group by date
        daily: Dict[str, list] = {}
        for item in data["list"]:
            date = item["dt_txt"].split(" ")[0]
            daily.setdefault(date, []).append(item)

        forecast = []
        for date, readings in list(daily.items())[:days]:
            temps = [r["main"]["temp"] for r in readings]
            icon_code = readings[len(readings) // 2]["weather"][0]["icon"]
            desc = readings[len(readings) // 2]["weather"][0]["description"].capitalize()
            forecast.append({
                "date": date,
                "min_temp": round(min(temps), 1),
                "max_temp": round(max(temps), 1),
                "description": desc,
                "icon": _weather_icon_emoji(icon_code),
            })

        return forecast
    except requests.exceptions.RequestException as e:
        print(f"[WeatherService] Forecast fetch failed: {e}")
        return _mock_forecast(days)


def get_weather_for_destination(city: str) -> Dict[str, Any]:
    """Combined call: current weather + forecast."""
    current = get_current_weather(city)
    if current is None:
        current = _mock_weather(city)
    current["forecast"] = get_forecast(city)
    return current


# ─── Mock / fallback data ────────────────────────────────────────────────────

def _mock_weather(city: str) -> Dict[str, Any]:
    """Return plausible mock weather when the API key is missing."""
    city_lower = city.lower()
    if any(c in city_lower for c in ["goa", "kerala", "kochi", "andaman"]):
        temp, desc, icon = 30.0, "Warm and humid", "☀️"
    elif any(c in city_lower for c in ["shimla", "manali", "ladakh", "leh", "darjeeling"]):
        temp, desc, icon = 12.0, "Cool and breezy", "⛅"
    elif any(c in city_lower for c in ["jaipur", "jodhpur", "udaipur", "rajasthan"]):
        temp, desc, icon = 35.0, "Hot and dry", "☀️"
    elif any(c in city_lower for c in ["mumbai", "pune", "bangalore", "chennai"]):
        temp, desc, icon = 28.0, "Partly cloudy", "🌥️"
    else:
        temp, desc, icon = 27.0, "Clear sky", "☀️"

    return {
        "temperature": temp,
        "feels_like": temp - 2.0,
        "description": desc,
        "humidity": 65,
        "wind_speed": 15.0,
        "icon": icon,
        "icon_code": "01d",
        "forecast": _mock_forecast(5),
    }


def _mock_forecast(days: int) -> list:
    from datetime import date, timedelta

    forecast = []
    base_temp = 28.0
    descs = ["Sunny", "Partly cloudy", "Cloudy", "Light rain", "Clear sky"]
    icons = ["☀️", "⛅", "🌥️", "🌧️", "☀️"]
    for i in range(min(days, 5)):
        d = date.today() + timedelta(days=i + 1)
        forecast.append({
            "date": d.strftime("%Y-%m-%d"),
            "min_temp": round(base_temp - 4 + i * 0.5, 1),
            "max_temp": round(base_temp + 3 + i * 0.3, 1),
            "description": descs[i % len(descs)],
            "icon": icons[i % len(icons)],
        })
    return forecast
