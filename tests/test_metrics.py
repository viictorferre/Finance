from __future__ import annotations

import pandas as pd

from macroquant_lab.metrics import calculate_returns, max_drawdown, performance_summary


def test_calculate_returns_drops_initial_missing_row() -> None:
    prices = pd.DataFrame({"Asset": [100.0, 110.0, 121.0]})

    returns = calculate_returns(prices)

    assert returns.shape == (2, 1)
    assert returns["Asset"].round(4).tolist() == [0.1, 0.1]


def test_max_drawdown_uses_previous_peak() -> None:
    prices = pd.Series([100.0, 110.0, 88.0, 132.0], name="Asset")

    assert round(max_drawdown(prices), 4) == -0.2


def test_performance_summary_contains_core_metrics() -> None:
    prices = pd.DataFrame(
        {
            "Asset A": [100.0, 102.0, 104.0, 106.0],
            "Asset B": [100.0, 99.0, 98.0, 97.0],
        }
    )

    summary = performance_summary(prices)

    assert set(summary.columns) == {
        "total_return",
        "annualized_return",
        "annualized_volatility",
        "sharpe_ratio",
        "max_drawdown",
    }
    assert set(summary.index) == {"Asset A", "Asset B"}


def test_performance_summary_uses_first_and_last_valid_prices() -> None:
    prices = pd.DataFrame(
        {
            "Asset A": [None, 100.0, 110.0],
            "Asset B": [50.0, 60.0, None],
        }
    )

    summary = performance_summary(prices)

    assert round(summary.loc["Asset A", "total_return"], 4) == 0.1
    assert round(summary.loc["Asset B", "total_return"], 4) == 0.2


def test_calculate_returns_uses_each_asset_valid_calendar() -> None:
    prices = pd.DataFrame(
        {
            "Asset A": [100.0, None, None, 110.0],
            "Asset B": [50.0, 55.0, 60.5, 66.55],
        },
        index=pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"]),
    )

    returns = calculate_returns(prices)

    assert round(returns.loc["2024-01-04", "Asset A"], 4) == 0.1
    assert returns["Asset B"].round(4).dropna().tolist() == [0.1, 0.1, 0.1]
