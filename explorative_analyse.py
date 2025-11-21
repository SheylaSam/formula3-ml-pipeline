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
