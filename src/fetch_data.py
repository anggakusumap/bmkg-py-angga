"""
Fetches weather forecast data from the BMKG API
and saves it as a raw JSON file.
"""

import requests
import json
import os


API_URL = "https://api.bmkg.go.id/publik/prakiraan-cuaca"
PARAMS  = {"adm4": "51.71.01.1004"}
OUTPUT_PATH = "data/weather_raw.json"


def fetch_weather_data(url: str, params: dict, output_path: str) -> dict | None:
    print("Connecting ke API BMKG...")

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        print(f"Data berhasil di-fetch! Status code: {response.status_code}")

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"Raw data saved di: {output_path}")
        return data

    except requests.exceptions.ConnectionError:
        print("Error: Connection Error. Periksa koneksi.")
    except requests.exceptions.Timeout:
        print("Error: Request timeout.")
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Unexpected Error: {e}")

    return None


if __name__ == "__main__":
    fetch_weather_data(API_URL, PARAMS, OUTPUT_PATH)
