# 🏎️ Formel 3 – Datenpipeline, Feature Engineering & Machine Learning  
### Multi-Season Data Analysis (2019–2025)

Dieses Projekt automatisiert das Sammeln, Bereinigen und Analysieren von FIA Formel 3 Renndaten.  
Die Pipeline lädt Rennresultate über mehrere Jahre, bereitet sie konsistent auf und erstellt daraus einen ML-ready Datensatz, der für Rennanalysen, Fahrerbewertungen und Machine-Learning-Modelle genutzt werden kann.

---

## 📦 Projektinhalt

Das Repository umfasst:

- **Datenscraping** (HTML Tabellen von der offiziellen FIA-Website)
- **Data Cleaning & Normalisierung**
- **Feature Engineering**
- **Explorative Datenanalyse (EDA)**
- **Vorbereitung für Machine Learning**
- **Plots & Grafiken zur Performance-Analyse**

---

## 🗂️ Verwendete Dateien

### 1. `f3_2019_2025_raw_results.csv`
Alle Rohdaten aus FIA Tabellen, inkl. Sessions wie:
- Standings  
- Summary  
- Race Tables  
- Trainingssessions  

### 2. `f3_2019_2025_races_only_final.csv`
Nur echte Rennen:
- ROUND1Summary  
- ROUND2Summary  
- ROUND3Summary  

### 3. `f3_2019_2025_races_features.csv`
Bereinigter, vollständig featurisierter Datensatz:
- Zeitfeatures (time_s, best_lap_s, avg_lap_time_s)
- Rundenfeatures (laps_clean, rel_laps, race_max_laps)
- Performancefeatures (time_from_winner_s, best_lap_from_best_s)
- Statusfeatures (finished, is_dnf usw.)
- Team- und Fahrerstatistiken
- Session Round Encoding

---

## ⚙️ Python Skripte

### `data_collection.py`
Automatisches Laden aller Rennseiten basierend auf einer Liste von race_ids.  
Extrahiert alle FIA Tabellen als DataFrame und speichert den Rohdatensatz.

### `data_cleaning.py`
- Zerlegt Fahrerinformationen  
- Filtert nur echte Rennsessions  
- Konvertiert Zeiten in Sekunden  
- Bereinigt Rennstatus  
- Erstellt Race-Only Datensatz  

### `feature_engineering.py`
Berechnet zusätzliche ML-Features:
- Siegerzeit  
- Relative Pace  
- Team Speed Index  
- Driver Speed Index  
- Top-10-Rate pro Fahrer  
- Sessionkodierung  
- Positionen pro Rennen  

### `explorative_analysen.py`
Generiert erste Visualisierungen:
- Positionsverteilung  
- Team Performance Ranking  
- Schnellste Fahrer nach durchschnittlicher Rundenzeit  

---

## 📊 Beispielplots

### Verteilung der Rennpositionen
Zeigt die typische Formel-3-Verteilung basierend auf mehreren Saisons.

### Team Performance
Durchschnittliche Positionen der Teams über mehrere Jahre.

### Fahrer Pace
Basierend auf der durchschnittlichen Rundenzeit.

---

## 🧠 Machine Learning (geplant)

Nächste Schritte:
- Klassifikation: Top-10 Prediction  
- Regression: Positionsvorhersage  
- Fahrer Pace Prediction  
- DNF Prediction  
- Feature Importance Analysen  

---

## 🔧 Installation

### Voraussetzungen:
- Python 3.10  
- pandas  
- numpy  
- matplotlib  

### Installation

```bash
pip install -r requirements.txt
