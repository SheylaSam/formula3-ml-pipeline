# feature_engineering.py

import pandas as pd
import numpy as np

# 1. Daten einlesen
df = pd.read_csv("f3_2019_2025_races_only_final.csv")

print("Zeilen:", len(df))
print("Spalten:", df.columns.tolist())
print(df[["season", "race_id", "session_type", "driver_name", "laps", "time", "time_s", "status"]].head(15))

# 2. Laps bereinigen (Zahl oder NaN)
df["laps_clean"] = pd.to_numeric(df["laps"], errors="coerce")

# 3. Finisher kennzeichnen
# Finisher = Status leer und time_s vorhanden und laps_clean > 0
df["is_finisher"] = (
    df["status"].isna()
    & df["time_s"].notna()
    & df["laps_clean"].notna()
    & (df["laps_clean"] > 0)
).astype(int)

print("\nVerteilung is_finisher:")
print(df["is_finisher"].value_counts(dropna=False))

# 4. Sortierung innerhalb eines Rennens
# Ziel: Finisher zuerst, danach Nichtfinisher
# Innerhalb der Finisher: zuerst Fahrer mit mehr Runden, dann nach Zeit
df = df.sort_values(
    by=["season", "race_id", "session_type",
        "is_finisher", "laps_clean", "time_s"],
    ascending=[True, True, True,
               False, False, True]
).reset_index(drop=True)

# 5. Position innerhalb jedes Rennens vergeben
df["position"] = df.groupby(
    ["season", "race_id", "session_type"]
).cumcount() + 1

# 6. Position für Nichtfinisher entfernen
df.loc[df["is_finisher"] == 0, "position"] = np.nan

print("\nBeispiel mit Position (eine Runde):")
example_race = df[(df["season"] == df["season"].min()) &
                  (df["session_type"] == df["session_type"].unique()[0])]
print(example_race[["season", "race_id", "session_type",
                    "driver_name", "status", "laps_clean", "time_s", "position"]].head(25))

# 7. Basis Features pro Rennen

# 7.1 Korrekte Rennzeit des Siegers pro Rennen (nur Position == 1)
winners = (
    df[df["position"] == 1]
    .groupby(["season", "race_id", "session_type"])["time_s"]
    .first()
    .rename("winner_time_s")
)

# Zurück in den Haupt-Datensatz mergen
df = df.merge(
    winners,
    on=["season", "race_id", "session_type"],
    how="left"
)


# 7.2 Beste Rennrunde
df["best_race_lap_s"] = df.groupby(
    ["season", "race_id", "session_type"]
)["best_lap_s"].transform("min")

# 7.3 Maximale Rundenzahl im Rennen
df["race_max_laps"] = df.groupby(
    ["season", "race_id", "session_type"]
)["laps_clean"].transform("max")

# 7.4 Relative Rundenzahl
df["rel_laps"] = df["laps_clean"] / df["race_max_laps"]

# 8. Performance Features

# 8.1 Zeitabstand zum Sieger
df["time_from_winner_s"] = df["time_s"] - df["winner_time_s"]

# Fahrer ohne Zieleinlauf (is_finisher == 0) sollen keinen Zeitabstand bekommen
df.loc[df["is_finisher"] == 0, "time_from_winner_s"] = np.nan


# 8.2 Abstand zur besten Rennrunde
df["best_lap_from_best_s"] = df["best_lap_s"] - df["best_race_lap_s"]

# 8.3 Durchschnittliche Rundenzeit
df["avg_lap_time_s"] = df["time_s"] / df["laps_clean"]
df.loc[df["laps_clean"].isna() | (df["laps_clean"] <= 0), "avg_lap_time_s"] = np.nan

# 9. Status Features

df["finished"] = df["is_finisher"]
df["is_dnf"] = df["status"].eq("DNF").astype(int)
df["is_dns"] = df["status"].eq("DNS").astype(int)
df["is_dsq"] = df["status"].eq("DSQ").astype(int)

# 10. Position als Zahl (für Aggregationen)
df["position_clean"] = pd.to_numeric(df["position"], errors="coerce")

# 11. Team und Fahrer Aggregationen pro Saison

# 11.1 Teamdurchschnittsplatzierung pro Saison
df["team_avg_pos_season"] = df.groupby(
    ["season", "team_name"]
)["position_clean"].transform("mean")

# 11.2 Team Speed Index
df["team_speed"] = df.groupby(
    ["season", "team_name"]
)["avg_lap_time_s"].transform("mean")

# 11.3 Driver Speed Index
df["driver_speed"] = df.groupby(
    ["season", "driver_name"]
)["avg_lap_time_s"].transform("mean")

# 11.4 Top 10 Rate pro Fahrer
def top10_rate(series):
    return (series <= 10).mean()

df["driver_top10_rate"] = df.groupby(
    ["season", "driver_name"]
)["position_clean"].transform(top10_rate)

# 11.5 Durchschnittliche Rundenzeit im Rennen
df["race_avg_lap_time_s"] = df.groupby(
    ["season", "race_id", "session_type"]
)["avg_lap_time_s"].transform("mean")

# 11.6 Fahrer vs Team Pace
df["driver_vs_team"] = df["avg_lap_time_s"] - df["team_speed"]

# 11.7 Fahrer vs Rennschnitt
df["lap_vs_race_avg"] = df["avg_lap_time_s"] - df["race_avg_lap_time_s"]

# 12. Session Round als Zahl (1 bis 10)
df["session_round"] = (
    df["session_type"]
    .astype(str)
    .str.extract(r"ROUND(\d+)")
    .astype(float)
    .astype("Int64")
)

print("\nSession Rounds:", df["session_round"].unique())

# 13. Aufräumen von Hilfsspalten
df = df.drop(columns=["is_finisher"], errors="ignore")

# Zahlen sauber runden
round_cols = [
    "time_s", "best_lap_s", "gap_s",
    "winner_time_s", "best_race_lap_s", "rel_laps",
    "avg_lap_time_s", "time_from_winner_s", "team_avg_pos_season",
    "best_lap_from_best_s", "lap_vs_race_avg", "driver_top10_rate", "race_avg_lap_time_s"
    "team_speed", "driver_speed", "driver_vs_team"
]

for col in round_cols:
    if col in df.columns:
        df[col] = df[col].round(3)    # auf 3 Nachkommastellen runden

# 14. Ergebnis speichern
df.to_csv("f3_2019_2025_races_features.csv", index=False)




print("\nFeature Engineering abgeschlossen.")
print("Gespeichert als: f3_2019_2025_races_features.csv")
print("Beispiel mit Features:")
print(df[[
    "season", "race_id", "session_type", "driver_name",
    "position", "finished",
    "time_s", "winner_time_s", "time_from_winner_s",
    "best_lap_s", "best_race_lap_s", "best_lap_from_best_s",
    "laps_clean", "race_max_laps", "rel_laps",
    "avg_lap_time_s",
    "team_avg_pos_season", "driver_speed", "team_speed",
    "driver_top10_rate", "driver_vs_team", "lap_vs_race_avg",
    "session_round"
]].head(20))
