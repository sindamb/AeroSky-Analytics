import requests
import pandas as pd
from datetime import datetime, timedelta

def fetch_live_only_data():
    """
    Fetches weather telemetry for Kigali, Rwanda (1.9441° S, 30.0619° E)
    from the Open-Meteo API. Enforces a strict timeout to prevent Streamlit freezes.
    """
    # Coordinates for Kigali, Rwanda
    LATITUDE = -1.9441
    LONGITUDE = 30.0619
    
    # Define time window (e.g., past 3 days up to today for historical context)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=3)
    
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")
    
    # Open-Meteo API URL with all necessary parameters required by AeroSky Analytics
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "start_date": start_str,
        "end_date": end_str,
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "wind_speed_10m_max",
            "sunrise",
            "sunset"
        ],
        "hourly": [
            "relative_humidity_2m",
            "surface_pressure",
            "cloud_cover",
            "visibility"
        ],
        "timezone": "Africa/Kigali"
    }
    
    try:
        # Enforce a strict 5-second timeout so the app fails gracefully if the API is slow or down
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status() # Raise an error for bad status codes (44, 500, etc.)
        data = response.json()
        
        # -------------------------------------------------------------
        # PARSE HOURLY DATA (Aggregate hourly metrics into daily means)
        # -------------------------------------------------------------
        hourly = data.get("hourly", {})
        df_hourly = pd.DataFrame({
            "time": pd.to_datetime(hourly.get("time")),
            "relative_humidity_2m": hourly.get("relative_humidity_2m"),
            "surface_pressure": hourly.get("surface_pressure"),
            "cloud_cover": hourly.get("cloud_cover"),
            "visibility": hourly.get("visibility")
        })
        
        # Group by date to match the daily framework row structure
        df_hourly["date"] = df_hourly["time"].dt.strftime("%Y-%m-%d")
        daily_averages = df_hourly.groupby("date").agg({
            "relative_humidity_2m": "mean",
            "surface_pressure": "mean",
            "cloud_cover": "mean",
            "visibility": "mean"
        }).reset_index()
        
        # -------------------------------------------------------------
        # PARSE DAILY DATA
        # -------------------------------------------------------------
        daily = data.get("daily", {})
        df_daily = pd.DataFrame({
            "date": daily.get("time"),
            "temperature_2m_max": daily.get("temperature_2m_max"),
            "temperature_2m_min": daily.get("temperature_2m_min"),
            "precipitation_sum": daily.get("precipitation_sum"),
            "wind_speed_10m_max": daily.get("wind_speed_10m_max"),
            "sunrise": [t.split("T")[-1] if "T" in t else t for t in daily.get("sunrise", [])],
            "sunset": [t.split("T")[-1] if "T" in t else t for t in daily.get("sunset", [])]
        })
        
        # -------------------------------------------------------------
        # MERGE DATA & CALCULATE MOCK MOON PHASE FOR THE REGISTRY
        # -------------------------------------------------------------
        final_df = pd.merge(df_daily, daily_averages, on="date")
        
        # Clean column names to match what app.py expects
        final_df = final_df.rename(columns={
            "relative_humidity_2m": "relative_humidity_2m_mean",
            "surface_pressure": "surface_pressure_mean",
            "cloud_cover": "cloud_cover_mean",
            "visibility": "visibility_mean"
        })
        
        # Mock a moon phase value if not provided by core API payload (required by app.py)
        final_df["moon_phase"] = "Waxing Gibbous"
        
        return final_df

    except requests.exceptions.Timeout:
        raise RuntimeError("The connection to the weather telemetry API timed out. Please retry.")
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Network error interface dropped: {e}")
    except Exception as e:
        raise RuntimeError(f"Failed to process telemetry payload structure: {e}")

# Simple standalone validation test
if __name__ == "__main__":
    print("Testing Kigali telemetry fetch...")
    try:
        test_df = fetch_live_only_data()
        print("\nSuccess! Sample Data Frame Constructed:")
        print(test_df.tail(1).to_string())
    except Exception as error:
        print(f"\nTest Failed: {error}")
