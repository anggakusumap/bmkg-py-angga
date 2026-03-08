"""
Creates and saves charts from the cleaned weather CSV.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import os


INPUT_PATH  = "data/weather_clean.csv"
OUTPUT_DIR  = "data/charts"

sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams["figure.dpi"] = 120


def plot_temperature_line(df: pd.DataFrame, output_dir: str) -> None:
    """Plots temperature (°C) over time as a line chart."""
    fig, ax = plt.subplots(figsize=(12, 5))

    ax.plot(
        df["datetime"],
        df["temperature_c"],
        marker="o",
        linewidth=2,
        color="#E74C3C",
        markersize=5,
        label="Temperature (°C)",
    )

    ax.fill_between(df["datetime"], df["temperature_c"], alpha=0.1, color="#E74C3C")

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b\n%H:%M"))
    fig.autofmt_xdate(rotation=30)

    ax.set_title("🌡️  Temperature Forecast — Panjer Village, Denpasar", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Date & Time (Local)", fontsize=11)
    ax.set_ylabel("Temperature (°C)", fontsize=11)
    ax.legend(fontsize=10)
    ax.set_ylim(20, 38)

    plt.tight_layout()
    path = os.path.join(output_dir, "01_temperature_line.png")
    plt.savefig(path)
    print(f"  ✅ Saved: {path}")
    plt.show()
    plt.close()


def plot_temperature_histogram(df: pd.DataFrame, output_dir: str) -> None:
    """Shows frequency distribution of the temperature."""
    fig, ax = plt.subplots(figsize=(8, 5))

    ax.hist(
        df["temperature_c"],
        bins=10,
        color="#3498DB",
        edgecolor="white",
        linewidth=0.8,
    )

    mean_temp = df["temperature_c"].mean()
    ax.axvline(mean_temp, color="#E74C3C", linestyle="--", linewidth=1.5, label=f"Mean: {mean_temp:.1f} °C")

    ax.set_title("📊 Temperature Distribution", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Temperature (°C)", fontsize=11)
    ax.set_ylabel("Frequency (Number of Time Slots)", fontsize=11)
    ax.legend(fontsize=10)

    plt.tight_layout()
    path = os.path.join(output_dir, "02_temperature_histogram.png")
    plt.savefig(path)
    print(f"  ✅ Saved: {path}")
    plt.show()
    plt.close()


def plot_temp_vs_humidity(df: pd.DataFrame, output_dir: str) -> None:
    """Scatter plot to explore the relationship between temperature and humidity."""
    fig, ax = plt.subplots(figsize=(8, 6))

    conditions = df["weather_condition"].unique()
    cmap = plt.get_cmap("Set2")
    color_map  = {cond: cmap(i / len(conditions)) for i, cond in enumerate(conditions)}

    for cond in conditions:
        subset = df[df["weather_condition"] == cond]
        ax.scatter(
            subset["temperature_c"],
            subset["humidity_pct"],
            label=cond,
            s=80,
            alpha=0.8,
            color=color_map[cond],
            edgecolors="white",
            linewidths=0.5,
        )

    ax.set_title("🌡️  Temperature vs. Humidity", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Temperature (°C)", fontsize=11)
    ax.set_ylabel("Humidity (%)", fontsize=11)
    ax.legend(title="Weather Condition", fontsize=9, title_fontsize=10, loc="upper right")

    plt.tight_layout()
    path = os.path.join(output_dir, "03_temp_vs_humidity_scatter.png")
    plt.savefig(path)
    print(f"  ✅ Saved: {path}")
    plt.show()
    plt.close()


def plot_weather_condition_bar(df: pd.DataFrame, output_dir: str) -> None:
    """Bar chart showing how many time slots have each weather condition."""
    condition_counts = df["weather_condition"].value_counts()

    fig, ax = plt.subplots(figsize=(9, 5))

    bars = ax.bar(
        condition_counts.index,
        condition_counts.values,
        color=sns.color_palette("pastel", len(condition_counts)),
        edgecolor="gray",
        linewidth=0.7,
    )

    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + 0.1,
            str(int(height)),
            ha="center", va="bottom", fontsize=11, fontweight="bold"
        )

    ax.set_title("🌤️  Weather Condition Frequency", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Weather Condition", fontsize=11)
    ax.set_ylabel("Number of 3-Hour Time Slots", fontsize=11)
    ax.set_ylim(0, condition_counts.max() + 2)

    plt.tight_layout()
    path = os.path.join(output_dir, "04_weather_condition_bar.png")
    plt.savefig(path)
    print(f"  ✅ Saved: {path}")
    plt.show()
    plt.close()


def generate_all_charts(input_path: str, output_dir: str) -> None:
    """Loads the cleaned CSV and generates all four visualizations."""
    print(f"\n🎨 Loading data from: {input_path}")

    try:
        df = pd.read_csv(input_path, parse_dates=["datetime"])
    except FileNotFoundError:
        print(f"❌ File not found: {input_path}")
        print("   → Please run process_data.py first.")
        return

    os.makedirs(output_dir, exist_ok=True)

    print("\n📈 Generating charts...")
    plot_temperature_line(df, output_dir)
    plot_temperature_histogram(df, output_dir)
    plot_temp_vs_humidity(df, output_dir)
    plot_weather_condition_bar(df, output_dir)

    print(f"\n🎉 All charts saved to: {output_dir}/")


if __name__ == "__main__":
    generate_all_charts(INPUT_PATH, OUTPUT_DIR)
