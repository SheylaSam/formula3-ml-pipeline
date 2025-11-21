# explorative_analysen.py

import pandas as pd
import matplotlib.pyplot as plt

# 1. Daten laden
df = pd.read_csv("f3_2019_2025_races_features.csv")

print("Daten erfolgreich geladen!")
print("Zeilen:", len(df))
print("Spalten:", df.columns.tolist(), "\n")


# ---------------------------------------------------------
# 2. Plot 1 – Verteilung der Rennpositionen
# ---------------------------------------------------------
plt.figure(figsize=(12, 6))
df["position"].dropna().astype(int).hist(bins=30)
plt.title("Verteilung der Rennpositionen")
plt.xlabel("Position")
plt.ylabel("Anzahl")
plt.grid(True)
plt.tight_layout()
plt.savefig("plot_positions_distribution.png")
plt.show()


# ---------------------------------------------------------
# 3. Plot 2 – Team-Performance (durchschnittliche Position)
# ---------------------------------------------------------
team_perf = (
    df.groupby("team_name")["position"]
    .mean()
    .sort_values()
    .reset_index()
)

plt.figure(figsize=(14, 8))
plt.barh(team_perf["team_name"], team_perf["position"])
plt.title("Team Performance – Durchschnittliche Position (niedriger = besser)")
plt.xlabel("Durchschnittliche Position")
plt.ylabel("Team")
plt.gca().invert_yaxis()  # bestes Team oben
plt.tight_layout()
plt.savefig("plot_team_performance.png")
plt.show()


# ---------------------------------------------------------
# 4. Plot 3 – Schnellste Fahrer nach durchschnittlicher Rundenzeit
# ---------------------------------------------------------
driver_perf = (
    df.groupby("driver_name")["avg_lap_time_s"]
    .mean()
    .sort_values()
    .head(20)
    .reset_index()
)

plt.figure(figsize=(14, 8))
plt.barh(driver_perf["driver_name"], driver_perf["avg_lap_time_s"])
plt.title("Top 20 Fahrer – Durchschnittliche Rundenzeit (schneller = links)")
plt.xlabel("Durchschnittliche Rundenzeit (Sekunden)")
plt.ylabel("Fahrer")
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig("plot_best_drivers.png")
plt.show()

print("\nAlle 3 Plots wurden erstellt und gespeichert:")
print(" - plot_positions_distribution.png")
print(" - plot_team_performance.png")
print(" - plot_best_drivers.png")

# ---------------------------------------------------------
# 5. Plot 4 – Fahrer, die über alle Rennen am konstant besten abschneiden
# ---------------------------------------------------------

# 1. Daten einlesen
df = pd.read_csv("f3_2019_2025_races_features.csv")

print("Zeilen:", len(df))
print("Spalten:", df.columns.tolist())

# Nur Fahrer, die das Rennen beendet haben (finished = 1)
finished = df[df["finished"] == 1].copy()

# 2. Fahrer-Statistiken berechnen
driver_stats = (
    finished
    .groupby("driver_name")
    .agg(
        starts=("race_id", "count"),
        wins=("position", lambda s: (s == 1).sum()),
        podiums=("position", lambda s: (s <= 3).sum()),
        top10=("position", lambda s: (s <= 10).sum()),
        avg_position=("position", "mean"),
        avg_time_gap_s=("time_from_winner_s", "mean"),
    )
    .reset_index()
)

# Top-10-Quote
driver_stats["top10_rate"] = driver_stats["top10"] / driver_stats["starts"]

# 3. Nur Fahrer mit genügend Starts (z. B. mindestens 5)
min_starts = 5
driver_stats_filtered = driver_stats[driver_stats["starts"] >= min_starts].copy()

# Sortierung: beste Durchschnittsposition zuerst
driver_stats_filtered = driver_stats_filtered.sort_values("avg_position")

print("\nFahrer-Statistiken (Top 10):")
print(driver_stats_filtered.head(10))

# 4. Plot: Top 20 Fahrer nach durchschnittlicher Position
top_n = 20
top_drivers = driver_stats_filtered.head(top_n)

