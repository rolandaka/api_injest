# Open-Meteo Weather Data Pipeline

A modular, production-grade Python ETL (Extract, Transform, Load) pipeline that extracts 3-day weather forecasts from the **Open-Meteo API**, normalizes nested response matrices, and outputs clean, structured time-series data.

## 🚀 Features
- **Resilient Network Requests:** Equipped with an exponential backoff retry mechanism to safely navigate API limits and connection timeouts.
- **Structured Logging:** Integrated Python's standard `logging` module to track start times, raw row counts, errors, and metadata statuses out to the console.
- **Type Safety & Design:** Uses explicit Python Type Hints and clear functional encapsulation (`fetch_data`, `clean_data`, `save_data`) for easy updates.

## 🛠️ Installation & Setup

1. **Clone this repository down to your machine:**
   ```bash
   git clone https://github.com
   cd your-repository-name
   ```

2. **Initialize and activate an isolated Python Virtual Environment:**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # macOS / Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install the project dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## 🏃 Running the Pipeline

Execute the main pipeline process from your terminal:
```bash
python weather_pipeline.py
```

### Expected Logging Output:
```text
2026-10-25 14:55:01 [INFO] === Pipeline Execution Started ===
2026-10-25 14:55:01 [INFO] API request attempt 1 of 3...
2026-10-25 14:55:02 [INFO] API request successful.
2026-10-25 14:55:02 [INFO] Starting data cleaning and transformation...
2026-10-25 14:55:02 [INFO] Successfully processed and cleaned 3 rows of data.
2026-10-25 14:55:02 [INFO] Saving extracted dataset down to local storage: daily_weather_data.csv
2026-10-25 14:55:02 [INFO] Data export completed successfully.
2026-10-25 14:55:02 [INFO] === Pipeline Finished Execution (Success) ===
```

## 📊 Output Data Structure

The code writes results out locally into a clear, tabular spreadsheet named `daily_weather_data.csv` with a pipeline run-tracking audit column:

| date | max_temperature | min_temperature | weather_code | sunrise | sunset | loaded_at |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 2026-10-25 | 32.5 | 24.1 | 3 | 05:48 | 17:39 | 2026-10-25 14:55:02 |
| 2026-10-26 | 31.8 | 23.9 | 51 | 05:48 | 17:38 | 2026-10-25 14:55:02 |
| 2026-10-27 | 33.0 | 24.5 | 0 | 05:49 | 17:38 | 2026-10-25 14:55:02 |
