# 🏎️ Formel 3 Machine Learning Pipeline  
## Multi-Season Data Analysis (2019–2025)

Dieses Projekt automatisiert das Sammeln, Bereinigen und Analysieren von FIA Formel 3 Renndaten. Die Pipeline lädt Rennresultate über mehrere Jahre, bereitet sie konsistent auf und erstellt daraus einen ML-ready Datensatz. Alle Analysen und Diagramme in diesem Projekt wurden vollständig mit Python erstellt.

[🇬🇧 English Version](README_EN.md)

---

# 📂 Projektübersicht

- Datenscraping  
- Datenbereinigung  
- Feature Engineering  
- Explorative Analyse  
- Machine Learning (in Vorbereitung)  

---

# 📥 Datenquellen

Die Daten stammen von der offiziellen FIA Formel 3 Website. Jede Rennveranstaltung ist über eine race_id abrufbar:

https://www.fiaformula3.com/Results?raceid=1002

Wir haben die Renn-IDs für die Saisons 2019 bis 2025 gesammelt und automatisch verarbeitet.

---

# 🧹 Datenbereinigung

### Schritte:
- Extraktion aller HTML-Tabellen über pandas  
- Spaltung der Fahrerinformationen in: Name, Fahrernummer, Team, Status  
- Entfernen irrelevanter Sessions (Trainings, Standings, Infos)  
- Behalten nur echter Rennen: ROUND1Summary, ROUND2Summary, ROUND3Summary  
- Konvertieren aller Zeitangaben in Sekunden  
- Bereinigung von DNF, DNS, DSQ  
- Erstellung eines sauberen Race-Only Datensatzes  

Resultatdateien:

- `f3_2019_2025_raw_results.csv`  
- `f3_2019_2025_races_only_final.csv`

---

# 🧠 Feature Engineering

Wir haben zahlreiche Features erzeugt, die später für Machine Learning genutzt werden.

### Zeit- und Performance-Features
- time_s (Gesamtzeit in Sekunden)  
- best_lap_s (beste Runde des Fahrers)  
- avg_lap_time_s (Durchschnittliche Rundenzeit)  
- winner_time_s (Schnellste Zeit im Rennen)  
- time_from_winner_s  

### Runden-Features
- laps_clean (numerisch bereinigte Rundenzahl)  
- race_max_laps  
- rel_laps (gefahrene Runden relativ zur Gesamtrundenzahl)

### Team- und Fahrerfeatures
- team_speed (Durchschnittliche Pace pro Team)  
- driver_speed (Durchschnittliche Pace pro Fahrer)  
- driver_top10_rate (Quote der Top 10 Platzierungen)  
- driver_vs_team (relative Pace im Vergleich zum Team)  
- lap_vs_race_avg (Pace im Vergleich zum Rennschnitt)

### Status-Flags
- finished  
- is_dnf  
- is_dns  
- is_dsq  

### Session-Kodierung
- ROUND1Summary → 1  
- ROUND2Summary → 2  
- ROUND3Summary → 3  

Finale Datei:

`f3_2019_2025_races_features.csv`

---

# 📊 Explorative Analyse (EDA)

Nach dem Aufbau des ML-Datensatzes wurden erste Visualisierungen erstellt.

---

## 1. Verteilung der Rennpositionen
![Positionsverteilung](plot_positions_distribution.png)

**Interpretation:**  
Die Positionen sind relativ gleichmässig verteilt. Es gibt keine strukturelle Verzerrung und die Daten sind historisch balanciert. Alle Plätze von 1 bis 30 treten regelmässig auf.

---

## 2. Team Performance – Durchschnittliche Rennposition
![Team Performance](plot_team_performance.png)

**Interpretation:**  
TRIDENT, PREMA und ART Grand Prix sind über alle Jahre hinweg klar die stärksten Teams.  
Teams wie PHM Racing oder Charouz liegen konstant am Ende des Feldes.

---

## 3. Schnellste Fahrer – Durchschnittliche Rundenzeit
![Schnellste Fahrer](plot_best_drivers.png)

**Interpretation:**  
Die Top-20 Fahrer haben im Schnitt extrem ähnliche Rundentzeiten.  
Mehrere Fahrer aus kleineren Teams tauchen erstaunlich weit oben auf – das zeigt, dass Talent nicht immer ans Team gekoppelt ist.

---

## 4. Top-Fahrer nach durchschnittlicher Position
![Driver Avg Position](plot_driver_avg_position.png)

