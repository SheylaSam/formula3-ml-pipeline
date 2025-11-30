from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

# Ordner, in dem unser Basis-CSV liegt
PROCESSED_DIR = Path(__file__).resolve().parents[3] / "data" / "f1" / "processed"


def load_f1_base_dataset() -> pd.DataFrame:
    """
    Lädt das von f1_build_dataset.py erzeugte Basis-Dataset:
    data/f1/processed/f1_base_dataset.csv
    """
    path = PROCESSED_DIR / "f1_base_dataset.csv"
    if not path.exists():
        raise FileNotFoundError(f"Base-Dataset nicht gefunden: {path}")
    return pd.read_csv(path, low_memory=False)


def _time_str_to_seconds(x: Optional[str]) -> float:
    """
    Konvertiert Zeitstrings wie '1:23.456' in Sekunden (float).
    Gibt np.nan zurück, wenn Parsing nicht möglich ist.
    """
    if x is None or pd.isna(x):
        return np.nan
    s = str(x).strip()
    if not s or s in ["\\N", "nan"]:
        return np.nan

    try:
        parts = s.split(":")
        if len(parts) == 2:
            minutes = int(parts[0])
            seconds = float(parts[1])
            return minutes * 60 + seconds
        elif len(parts) == 3:
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = float(parts[2])
            return (hours * 60 + minutes) * 60 + seconds
    except Exception:
        return np.nan

    return np.nan


