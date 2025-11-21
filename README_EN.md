# 🏎️ Formula 3 Machine Learning Pipeline  
## Multi-Season Data Analysis (2019–2025)

This project automates the collection, cleaning and analysis of FIA Formula 3 race data.  
The pipeline downloads race results across multiple seasons, standardizes them and produces an ML-ready dataset.  
All analyses, visualizations and transformations were carried out entirely in Python.

[🇩🇪 Zur deutschen Version](README.md)

---

# 📂 Project Overview

- Data scraping  
- Data cleaning  
- Feature engineering  
- Exploratory analysis  
- Machine learning (in preparation)  

---

# 📥 Data Sources

All data is collected from the official FIA Formula 3 website.  
Each race is accessible via a `race_id`, for example:

https://www.fiaformula3.com/Results?raceid=1002

We collected all race IDs for the seasons 2019 to 2025 and processed them automatically.

---

# 🧹 Data Cleaning

### Steps:

- Extraction of all HTML tables via pandas  
- Parsing of the driver information into: name, car number, team, status  
- Removal of irrelevant sessions (practice, standings, info tables)  
- Keeping only true race sessions:  
  **ROUND1Summary, ROUND2Summary, ROUND3Summary**  
- Conversion of all time fields into seconds  
- Cleaning of DNF, DNS and DSQ statuses  
- Creation of a clean race-only dataset  

Resulting files:

- `f3_2019_2025_raw_results.csv`  
- `f3_2019_2025_races_only_final.csv`

---

# 🧠 Feature Engineering

We generated a broad set of features for later machine learning tasks.

### Time & Performance Features
- `time_s` (total race time in seconds)  
- `best_lap_s` (best lap of the driver)  
- `avg_lap_time_s` (average lap time)  
- `winner_time_s` (fastest race time)  
- `time_from_winner_s`  

### Lap-Based Features
- `laps_clean` (numeric lap count)  
- `race_max_laps`  
- `rel_laps` (relative number of laps completed)

### Team & Driver Features
- `team_speed` (average pace per team — derived for ML prep)  
- `driver_speed`  
- `driver_top10_rate`  
- `driver_vs_team` (driver pace relative to team average)  
- `lap_vs_race_avg` (lap time vs. race average)

### Status Flags
- `finished`  
- `is_dnf`  
- `is_dns`  
- `is_dsq`  

### Session Encoding
- `ROUND1Summary` → 1  
- `ROUND2Summary` → 2  
- `ROUND3Summary` → 3  

Final file:

`f3_2019_2025_races_features.csv`

---

# 📊 Exploratory Data Analysis (EDA)

After constructing the ML dataset, several visualizations were produced.

---

## 1. Distribution of Race Positions
![Position Distribution](plot_positions_distribution.png)

---

## 2. Team Performance
![Team Performance](plot_team_performance.png)

---

## 3. Fastest Drivers (Average Lap Time)
![Fastest Drivers](plot_best_drivers.png)

---

# 🧠 Machine Learning (Next Step)

Planned models:

- Classification: Top-10 prediction  
- Regression: race position prediction  
- Survival / hazard models: probability of DNF  
- Team ranking models  
- Feature importance (XGBoost, Random Forest, SHAP)  

---

# 📎 Reproducibility

All steps were performed entirely in Python using:

- pandas  
- numpy  
- requests  
- BeautifulSoup (optional)  
- matplotlib / seaborn  
- scikit-learn (planned)  

Python scripts in this project:

- `Daten_hinzufügen.py`  
- `driver_cleaning.py`  
- `times_cleaning.py`  
- `race_only_bereinigung.py`  
- `feature_engineering.py`  
- `explorative_analyse.py`

---

# 👤 Project Team

This project is part of our Formula Data Analysis (F1/F2/F3/F4).  
Formula 3 serves as the first fully completed example used to build and validate the entire pipeline.

---

# ✔️ Status

- Data collection: completed  
- Data cleaning: completed  
- Feature engineering: completed  
- Exploratory analysis: completed  
- ML models: in planning  

---

# 📌 License

For study and analysis purposes only.  
No commercial use of the original data is permitted.
