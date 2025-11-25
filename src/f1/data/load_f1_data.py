import fastf1
import pandas as pd


def load_race_session(year: int, round_number: int, session_type: str = "R") -> pd.DataFrame:
    """
    Lädt eine bestimmte Formel-1-Session (Race, Qualifying, FP1 usw.)
    und gibt einen DataFrame mit allen Runden zurück.

    Parameter:
    year: Jahr des Rennens, z. B. 2023
    round_number: Lauf im Rennkalender, z. B. 1 = Bahrain
    session_type: "R" (Race), "Q" (Qualifying), "FP1", "FP2", "FP3", "SPR" usw.
    """

    # Cache aktivieren (damit FastF1 die Daten lokal speichert)
    fastf1.Cache.enable_cache("data/raw")

    # Session laden
    session = fastf1.get_session(year, round_number, session_type)
    session.load()  # lädt alle Telemetrie- und Timingdaten

    # DataFrame mit allen gefahrenen Runden
    laps_df = session.laps

    # Datei speichern
    file_path = f"data/raw/f1_{year}_round{round_number}_{session_type}.csv"
    laps_df.to_csv(file_path, index=False)

    return laps_df
