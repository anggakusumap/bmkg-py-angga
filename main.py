"""
Entry point for the BMKG Weather Analysis project.

Run this file to execute the full pipeline:
  Step 1 → Fetch data from the BMKG API
  Step 2 → Process and clean the data
  Step 3 → Calculate descriptive statistics
  Step 4 → Generate basic visualizations (Level 2)
  Step 5 → EDA: heatmap, pairplot, insights (Level 3)
  Step 6 → SQL exploration via SQLite (Level 3)
  Step 7 → Prediction: Linear Regression (Level 3+)

Usage:
    python main.py
"""

from src.fetch_data    import fetch_weather_data
from src.process_data  import process_data
from src.statistics    import calculate_statistics
from src.visualization import generate_all_charts
from src.eda           import run_eda_pipeline
from src.database      import run_database_pipeline
from src.prediction    import run_prediction_pipeline


API_URL    = "https://api.bmkg.go.id/publik/prakiraan-cuaca"
API_PARAMS = {"adm4": "51.71.01.1004"}

RAW_JSON   = "data/weather_raw.json"
CLEAN_CSV  = "data/weather_clean.csv"
CHARTS_DIR = "data/charts"
DB_PATH    = "data/weather.db"


def main():
    print("=" * 55)
    print("  ANALISIS CUACA BMKG — Panjer, Denpasar, Bali")
    print("  [Level 1–3 + Prediction]")
    print("=" * 55)

    # ── Step 1: Fetch ────────────────────────────────────────
    print("\nStep 1: Fetching data dari API BMKG...")
    data = fetch_weather_data(API_URL, API_PARAMS, RAW_JSON)
    if data is None:
        print("  Gagal fetch live data. Mencoba pakai file raw yang ada...")

    # ── Step 2: Process ──────────────────────────────────────
    print("\nStep 2: Processing dan membersihkan data...")
    df = process_data(RAW_JSON, CLEAN_CSV)
    if df is None:
        print("  Processing gagal. Pastikan data/weather_raw.json tersedia.")
        return

    # ── Step 3: Statistics ───────────────────────────────────
    print("\nStep 3: Menghitung statistik deskriptif...")
    calculate_statistics(CLEAN_CSV)

    # ── Step 4: Basic Visualizations (Level 2) ───────────────
    print("\nStep 4: Generate visualisasi dasar (Level 2)...")
    generate_all_charts(CLEAN_CSV, CHARTS_DIR)

    # ── Step 5: EDA — Heatmap, Pairplot, Insights (Level 3) ──
    print("\nStep 5: EDA lanjutan — heatmap, pairplot, insight (Level 3)...")
    run_eda_pipeline(CLEAN_CSV, CHARTS_DIR)

    # ── Step 6: SQL Exploration (Level 3) ────────────────────
    print("\nStep 6: SQL exploration via SQLite (Level 3)...")
    run_database_pipeline(CLEAN_CSV, DB_PATH)

    # ── Step 7: Prediction — Linear Regression (Level 3+) ────
    print("\nStep 7: Prediksi suhu dengan Linear Regression...")
    run_prediction_pipeline(CLEAN_CSV, CHARTS_DIR)

    # ── Summary ──────────────────────────────────────────────
    print("\n" + "=" * 55)
    print("  Pipeline complete!")
    print(f"  Raw JSON  → {RAW_JSON}")
    print(f"  Clean CSV → {CLEAN_CSV}")
    print(f"  Database  → {DB_PATH}")
    print(f"  Charts    → {CHARTS_DIR}/  (10 charts total)")
    print("=" * 55)
    print("""
  Charts yang dihasilkan:
    01_temperature_line.png
    02_temperature_histogram.png
    03_temp_vs_humidity_scatter.png
    04_weather_condition_bar.png
    05_correlation_heatmap.png       ← Level 3 EDA
    06_pairplot.png                  ← Level 3 EDA
    07_humidity_line.png             ← Level 3 EDA
    08_actual_vs_predicted.png       ← Prediction
    09_prediction_timeline.png       ← Prediction
    10_residuals.png                 ← Prediction
""")


if __name__ == "__main__":
    main()
