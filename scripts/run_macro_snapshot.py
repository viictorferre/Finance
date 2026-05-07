"""Run a first macro-regime snapshot and save derived datasets."""

from __future__ import annotations

from pathlib import Path

from macroquant_lab.config import CORE_ASSET_TICKERS, FRED_SERIES
from macroquant_lab.data_loader import download_fred_series, download_prices, monthly_prices
from macroquant_lab.macro import (
    build_macro_features,
    classify_macro_regimes,
    summarize_returns_by_regime,
)
from macroquant_lab.metrics import calculate_returns


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MACRO_OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "macro_features.csv"
REGIME_OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "asset_returns_by_macro_regime.csv"


def main() -> None:
    prices = download_prices(CORE_ASSET_TICKERS, start="2015-01-01")
    raw_macro = download_fred_series(FRED_SERIES, start="2015-01-01")

    macro_features = classify_macro_regimes(build_macro_features(raw_macro))
    monthly_returns = calculate_returns(monthly_prices(prices))
    regime_summary = summarize_returns_by_regime(monthly_returns, macro_features)

    MACRO_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    macro_features.to_csv(MACRO_OUTPUT_PATH)
    regime_summary.to_csv(REGIME_OUTPUT_PATH, index=False)

    latest = macro_features.dropna(how="all").iloc[-1]
    print("\nMacroQuant Lab: first macro snapshot\n")
    print("Latest macro regime:")
    print(latest[["macro_regime", "inflation_regime", "rate_regime", "growth_regime", "curve_regime"]])
    print("\nBest assets by macro regime:")
    print(regime_summary.groupby("macro_regime").head(2).round(4).to_string(index=False))
    print(f"\nSaved macro features to: {MACRO_OUTPUT_PATH}")
    print(f"Saved regime summary to: {REGIME_OUTPUT_PATH}")


if __name__ == "__main__":
    main()

