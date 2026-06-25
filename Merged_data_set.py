import pandas as pd
from datetime import date, timedelta


weather = pd.read_csv("Kigali_weather.csv")
astro = pd.read_csv("Kigali_astronomy.csv")

weather["date"] = pd.to_datetime(weather["date"])
astro["date"] = pd.to_datetime(astro["date"])

master = pd.merge(weather, astro, on="date", how="inner")

master.to_csv("kigali_master_dataset.csv", index=False)