import pandas as pd

df = pd.read_csv("f3_2019_2025_with_drivers_and_status.csv")

# 1) Nur Zeilen mit echten Runden behalten
mask_laps = df["laps"].notna()

# 2) Standings Tabellen rauswerfen
session = df["session_type"].astype(str)
mask_no_standings = ~session.str.startswith("Standings", na=False)

# 3) Nur Renn-Tabellen (beides muss true sein)
race_df = df[mask_laps & mask_no_standings].copy()

print("Zeilen nach Renn-Filter:", len(race_df))
print(race_df[["session_type", "driver_name", "laps", "time"]].head(20))

race_df.to_csv("f3_2019_2025_races_only.csv", index=False)
print("Neue races_only gespeichert!")