plt.figure(figsize=(12, 8))
plt.barh(top_drivers["driver_name"], top_drivers["avg_position"])
plt.gca().invert_yaxis()
plt.xlabel("Durchschnittliche Position (niedriger = besser)")
plt.ylabel("Fahrer")
plt.title(f"Top {top_n} Fahrer – Durchschnittliche Position (min. {min_starts} Starts)")
plt.tight_layout()
plt.savefig("plot_driver_avg_position.png", dpi=150)
plt.close()

print("\nPlot gespeichert als: plot_driver_avg_position.png")

# ---------------------------------------------------------
# 6. Plot 5 – Team-Performance im Zeitverlauf
# ---------------------------------------------------------

team_year_perf = (
    df.groupby(["season", "team_name"])["position"]
      .mean()
      .reset_index()
)

plt.figure(figsize=(14, 8))

for team in team_year_perf["team_name"].unique():
    subset = team_year_perf[team_year_perf["team_name"] == team]
    plt.plot(subset["season"], subset["position"], marker="o", alpha=0.7, label=team)

plt.gca().invert_yaxis()  # bessere Position oben
plt.title("Team-Performance im Zeitverlauf (niedriger = besser)")
plt.xlabel("Saison")
plt.ylabel("Durchschnittliche Position")
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig("plot_team_performance_over_time.png", dpi=150)
plt.show()

# ---------------------------------------------------------
# 7. Plot 6 – Entwicklung der Fahrer über die Saisons
# ---------------------------------------------------------

driver_year_perf = (
    df.groupby(["season", "driver_name"])["position"]
      .mean()
      .reset_index()
)

top_drivers = driver_year_perf["driver_name"].value_counts().head(10).index

plt.figure(figsize=(14, 8))

for driver in top_drivers:
    subset = driver_year_perf[driver_year_perf["driver_name"] == driver]
    plt.plot(subset["season"], subset["position"], marker="o", label=driver)

plt.gca().invert_yaxis()
plt.title("Fahrerentwicklung über die Saisons (Top 10 Fahrer)")
plt.xlabel("Saison")
plt.ylabel("Durchschnittliche Position")
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig("plot_driver_development.png", dpi=150)
plt.show()

# ---------------------------------------------------------
# 8. Plot 7 – Konsistenz der Fahrer (Positions-Varianz)
# ---------------------------------------------------------

driver_consistency = (
    df.groupby("driver_name")["position"]
      .std()
      .reset_index()
      .rename(columns={"position": "position_std"})
      .dropna()
      .sort_values("position_std")
)

top_consistent = driver_consistency.head(20)

plt.figure(figsize=(14, 8))
plt.barh(top_consistent["driver_name"], top_consistent["position_std"])
plt.gca().invert_yaxis()
plt.title("Top 20 konstanteste Fahrer (niedrige Std = stabil)")
plt.xlabel("Standardabweichung der Position")
plt.ylabel("Fahrer")
plt.tight_layout()
plt.savefig("plot_driver_consistency.png", dpi=150)
plt.show()

# ---------------------------------------------------------
# 9. Plot 8 – DNF-Analyse nach Team
# ---------------------------------------------------------

# Nur Zeilen, bei denen der Fahrer überhaupt im Grid stand
df_status = df.copy()

team_dnf = (
    df_status.groupby("team_name")
    .agg(
        starts=("race_id", "count"),
        dnfs=("is_dnf", "sum"),
        dns=("is_dns", "sum"),
        dsq=("is_dsq", "sum"),
    )
    .reset_index()
)

team_dnf["dnf_rate"] = team_dnf["dnfs"] / team_dnf["starts"]

# Teams mit genügend Starts filtern (z. B. >= 10)
team_dnf_filtered = team_dnf[team_dnf["starts"] >= 10].sort_values("dnf_rate", ascending=False)

plt.figure(figsize=(14, 8))
plt.barh(team_dnf_filtered["team_name"], team_dnf_filtered["dnf_rate"])
plt.title("DNF-Rate pro Team (nur Teams mit ≥10 Starts)")
plt.xlabel("DNF-Rate")
plt.ylabel("Team")
plt.tight_layout()
plt.savefig("plot_team_dnf_rate.png", dpi=150)
plt.show()

# ---------------------------------------------------------
# 10. Plot 9 – Boxplot der Positionsverteilung pro Team
# ---------------------------------------------------------

# Nur beendete Rennen für faire Positionsverteilung
df_finished = df[df["finished"] == 1].copy()

