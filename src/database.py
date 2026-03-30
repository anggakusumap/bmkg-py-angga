"""
Loads cleaned weather CSV into a SQLite database,
then runs SQL queries for exploration (SELECT, JOIN, agregasi).
"""

import pandas as pd
from sqlalchemy import create_engine, text
import os


INPUT_PATH = "data/weather_clean.csv"
DB_PATH    = "data/weather.db"


def load_to_sqlite(input_path: str, db_path: str) -> None:
    """Loads the cleaned CSV into a SQLite database."""
    print(f"\nLoading CSV ke SQLite: {db_path}")

    try:
        df = pd.read_csv(input_path, parse_dates=["datetime"])
    except FileNotFoundError:
        print(f"File not found: {input_path}")
        return None

    engine = create_engine(f"sqlite:///{db_path}")

    # Main weather table
    df.to_sql("weather", engine, if_exists="replace", index=False)
    print(f"  Tabel 'weather' berhasil dibuat ({len(df)} baris)")

    # Derived table: daily aggregates (for JOIN demo)
    df["date"] = df["datetime"].dt.date.astype(str)
    daily = df.groupby("date").agg(
        avg_temp   = ("temperature_c",  "mean"),
        max_temp   = ("temperature_c",  "max"),
        min_temp   = ("temperature_c",  "min"),
        avg_hum    = ("humidity_pct",   "mean"),
        avg_wind   = ("wind_speed_kmh", "mean"),
        total_rain = ("rainfall_mm",    "sum"),
    ).reset_index()
    daily.to_sql("daily_summary", engine, if_exists="replace", index=False)
    print(f"  Tabel 'daily_summary' berhasil dibuat ({len(daily)} baris)")

    return engine


def run_sql_queries(db_path: str) -> None:
    """Demonstrates SQL exploration: SELECT, agregasi, dan JOIN."""
    engine = create_engine(f"sqlite:///{db_path}")

    queries = {
        "1. SELECT — 5 Data Terpanas": """
            SELECT datetime, temperature_c, humidity_pct, weather_condition
            FROM weather
            ORDER BY temperature_c DESC
            LIMIT 5
        """,

        "2. AGREGASI — Rata-rata per Kondisi Cuaca": """
            SELECT
                weather_condition,
                ROUND(AVG(temperature_c), 1)  AS avg_suhu,
                ROUND(AVG(humidity_pct), 1)   AS avg_kelembapan,
                ROUND(AVG(wind_speed_kmh), 1) AS avg_angin,
                COUNT(*)                      AS jumlah_slot
            FROM weather
            GROUP BY weather_condition
            ORDER BY avg_suhu DESC
        """,

        "3. JOIN — Gabung weather + daily_summary": """
            SELECT
                w.datetime,
                w.temperature_c,
                d.avg_temp   AS rata_harian,
                ROUND(w.temperature_c - d.avg_temp, 1) AS deviasi_dari_rata
            FROM weather w
            JOIN daily_summary d ON DATE(w.datetime) = d.date
            ORDER BY ABS(w.temperature_c - d.avg_temp) DESC
            LIMIT 10
        """,

        "4. AGREGASI — Ringkasan per Hari": """
            SELECT
                date,
                ROUND(avg_temp, 1)  AS avg_suhu,
                ROUND(min_temp, 1)  AS suhu_min,
                ROUND(max_temp, 1)  AS suhu_max,
                ROUND(avg_hum, 1)   AS avg_kelembapan,
                ROUND(total_rain, 1) AS total_hujan_mm
            FROM daily_summary
            ORDER BY date
        """,
    }

    print("\n" + "=" * 60)
    print("  SQL EXPLORATION RESULTS")
    print("=" * 60)

    with engine.connect() as conn:
        for title, query in queries.items():
            print(f"\n── {title} {'─' * (55 - len(title))}")
            result = pd.read_sql(text(query), conn)
            print(result.to_string(index=False))

    print("\n" + "=" * 60)


def run_database_pipeline(input_path: str = INPUT_PATH,
                           db_path: str    = DB_PATH) -> None:
    """Full pipeline: load CSV → SQLite, then run SQL queries."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    load_to_sqlite(input_path, db_path)
    run_sql_queries(db_path)


if __name__ == "__main__":
    run_database_pipeline()
