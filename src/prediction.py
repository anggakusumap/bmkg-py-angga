"""
Prediction module: uses linear regression (scikit-learn) to predict
future temperature based on time-derived features.

Features used:
  - hour_of_day    : captures daily temperature cycle
  - day_of_week    : weekly pattern
  - time_index     : overall trend over the forecast period
  - humidity_pct   : inverse correlation with temperature
  - cloud_cover_pct: clouds reduce daytime heating
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import os

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler


INPUT_PATH = "data/weather_clean.csv"
OUTPUT_DIR = "data/charts"

sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams["figure.dpi"] = 120

FEATURES = [
    "hour_of_day",
    "day_of_week",
    "time_index",
    "humidity_pct",
    "cloud_cover_pct",
]
TARGET = "temperature_c"


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Engineers time-based features from the datetime column."""
    df = df.copy()
    df["hour_of_day"]  = df["datetime"].dt.hour
    df["day_of_week"]  = df["datetime"].dt.dayofweek
    df["time_index"]   = range(len(df))
    return df


def train_model(df: pd.DataFrame):
    """Trains a LinearRegression model and returns model + scaler + split data."""
    df = build_features(df)
    df = df.dropna(subset=FEATURES + [TARGET])

    X = df[FEATURES].values
    y = df[TARGET].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    scaler = StandardScaler()
    X_train_sc = scaler.fit_transform(X_train)
    X_test_sc  = scaler.transform(X_test)

    model = LinearRegression()
    model.fit(X_train_sc, y_train)

    return model, scaler, X_train_sc, X_test_sc, y_train, y_test, df


def evaluate_model(model, X_test_sc, y_test) -> dict:
    """Calculates and prints model performance metrics."""
    y_pred = model.predict(X_test_sc)

    mae  = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2   = r2_score(y_test, y_pred)

    print("\n" + "=" * 55)
    print("  MODEL EVALUATION — Linear Regression")
    print("=" * 55)
    print(f"  MAE  (Mean Absolute Error)  : {mae:.2f} °C")
    print(f"  RMSE (Root Mean Sq. Error)  : {rmse:.2f} °C")
    print(f"  R²   (Coefficient of Det.)  : {r2:.4f}")
    print()

    if r2 >= 0.85:
        verdict = "Sangat baik — model menjelaskan variasi suhu dengan kuat."
    elif r2 >= 0.65:
        verdict = "Cukup baik — model menangkap tren utama suhu."
    else:
        verdict = "Terbatas — linear regression mungkin perlu fitur tambahan."
    print(f"  Interpretasi: {verdict}")
    print("=" * 55)

    # Feature importance (coefficients)
    print("\n  Koefisien Fitur (pengaruh relatif setelah scaling):")
    for feat, coef in zip(FEATURES, model.coef_):
        direction = "↑ naik" if coef > 0 else "↓ turun"
        print(f"    {feat:<20} : {coef:+.4f}  ({direction})")
    print(f"    {'intercept':<20} : {model.intercept_:.4f}")

    return {"mae": mae, "rmse": rmse, "r2": r2, "y_pred": y_pred}


