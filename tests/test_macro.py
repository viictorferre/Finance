from __future__ import annotations

import pandas as pd

from macroquant_lab.macro import (
    build_macro_features,
    classify_macro_regimes,
    summarize_returns_by_regime,
)


def test_build_macro_features_creates_derived_columns() -> None:
    index = pd.date_range("2020-01-31", periods=13, freq="ME")
    raw_macro = pd.DataFrame(
        {
            "US CPI": [100.0] * 12 + [104.0],
            "Fed Funds Rate": [1.0] * 13,
            "US 10Y Yield": [3.0] * 13,
            "US 2Y Yield": [2.0] * 13,
        },
        index=index,
    )

    features = build_macro_features(raw_macro)

    assert round(features.loc[index[-1], "Inflation YoY"], 4) == 4.0
    assert round(features.loc[index[-1], "Yield Curve 10Y-2Y"], 4) == 1.0
    assert round(features.loc[index[-1], "Real Fed Funds Proxy"], 4) == -3.0


def test_classify_macro_regimes_identifies_high_inflation_high_rates() -> None:
    features = pd.DataFrame(
        {
            "Inflation YoY": [4.0],
            "Fed Funds Rate": [5.0],
            "GDP YoY": [2.0],
            "Yield Curve 10Y-2Y": [0.5],
        },
        index=pd.to_datetime(["2024-01-31"]),
    )

    regimes = classify_macro_regimes(features)

    assert regimes.loc["2024-01-31", "macro_regime"] == "High inflation / high rates"
    assert regimes.loc["2024-01-31", "inflation_regime"] == "High inflation"
    assert regimes.loc["2024-01-31", "rate_regime"] == "High rates"


def test_summarize_returns_by_regime_returns_tidy_table() -> None:
    index = pd.date_range("2024-01-31", periods=3, freq="ME")
    monthly_returns = pd.DataFrame(
        {
            "S&P 500": [0.01, 0.02, -0.01],
            "Gold": [0.00, 0.01, 0.03],
        },
        index=index,
    )
    regimes = pd.DataFrame(
        {"macro_regime": ["A", "A", "B"]},
        index=index,
    )

    summary = summarize_returns_by_regime(monthly_returns, regimes)

    assert set(summary["asset"]) == {"S&P 500", "Gold"}
    assert set(summary["macro_regime"]) == {"A", "B"}
    assert summary.loc[summary["macro_regime"].eq("A"), "months"].unique().tolist() == [2]

