"""
Loads raw BMKG JSON data, extracts relevant fields, cleans it,
and exports as a CSV file.
"""

import json
import pandas as pd


INPUT_PATH  = "data/weather_raw.json"
OUTPUT_PATH = "data/weather_clean.csv"


def extract_records(raw_data: dict) -> list[dict]:
    """Flattens the nested JSON structure into a single list of forecast records."""
    records = []

    try:
        cuaca_days = raw_data["data"][0]["cuaca"]

        for day_group in cuaca_days:
            for forecast in day_group:
                records.append(forecast)

        print(f"📦 Extracted {len(records)} forecast records.")

    except (KeyError, IndexError) as e:
        print(f"❌ Error navigating JSON structure: {e}")

    return records


def build_dataframe(records: list[dict]) -> pd.DataFrame:
    """Converts records into a cleaned pandas DataFrame."""
    field_map = {
        "local_datetime": "datetime",
        "t": "temperature_c",
        "hu": "humidity_pct",
        "weather_desc_en": "weather_condition",
        "ws": "wind_speed_kmh",
        "wd": "wind_direction",
        "vs_text": "visibility",
        "tcc": "cloud_cover_pct",
        "tp": "rainfall_mm",
    }

    cleaned = []
    for record in records:
        row = {new_name: record.get(old_key) for old_key, new_name in field_map.items()}
        cleaned.append(row)

    df = pd.DataFrame(cleaned)
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.sort_values("datetime").reset_index(drop=True)

    print("✅ DataFrame created successfully.")
    return df


def process_data(input_path: str, output_path: str) -> pd.DataFrame | None:
    """Loads JSON, extracts records, builds DataFrame, and exports to CSV."""
    print(f"\n📂 Loading raw data from: {input_path}")

    try:
        with open(input_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ File not found: {input_path}")
        print("   → Please run fetch_data.py first.")
        return None

    records = extract_records(raw_data)
    if not records:
        print("❌ No records found. Check the JSON structure.")
        return None

    df = build_dataframe(records)

    print("\n── df.head() ──────────────────────────────────────────────")
    print(df.head())

    print("\n── df.info() ──────────────────────────────────────────────")
    df.info()

    print("\n── df.describe() ──────────────────────────────────────────")
    print(df.describe())

    df.to_csv(output_path, index=False)
    print(f"\n💾 Clean data saved to: {output_path}")

    return df


if __name__ == "__main__":
    process_data(INPUT_PATH, OUTPUT_PATH)