def plot_actual_vs_predicted(y_test, y_pred, output_dir: str) -> None:
    """Scatter plot: actual vs predicted temperature."""
    fig, ax = plt.subplots(figsize=(7, 6))

    ax.scatter(y_test, y_pred, alpha=0.7, color="#3498DB",
               edgecolors="white", linewidths=0.5, s=60, label="Prediksi")

    lim_min = min(y_test.min(), y_pred.min()) - 1
    lim_max = max(y_test.max(), y_pred.max()) + 1
    ax.plot([lim_min, lim_max], [lim_min, lim_max],
            color="#E74C3C", linewidth=1.5, linestyle="--", label="Ideal (y = x)")

    ax.set_title("Actual vs Predicted — Suhu (°C)", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Suhu Aktual (°C)", fontsize=11)
    ax.set_ylabel("Suhu Prediksi (°C)", fontsize=11)
    ax.legend(fontsize=10)
    ax.set_xlim(lim_min, lim_max)
    ax.set_ylim(lim_min, lim_max)

    plt.tight_layout()
    path = os.path.join(output_dir, "08_actual_vs_predicted.png")
    plt.savefig(path)
    print(f"  Saved: {path}")
    plt.close()


def plot_prediction_timeline(df: pd.DataFrame, model,
                             scaler, output_dir: str) -> None:
    """Line chart comparing actual vs predicted temperature over time."""
    df = build_features(df)
    df = df.dropna(subset=FEATURES + [TARGET])

    X_all_sc = scaler.transform(df[FEATURES].values)
    df["predicted_temp"] = model.predict(X_all_sc)

    fig, ax = plt.subplots(figsize=(13, 5))

    ax.plot(df["datetime"], df["temperature_c"],
            color="#E74C3C", linewidth=2, label="Aktual", zorder=3)
    ax.plot(df["datetime"], df["predicted_temp"],
            color="#3498DB", linewidth=1.8, linestyle="--",
            label="Prediksi (Linear Regression)", zorder=2)

    ax.fill_between(df["datetime"],
                    df["temperature_c"], df["predicted_temp"],
                    alpha=0.15, color="#9B59B6", label="Selisih")

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b\n%H:%M"))
    fig.autofmt_xdate(rotation=30)

    ax.set_title("Prediksi Suhu vs Aktual — Desa Panjer, Denpasar",
                 fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Tanggal & Waktu", fontsize=11)
    ax.set_ylabel("Suhu (°C)", fontsize=11)
    ax.legend(fontsize=10)

    plt.tight_layout()
    path = os.path.join(output_dir, "09_prediction_timeline.png")
    plt.savefig(path)
    print(f"  Saved: {path}")
    plt.close()


def plot_residuals(y_test, y_pred, output_dir: str) -> None:
    """Residual distribution — diagnoses model bias."""
    residuals = y_test - y_pred

    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    # Residual histogram
    axes[0].hist(residuals, bins=15, color="#27AE60",
                 edgecolor="white", linewidth=0.8)
    axes[0].axvline(0, color="#E74C3C", linewidth=1.5, linestyle="--")
    axes[0].set_title("Distribusi Residual", fontsize=12, fontweight="bold")
    axes[0].set_xlabel("Residual (°C)")
    axes[0].set_ylabel("Frekuensi")

    # Residual vs predicted
    axes[1].scatter(y_pred, residuals, alpha=0.6, color="#8E44AD",
                    edgecolors="white", linewidths=0.4, s=50)
    axes[1].axhline(0, color="#E74C3C", linewidth=1.5, linestyle="--")
    axes[1].set_title("Residual vs Predicted", fontsize=12, fontweight="bold")
    axes[1].set_xlabel("Predicted Suhu (°C)")
    axes[1].set_ylabel("Residual (°C)")

    plt.tight_layout()
    path = os.path.join(output_dir, "10_residuals.png")
    plt.savefig(path)
    print(f"  Saved: {path}")
    plt.close()


def run_prediction_pipeline(input_path: str = INPUT_PATH,
                             output_dir: str = OUTPUT_DIR) -> None:
    """Full prediction pipeline: load → train → evaluate → visualize."""
    print(f"\nLoading data dari: {input_path}")

    try:
        df = pd.read_csv(input_path, parse_dates=["datetime"])
    except FileNotFoundError:
        print(f"File not found: {input_path}")
        return

    os.makedirs(output_dir, exist_ok=True)

    print("\nTraining Linear Regression model...")
    model, scaler, X_train_sc, X_test_sc, y_train, y_test, df_feat = train_model(df)

    metrics = evaluate_model(model, X_test_sc, y_test)

    print("\nGenerating prediction charts...")
    plot_actual_vs_predicted(y_test, metrics["y_pred"], output_dir)
    plot_prediction_timeline(df, model, scaler, output_dir)
    plot_residuals(y_test, metrics["y_pred"], output_dir)

    print("\nPrediction pipeline selesai!")


if __name__ == "__main__":
    run_prediction_pipeline()
