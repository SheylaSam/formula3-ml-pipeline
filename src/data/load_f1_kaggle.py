from pathlib import Path
import pandas as pd

# Pfad zu deinen Kaggle CSVs: <projektroot>/data/f1/raw
DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "f1" / "raw"


def _load_csv(filename: str, **read_csv_kwargs) -> pd.DataFrame:
    """
    Hilfsfunktion zum Laden einer einzelnen CSV aus data/f1/raw.
    """
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Datei nicht gefunden: {path}")
    return pd.read_csv(path, **read_csv_kwargs)


def load_races() -> pd.DataFrame:
    """Lädt races.csv"""
    return _load_csv("races.csv")


def load_results() -> pd.DataFrame:
    """Lädt results.csv"""
    return _load_csv("results.csv")


def load_drivers() -> pd.DataFrame:
    """Lädt drivers.csv"""
    return _load_csv("drivers.csv")


def load_constructors() -> pd.DataFrame:
    """Lädt constructors.csv"""
    return _load_csv("constructors.csv")


def load_circuits() -> pd.DataFrame:
    """Lädt circuits.csv"""
    return _load_csv("circuits.csv")


def load_lap_times() -> pd.DataFrame:
    """Lädt lap_times.csv (falls vorhanden)"""
    return _load_csv("lap_times.csv")


def load_pit_stops() -> pd.DataFrame:
    """Lädt pit_stops.csv (falls vorhanden)"""
    return _load_csv("pit_stops.csv")


def load_status() -> pd.DataFrame:
    """Lädt status.csv (falls vorhanden)"""
    return _load_csv("status.csv")


def load_seasons() -> pd.DataFrame:
    """Lädt seasons.csv (falls vorhanden)"""
    return _load_csv("seasons.csv")


def load_qualifying() -> pd.DataFrame:
    """Lädt qualifying.csv (falls vorhanden)"""
    return _load_csv("qualifying.csv")


def load_sprint_results() -> pd.DataFrame:
    """Lädt sprint_results.csv (falls vorhanden)"""
    return _load_csv("sprint_results.csv")


def load_core_tables() -> dict:
    """
    Lädt die wichtigsten Kern-Tabellen und gibt sie als Dict zurück.
    Praktisch für Notebooks / erste EDA.
    """
    return {
        "races": load_races(),
        "results": load_results(),
        "drivers": load_drivers(),
        "constructors": load_constructors(),
        "circuits": load_circuits(),
    }
