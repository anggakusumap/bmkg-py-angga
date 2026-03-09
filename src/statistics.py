"""
Calculates and prints descriptive statistics from the cleaned weather CSV.
"""

import pandas as pd


INPUT_PATH = "data/weather_clean.csv"


def calculate_statistics(input_path: str) -> dict | None:
    """Loads the cleaned CSV and calculates descriptive statistics."""
    print(f"\nLoading clean data dari: {input_path}")

    try:
        df = pd.read_csv(input_path, parse_dates=["datetime"])
    except FileNotFoundError:
        print(f"File not found: {input_path}")
        print("   → Tolong run process_data.py dulu.")
        return None

    temp_mean   = df["temperature_c"].mean()
    temp_median = df["temperature_c"].median()
    temp_mode   = df["temperature_c"].mode()[0]
    temp_min    = df["temperature_c"].min()
    temp_max    = df["temperature_c"].max()
    temp_std    = df["temperature_c"].std()

    hum_mean    = df["humidity_pct"].mean()
    hum_median  = df["humidity_pct"].median()
    hum_min     = df["humidity_pct"].min()
    hum_max     = df["humidity_pct"].max()

    wind_mean   = df["wind_speed_kmh"].mean()
    wind_max    = df["wind_speed_kmh"].max()

    condition_counts = df["weather_condition"].value_counts()

    print("\n" + "="*55)
    print("  PRAKIRAAN CUACA BMKG")
    print("  Desa Panjer, Denpasar Selatan, Denpasar Bali")
    print("="*55)

    print("\nSUHU (°C)")
    print(f"   Rata-rata : {temp_mean:.1f} °C")
    print(f"   Median    : {temp_median:.1f} °C")
    print(f"   Modus     : {temp_mode:.1f} °C")
    print(f"   Min       : {temp_min:.1f} °C")
    print(f"   Maks      : {temp_max:.1f} °C")
    print(f"   Std Dev   : {temp_std:.2f} °C")

    print("\nKELEMBAPAN (%)")
    print(f"   Rata-rata : {hum_mean:.1f} %")
    print(f"   Median    : {hum_median:.1f} %")
    print(f"   Min       : {hum_min:.0f} %")
    print(f"   Maks      : {hum_max:.0f} %")

    print("\nKECEPATAN ANGIN (km/jam)")
    print(f"   Rata-rata : {wind_mean:.1f} km/jam")
    print(f"   Maks      : {wind_max:.1f} km/jam")

    print("\nKONDISI CUACA (Frekuensi)")
    for condition, count in condition_counts.items():
        print(f"   {condition:<20} : {count} waktu")

    print("="*55)

    return {
        "temp_mean"        : temp_mean,
        "temp_median"      : temp_median,
        "temp_mode"        : temp_mode,
        "temp_min"         : temp_min,
        "temp_max"         : temp_max,
        "hum_mean"         : hum_mean,
        "wind_mean"        : wind_mean,
        "condition_counts" : condition_counts.to_dict(),
    }


if __name__ == "__main__":
    calculate_statistics(INPUT_PATH)
