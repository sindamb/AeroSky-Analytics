import pandas as pd
from astral import LocationInfo
from astral.sun import sun, dawn, dusk
from datetime import date, timedelta


# Load the cleaned master dataset
master = pd.read_csv("/home/sindambiwe/Downloads/BRICS_PROJECT/kigali_master_dataset_cleaned.csv")



print(master.columns)

wind_df = master[
    [
        'date', 'temperature_2m_max', 'temperature_2m_min',
       'precipitation_sum', 'wind_speed_10m_max',
       'wind_direction_10m_dominant', 'relative_humidity_2m_mean',
       'surface_pressure_mean', 'cloud_cover_mean', 'visibility_mean',
       'sunrise', 'sunset', 'moon_phase'
    ]
]

wind_df.head()

wind_df.to_csv(
    "/home/sindambiwe/Downloads/BRICS_PROJECT/master_wind.csv",
    index=False
)

print("Wind dataset saved successfully.")


cloud_df = master[
    [
        'date', 'temperature_2m_max', 'temperature_2m_min',
       'precipitation_sum', 'wind_speed_10m_max',
       'wind_direction_10m_dominant', 'relative_humidity_2m_mean',
       'surface_pressure_mean', 'cloud_cover_mean', 'visibility_mean',
       'sunrise', 'sunset', 'moon_phase'
    ]
]

cloud_df.head()

cloud_df.to_csv(
    "/home/sindambiwe/Downloads/BRICS_PROJECT/master_cloud.csv",
    index=False
)

print("Cloud dataset saved successfully.")


precipitation_df = master[
    [
       'date', 'temperature_2m_max', 'temperature_2m_min',
       'precipitation_sum', 'wind_speed_10m_max',
       'wind_direction_10m_dominant', 'relative_humidity_2m_mean',
       'surface_pressure_mean', 'cloud_cover_mean', 'visibility_mean',
       'sunrise', 'sunset', 'moon_phase'
    ]
]

precipitation_df.head()

precipitation_df.to_csv(
    "/home/sindambiwe/Downloads/BRICS_PROJECT/master_precipitation.csv",
    index=False
)


print("Precipitation dataset saved successfully.")


humidity_df = master[
    [
       'date', 'temperature_2m_max', 'temperature_2m_min',
       'precipitation_sum', 'wind_speed_10m_max',
       'wind_direction_10m_dominant', 'relative_humidity_2m_mean',
       'surface_pressure_mean', 'cloud_cover_mean', 'visibility_mean',
       'sunrise', 'sunset', 'moon_phase'
    ]
]

humidity_df.head()

humidity_df.to_csv(
    "/home/sindambiwe/Downloads/BRICS_PROJECT/master_humidity.csv",
    index=False
)

print("Humidity dataset saved successfully.")