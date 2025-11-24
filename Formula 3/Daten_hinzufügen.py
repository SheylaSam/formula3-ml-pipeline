import pandas as pd

# Zeige alle Blattnamen der Datei
xlsx = pd.ExcelFile("/Users/sheyla/Desktop/F3_Python/Kopie von F3 Dataset manuell.xlsx")
print(xlsx.sheet_names)

# 1. Excel Datei einlesen
df_ids = pd.read_excel("/Users/sheyla/Desktop/F3_Python/Kopie von F3 Dataset manuell.xlsx")  # Pfad zur Datei

print(df_ids.head())
print(df_ids.columns)

# Gruppe nach Saison bilden
for season, group in df_ids.groupby("season"):
    print(season, group["race_id"].tolist()[:5])

import requests
from bs4 import BeautifulSoup

# Kleine Testfunktion: nur eine einzige Race ID laden
def test_single_race(race_id):
    url = f"https://www.fiaformula3.com/Results?raceid={race_id}"
    print("Testlade:", url)

    resp = requests.get(url)
    print("Statuscode:", resp.status_code)

    # Tabellen testen
    tables = pd.read_html(resp.text)
    print("Gefundene Tabellen:", len(tables))

    # Erste Tabelle ausgeben (nur Kopfzeilen)
    if len(tables) > 0:
        print(tables[0].head())
    else:
        print("Keine Tabelle gefunden.")


# **Testlauf mit der ersten Race ID aus 2019**
first_test_id = df_ids[df_ids["season"] == 2019]["race_id"].iloc[0]
test_single_race(first_test_id)


# Test: zwei Rennen laden (2019, erste zwei Race IDs)
test_ids = df_ids[df_ids["season"] == 2019]["race_id"].tolist()[:2]

print("Starte Mini-Test mit Race IDs:", test_ids)

mini_results = []

for rid in test_ids:
    url = f"https://www.fiaformula3.com/Results?raceid={rid}"
    print("Lade:", url)

    html = requests.get(url).text
    tables = pd.read_html(html)

    for t in tables:
        t["race_id"] = rid
        mini_results.append(t)

mini_df = pd.concat(mini_results, ignore_index=True)
print(mini_df.head())
print("Mini-Test Anzahl Zeilen:", len(mini_df))


def load_f3_results(race_ids, season):
    all_data = []
    base = "https://www.fiaformula3.com/Results?raceid="

    for rid in race_ids:
        url = base + str(rid)
        print(f"Lade Rennen: {url}")

        response = requests.get(url)
        html = response.text

        # Session Titel (z. B. "Feature Race", "Sprint Race")
        soup = BeautifulSoup(html, "html.parser")
        session_headers = [h.get_text(strip=True) for h in soup.select("h3")]

        # Alle Tabellen lesen
        tables = pd.read_html(html)

        # Tabellen + Session-Verknüpfung
        for i, table in enumerate(tables):
            if i < len(session_headers):
                session = session_headers[i]
            else:
                session = f"Session_{i}"

            # Spalten vereinheitlichen
            table.columns = [str(c).strip().lower().replace(" ", "_") for c in table.columns]

            # Fahrer-Info normieren
            driver_cols = [c for c in table.columns if "driver" in c]
            if driver_cols:
                table.rename(columns={driver_cols[0]: "driver_info"}, inplace=True)
            else:
                table["driver_info"] = None

            # Meta-Daten
            table["race_id"] = rid
            table["season"] = season
            table["session_type"] = session

            all_data.append(table)

    return pd.concat(all_data, ignore_index=True)


print("Starte Gesamtdownload 2019 bis 2025...")

all_results = []

for season, group in df_ids.groupby("season"):
    race_ids = group["race_id"].astype(int).tolist()
    print(f"\n=== Saison {season} | {len(race_ids)} Rennen ===")
    
    season_df = load_f3_results(race_ids, season)
    all_results.append(season_df)

full_df = pd.concat(all_results, ignore_index=True)

full_df.to_csv("f3_2019_2025_raw_results.csv", index=False)

print("\nDownload abgeschlossen!")
print("Gesamtzeilen:", len(full_df))
print("Gespeichert als: f3_2019_2025_raw_results.csv")
