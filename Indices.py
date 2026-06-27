import pandas as pd

def compute_all_indices(df):
    """
    Computes system operational feasibility weights for the live tracking dataset,
    heavily leaning on visibility minimums for aviation and astronomy profiles.
    """
    # 1. FEATURE SCALING / NORMALIZATION SUB-SCORES
    df['wind_score'] = df['wind_speed_10m_max'].apply(lambda x: max(0.0, 1.0 - (x / 25.0)))
    df['rain_score'] = df['precipitation_sum'].apply(lambda x: max(0.0, 1.0 - (x / 20.0)))
    df['vis_score'] = df['visibility_mean'].apply(lambda x: min(1.0, x / 10000.0))
    df['cloud_score'] = df['cloud_cover_mean'].apply(lambda x: 1.0 - (x / 100.0))
    df['humidity_score'] = df['relative_humidity_2m_mean'].apply(lambda x: 1.0 - (x / 100.0))
    
    moon_map = {
        'New Moon': 1.0, 'Waning Crescent': 0.8, 'Waxing Crescent': 0.8,
        'First Quarter': 0.5, 'Last Quarter': 0.5, 'Waning Gibbous': 0.2,
        'Waxing Gibbous': 0.2, 'Full Moon': 0.0
    }
    df['moon_score'] = df['moon_phase'].map(moon_map).fillna(0.5)

    # 2. INDEX FORMULA CALCULATIONS (Heavy weight on Visibility)
    df['ASI_Aviation'] = (df['wind_score'] * 0.40 + df['rain_score'] * 0.30 + df['vis_score'] * 0.30) * 100
    df['ASI_Astronomy'] = (df['cloud_score'] * 0.50 + df['vis_score'] * 0.20 + df['moon_score'] * 0.20 + df['humidity_score'] * 0.10) * 100
    
    # 3. CRITICAL PENALTY THRESHOLDS
    def determine_aviation_status(row):
        if row['visibility_mean'] < 4000:  # Visual Flight Rules (VFR) critical ceiling minimum
            return 'Sub-optimal (No-Go) [Low Visibility]'
        if row['ASI_Aviation'] >= 75.0: return 'Optimal (Go)'
        elif row['ASI_Aviation'] >= 50.0: return 'Marginal (Caution)'
        else: return 'Sub-optimal (No-Go)'
        
    def determine_astronomy_status(row):
        if row['visibility_mean'] < 3000 or row['cloud_cover_mean'] > 75:
            return 'Sub-optimal (No-Go)'
        if row['ASI_Astronomy'] >= 75.0: return 'Optimal (Go)'
        elif row['ASI_Astronomy'] >= 50.0: return 'Marginal (Caution)'
        else: return 'Sub-optimal (No-Go)'
        
    df['Aviation_Status'] = df.apply(determine_aviation_status, axis=1)
    df['Astronomy_Status'] = df.apply(determine_astronomy_status, axis=1)
    
    columns_to_drop = ['wind_score', 'rain_score', 'vis_score', 'cloud_score', 'humidity_score', 'moon_score']
    return df.drop(columns=columns_to_drop)