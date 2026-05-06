"""Run a first market snapshot and save the downloaded prices."""

from __future__ import annotations

from pathlib import Path

from macroquant_lab.config import CORE_ASSET_TICKERS
from macroquant_lab.data_loader import download_prices
from macroquant_lab.metrics import performance_summary


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "core_asset_prices.csv"


def main() -> None:
    prices = download_prices(CORE_ASSET_TICKERS, start="2015-01-01")
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    prices.to_csv(OUTPUT_PATH)

    summary = performance_summary(prices)
    print("\nMacroQuant Lab: first asset snapshot\n")
    print(summary.round(4).to_string())
    print(f"\nSaved prices to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

