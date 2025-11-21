import pandas as pd

df = pd.read_csv("f3_2019_2025_with_times.csv")

# Session Types, die echte Rennen sind
race_sessions = [
    "ROUND1Summary",
    "ROUND2Summary",
    "ROUND3Summary"
]

# Filter anwenden
df_races = df[df["session_type"].isin(race_sessions)]

print("Gesamtzeilen vorher:", len(df))
print("Gesamtzeilen nach Race-Filter:", len(df_races))
print("Beispiel:")
print("Spalten in df_races:", df_races.columns.tolist())
print(df_races[["session_type", "race_id", "driver_name"]].head())


# Datei speichern
df_races.to_csv("f3_2019_2025_races_only_final.csv", index=False)
print("Gespeichert als f3_2019_2025_races_only_final.csv")
