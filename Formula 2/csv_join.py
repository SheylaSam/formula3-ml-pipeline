import pandas as pd

# === 1. CSV-Dateien laden ===
drivers = pd.read_csv("/mnt/data/f2_drivers_to_f1.csv")
feature = pd.read_csv("/mnt/data/Feature-Race.csv")
feature["Session"] = "Feature"

sprint1 = pd.read_csv("/mnt/data/Sprint-Race.csv")
sprint1["Session"] = "Sprint1"

sprint2 = pd.read_csv("/mnt/data/Sprint-Race-2.csv")
sprint2["Session"] = "Sprint2"

qualifying = pd.read_csv("/mnt/data/Qualifying-Session.csv")
qualifying["Session"] = "Qualifying"

practice = pd.read_csv("/mnt/data/Free-Practice.csv")
practice["Session"] = "Practice"

race_results = pd.read_csv("/mnt/data/Formula2_Race_Results.csv")
race_results["Session"] = "RaceResult"


# === 2. Alle Sessions zusammenfügen ===
sessions = pd.concat(
    [practice, qualifying, feature, sprint1, sprint2],
    ignore_index=True
)

# === 3. Key-Spalten vereinheitlichen ===
# Wenn deine Dateien unterschiedlich heißen (z. B. Driver vs. driver), bitte anpassen
sessions.rename(columns=lambda c: c.strip().lower(), inplace=True)
race_results.rename(columns=lambda c: c.strip().lower(), inplace=True)
drivers.rename(columns=lambda c: c.strip().lower(), inplace=True)

# Häufige Standard-Key-Spalten:
possible_keys = ["driver", "driver_name", "name"]

key = None
for k in possible_keys:
    if k in sessions.columns:
        key = k
        break

if key is None:
    raise ValueError("Keine gemeinsame Fahrer-Spalte gefunden. Bitte überprüfen!")

print(f"→ Join-Key ist: {key}")


# === 4. Merge: Sessions + Race Results ===
df = sessions.merge(race_results, on=[key, "race_id"], how="left")

# === 5. Fahrer-Metadaten (Wechsel zu F1 etc.) hinzufügen ===
df = df.merge(drivers, on=key, how="left")


# === 6. Ergebnis speichern ===
df.to_csv("f2_merged_dataset.csv", index=False)

print("✔️ Fertig! Datei gespeichert als f2_merged_dataset.csv")
print(df.head())
print(df.shape)
