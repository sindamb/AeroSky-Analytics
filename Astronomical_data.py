import pandas as pd
from astral import LocationInfo
from astral.sun import sun, dawn, dusk
from datetime import date, timedelta
import math

# -------------------------
# LOCATION: Kigali
# -------------------------
city = LocationInfo("Kigali", "Rwanda", "Africa/Kigali", -1.9441, 30.0619)

# -------------------------
# FUNCTION: Moon phase (simple approximation)
# -------------------------
def moon_phase(d):
    diff = d - date(2001, 1, 1)
    days = diff.days % 29.53
    if days < 1:
        return "New Moon"
    elif days < 7:
        return "Waxing Crescent"
    elif days == 7:
        return "First quarter moon"
    elif days<14:
        return "Waxing gibbous"
    elif days == 14:
        return "Full moon"
    elif days < 22:
        return "Waning Gibbous"
    else:
        return "Last Quarter"

# -------------------------
# GENERATE DATA (1 YEAR)
# -------------------------
start_date = date(2025, 1, 1)
end_date = date(2025, 12, 31)

data = []

current = start_date

while current <= end_date:
    s = sun(city.observer, date=current)

    data.append({
        "date": current,
        "sunrise": s["sunrise"],
        "sunset": s["sunset"],
        "moon_phase": moon_phase(current),
    })

    current += timedelta(days=1)

df_astro = pd.DataFrame(data)

df_astro.to_csv("Kigali_astronomy.csv", index = False)