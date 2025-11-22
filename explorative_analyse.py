import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

# ---------------------------------------------------------
# 1. Daten laden
# ---------------------------------------------------------

df = pd.read_csv("f3_2019_2025_races_features.csv")

print("Daten erfolgreich geladen.")
print("Zeilen:", len(df))
print("Spalten:", df.columns.tolist(), "\n")


# =========================================================
# A) BASIS PLOTS
# =========================================================

# ---------------------------------------------------------
# 2. Plot 1: Verteilung der Rennpositionen
# ---------------------------------------------------------

# Position in numerisch umwandeln
pos = pd.to_numeric(df["position"], errors="coerce")

# NaN entfernen, auf ganze Zahlen casten und alle Positionen 1 bis 30 anzeigen
position_counts = (
    pos.dropna()
       .astype(int)
       .value_counts()
       .reindex(range(1, 31), fill_value=0)
)

plt.figure(figsize=(12, 6))
position_counts.plot(kind="bar")

plt.title("Verteilung der Rennpositionen")
plt.xlabel("Position")
plt.ylabel("Anzahl")
plt.grid(axis="y")
plt.tight_layout()

plt.savefig("plot_positions_distribution_bar.png", dpi=150)
plt.show()


# ---------------------------------------------------------
# 3. Plot 2: Team Performance nach durchschnittlicher Position
#    Nur Finisher berücksichtigen
# ---------------------------------------------------------

team_perf = (
    df[df["finished"] == 1]
    .groupby("team_name")["position"]
    .mean()
    .sort_values()
    .reset_index()
)

plt.figure(figsize=(14, 8))
plt.barh(team_perf["team_name"], team_perf["position"])
plt.title("Team Performance, durchschnittliche Position pro Rennen (niedriger ist besser)")
plt.xlabel("Durchschnittliche Position")
plt.ylabel("Team")
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig("plot_team_performance.png", dpi=150)
plt.show()


# ---------------------------------------------------------
# 4. Plot 3: Schnellste Fahrer nach durchschnittlicher Rundenzeit
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
plt.title("Top 20 Fahrer nach durchschnittlicher Rundenzeit (je weiter links desto schneller)")
plt.xlabel("Durchschnittliche Rundenzeit in Sekunden")
plt.ylabel("Fahrer")
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig("plot_best_drivers.png", dpi=150)
plt.show()

print("\nBasisplots wurden erstellt und gespeichert:")
print(" - plot_positions_distribution_bar.png")
print(" - plot_team_performance.png")
print(" - plot_best_drivers.png")


# =========================================================
# B) FAHRER PERFORMANCE
# =========================================================

# ---------------------------------------------------------
# 5. Plot 4: Fahrer, die über alle Rennen am konstant besten abschneiden
# ---------------------------------------------------------

# Nur Finisher
finished = df[df["finished"] == 1].copy()

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

driver_stats["top10_rate"] = driver_stats["top10"] / driver_stats["starts"]

min_starts = 5
driver_stats_filtered = driver_stats[driver_stats["starts"] >= min_starts].copy()
driver_stats_filtered = driver_stats_filtered.sort_values("avg_position")

print("\nFahrerstatistiken, Top 10 nach Durchschnittsposition:")
print(driver_stats_filtered.head(10))

top_n = 20
top_drivers = driver_stats_filtered.head(top_n)

plt.figure(figsize=(12, 8))
plt.barh(top_drivers["driver_name"], top_drivers["avg_position"])
plt.gca().invert_yaxis()
plt.xlabel("Durchschnittliche Position (niedriger ist besser)")
plt.ylabel("Fahrer")
plt.title(f"Top {top_n} Fahrer nach Durchschnittsposition bei mindestens {min_starts} Starts")
plt.tight_layout()
plt.savefig("plot_driver_avg_position.png", dpi=150)
plt.close()

print("Plot gespeichert als: plot_driver_avg_position.png")


# ---------------------------------------------------------
# 6. Plot 5: Team Performance im Zeitverlauf
# ---------------------------------------------------------

team_year_perf = (
    df[df["finished"] == 1]
    .groupby(["season", "team_name"])["position"]
    .mean()
    .reset_index()
)

plt.figure(figsize=(14, 8))

for team in team_year_perf["team_name"].unique():
    subset = team_year_perf[team_year_perf["team_name"] == team]
    plt.plot(subset["season"], subset["position"], marker="o", alpha=0.7, label=team)

plt.gca().invert_yaxis()
plt.title("Team Performance im Zeitverlauf, durchschnittliche Position (niedriger ist besser)")
plt.xlabel("Saison")
plt.ylabel("Durchschnittliche Position")
plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()
plt.savefig("plot_team_performance_over_time.png", dpi=150)
plt.show()


