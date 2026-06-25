import pandas as pd
from astral import LocationInfo
from astral.sun import sun, dawn, dusk
from datetime import date, timedelta


# Load the cleaned master dataset
master = pd.read_csv("/home/sindambiwe/Downloads/BRICS_PROJECT/kigali_master_dataset_cleaned.csv")



print(master.columns)

# Select useful columns for temperature prediction

temperature_df = master[
    [
        'date', 'temperature_2m_max', 'temperature_2m_min',
       'precipitation_sum', 'wind_speed_10m_max',
       'wind_direction_10m_dominant', 'relative_humidity_2m_mean',
       'surface_pressure_mean', 'cloud_cover_mean', 'visibility_mean',
       'sunrise', 'sunset', 'moon_phase'
    ]
]

temperature_df.head()

temperature_df.to_csv(
    "/home/sindambiwe/Downloads/BRICS_PROJECT/master_temperature.csv",
    index=False
)

print("Temperature dataset saved successfully.")