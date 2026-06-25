import requests
import pandas as pd
from datetime import date
from astral import LocationInfo
from astral.sun import sun

def fetch_live_only_data():
    """
    Queries the live Open-Meteo forecast API for today's real-time parameters only.
    """
    url = (
        "https://api.open-meteo.com/v1/forecast?"
        "latitude=-1.9441&longitude=30.0619&"
        "daily=temperature_2m_max,temperature_2m_min,precipitation_sum,"
        "wind_speed_10m_max,wind_direction_10m_dominant,relative_humidity_2m_mean,"
        "surface_pressure_mean,cloud_cover_mean,visibility_mean&"
        "timezone=auto&forecast_days=1"
    )
    
    response = requests.get(url).json()
    if "daily" not in response:
        raise RuntimeError("Open-Meteo live feed down or timed out.")
        
    daily = response["daily"]
    today = date.today()
    
    # Live Astronomy logic
    city = LocationInfo("Kigali", "Rwanda", "Africa/Kigali", -1.9441, 30.0619)
    try:
        s = sun(city.observer, date=today)
        sunrise_time = s["sunrise"].strftime("%H:%M")
        sunset_time = s["sunset"].strftime("%H:%M")
    except Exception:
        sunrise_time = "06:00"
        sunset_time = "18:00"
        
    diff = today - date(2001, 1, 1)
    days = diff.days % 29.53
    if days < 1: moon_p = "New Moon"
    elif days < 7: moon_p = "Waxing Crescent"
    elif days == 7: moon_p = "First Quarter"
    elif days < 14: moon_p = "Waxing Gibbous"
    elif days == 14: moon_p = "Full Moon"
    elif days < 22: moon_p = "Waning Gibbous"
    else: moon_p = "Last Quarter"
    
    live_data = {
        "date": [pd.to_datetime(today)],
        "temperature_2m_max": [daily["temperature_2m_max"][0]],
        "temperature_2m_min": [daily["temperature_2m_min"][0]],
        "precipitation_sum": [daily["precipitation_sum"][0]],
        "wind_speed_10m_max": [daily["wind_speed_10m_max"][0]],
        "wind_direction_10m_dominant": [daily["wind_direction_10m_dominant"][0]],
        "relative_humidity_2m_mean": [daily["relative_humidity_2m_mean"][0]],
        "surface_pressure_mean": [daily["surface_pressure_mean"][0]],
        "cloud_cover_mean": [daily["cloud_cover_mean"][0]],
        "visibility_mean": [daily["visibility_mean"][0] if daily["visibility_mean"][0] is not None else 0.0],
        "moon_phase": [moon_p],
        "sunrise": [sunrise_time],
        "sunset": [sunset_time]
    }
    
    return pd.DataFrame(live_data)