# ---------------------------------------------------------
# 7. Plot 6: Entwicklung der Fahrer über die Saisons
# ---------------------------------------------------------

driver_year_perf = (
    df[df["finished"] == 1]
    .groupby(["season", "driver_name"])["position"]
    .mean()
    .reset_index()
)

top_drivers = driver_year_perf["driver_name"].value_counts().head(10).index

plt.figure(figsize=(14, 8))

for driver in top_drivers:
    subset = driver_year_perf[driver_year_perf["driver_name"] == driver]
    plt.plot(subset["season"], subset["position"], marker="o", label=driver)

plt.gca().invert_yaxis()
plt.title("Entwicklung der Top Fahrer über die Saisons")
plt.xlabel("Saison")
plt.ylabel("Durchschnittliche Position")
plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()
plt.savefig("plot_driver_development.png", dpi=150)
plt.show()


# ---------------------------------------------------------
# 8. Plot 7: Konsistenz der Fahrer (Varianz der Position)
# ---------------------------------------------------------

driver_consistency = (
    df[df["finished"] == 1]
    .groupby("driver_name")["position"]
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
plt.title("Top 20 konstanteste Fahrer (niedrige Standardabweichung ist stabil)")
plt.xlabel("Standardabweichung der Position")
plt.ylabel("Fahrer")
plt.tight_layout()
plt.savefig("plot_driver_consistency.png", dpi=150)
plt.show()


# =========================================================
# C) TEAMZUVERLÄSSIGKEIT UND VERTEILUNGEN
# =========================================================

# ---------------------------------------------------------
# 9. Plot 8: DNF Analyse nach Team
# ---------------------------------------------------------

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

team_dnf_filtered = team_dnf[team_dnf["starts"] >= 10].sort_values("dnf_rate", ascending=False)

plt.figure(figsize=(14, 8))
plt.barh(team_dnf_filtered["team_name"], team_dnf_filtered["dnf_rate"])
plt.title("DNF Rate pro Team, nur Teams mit mindestens 10 Starts")
plt.xlabel("DNF Rate")
plt.ylabel("Team")
plt.tight_layout()
plt.savefig("plot_team_dnf_rate.png", dpi=150)
plt.show()


# ---------------------------------------------------------
# 10. Plot 9: Boxplot der Positionsverteilung pro Team
# ---------------------------------------------------------

df_finished = df[df["finished"] == 1].copy()

team_counts = df_finished["team_name"].value_counts()
valid_teams = team_counts[team_counts >= 15].index

df_box = df_finished[df_finished["team_name"].isin(valid_teams)]

plt.figure(figsize=(14, 8))

positions_by_team = [df_box[df_box["team_name"] == t]["position"] for t in valid_teams]

plt.boxplot(positions_by_team, labels=valid_teams, vert=False)
plt.gca().invert_xaxis()
plt.title("Positionsverteilung pro Team, nur beendete Rennen")
plt.xlabel("Position (niedriger ist besser)")
plt.ylabel("Team")
plt.tight_layout()
plt.savefig("plot_team_position_boxplot.png", dpi=150)
plt.show()


# =========================================================
# D) HEATMAP UND DRIVER VS TEAM PACE
# =========================================================

# ---------------------------------------------------------
# 11. Plot 10: Heatmap der Rennpositionen in der neuesten Saison
# ---------------------------------------------------------

latest_season = df["season"].max()
df_latest = df[(df["season"] == latest_season) & (df["finished"] == 1)].copy()

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
plt.title(f"Heatmap der Rennpositionen in Saison {latest_season}")
plt.xlabel("Race ID")
plt.ylabel("Fahrer")
plt.tight_layout()
plt.savefig("plot_heatmap_positions_latest_season.png", dpi=150)
plt.show()


# ---------------------------------------------------------
# 12. Plot 11: Fahrer vs Team Pace
# ---------------------------------------------------------

driver_pace = (
    df.groupby("driver_name")
    .agg(
        starts=("race_id", "count"),
        driver_vs_team_mean=("driver_vs_team", "mean"),
    )
    .reset_index()
)

driver_pace_filtered = driver_pace[driver_pace["starts"] >= 5].dropna()

best_drivers_vs_team = driver_pace_filtered.sort_values("driver_vs_team_mean").head(10)
worst_drivers_vs_team = driver_pace_filtered.sort_values("driver_vs_team_mean").tail(10)

plt.figure(figsize=(12, 6))
plt.barh(best_drivers_vs_team["driver_name"], best_drivers_vs_team["driver_vs_team_mean"])
plt.gca().invert_yaxis()
plt.title("Top 10 Fahrer schneller als Teamdurchschnitt, negative Werte sind besser")
plt.xlabel("Durchschnittlicher Unterschied zur Team Pace in Sekunden")
plt.ylabel("Fahrer")
plt.tight_layout()
plt.savefig("plot_driver_vs_team_best.png", dpi=150)
plt.show()

plt.figure(figsize=(12, 6))
plt.barh(worst_drivers_vs_team["driver_name"], worst_drivers_vs_team["driver_vs_team_mean"])
plt.gca().invert_yaxis()
plt.title("Bottom 10 Fahrer langsamer als Teamdurchschnitt, positive Werte sind schlechter")
plt.xlabel("Durchschnittlicher Unterschied zur Team Pace in Sekunden")
plt.ylabel("Fahrer")
plt.tight_layout()
plt.savefig("plot_driver_vs_team_worst.png", dpi=150)
plt.show()


# =========================================================
# E) ERWEITERTE EDA UND DISTRIBUTIONEN
# =========================================================

print("\nStarte erweiterte EDA.")

df_valid = df.copy()

# ---------------------------------------------------------
# 13. Plot 12: Korrelationsmatrix wichtiger numerischer Features
# ---------------------------------------------------------

numeric_cols = [
    "position",
    "time_s",
    "best_lap_s",
    "avg_lap_time_s",
    "time_from_winner_s",
    "laps_clean",
    "race_max_laps",
    "rel_laps",
    "driver_vs_team",
]

available_numeric = [c for c in numeric_cols if c in df_valid.columns]

corr = df_valid[available_numeric].corr()

plt.figure(figsize=(10, 8))
im = plt.imshow(corr.values, cmap="coolwarm", vmin=-1, vmax=1)
plt.colorbar(im, label="Korrelationskoeffizient")

plt.xticks(
    ticks=range(len(available_numeric)),
    labels=available_numeric,
    rotation=45,
    ha="right"
)
plt.yticks(
    ticks=range(len(available_numeric)),
    labels=available_numeric
)

plt.title("Korrelationsmatrix wichtiger numerischer Features")
plt.tight_layout()
plt.savefig("plot_corr_matrix.png", dpi=150)
plt.close()

print("Plot gespeichert: plot_corr_matrix.png")


# ---------------------------------------------------------
# 14. Plot 13: Best Lap vs Position
# ---------------------------------------------------------

df_bl = df_valid[["best_lap_s", "position"]].dropna()

plt.figure(figsize=(8, 6))
plt.scatter(df_bl["best_lap_s"], df_bl["position"], alpha=0.3)
plt.gca().invert_yaxis()
plt.xlabel("Beste Rundenzeit in Sekunden")
plt.ylabel("Endposition, 1 ist Sieger")
plt.title("Zusammenhang Best Lap und Endposition")
plt.tight_layout()
plt.savefig("plot_bestlap_vs_position.png", dpi=150)
plt.close()

print("Plot gespeichert: plot_bestlap_vs_position.png")


# ---------------------------------------------------------
# 15. Plot 14: Zeitabstand zum Sieger vs relative Rundenzahl
# ---------------------------------------------------------

if "rel_laps" in df_valid.columns:
    df_rel = df_valid[["rel_laps", "time_from_winner_s"]].dropna()

    plt.figure(figsize=(8, 6))
    plt.scatter(df_rel["rel_laps"], df_rel["time_from_winner_s"], alpha=0.3)
    plt.xlabel("Relative Rundenzahl, 0 bis 1")
    plt.ylabel("Zeitabstand zum Sieger in Sekunden")
    plt.title("Zeitabstand zum Sieger nach gefahrenem Rundenanteil")
    plt.tight_layout()
    plt.savefig("plot_rel_laps_vs_gap.png", dpi=150)
    plt.close()

    print("Plot gespeichert: plot_rel_laps_vs_gap.png")
else:
    print("Spalte rel_laps fehlt, Plot 14 wird übersprungen.")


# ---------------------------------------------------------
# 16. Plot 15: Histogramme wichtiger Features
# ---------------------------------------------------------

features_hist = [
    "position",
    "time_s",
    "best_lap_s",
    "avg_lap_time_s",
    "time_from_winner_s",
]

for col in features_hist:
    if col in df_valid.columns:
        plt.figure(figsize=(8, 5))
        df_valid[col].dropna().hist(bins=40)
        plt.title(f"Verteilung von {col}")
        plt.xlabel(col)
        plt.ylabel("Häufigkeit")
        plt.tight_layout()
        fname = f"hist_{col}.png"
        plt.savefig(fname, dpi=150)
        plt.close()
        print(f"Plot gespeichert: {fname}")

print("\nErweiterte EDA abgeschlossen.")
