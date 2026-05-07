"""Macroeconomic feature engineering and regime classification."""

from __future__ import annotations

import numpy as np
import pandas as pd


def build_macro_features(raw_macro: pd.DataFrame) -> pd.DataFrame:
    """Build interpretable monthly macro features from raw FRED data.

    FRED mixes daily, monthly and quarterly series. For this first macro phase,
    everything is aligned to month-end and forward-filled so market returns and
    macro states can be compared on the same calendar.
    """

    monthly = raw_macro.resample("ME").last().ffill()
    monthly = monthly.loc[monthly.index <= pd.Timestamp.today().normalize()]
    features = pd.DataFrame(index=monthly.index)

    _copy_if_available(monthly, features, "Fed Funds Rate", "Fed Funds Rate")
    _copy_if_available(monthly, features, "US Unemployment", "Unemployment Rate")
    _copy_if_available(monthly, features, "US 10Y Yield", "10Y Yield")
    _copy_if_available(monthly, features, "US 2Y Yield", "2Y Yield")
    _copy_if_available(monthly, features, "US 10Y Real Yield", "10Y Real Yield")
    _copy_if_available(monthly, features, "VIX", "VIX")

    if "US CPI" in monthly:
        features["Inflation YoY"] = monthly["US CPI"].pct_change(12, fill_method=None) * 100

    if "US Real GDP" in monthly:
        features["GDP YoY"] = monthly["US Real GDP"].pct_change(12, fill_method=None) * 100

    if "US Money Supply M2" in monthly:
        features["M2 YoY"] = monthly["US Money Supply M2"].pct_change(12, fill_method=None) * 100

    if {"US 10Y Yield", "US 2Y Yield"}.issubset(monthly.columns):
        features["Yield Curve 10Y-2Y"] = monthly["US 10Y Yield"] - monthly["US 2Y Yield"]

    if {"Fed Funds Rate", "Inflation YoY"}.issubset(features.columns):
        features["Real Fed Funds Proxy"] = features["Fed Funds Rate"] - features["Inflation YoY"]

    return features.dropna(how="all")


def classify_macro_regimes(features: pd.DataFrame) -> pd.DataFrame:
    """Add simple rule-based macro regimes to monthly features.

    The thresholds are deliberately simple and educational. Later we can replace
    them with rolling percentiles, clustering or hidden Markov models.
    """

    regimes = features.copy()

    regimes["inflation_regime"] = _threshold_regime(
        regimes.get("Inflation YoY"),
        index=regimes.index,
        low_threshold=2.0,
        high_threshold=3.0,
        low_label="Low inflation",
        middle_label="Normal inflation",
        high_label="High inflation",
    )
    regimes["rate_regime"] = _threshold_regime(
        regimes.get("Fed Funds Rate"),
        index=regimes.index,
        low_threshold=1.5,
        high_threshold=3.0,
        low_label="Low rates",
        middle_label="Neutral rates",
        high_label="High rates",
    )
    regimes["growth_regime"] = _threshold_regime(
        regimes.get("GDP YoY"),
        index=regimes.index,
        low_threshold=1.0,
        high_threshold=2.5,
        low_label="Weak growth",
        middle_label="Moderate growth",
        high_label="Strong growth",
    )

    curve = regimes.get("Yield Curve 10Y-2Y")
    if curve is None:
        regimes["curve_regime"] = "Unknown"
    else:
        regimes["curve_regime"] = np.where(curve < 0, "Inverted curve", "Normal curve")
        regimes.loc[curve.isna(), "curve_regime"] = "Unknown"

    regimes["macro_regime"] = "Mixed / transition"

    high_inflation = regimes["inflation_regime"].eq("High inflation")
    high_rates = regimes["rate_regime"].eq("High rates")
    low_rates = regimes["rate_regime"].eq("Low rates")
    strong_growth = regimes["growth_regime"].eq("Strong growth")
    weak_growth = regimes["growth_regime"].eq("Weak growth")
    inverted_curve = regimes["curve_regime"].eq("Inverted curve")

    regimes.loc[high_inflation & high_rates, "macro_regime"] = "High inflation / high rates"
    regimes.loc[high_inflation & low_rates, "macro_regime"] = "High inflation / low rates"
    regimes.loc[~high_inflation & strong_growth, "macro_regime"] = (
        "Low/normal inflation / strong growth"
    )
    regimes.loc[weak_growth, "macro_regime"] = "Weak growth"
    regimes.loc[inverted_curve & ~high_inflation & ~weak_growth, "macro_regime"] = (
        "Inverted curve"
    )

    return regimes


def summarize_returns_by_regime(
    monthly_returns: pd.DataFrame,
    regimes: pd.DataFrame,
    regime_column: str = "macro_regime",
) -> pd.DataFrame:
    """Summarize asset returns by macro regime in a tidy table."""

    if regime_column not in regimes:
        raise ValueError(f"`{regime_column}` is missing from regimes.")

    aligned = monthly_returns.join(regimes[[regime_column]], how="inner")
    aligned = aligned.dropna(subset=[regime_column])
    if aligned.empty:
        return pd.DataFrame(
            columns=[
                regime_column,
                "asset",
                "months",
                "mean_monthly_return",
                "annualized_return",
                "annualized_volatility",
            ]
        )

    grouped = aligned.groupby(regime_column)
    months = grouped.size().rename("months")
    mean_monthly = grouped.mean(numeric_only=True)
    monthly_vol = grouped.std(numeric_only=True)

    annualized = (1 + mean_monthly) ** 12 - 1
    annualized_vol = monthly_vol * np.sqrt(12)

    annualized_long = _stack_metric(annualized, "annualized_return", regime_column)
    mean_long = _stack_metric(mean_monthly, "mean_monthly_return", regime_column)
    vol_long = _stack_metric(annualized_vol, "annualized_volatility", regime_column)

    summary = annualized_long.merge(mean_long, on=[regime_column, "asset"], how="left")
    summary = summary.merge(vol_long, on=[regime_column, "asset"], how="left")
    summary = summary.merge(months.reset_index(), on=regime_column, how="left")

    return summary[
        [
            regime_column,
            "asset",
            "months",
            "mean_monthly_return",
            "annualized_return",
            "annualized_volatility",
        ]
    ].sort_values([regime_column, "annualized_return"], ascending=[True, False])


def _copy_if_available(
    source: pd.DataFrame,
    target: pd.DataFrame,
    source_column: str,
    target_column: str,
) -> None:
    if source_column in source:
        target[target_column] = source[source_column]


def _threshold_regime(
    values: pd.Series | None,
    index: pd.Index,
    low_threshold: float,
    high_threshold: float,
    low_label: str,
    middle_label: str,
    high_label: str,
) -> pd.Series:
    if values is None:
        return pd.Series("Unknown", index=index, dtype="object")

    regime = pd.Series(middle_label, index=values.index, dtype="object")
    regime.loc[values < low_threshold] = low_label
    regime.loc[values >= high_threshold] = high_label
    regime.loc[values.isna()] = "Unknown"
    return regime


def _stack_metric(frame: pd.DataFrame, metric_name: str, regime_column: str) -> pd.DataFrame:
    return (
        frame.rename_axis(index=regime_column, columns="asset")
        .stack(future_stack=True)
        .rename(metric_name)
        .reset_index()
    )
