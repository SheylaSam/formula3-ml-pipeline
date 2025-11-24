import pandas as pd

df = pd.read_csv("f3_2019_2025_with_drivers_and_status.csv")

print("Zeilen:", len(df))
print(df[["time", "gap", "best"]].head())

def time_to_seconds(t):
    """Wandelt Zeitstrings wie '40:29.021' oder '1:34.711' in Sekunden um."""
    if pd.isna(t):
        return None

    t = str(t).strip()
    # Sonderwerte rausfiltern
    if t in ["-", "", "RET", "DNS", "DNF", "DSQ"]:
        return None

    if ":" not in t:
        # z.B. '1 LAP' oder reine Gap-Werte wie '2.121'
        return None

    parts = t.split(":")
    try:
        if len(parts) == 2:
            m, s = parts
            return int(m) * 60 + float(s)
        elif len(parts) == 3:
            h, m, s = parts
            return int(h) * 3600 + int(m) * 60 + float(s)
        else:
            return None
    except ValueError:
        return None

# Renndauer in Sekunden
df["time_s"] = df["time"].apply(time_to_seconds)

# Best Lap in Sekunden
df["best_lap_s"] = df["best"].apply(time_to_seconds)

def gap_to_seconds(g):
    if pd.isna(g):
        return None
    g = str(g).strip()
    if g in ["-", "", "RET", "DNS", "DNF", "DSQ"]:
        return None
    try:
        return float(g)
    except ValueError:
        # z.B. '1 LAP' oder '2 LAPS'
        return None

df["gap_s"] = df["gap"].apply(gap_to_seconds)

print(df[["time", "time_s", "best", "best_lap_s", "gap", "gap_s"]].head(15))

df.to_csv("f3_2019_2025_with_times.csv", index=False)
print("Gespeichert als f3_2019_2025_with_times.csv")
