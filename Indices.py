import pandas as pd
import numpy as np

def compute_all_indices(df):
    """
    Computes aviation and astronomy suitability metrics safely.
    Guaranteed not to cause infinite loops or block the UI pipeline.
    """
    # Prevent modifying original DataFrame
    df = df.copy()
    
    # -------------------------------------------------------------
    # 1. FLIGHT SAFETY SYSTEM (ASI Aviation Calculation)
    # Base formula drops points for high winds, precipitation, and poor visibility
    # -------------------------------------------------------------
    asi_aviation_list = []
    aviation_status_list = []
    
    for _, row in df.iterrows():
        score = 100.0
        
        # Wind Penalty: Deduct points if wind exceeds 15 km/h
        wind = float(row.get('wind_speed_10m_max', 0))
        if wind > 15:
            score -= (wind - 15) * 2
            
        # Rain Penalty: Severe deduction for precipitation
        rain = float(row.get('precipitation_sum', 0))
        if rain > 0:
            score -= (rain * 15)
            
        # Visibility Penalty: Deduct if visibility falls below 8 km (8000m)
        # Handle both meters and kilometers gracefully
        vis = float(row.get('visibility_mean', 10000))
        if vis > 150:  # Check if in meters
            vis_km = vis / 1000.0
        else:
            vis_km = vis
            
        if vis_km < 8.0:
            score -= (8.0 - vis_km) * 10
            
        # Ensure score stays between 0 and 100
        score = max(0.0, min(100.0, score))
        asi_aviation_list.append(score)
        
        # Categorize status based on score thresholds
        if score >= 75:
            aviation_status_list.append("Optimal Conditions")
        elif score >= 45:
            aviation_status_list.append("Marginal Operations")
        else:
            aviation_status_list.append("Suboptimal / Grounded")

    df['ASI_Aviation'] = asi_aviation_list
    df['Aviation_Status'] = aviation_status_list

    # -------------------------------------------------------------
    # 2. OBSERVATION WINDOW (ASI Astronomy Calculation)
    # Base formula drops points primarily for cloud cover and relative humidity
    # -------------------------------------------------------------
    asi_astronomy_list = []
    astronomy_status_list = []
    
    for _, row in df.iterrows():
        score = 100.0
        
        # Cloud Cover Penalty: Heavy penalty for astronomical sight blockage
        clouds = float(row.get('cloud_cover_mean', 0))
        score -= (clouds * 0.8)
        
        # Humidity Penalty: High moisture creates dew/lens fogging
        humidity = float(row.get('relative_humidity_2m_mean', 0))
        if humidity > 70:
            score -= (humidity - 70) * 0.5
            
        # Rain Penalty: Zero out astronomical viewing if it's raining
        if float(row.get('precipitation_sum', 0)) > 0:
            score -= 40
            
        # Ensure score stays between 0 and 100
        score = max(0.0, min(100.0, score))
        asi_astronomy_list.append(score)
        
        # Categorize status
        if score >= 70:
            astronomy_status_list.append("Optimal Clear Skies")
        elif score >= 40:
            astronomy_status_list.append("Marginal Overcast")
        else:
            astronomy_status_list.append("Suboptimal / No Viewing")

    df['ASI_Astronomy'] = asi_astronomy_list
    df['Astronomy_Status'] = astronomy_status_list

    return df

# Simple verification routine
if __name__ == "__main__":
    print("Testing index calculation framework matrix...")
    mock_data = pd.DataFrame([{
        'date': '2026-06-27',
        'wind_speed_10m_max': 12.0,
        'precipitation_sum': 0.0,
        'visibility_mean': 10000.0,
        'cloud_cover_mean': 15.0,
        'relative_humidity_2m_mean': 55.0,
        'temperature_2m_max': 26.0,
        'temperature_2m_min': 17.0,
        'surface_pressure_mean': 850.0,
        'sunrise': '06:01',
        'sunset': '18:12',
        'moon_phase': 'Waxing Gibbous'
    }])
    
    result = compute_all_indices(mock_data)
    print("Execution completely clear! Results sample:")
    print(result[['ASI_Aviation', 'Aviation_Status', 'ASI_Astronomy', 'Astronomy_Status']])
