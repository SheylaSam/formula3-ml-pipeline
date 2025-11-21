# feature_engineering.py

import pandas as pd
import numpy as np

# 1. Daten einlesen
df = pd.read_csv("f3_2019_2025_races_only_final.csv")

print("Zeilen:", len(df))
print("Spalten:", df.columns.tolist())
print(df[["season", "race_id", "session_type", "driver_name", "time", "time_s", "status"]].head())


# 2. Sortierung innerhalb jedes Rennens
#    Ziel: zuerst alle Finisher mit aufsteigender Zeit, dann DNF / DNS / DSQ
df["time_s_sort"] = df["time_s"].fillna(1e12)  # grosse Zahl als Platzhalter für DNF etc.

df = df.sort_values(
    by=["season", "race_id", "session_type", "time_s_sort"],
    ascending=[True, True, True, True]
).reset_index(drop=True)


# 3. Position innerhalb jedes Rennens vergeben
#    Hinweis: Reihenfolge ist nun Zieleinlauf
df["position"] = df.groupby(["season", "race_id", "session_type"]).cumcount() + 1

# 4. Position für nicht beendete Fahrer entfernen
#    Status ist z B DNF, DNS, DSQ. Diese Fahrer bekommen keine Platzierung
df.loc[df["status"].notna(), "position"] = np.nan

print("\nBeispiel mit Position:")
print(df[["season", "race_id", "session_type", "driver_name", "status", "time_s", "position"]].head(20))


# 5. Basis Features pro Rennen erstellen

# 5.1 Beste Rennzeit pro Rennen (Gewinnerzeit)
df["winner_time_s"] = df.groupby(["season", "race_id", "session_type"])["time_s"].transform("min")

# 5.2 Bester Best-Lap Wert pro Rennen
df["best_race_lap_s"] = df.groupby(["season", "race_id", "session_type"])["best_lap_s"].transform("min")

# 5.3 Laps in Zahlen umwandeln
# alles, was keine Zahl ist, wird zu NaN
df["laps_clean"] = pd.to_numeric(df["laps"], errors="coerce")

# Maximale Rundenzahl pro Rennen auf Basis der bereinigten Laps
df["race_max_laps"] = df.groupby(["season", "race_id", "session_type"])["laps_clean"].transform("max")

# 5.4 Relative Rundenzahl des Fahrers
df["rel_laps"] = df["laps_clean"] / df["race_max_laps"]


# 6. Abgeleitete Performance Features

# 6.1 Zeitabstand zum Sieger in Sekunden
df["time_from_winner_s"] = df["time_s"] - df["winner_time_s"]

# 6.2 Abstand in Sekunden zur besten Rennrunde
df["best_lap_from_best_s"] = df["best_lap_s"] - df["best_race_lap_s"]

# 6.3 Durchschnittliche Rundenzeit (nur wenn time_s und laps vorhanden)
df["avg_lap_time_s"] = df["time_s"] / df["laps_clean"]
df.loc[df["laps_clean"] == 0, "avg_lap_time_s"] = np.nan


# 6.4 Binäre Features für Status
df["finished"] = df["status"].isna().astype(int)
df["is_dnf"] = df["status"].eq("DNF").astype(int)
df["is_dns"] = df["status"].eq("DNS").astype(int)
df["is_dsq"] = df["status"].eq("DSQ").astype(int)

# 6.5 Position als Zahl für Aggregationen
df["position_clean"] = pd.to_numeric(df["position"], errors="coerce")

# 6.6 Teamdurchschnittsplatzierung pro Saison
df["team_avg_pos_season"] = (
    df.groupby(["season", "team_name"])["position_clean"]
      .transform("mean")
)

# 6.7 Team Speed Index: durchschnittliche Rundenzeit des Teams pro Saison
df["team_speed"] = (
    df.groupby(["season", "team_name"])["avg_lap_time_s"]
      .transform("mean")
)

# 6.8 Driver Speed Index: durchschnittliche Rundenzeit des Fahrers pro Saison
df["driver_speed"] = (
    df.groupby(["season", "driver_name"])["avg_lap_time_s"]
      .transform("mean")
)

# 6.9 Top 10 Rate pro Fahrer in der Saison
def top10_rate(series):
    return (series <= 10).mean()

df["driver_top10_rate"] = (
    df.groupby(["season", "driver_name"])["position_clean"]
      .transform(top10_rate)
)

# 6.10 Rennschnitt der durchschnittlichen Rundenzeit
df["race_avg_lap_time_s"] = (
    df.groupby(["season", "race_id", "session_type"])["avg_lap_time_s"]
      .transform("mean")
)

# 6.11 Fahrer im Vergleich zum Team (negative Werte = schneller als Teamdurchschnitt)
df["driver_vs_team"] = df["avg_lap_time_s"] - df["team_speed"]

# 6.12 Fahrer im Vergleich zum Rennschnitt
df["lap_vs_race_avg"] = df["avg_lap_time_s"] - df["race_avg_lap_time_s"]

# 7. Session Typ kodieren (z B Round 1, 2, 3)

session_map = {
    "ROUND1Summary": 1,
    "ROUND2Summary": 2,
    "ROUND3Summary": 3
}

df["session_round"] = df["session_type"].map(session_map).astype("Int64")


# 8. Aufräumen von Hilfsspalten
df = df.drop(columns=["time_s_sort"])

# 9. Ergebnis speichern

df.to_csv("f3_2019_2025_races_features.csv", index=False)

print("\nFeature Engineering abgeschlossen.")
print("Gespeichert als: f3_2019_2025_races_features.csv")
print("Beispielzeilen mit Features:")
print(df[[
    "season", "race_id", "session_type", "driver_name",
    "position", "finished",
    "time_s", "winner_time_s", "time_from_winner_s",
    "best_lap_s", "best_race_lap_s", "best_lap_from_best_s",
    "laps", "race_max_laps", "rel_laps",
    "avg_lap_time_s"
]].head(20))

print("\nNeue Feature Spalten (Auszug):")
print(df[[
    "season", "driver_name", "team_name",
    "position", "position_clean",
    "team_avg_pos_season",
    "driver_speed", "team_speed",
    "driver_top10_rate",
    "driver_vs_team", "lap_vs_race_avg"
]].head(20))
