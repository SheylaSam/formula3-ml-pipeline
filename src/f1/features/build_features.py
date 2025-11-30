from pathlib import Path
import pandas as pd

# Basisverzeichnis: .../formula3-ml-pipeline
BASE_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = BASE_DIR / "data" / "f1" / "processed"

INPUT = DATA_DIR / "f1_2023_round1_R_clean.csv"
OUTPUT = DATA_DIR / "f1_2023_round1_R_features.csv"


def build_features():
    print(f"Lese Daten aus: {INPUT}")
    df = pd.read_csv(INPUT)

    # Zur Sicherheit sortieren
    df = df.sort_values(["Driver", "LapNumber"]).reset_index(drop=True)

    # -------------------------
    # 1) Pitlaps über TyreLife-Reset / Compound-Wechsel
    # -------------------------
    df["TyreLife_prev"] = df.groupby("Driver")["TyreLife"].shift(1)
    df["Compound_prev"] = df.groupby("Driver")["Compound"].shift(1)

    # TyreLife-Reset (neuer Stint)
    tyre_reset = df["TyreLife"] < df["TyreLife_prev"]

    # Compound-Wechsel NUR zählen, wenn vorheriger Compound existiert
    compound_change = (
        (df["Compound"] != df["Compound_prev"]) &
        df["Compound_prev"].notna()
    )

    # Pitlap = TyreLife-Reset ODER Compound-Wechsel
    df["is_pit_lap"] = (tyre_reset | compound_change).fillna(False)

    # Erste Runde pro Fahrer niemals als Pitlap zählen
    first_laps = df.groupby("Driver").head(1).index
    df.loc[first_laps, "is_pit_lap"] = False

    # -------------------------
    # 2) LapTime-Differenz zur vorherigen Runde
    # -------------------------
    df["lap_time_prev"] = df.groupby("Driver")["LapTime_s"].shift(1)
    df["lap_time_diff_prev"] = df["LapTime_s"] - df["lap_time_prev"]

    # -------------------------
    # 3) Rolling-Feature (Durchschnitt der letzten 3 Runden)
    # -------------------------
    df["rolling_lap_time_3"] = (
        df.groupby("Driver")["LapTime_s"]
          .transform(lambda s: s.rolling(window=3, min_periods=1).mean())
    )

    # -------------------------
    # 4) Kumulative Rennzeit pro Fahrer
    # -------------------------
    df["cumulative_race_time"] = (
        df.groupby("Driver")["LapTime_s"].cumsum()
    )

    # Hilfsspalten löschen
    df = df.drop(columns=["TyreLife_prev", "Compound_prev", "lap_time_prev"])

    # Output-Ordner sicherstellen
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    # Speichern
    df.to_csv(OUTPUT, index=False)
    print(f"Features gespeichert unter: {OUTPUT}")
    print("Shape mit Features:", df.shape)


if __name__ == "__main__":
    build_features()


