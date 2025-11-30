import pandas as pd
import numpy as np
from pathlib import Path

# ============================================================
# 1. Pfade definieren (für deine Struktur)
# ============================================================

# __file__ liegt in src/f2/f2_feature_engineering.py
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "f2"   # <--- WICHTIG: nur ein "f2"!

print("PROJECT ROOT:", PROJECT_ROOT)
print("F2 DATA DIR:", DATA_DIR)

csv_files = list(DATA_DIR.glob("*.csv"))
print("Gefundene CSV-Dateien im F2-Ordner:")
for f in csv_files:
    print("  -", f.name)


# ============================================================
# 2. Helper: Zeitstring → Sekunden
# ============================================================

def time_to_seconds(t):
    if pd.isna(t) or t in ["-", "", " "]:
        return np.nan
    t = str(t).strip()
    try:
        parts = t.split(":")
        if len(parts) == 2:
            minutes, seconds = parts
            return int(minutes) * 60 + float(seconds)
        if len(parts) == 3:
            hours, minutes, seconds = parts
            return int(hours)*3600 + int(minutes)*60 + float(seconds)
    except:
        return np.nan
    return np.nan


# ============================================================
# 3. Helper zum Laden: nach Pattern suchen
# ============================================================

def load_csv(pattern: str) -> pd.DataFrame:
    """
    Lädt die erste CSV, die auf das Pattern passt.
    z.B. load_csv("Free-Practice") findet "Free-Practice.csv".
    """
    matches = list(DATA_DIR.glob(pattern + ".csv")) + list(DATA_DIR.glob(pattern + "*.csv"))
    if not matches:
        raise FileNotFoundError(
            f"Keine Datei gefunden für Pattern '{pattern}'. "
            f"Verfügbare Dateien: {[f.name for f in DATA_DIR.glob('*.csv')]}"
        )
    print(f"Lade Datei für Pattern '{pattern}':", matches[0].name)
    return pd.read_csv(matches[0])


# ============================================================
# 4. CSV-Dateien laden
# ============================================================

free_practice = load_csv("Free-Practice")
qualifying    = load_csv("Qualifying-Session")
feature_race  = load_csv("Feature-Race")
sprint_race1  = load_csv("Sprint-Race")
sprint_race2  = load_csv("Sprint-Race-2")
race_results  = load_csv("Formula2_Race_Results")
drivers_to_f1 = load_csv("f2_drivers_to_f1")


# ============================================================
# 5. Spalten vereinheitlichen
# ============================================================

def clean_cols(df):
    df = df.copy()
    df.columns = [c.lower().replace(" ", "_") for c in df.columns]
    return df

free_practice, qualifying, feature_race, sprint_race1, sprint_race2, race_results, drivers_to_f1 = \
    [clean_cols(df) for df in
     [free_practice, qualifying, feature_race, sprint_race1, sprint_race2, race_results, drivers_to_f1]]

# Fahrername einheitlich "driver"
rename_candidates = ["pilot_name", "driver_name", "name"]

for df in [free_practice, qualifying, feature_race, sprint_race1, sprint_race2]:
    for c in rename_candidates:
        if c in df.columns:
            df.rename(columns={c: "driver"}, inplace=True)

if "driver_name" in race_results.columns:
    race_results.rename(columns={"driver_name": "driver"}, inplace=True)

if "pilot_name" in drivers_to_f1.columns:
    drivers_to_f1.rename(columns={"pilot_name": "driver"}, inplace=True)


# ============================================================
# 6. Sessions vorbereiten
# ============================================================

def prepare_session(df, session_name):
    df = df.copy()
    df["session_type"] = session_name

    # numerische Spalten
    for col in ["pos", "laps", "kph"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Zeiten
    if "time" in df.columns:
        df["time_seconds"] = df["time"].apply(time_to_seconds)

    if "best" in df.columns:
        df["best_lap_seconds"] = df["best"].apply(time_to_seconds)

    return df

free_practice  = prepare_session(free_practice,  "free_practice")
qualifying     = prepare_session(qualifying,     "qualifying")
feature_race   = prepare_session(feature_race,   "feature_race")
sprint_race1   = prepare_session(sprint_race1,   "sprint_race1")
sprint_race2   = prepare_session(sprint_race2,   "sprint_race2")


# ============================================================
# 7. Sessions zusammenführen
# ============================================================

sessions = pd.concat(
    [free_practice, qualifying, feature_race, sprint_race1, sprint_race2],
    ignore_index=True
)


# ============================================================
# 8. Feature Engineering pro Fahrer
# ============================================================

driver_base = sessions.groupby("driver").agg(
    total_laps=("laps", "sum"),
    avg_kph=("kph", "mean"),
    avg_position=("pos", "mean"),
    best_position=("pos", "min"),
    avg_best_lap=("best_lap_seconds", "mean")
).reset_index()

session_positions = (
    sessions.groupby(["driver", "session_type"])["pos"]
    .mean()
    .unstack()
    .add_prefix("avg_pos_")
    .reset_index()
)

features = driver_base.merge(session_positions, on="driver", how="left")


# ============================================================
# 9. Finale Platzierung (Race Results) hinzufügen
# ============================================================

if "position" in race_results.columns:
    final_pos = race_results.groupby("driver")["position"].mean().reset_index()
    final_pos.rename(columns={"position": "avg_final_position"}, inplace=True)
    features = features.merge(final_pos, on="driver", how="left")


# ============================================================
# 10. Label: reached_f1 hinzufügen
# ============================================================

if "reached_f1" in drivers_to_f1.columns:
    labels = drivers_to_f1[["driver", "reached_f1"]]
    features = features.merge(labels, on="driver", how="left")


# ============================================================
# 11. Speichern
# ============================================================

OUTFILE = DATA_DIR / "f2_features.csv"
features.to_csv(OUTFILE, index=False)

print("✔ Feature Engineering abgeschlossen!")
print("→ Datei gespeichert unter:", OUTFILE)
print("Anzahl Fahrer:", len(features))
print("Anzahl Features:", features.shape[1])
print(features.head())
