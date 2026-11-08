import logging
import time
import pandas as pd
import requests
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os



# ==========================================
# CONFIGURATION / CONSTANTS
# ==========================================
# Open-Meteo API setup for latitude/longitude
LATITUDE = 11.1492
LONGITUDE = 104.5364

# FIXED: Added missing 'latitude=' and 'longitude=' keywords to the query string
API_URL = f"https://api.open-meteo.com/v1/forecast?latitude={LATITUDE}&longitude={LONGITUDE}&daily=temperature_2m_max,temperature_2m_min,weather_code,sunrise,sunset&timezone=auto&forecast_days=3"

MAX_RETRIES = 3
INITIAL_DELAY = 2

# ==========================================
# LOGGING SETUP
# ==========================================
# FIXED: Added force=True to ensure pre-existing logging configs don't block this setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
    force=True,
)


# ==========================================
# PIPELINE FUNCTIONS
# ==========================================
def fetch_data(url: str) -> dict:
    """Fetches raw JSON data from the API endpoint using exponential backoff."""
    delay = INITIAL_DELAY

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logging.info("API request attempt %s of %s...", attempt, MAX_RETRIES)
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            logging.info("API request successful.")
            return response.json()

        except requests.exceptions.RequestException as e:
            logging.warning("Attempt %s failed. Error: %s", attempt, e)

            if attempt == MAX_RETRIES:
                logging.error("Max retries reached. API extraction failed.")
                raise e

            logging.info("Waiting %s seconds before retrying...", delay)
            time.sleep(delay)
            delay *= 2


def clean_data(raw_json: dict) -> pd.DataFrame:
    """Transforms raw nested API lists into a clean, structural DataFrame."""
    logging.info("Starting data cleaning and transformation...")

    # Extract the nested daily data array
    if "daily" not in raw_json:
        raise KeyError(
            "Expected 'daily' metrics missing from API response payload."
        )

    # FIXED: Replaced pd.json_normalize() with standard pd.DataFrame constructor
    # directly on the 'daily' dict. This ensures columns match perfectly for exploding.
    df = pd.DataFrame(raw_json["daily"])

    # 2. Explode the aligned daily lists into multiple vertical rows
    df = df.explode(
        [
            "time",
            "temperature_2m_max",
            "temperature_2m_min",
            "weather_code",
            "sunrise",
            "sunset",
        ]
    ).reset_index(drop=True)

    # 3. Rename columns for clear business context
    df = df.rename(
        columns={
            "time": "date",
            "temperature_2m_max": "max_temperature",
            "temperature_2m_min": "min_temperature",
        }
    )

    # 4. Clean up columns (e.g., extract time component only: '2026-10-23T17:40' -> '17:40')
    df["sunrise"] = df["sunrise"].apply(
        lambda x: str(x)[-5:] if pd.notnull(x) else x
    )
    df["sunset"] = df["sunset"].apply(
        lambda x: str(x)[-5:] if pd.notnull(x) else x
    )

    # 5. Append pipeline execution metadata timestamp
    df["loaded_at"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

    logging.info("Successfully processed and cleaned %s rows of data.", len(df))
    return df


def save_data(df: pd.DataFrame) -> None:
    """Persists data down into its final storage target destination."""
    filename = "daily_weather_data.csv"
    logging.info("Saving extracted dataset down to local storage: %s", filename)

    # Output to csv
    df.to_csv(filename, index=False)
    logging.info("Data export completed successfully.")





# ==========================================
# MAIN EXECUTION CONTROLLER
# ==========================================
def main():
    logging.info("=== Pipeline Execution Started ===")

    try:
        raw_data = fetch_data(API_URL)
        cleaned_df = clean_data(raw_data)
        save_data(cleaned_df)

        logging.info("=== Pipeline Finished Execution (Success) ===")

    except Exception as e:
        logging.critical(
            "Pipeline crashed due to an unhandled exception: %s",
            e,
            exc_info=True,
        )


if __name__ == "__main__":
    main()


# =====================================================================
# IDEMPOTENT PIPELINE LAYER
# =====================================================================
def load_data(df: pd.DataFrame, database_url: str):
    """Inserts a cleaned weather DataFrame into PostgreSQL idempotently."""
    engine = create_engine(database_url)
    temp_table = "temp_staged_weather"
    prod_table = "3_day_weather_forecast"

    print(f"Staging {len(df)} rows into temporary table '{temp_table}'...")
    df.to_sql(name=temp_table, con=engine, if_exists='replace', index=False)


