import pandas as pd
master = pd.read_csv("kigali_master_dataset.csv")
master ["visibility_mean"] = master ["visibility_mean"].fillna(0)
master.to_csv("kigali_master_dataset_cleaned.csv")

print(master.describe().round(2))
print(master.isnull().sum())
print(master.duplicated().sum())