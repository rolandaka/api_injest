# Open-Meteo Weather Data Pipeline

A modular, production-grade Python ETL (Extract, Transform, Load) pipeline that extracts 3-day weather forecasts from the **Open-Meteo API**, normalizes nested response matrices, and outputs clean, structured time-series data.

## 🚀 Features
- **Resilient Network Requests:** Equipped with an exponential backoff retry mechanism to safely navigate API limits and connection timeouts.
- **Structured Logging:** Integrated Python's standard `logging` module to track start times, raw row counts, errors, and metadata statuses out to the console.
- **Type Safety & Design:** Uses explicit Python Type Hints and clear functional encapsulation (`fetch_data`, `clean_data`, `save_data`, `load_data`) for easy updates.
- **PostgreSQL Database Integration:** Idempotently loads cleaned weather data into a PostgreSQL database using a staging table and upsert pattern, enabling safe re-runs without duplicate entries.

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

4. **Configure database credentials (optional):**
   Create a `.env` file in the project root with your PostgreSQL connection details:
   ```env
   DB_USER=your_username
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=your_database
   ```
   The `.env` file is gitignored for security. If database variables are not set, the pipeline will skip the database load step and still export to CSV.

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
2026-10-25 14:55:02 [INFO] Staging 3 rows into temporary table 'temp_staged_weather'...
2026-10-25 14:55:02 [INFO] Upserted data into '3_day_weather_forecast' successfully.
2026-10-25 14:55:02 [INFO] Dropped temporary table 'temp_staged_weather'.
2026-10-25 14:55:02 [INFO] === Pipeline Finished Execution (Success) ===
```

If database environment variables are not configured, you will see a warning instead:
```text
2026-10-25 14:55:02 [WARNING] Database environment variables not set. Skipping database load. Set DB_USER, DB_PASSWORD, DB_HOST, and DB_NAME in your .env file.
```

## 📊 Output Data Structure

The code writes results out locally into a clear, tabular spreadsheet named `daily_weather_data.csv` with a pipeline run-tracking audit column:

| date | max_temperature | min_temperature | weather_code | sunrise | sunset | loaded_at |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 2026-10-25 | 32.5 | 24.1 | 3 | 05:48 | 17:39 | 2026-10-25 14:55:02 |
| 2026-10-26 | 31.8 | 23.9 | 51 | 05:48 | 17:38 | 2026-10-25 14:55:02 |
| 2026-10-27 | 33.0 | 24.5 | 0 | 05:49 | 17:38 | 2026-10-25 14:55:02 |


## 🗄️ Database Schema

When database credentials are configured, the pipeline loads data into a PostgreSQL table named `3_day_weather_forecast`:

| Column | Type | Description |
| :--- | :--- | :--- |
| `date` | DATE | Forecast date (unique constraint) |
| `max_temperature` | FLOAT | Maximum temperature in °C |
| `min_temperature` | FLOAT | Minimum temperature in °C |
| `weather_code` | INTEGER | WMO weather code |
| `sunrise` | TEXT | Sunrise time (HH:MM) |
| `sunset` | TEXT | Sunset time (HH:MM) |
| `loaded_at` | TEXT | Pipeline execution timestamp |

### Upsert Logic
The pipeline uses a **staging table** approach to ensure idempotent loads:
1. Data is first written to a temporary table `temp_staged_weather`.
2. An `INSERT ... ON CONFLICT (date) DO UPDATE` statement merges the staged data into the production table, updating existing rows for the same date rather than creating duplicates.
3. The temporary table is dropped after the upsert completes.

This pattern allows safe re-runs of the pipeline without duplicating or corrupting data.
