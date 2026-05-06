"""Data access helpers for market prices and macroeconomic series."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import date

import pandas as pd


def download_prices(
    tickers: Mapping[str, str] | Sequence[str],
    start: str | date = "2015-01-01",
    end: str | date | None = None,
    business_days_only: bool = True,
) -> pd.DataFrame:
    """Download adjusted close prices from Yahoo Finance.

    Parameters
    ----------
    tickers:
        Either a mapping like {"S&P 500": "SPY"} or a sequence of Yahoo tickers.
        If a mapping is passed, output columns use the readable labels.
    start, end:
        Date range. ``end`` follows Yahoo Finance conventions and is exclusive.
    business_days_only:
        Keep Monday-Friday observations. This makes crypto and traditional assets
        easier to compare with the same annualization convention.
    """

    try:
        import yfinance as yf
    except ImportError as exc:
        raise ImportError("Install yfinance with `pip install yfinance`.") from exc

    labels, yahoo_tickers = _normalize_tickers(tickers)
    raw = yf.download(
        yahoo_tickers,
        start=start,
        end=end,
        auto_adjust=True,
        progress=False,
        threads=True,
    )
    close = _extract_close(raw, yahoo_tickers)
    close = close.rename(columns={ticker: label for label, ticker in zip(labels, yahoo_tickers)})
    close.columns.name = None
    close = close.sort_index().dropna(how="all")

    if business_days_only:
        close = close[close.index.dayofweek < 5]

    return close


def download_fred_series(
    series: Mapping[str, str],
    start: str | date = "2015-01-01",
    end: str | date | None = None,
) -> pd.DataFrame:
    """Download macroeconomic time series from FRED."""

    try:
        from pandas_datareader import data as pdr
    except ImportError as exc:
        raise ImportError("Install pandas-datareader with `pip install pandas-datareader`.") from exc

    frames: list[pd.DataFrame] = []
    for label, fred_code in series.items():
        frame = pdr.DataReader(fred_code, "fred", start, end).rename(columns={fred_code: label})
        frames.append(frame)

    return pd.concat(frames, axis=1).sort_index()


def monthly_prices(prices: pd.DataFrame) -> pd.DataFrame:
    """Convert daily prices to month-end prices."""

    return prices.resample("ME").last()


def align_to_monthly(market_data: pd.DataFrame, macro_data: pd.DataFrame) -> pd.DataFrame:
    """Join market and macro data at month-end frequency."""

    monthly_market = monthly_prices(market_data)
    monthly_macro = macro_data.resample("ME").last().ffill()
    return monthly_market.join(monthly_macro, how="inner")


def _normalize_tickers(tickers: Mapping[str, str] | Sequence[str]) -> tuple[list[str], list[str]]:
    if isinstance(tickers, Mapping):
        labels = list(tickers.keys())
        yahoo_tickers = list(tickers.values())
    else:
        yahoo_tickers = list(tickers)
        labels = yahoo_tickers

    if not yahoo_tickers:
        raise ValueError("Pass at least one ticker.")

    return labels, yahoo_tickers


def _extract_close(raw: pd.DataFrame, tickers: Sequence[str]) -> pd.DataFrame:
    if raw.empty:
        raise ValueError("No price data was returned. Check tickers, dates or network access.")

    if isinstance(raw.columns, pd.MultiIndex):
        if "Close" not in raw.columns.get_level_values(0):
            raise ValueError("Yahoo response did not include Close prices.")
        close = raw["Close"]
    else:
        if "Close" not in raw.columns:
            raise ValueError("Yahoo response did not include a Close column.")
        close = raw["Close"]

    if isinstance(close, pd.Series):
        return close.to_frame(name=tickers[0])

    return close
