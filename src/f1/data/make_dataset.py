import pandas as pd
from pathlib import Path


def create_clean_lap_dataset(
    input_path: str,
    output_path: str,
    year: int | None = None,
    round_number: int | None = None,
    session_type: str | None = None,
) -> pd.DataFrame:
    """
    Nimmt eine rohe FastF1-CSV (z. B. data/raw/f1_2023_round1_R.csv),
    bereinigt sie und speichert ein sauberes Dataset unter output_path.

    Rückgabe: der bereinigte DataFrame.
    """

    # 1) CSV einlesen
    input_path = Path(input_path)
    df = pd.read_csv(input_path)

    # Hier kommen im nächsten Schritt die Cleaning-Schritte rein
    # (ungültige Runden löschen, Zeiten umrechnen, Spalten auswählen usw.)

    # -----------------------------
    # CLEANING-SCHRITTE
    # -----------------------------

    # 1) Ungültige Runden entfernen
    # Deleted == True → Runde gestrichen (Track Limits)
    # IsAccurate == False → stimmt nicht genau
    if "Deleted" in df.columns:
        df = df[df["Deleted"] != True]
    if "IsAccurate" in df.columns:
        df = df[df["IsAccurate"] == True]

    # 2) In- und Outlaps entfernen (optional)
    # FastF1 markiert PitInTime / PitOutTime mit Zeitstempeln
    if "PitInTime" in df.columns:
        df = df[df["PitInTime"].isna()]
    if "PitOutTime" in df.columns:
        df = df[df["PitOutTime"].isna()]

    # 3) LapTime in Sekunden umwandeln
    def to_seconds(val):
        try:
            return pd.to_timedelta(val).total_seconds()
        except:
            return None

    if "LapTime" in df.columns:
        df["LapTime_s"] = df["LapTime"].apply(to_seconds)

    # 4) Sektorzeiten in Sekunden umwandeln
    for col in ["Sector1Time", "Sector2Time", "Sector3Time"]:
        if col in df.columns:
            df[col + "_s"] = df[col].apply(to_seconds)

    # 5) Nur relevante Spalten behalten
    keep_cols = [
        "Driver", "DriverNumber", "Team",
        "LapNumber", "Stint", "Compound", "TyreLife",
        "Position", "TrackStatus",
        "LapTime_s", "Sector1Time_s", "Sector2Time_s", "Sector3Time_s",
    ]

    df = df[[c for c in keep_cols if c in df.columns]]


    # 2) Metadaten optional ergänzen
    if year is not None:
        df["year"] = year
    if round_number is not None:
        df["round"] = round_number
    if session_type is not None:
        df["session_type"] = session_type

    # 3) Ergebnis speichern
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    return df
