import pandas as pd
import re

# 1. Rohdaten einlesen
df = pd.read_csv("f3_2019_2025_raw_results.csv")

print(df.columns)
print(df["driver_info"].head())

def parse_driver_info(cell):
    """
    Zerlegt driver_info in:
    status (DNF, DNS usw), car_number, driver_name, driver_code, team_name
    """
    if pd.isna(cell):
        return pd.Series(
            [None, None, None, None, None],
            index=["status", "car_number", "driver_name", "driver_code", "team_name"]
        )

    text = str(cell).strip().replace("\xa0", " ")

    # 1) Optionaler Status am Anfang (z. B. DNF, DNS, DSQ), dann Nummer
    m = re.match(r"^(?P<status>[A-Z]+)?(?P<number>\d+)\s*(?P<rest>.*)$", text)
    if not m:
        # Nichts Passendes gefunden
        return pd.Series(
            [None, None, None, None, None],
            index=["status", "car_number", "driver_name", "driver_code", "team_name"]
        )

    status = m.group("status")
    car_number = m.group("number")
    rest = m.group("rest").strip()

    # 2) Ersten Dreierblock Grossbuchstaben als Driver Code finden
    m2 = re.search(r"([A-Z]{3})", rest)
    if not m2:
        # Kein Code gefunden, lieber Name in rest lassen
        return pd.Series(
            [status, car_number, rest, None, None],
            index=["status", "car_number", "driver_name", "driver_code", "team_name"]
        )

    driver_code = m2.group(1)
    name_part = rest[:m2.start()].strip()
    team_part = rest[m2.end():].strip()

    # Punkt nach Initialen im Namen entfernen, evtl. doppelte Leerzeichen
    name_part = name_part.replace(".", " ").strip()

    return pd.Series(
        [status, car_number, name_part, driver_code, team_part],
        index=["status", "car_number", "driver_name", "driver_code", "team_name"]
    )

parsed = df["driver_info"].apply(parse_driver_info)

# neue Spalten anhängen
df = pd.concat([df.drop(columns=["car_number", "driver_name", "driver_code", "team_name"], errors="ignore"),
                parsed],
               axis=1)

# Stichprobe
print(df[["driver_info", "status", "car_number", "driver_name", "driver_code", "team_name"]].head(20))

problem_rows = df[df["driver_code"].isna() | df["car_number"].isna()]
print("Problemzeilen:", len(problem_rows))
print(problem_rows["driver_info"].head(30))

df.to_csv("f3_2019_2025_with_drivers_and_status.csv", index=False)