def build_f1_season_features(min_year: int = 2019) -> pd.DataFrame:
    """
    Baut saisonbasierte F1-Features pro Fahrer + Jahr.

    Orientierung:
    - F2: total_laps, avg_kph, avg_position, avg_best_lap, avg_final_position
    - F3 (driver_clusters_stats): avg_position, std_position, avg_best_lap,
      avg_gap_to_winner, dnf_rate
    - Zusätzlich: Team- und Speed-Kontext wie in F3 (team_speed, driver_speed, driver_vs_team)

    Hinweis: Keine echten Lap-Features (pro Runde), da im F1-Datensatz
    keine vollständigen Lap-Times vorhanden sind (nur Gesamtzeit + Bestlap).
    """

    df = load_f1_base_dataset().copy()

    # Auf moderne Jahre beschränken (wie dein aktuelles f1_features.csv)
    df = df[df["year"] >= min_year].copy()

    # Numerische Spalten sauber casten
    for col in ["positionOrder", "grid", "points", "laps", "milliseconds", "fastestLapSpeed"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Bestlap-Zeit in Sekunden
    if "fastestLapTime" in df.columns:
        df["fastestLapTime_s"] = df["fastestLapTime"].apply(_time_str_to_seconds)
    else:
        df["fastestLapTime_s"] = np.nan

    # DNF-Heuristik:
    # - positionText nicht numerisch (z.B. 'R', 'D', ...)
    # - ODER weniger Runden als der Rennsieger
    race_max_laps = df.groupby("raceId")["laps"].transform("max")
    is_pos_numeric = df["positionText"].astype(str).str.isnumeric()
    df["is_dnf"] = (~is_pos_numeric) | (df["laps"] < race_max_laps)

    # Gap zum Gewinner in Sekunden
    # (auf Basis der "milliseconds"-Spalte)
    winner_ms = df.groupby("raceId")["milliseconds"].transform("min")
    df["gap_to_winner_s"] = (df["milliseconds"] - winner_ms) / 1000.0

    # Positionsänderung (Racecraft)
    df["pos_change"] = df["grid"] - df["positionOrder"]

    # Basis-Flags
    df["finished_on_podium"] = df["positionOrder"] <= 3
    df["finished_top10"] = df["positionOrder"] <= 10

    if "finished_in_points" in df.columns:
        df["finished_in_points"] = df["finished_in_points"].astype(bool)
    else:
        df["finished_in_points"] = df["points"] > 0

    # -----------------------------------------------------
    # 1) Fahrer-Saison-Aggregate
    # -----------------------------------------------------
    grouped = df.groupby(["driverId", "year"])

    season = (
        grouped.agg(
            n_races=("raceId", "nunique"),
            total_points=("points", "sum"),
            avg_points=("points", "mean"),
            avg_grid=("grid", "mean"),
            avg_finish=("positionOrder", "mean"),
            best_finish=("positionOrder", "min"),
            worst_finish=("positionOrder", "max"),
            wins=("positionOrder", lambda s: (s == 1).sum()),
            total_laps=("laps", "sum"),
            avg_best_lap=("fastestLapTime_s", "mean"),
            avg_kph=("fastestLapSpeed", "mean"),
            avg_gap_to_winner=("gap_to_winner_s", "mean"),
            finish_std=("positionOrder", "std"),
            points_std=("points", "std"),
            pos_change_std=("pos_change", "std"),
            avg_pos_change=("pos_change", "mean"),
            dnf_count=("is_dnf", "sum"),
            podiums=("finished_on_podium", "sum"),
            top10_finishes=("finished_top10", "sum"),
            points_finishes=("finished_in_points", "sum"),
        )
        .reset_index()
    )

    # Quoten / Raten
    season["podium_rate"] = season["podiums"] / season["n_races"]
    season["win_rate"] = season["wins"] / season["n_races"]
    season["top10_rate"] = season["top10_finishes"] / season["n_races"]
    season["points_rate"] = season["points_finishes"] / season["n_races"]
    season["dnf_rate"] = season["dnf_count"] / season["n_races"]
    season["clean_race_rate"] = 1.0 - season["dnf_rate"]

    # Std-NaNs zu 0 (falls nur 1 Rennen)
    for col in ["finish_std", "points_std", "pos_change_std"]:
        season[col] = season[col].fillna(0.0)

    # -----------------------------------------------------
    # 2) Team-Zuordnung pro Fahrer/Saison (Mode)
    # -----------------------------------------------------
    constructor_map = (
        df.groupby(["driverId", "year"])["constructorId"]
        .agg(lambda x: x.mode().iloc[0] if not x.mode().empty else x.iloc[0])
        .reset_index()
    )
    season = season.merge(constructor_map, on=["driverId", "year"], how="left")

    # -----------------------------------------------------
    # 3) Team-Season-Features (Team-Speed & Team-Performance, F3-Style)
    # -----------------------------------------------------
    team_stats = (
        df.groupby(["constructorId", "year"])
        .agg(
            team_total_points=("points", "sum"),
            team_avg_points=("points", "mean"),
            team_avg_pos_season=("positionOrder", "mean"),
            team_speed=("fastestLapTime_s", "mean"),  # niedriger = schneller
        )
        .reset_index()
    )

    season = season.merge(team_stats, on=["constructorId", "year"], how="left")

    # Driver vs Team (Punkte & Position)
    season["driver_vs_team_avg_points"] = season["avg_points"] - season["team_avg_points"]
    season["driver_vs_team_avg_finish"] = season["avg_finish"] - season["team_avg_pos_season"]

    # -----------------------------------------------------
    # 4) Speed-Kontext: driver_speed & driver_vs_team_speed
    # -----------------------------------------------------
    # Analog zu F3: "speed" = durchschnittliche Bestlap-Zeit (je niedriger, desto besser)
    season["driver_speed"] = season["avg_best_lap"]
    season["driver_vs_team_speed"] = season["avg_best_lap"] - season["team_speed"]

    # -----------------------------------------------------
    # 5) Fahrer-Metadaten hinzufügen
    # -----------------------------------------------------
    meta_cols = ["driverId"]
    for c in ["code", "forename", "surname", "nationality", "driver_name"]:
        if c in df.columns:
            meta_cols.append(c)

    driver_meta = df[meta_cols].drop_duplicates("driverId")
    season = season.merge(driver_meta, on="driverId", how="left")

    # Falls driver_name fehlt, sinnvoll ersetzen
    if "driver_name" not in season.columns:
        if "forename" in season.columns and "surname" in season.columns:
            season["driver_name"] = season["forename"] + " " + season["surname"]
        else:
            season["driver_name"] = season["driverId"].astype(str)

    # -----------------------------------------------------
    # 6) Spalten sortieren – angelehnt an F2 & F3
    # -----------------------------------------------------
    id_cols = [
        "driverId",
        "driver_name",
        "code",
        "forename",
        "surname",
        "nationality",
        "year",
        "constructorId",
    ]

    perf_cols = [
        "n_races",
        "total_points",
        "avg_points",
        "avg_grid",
        "avg_finish",
        "best_finish",
        "worst_finish",
        "wins",
        "podiums",
        "podium_rate",
        "win_rate",
        "points_finishes",
        "points_rate",
        "top10_finishes",
        "top10_rate",
    ]

    pace_cols = [
        "total_laps",
        "avg_best_lap",
        "avg_kph",
        "avg_gap_to_winner",
        "driver_speed",
        "driver_vs_team_speed",
    ]

    consistency_cols = [
        "finish_std",
        "points_std",
        "pos_change_std",
        "avg_pos_change",
    ]

    dnf_cols = [
        "dnf_count",
        "dnf_rate",
        "clean_race_rate",
    ]

    team_cols = [
        "team_total_points",
        "team_avg_points",
        "team_avg_pos_season",
        "team_speed",
        "driver_vs_team_avg_finish",
        "driver_vs_team_avg_points",
    ]

    ordered_cols = id_cols + perf_cols + pace_cols + consistency_cols + dnf_cols + team_cols
    # Falls noch weitere Spalten existieren, hinten anhängen
    others = [c for c in season.columns if c not in ordered_cols]
    season = season[ordered_cols + others]

    return season


def main():
    out_path = PROCESSED_DIR / "f1_features.csv"
    df = build_f1_season_features()
    df.to_csv(out_path, index=False)
    print(
        f"F1-Season-Features gespeichert unter: {out_path} "
        f"mit {len(df)} Zeilen und {len(df.columns)} Spalten."
    )


if __name__ == "__main__":
    main()
