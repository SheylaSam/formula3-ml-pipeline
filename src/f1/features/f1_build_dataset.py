from pathlib import Path
import pandas as pd

# Importiere die Loader aus src/data/
from src.data.load_f1_kaggle import (
    load_races,
    load_results,
    load_drivers,
    load_constructors,
)

# Ausgabepfad relativ zum Projektroot:
PROCESSED_DIR = Path(__file__).resolve().parents[3] / "data" / "f1" / "processed"
# Erklärung:
# parents[3] = geht von src/f1/features/f1_build_dataset.py drei Ordner rauf:
# → features
# → f1
# → src
# → EINEN HÖHER → projektroot


def build_f1_base_dataset() -> pd.DataFrame:
    races = load_races()
    results = load_results()
    drivers = load_drivers()
    constructors = load_constructors()

    races_small = races[["raceId", "year", "round", "circuitId", "name", "date"]].rename(
        columns={"name": "race_name"}
    )

    drivers_small = drivers[
        ["driverId", "code", "forename", "surname", "nationality"]
    ].copy()
    drivers_small["driver_name"] = drivers_small["forename"] + " " + drivers_small["surname"]

    constructors_small = constructors[
        ["constructorId", "name", "nationality"]
    ].rename(
        columns={"name": "constructor_name", "nationality": "constructor_nationality"}
    )

    df = results.merge(races_small, on="raceId", how="left")
    df = df.merge(drivers_small, on="driverId", how="left")
    df = df.merge(constructors_small, on="constructorId", how="left")

    df["finished_in_points"] = df["points"] > 0
    df["driver_full"] = df["forename"] + " " + df["surname"]

    return df


def save_f1_base_dataset(csv_name: str = "f1_base_dataset.csv") -> Path:
    df = build_f1_base_dataset()
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PROCESSED_DIR / csv_name
    df.to_csv(out_path, index=False)
    print(f"Gespeichert unter: {out_path} mit {len(df)} Zeilen und {len(df.columns)} Spalten.")
    return out_path


if __name__ == "__main__":
    save_f1_base_dataset()