**Interpretation:**  
Dieser Plot zeigt, wer im Rennen am konstant besten abschneidet.  
Nur Fahrer mit mind. 5 Starts werden berücksichtigt, um Verzerrungen zu vermeiden.

---

## 5. Team-DNF-Rate
![Team DNF Rate](plot_team_dnf_rate.png)

**Interpretation:**  
Einige Teams (z. B. Charouz, PHM) fallen durch hohe Ausfallraten auf.  
Teams mit niedrigen DNF-Werten profitieren klar in der Gesamtwertung.

---

## 6. Fahrer-Konstanz (Varianz der Rennpositionen)
![Driver Consistency](plot_driver_consistency.png)

**Interpretation:**  
Fahrer mit niedriger Varianz sind besonders konstant.  
Eine tiefe Varianz bedeutet: der Fahrer liefert nahezu immer dieselbe Leistung ab – unabhängig vom Rennen.

---

## 7. Fahrerentwicklung über die Zeit
![Driver Development](plot_driver_development.png)

**Interpretation:**  
Der Plot zeigt das Leistungsniveau eines ausgewählten Fahrers pro Jahr.  
Trends wie Verbesserung, Stagnation oder Einbrüche werden sichtbar.

---

## 8. Team-Performance über die Jahre
![Team Performance Over Time](plot_team_performance_over_time.png)

**Interpretation:**  
Dieser Plot zeigt Trends in der Teamleistung.  
Man erkennt, welche Teams über Jahre dominieren und welche sich verbessern oder verschlechtern.

---

## 9. Team-Positions-Boxplot
![Team Position Boxplot](plot_team_position_boxplot.png)

**Interpretation:**  
Boxplots zeigen die Verteilung der Rennpositionen pro Team.  
Man sieht sofort, welche Teams stabil vorne sind und welche stark schwanken.

---

## 10. Fahrer vs Team – Beste Leistung
![Driver vs Team Best](plot_driver_vs_team_best.png)

**Interpretation:**  
Hier sieht man die Fahrer, die ihr Team regelmässig “überperformen”.  
Ein Fahrer mit viel besserer Pace als das Team kann ein zukünftiges F2/F1-Talent sein.

---

## 11. Fahrer vs Team – Schlechteste Leistung
![Driver vs Team Worst](plot_driver_vs_team_worst.png)

**Interpretation:**  
Zeigt Fahrer, die im Vergleich zur Team-Pace deutlich langsamer sind.  
Kann auf Anfängerfehler, Setup-Schwierigkeiten oder fehlende Konstanz hinweisen.

---

## 12. Heatmap – Aktuellste Saison (Startplatz vs Endplatz)
![Heatmap zuletzt Saison](plot_heatmap_positions_latest_season.png)

**Interpretation:**  
Visualisiert die Korrelation zwischen Start- und Endposition.  
Typisches Muster: Je weiter vorne der Start, desto besser die Zielposition – aber mit Überraschungen.

---

# 🧠 Machine Learning (nächster Schritt)

Geplant sind:

- Klassifikation: Top-10 Vorhersage  
- Regression: Positionsvorhersage  
- Survival / Hazard Modelle: Wahrscheinlichkeit eines DNFs  
- Team Ranking Modelle  
- Feature Importance Analyse über XGBoost / Random Forest / SHAP  

---

# 📎 Reproduzierbarkeit

Alle Schritte wurden vollständig mit Python realisiert:

- pandas  
- numpy  
- requests  
- BeautifulSoup (optional)  
- matplotlib / seaborn  
- scikit-learn (für ML geplant)

Die Python-Skripte:

Daten_hinzufügen.py
driver_cleaning.py
times_cleaning.py
race_only_bereinigung.py
feature_engineering.py
explorative_analyse.py


---

# 👤 Projektteam

Dieses Projekt ist Teil unserer Formel-Datenanalyse (F1/F2/F3/F4).  
Die Formel 3 dient als erstes vollständiges Beispiel, an dem wir die Pipeline entwickeln.

---

# ✔️ Status

- Datensammlung: abgeschlossen  
- Bereinigung: abgeschlossen  
- Feature Engineering: abgeschlossen  
- Explorative Analyse: abgeschlossen  
- ML-Modelle: in Planung  

---

# 📌 Lizenz

Nur für Studien- und Analysezwecke. Keine kommerzielle Nutzung der Originaldaten.
