import pandas as pd
from sklearn.preprocessing import LabelEncoder

# Load the dataset
df = pd.read_csv("/home/sindambiwe/Downloads/BRICS_PROJECT/kigali_master_dataset_cleaned.csv")

# Display the first rows
df.head()

# Convert the Date Column

df["date"] = pd.to_datetime(df["date"])

# Extract Useful Date Features

df["year"] = df["date"].dt.year
df["month"] = df["date"].dt.month
df["day"] = df["date"].dt.day
df["day_of_week"] = df["date"].dt.dayofweek
df["day_name"] = df["date"].dt.day_name()
df["week_of_year"] = df["date"].dt.isocalendar().week
df["quarter"] = df["date"].dt.quarter

# Convert Sunrise Time

df["sunrise"] = pd.to_datetime(df["sunrise"])

df["sunrise_hour"] = df["sunrise"].dt.hour
df["sunrise_minute"] = df["sunrise"].dt.minute


# Convert Sunset

df["sunset"] = pd.to_datetime(df["sunset"])

df["sunset_hour"] = df["sunset"].dt.hour
df["sunset_minute"] = df["sunset"].dt.minute





# Encode Day Name

encoder = LabelEncoder()

df["day_name"] = encoder.fit_transform(df["day_name"])

# Scale Numerical Variables

from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()

numeric_columns = df.select_dtypes(include=["int64", "float64"]).columns

df.to_csv("/home/sindambiwe/Downloads/BRICS_PROJECT/kigali_feature_engineered.csv", index=False)

print("Feature-engineered dataset saved successfully!")