"""
Download DVF data for all Paris arrondissements from geo-dvf (etalab).

Source: https://files.data.gouv.fr/geo-dvf/latest/csv/{year}/departements/75.csv.gz
- Comma-separated, snake_case columns — same schema as the existing DVF app exports.
- Covers years 2020-2024 (2025 is partial).

Usage:
    python data/download_dvf_paris.py              # all years, all arrondissements
    python data/download_dvf_paris.py --years 2023 2024
    python data/download_dvf_paris.py --years 2023 --arrondissements 75001 75002
"""

import argparse
import gzip
import io
import urllib.request
from pathlib import Path

import pandas as pd

BASE_URL = "https://files.data.gouv.fr/geo-dvf/latest/csv/{year}/departements/75.csv.gz"
AVAILABLE_YEARS = [2020, 2021, 2022, 2023, 2024]
ALL_ARRONDISSEMENTS = [f"750{i:02d}" for i in range(1, 21)]  # 75001–75020
OUTPUT_DIR = Path(__file__).parent


def download_year(year: int) -> pd.DataFrame:
    url = BASE_URL.format(year=year)
    print(f"  Downloading {url} ...")
    with urllib.request.urlopen(url) as response:
        data = response.read()
    with gzip.open(io.BytesIO(data)) as f:
        df = pd.read_csv(f, dtype=str)
    df["_year"] = str(year)
    return df


def main(years: list[int], arrondissements: list[str]) -> None:
    print(f"Years: {years}")
    print(f"Arrondissements: {arrondissements}")
    print()

    frames = []
    for year in years:
        try:
            df = download_year(year)
            frames.append(df)
            print(f"  -> {len(df):,} rows loaded for {year}")
        except Exception as e:
            print(f"  WARNING: failed to download {year}: {e}")

    if not frames:
        print("No data downloaded.")
        return

    combined = pd.concat(frames, ignore_index=True)
    combined["code_postal"] = combined["code_postal"].astype(str).str.strip()

    for arr in arrondissements:
        subset = combined[combined["code_postal"] == arr].drop(columns=["_year"])
        if subset.empty:
            print(f"  No data found for {arr}, skipping.")
            continue
        out_path = OUTPUT_DIR / f"dvf_{arr}_all_years.csv"
        subset.to_csv(out_path, sep=";", index=False)
        print(f"  Saved {len(subset):,} rows -> {out_path.name}")

    print("\nDone.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download DVF data for Paris arrondissements.")
    parser.add_argument(
        "--years",
        nargs="+",
        type=int,
        default=AVAILABLE_YEARS,
        help=f"Years to download (default: {AVAILABLE_YEARS})",
    )
    parser.add_argument(
        "--arrondissements",
        nargs="+",
        type=str,
        default=ALL_ARRONDISSEMENTS,
        help="Postal codes to extract (default: all 20, 75001–75020)",
    )
    args = parser.parse_args()
    main(args.years, args.arrondissements)