# Teams mit genügend Zielankünften
team_counts = df_finished["team_name"].value_counts()
valid_teams = team_counts[team_counts >= 15].index  # z. B. mindestens 15 Zielankünfte

df_box = df_finished[df_finished["team_name"].isin(valid_teams)]

plt.figure(figsize=(14, 8))

# Boxplot: Position pro Team
positions_by_team = [df_box[df_box["team_name"] == t]["position"] for t in valid_teams]

plt.boxplot(positions_by_team, labels=valid_teams, vert=False)
plt.gca().invert_xaxis()  # bessere Position (1) links
plt.title("Positionsverteilung pro Team (Boxplot, nur beendete Rennen)")
plt.xlabel("Position (niedriger = besser)")
plt.ylabel("Team")
plt.tight_layout()
plt.savefig("plot_team_position_boxplot.png", dpi=150)
plt.show()

# ---------------------------------------------------------
# 11. Plot 10 – Heatmap: Positionen pro Rennen (eine Saison, ausgewählte Fahrer)
# ---------------------------------------------------------

# Neueste Saison wählen
latest_season = df["season"].max()
df_latest = df[(df["season"] == latest_season) & (df["finished"] == 1)].copy()

# Fahrer mit den meisten Starts in dieser Saison
top_drivers_season = (
    df_latest["driver_name"]
    .value_counts()
    .head(15)
    .index
)

df_heat = df_latest[df_latest["driver_name"].isin(top_drivers_season)]

pivot = df_heat.pivot_table(
    index="driver_name",
    columns="race_id",
    values="position",
    aggfunc="min",
)

plt.figure(figsize=(12, 8))
im = plt.imshow(pivot.values, aspect="auto", cmap="viridis_r")

plt.colorbar(im, label="Position")
plt.xticks(
    ticks=range(len(pivot.columns)),
    labels=pivot.columns,
    rotation=45,
    ha="right"
)
plt.yticks(
    ticks=range(len(pivot.index)),
    labels=pivot.index
)
plt.title(f"Heatmap der Rennpositionen – Saison {latest_season}")
plt.xlabel("Race ID")
plt.ylabel("Fahrer")
plt.tight_layout()
plt.savefig("plot_heatmap_positions_latest_season.png", dpi=150)
plt.show()

# ---------------------------------------------------------
# 12. Plot 11 – Fahrer vs. Team-Pace (driver_vs_team)
# ---------------------------------------------------------

# Nur Fahrer mit genügend Starts
driver_pace = (
    df.groupby("driver_name")
    .agg(
        starts=("race_id", "count"),
        driver_vs_team_mean=("driver_vs_team", "mean"),
    )
    .reset_index()
)

driver_pace_filtered = driver_pace[driver_pace["starts"] >= 5].dropna()

# Beste (negativ = schneller als Team) und schlechteste Fahrer
best_drivers_vs_team = driver_pace_filtered.sort_values("driver_vs_team_mean").head(10)
worst_drivers_vs_team = driver_pace_filtered.sort_values("driver_vs_team_mean").tail(10)

# Plot: Beste Fahrer vs Team
plt.figure(figsize=(12, 6))
plt.barh(best_drivers_vs_team["driver_name"], best_drivers_vs_team["driver_vs_team_mean"])
plt.gca().invert_yaxis()
plt.title("Top 10 Fahrer – Schneller als Teamdurchschnitt (negativ = schneller)")
plt.xlabel("Durchschnittlicher Unterschied zur Team-Pace (Sekunden)")
plt.ylabel("Fahrer")
plt.tight_layout()
plt.savefig("plot_driver_vs_team_best.png", dpi=150)
plt.show()

# Plot: Schlechteste Fahrer vs Team
plt.figure(figsize=(12, 6))
plt.barh(worst_drivers_vs_team["driver_name"], worst_drivers_vs_team["driver_vs_team_mean"])
plt.gca().invert_yaxis()
plt.title("Bottom 10 Fahrer – Langsamer als Teamdurchschnitt (positiv = langsamer)")
plt.xlabel("Durchschnittlicher Unterschied zur Team-Pace (Sekunden)")
plt.ylabel("Fahrer")
plt.tight_layout()
plt.savefig("plot_driver_vs_team_worst.png", dpi=150)
plt.show()
