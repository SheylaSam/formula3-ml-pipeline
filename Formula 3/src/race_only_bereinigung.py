import pandas as pd

# Basisdaten mit Zeiten und Fahrerinfos
df = pd.read_csv("f3_2019_2025_with_times.csv")

print("Gesamtzeilen in with_times:", len(df))
print("Session Types (Top 20):")
print(df["session_type"].value_counts().head(20))

# Nur finale Rennresultate behalten
# ROUND1Summary, ROUND2Summary, ... ROUND10Summary
mask_round_summary = df["session_type"].astype(str).str.match(r"^ROUND\d+Summary$", na=False)
df_races = df[mask_round_summary].copy()

print("\nZeilen nach Filter auf ROUNDxSummary:", len(df_races))
print("Verteilung session_type:")
print(df_races["session_type"].value_counts())

# Kurze Stichprobe
print("\nBeispielzeilen:")
print(df_races[["season", "race_id", "session_type", "driver_name", "laps", "time", "status"]].head(15))

# Speichern
df_races.to_csv("f3_2019_2025_races_only_final.csv", index=False)
print("\nGespeichert als f3_2019_2025_races_only_final.csv")
