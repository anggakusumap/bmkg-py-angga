"""
Entry point for the BMKG Weather Analysis project.

Run this file to execute the full pipeline:
  Step 1 → Fetch data from the BMKG API
  Step 2 → Process and clean the data
  Step 3 → Calculate descriptive statistics
  Step 4 → Generate all visualizations

Usage:
    python main.py
"""

from src.fetch_data import fetch_weather_data
from src.process_data import process_data
from src.statistics import calculate_statistics
from src.visualization import generate_all_charts


API_URL = "https://api.bmkg.go.id/publik/prakiraan-cuaca"
API_PARAMS = {"adm4": "51.71.01.1004"}

RAW_JSON = "data/weather_raw.json"
CLEAN_CSV = "data/weather_clean.csv"
CHARTS_DIR = "data/charts"


def main():
    print("=" * 55)
    print("  🌦️  BMKG WEATHER ANALYSIS — Panjer, Denpasar, Bali")
    print("=" * 55)

    print("\n🔷 STEP 1: Fetching data from BMKG API...")
    data = fetch_weather_data(API_URL, API_PARAMS, RAW_JSON)

    if data is None:
        print("\n⚠️  Could not fetch live data. Trying to use existing raw file...")

    print("\n🔷 STEP 2: Processing and cleaning data...")
    df = process_data(RAW_JSON, CLEAN_CSV)

    if df is None:
        print("\n❌ Processing failed. Please check data/weather_raw.json exists.")
        return

    print("\n🔷 STEP 3: Calculating statistics...")
    calculate_statistics(CLEAN_CSV)

    print("\n🔷 STEP 4: Generating visualizations...")
    generate_all_charts(CLEAN_CSV, CHARTS_DIR)

    print("\n" + "=" * 55)
    print("  ✅  Analysis complete!")
    print(f"  📁  Raw JSON  → {RAW_JSON}")
    print(f"  📁  Clean CSV → {CLEAN_CSV}")
    print(f"  📁  Charts    → {CHARTS_DIR}/")
    print("=" * 55)


if __name__ == "__main__":
    main()