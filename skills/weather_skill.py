import random
from .base import BaseSkill
from nlp.entity_extractor import extract_location

# Mock weather; if WEATHER_API_KEY configured, use real API
import requests
from config import Config

class WeatherSkill(BaseSkill):
    name = "weather"
    description = "Provides weather information"
    intents = ["weather"]

    def handle(self, text, intent, entities):
        location = extract_location(text) or "your location"
        # Try real API if key present
        if Config.WEATHER_API_KEY:
            try:
                url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={Config.WEATHER_API_KEY}&units=metric"
                r = requests.get(url, timeout=5)
                if r.status_code == 200:
                    data = r.json()
                    temp = data["main"]["temp"]
                    desc = data["weather"][0]["description"]
                    humidity = data["main"]["humidity"]
                    return f"🌤️ Weather in **{data['name']}**: {desc}, {temp}°C, humidity {humidity}%."
                else:
                    return f"⚠️ Could not fetch weather for '{location}'. (API: {r.json().get('message','error')})"
            except Exception as e:
                return f"⚠️ Weather API error: {e}"

        # Mock fallback - deterministic but varied by location hash
        random.seed(hash(location) % 1000)
        temp = random.randint(18, 32)
        conditions = ["Sunny ☀️", "Partly Cloudy ⛅", "Cloudy ☁️", "Light Rain 🌧️", "Clear 🌤️"]
        cond = random.choice(conditions)
        humidity = random.randint(45, 85)
        return (
            f"🌦️ **Weather for {location.title()}** (mock data):\n"
            f"- Condition: {cond}\n"
            f"- Temperature: {temp}°C\n"
            f"- Humidity: {humidity}%\n"
            f"_Add OPENWEATHER API key in .env for live data._"
        )
