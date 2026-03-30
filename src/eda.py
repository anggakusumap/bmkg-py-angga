"""
Level 3 EDA: Generates heatmap, pairplot, and a printed
insight report (notebook-storytelling style).
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import os
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)


INPUT_PATH = "data/weather_clean.csv"
OUTPUT_DIR = "data/charts"

sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams["figure.dpi"] = 120

NUMERIC_COLS = [
    "temperature_c",
    "humidity_pct",
    "wind_speed_kmh",
    "cloud_cover_pct",
    "rainfall_mm",
]


def plot_correlation_heatmap(df: pd.DataFrame, output_dir: str) -> None:
    """Heatmap of Pearson correlation between all numeric variables."""
    corr = df[NUMERIC_COLS].corr()

    fig, ax = plt.subplots(figsize=(8, 6))

    sns.heatmap(
        corr,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        center=0,
        linewidths=0.5,
        linecolor="white",
        square=True,
        ax=ax,
    )

    ax.set_title(
        "Heatmap Korelasi — Variabel Cuaca",
        fontsize=14, fontweight="bold", pad=14
    )
    ax.set_xticklabels(ax.get_xticklabels(), rotation=30, ha="right", fontsize=10)
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=10)

    plt.tight_layout()
    path = os.path.join(output_dir, "05_correlation_heatmap.png")
    plt.savefig(path)
    print(f"  Saved: {path}")
    plt.close()


def plot_pairplot(df: pd.DataFrame, output_dir: str) -> None:
    """Pairplot for all numeric variables, colored by weather condition."""
    # Limit to top 4 conditions to keep the chart readable
    top_conditions = df["weather_condition"].value_counts().head(4).index
    df_filtered = df[df["weather_condition"].isin(top_conditions)].copy()

    g = sns.pairplot(
        df_filtered,
        vars=NUMERIC_COLS,
        hue="weather_condition",
        diag_kind="kde",
        plot_kws={"alpha": 0.6, "s": 30, "edgecolor": "none"},
        height=2.2,
    )

    g.figure.suptitle(
        "Pairplot — Hubungan Antar Variabel Cuaca",
        y=1.02, fontsize=13, fontweight="bold"
    )

    path = os.path.join(output_dir, "06_pairplot.png")
    g.figure.savefig(path, bbox_inches="tight")
    print(f"  Saved: {path}")
    plt.close()


def plot_humidity_line(df: pd.DataFrame, output_dir: str) -> None:
    """Line chart for humidity over time to complement temperature chart."""
    fig, ax = plt.subplots(figsize=(12, 4))

    ax.plot(
        df["datetime"], df["humidity_pct"],
        color="#2980B9", linewidth=1.8, marker="o", markersize=3,
        label="Kelembapan (%)"
    )
    ax.fill_between(df["datetime"], df["humidity_pct"], alpha=0.1, color="#2980B9")

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b\n%H:%M"))
    fig.autofmt_xdate(rotation=30)

    ax.set_title("Kelembapan Udara dari Waktu ke Waktu", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Tanggal & Waktu", fontsize=11)
    ax.set_ylabel("Kelembapan (%)", fontsize=11)
    ax.legend(fontsize=10)

    plt.tight_layout()
    path = os.path.join(output_dir, "07_humidity_line.png")
    plt.savefig(path)
    print(f"  Saved: {path}")
    plt.close()


def print_eda_insights(df: pd.DataFrame) -> None:
    """
    Notebook-storytelling style insight report.
    Prints key findings derived from the data.
    """
    print("\n" + "=" * 60)
    print("  INSIGHT REPORT — EDA CUACA BMKG")
    print("  Desa Panjer, Denpasar Selatan, Bali")
    print("=" * 60)

    # --- Suhu
    temp_mean  = df["temperature_c"].mean()
    temp_std   = df["temperature_c"].std()
    temp_range = df["temperature_c"].max() - df["temperature_c"].min()
    print(f"""
📌 SUHU
   Rata-rata suhu prakiraan adalah {temp_mean:.1f}°C dengan standar deviasi
   {temp_std:.2f}°C, menunjukkan variabilitas suhu {"tinggi" if temp_std > 3 else "moderat"}.
   Range suhu: {temp_range:.1f}°C (min → maks).
""")

    # --- Kelembapan
    hum_mean = df["humidity_pct"].mean()
    hum_corr = df["temperature_c"].corr(df["humidity_pct"])
    direction = "negatif" if hum_corr < 0 else "positif"
    print(f"""📌 KELEMBAPAN
   Rata-rata kelembapan {hum_mean:.1f}%. Korelasi dengan suhu: {hum_corr:.2f} ({direction}).
   {"→ Saat suhu naik, kelembapan cenderung turun." if hum_corr < 0 else "→ Suhu dan kelembapan bergerak searah."}
""")

    # --- Angin
    wind_corr = df["temperature_c"].corr(df["wind_speed_kmh"])
    print(f"""📌 ANGIN
   Korelasi kecepatan angin dengan suhu: {wind_corr:.2f}.
   Rata-rata kecepatan angin: {df["wind_speed_kmh"].mean():.1f} km/jam.
""")

    # --- Kondisi cuaca
    top_cond  = df["weather_condition"].value_counts()
    dominan   = top_cond.index[0]
    dominan_n = top_cond.iloc[0]
    total     = len(df)
    print(f"""📌 KONDISI CUACA DOMINAN
   '{dominan}' mendominasi {dominan_n}/{total} slot waktu ({dominan_n/total*100:.0f}%).
   Distribusi lengkap:""")
    for cond, count in top_cond.items():
        bar = "█" * int(count / total * 30)
        print(f"   {cond:<22} {bar} {count}")

    # --- Hari terpanas & terdingin
    hottest = df.loc[df["temperature_c"].idxmax()]
    coldest = df.loc[df["temperature_c"].idxmin()]
    print(f"""
📌 EKSTREM
   Slot terpanas : {hottest['datetime']} → {hottest['temperature_c']}°C ({hottest['weather_condition']})
   Slot terdingin: {coldest['datetime']} → {coldest['temperature_c']}°C ({coldest['weather_condition']})
""")

    print("=" * 60)


def run_eda_pipeline(input_path: str = INPUT_PATH,
                     output_dir: str = OUTPUT_DIR) -> None:
    """Full EDA pipeline: load data, generate charts, print insights."""
    print(f"\nLoading data dari: {input_path}")

    try:
        df = pd.read_csv(input_path, parse_dates=["datetime"])
    except FileNotFoundError:
        print(f"File not found: {input_path}")
        return

    os.makedirs(output_dir, exist_ok=True)

    print("\nGenerating EDA charts...")
    plot_correlation_heatmap(df, output_dir)
    plot_pairplot(df, output_dir)
    plot_humidity_line(df, output_dir)

    print_eda_insights(df)


if __name__ == "__main__":
    run_eda_pipeline()
