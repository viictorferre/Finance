"""Financial metrics used in the first research phase."""

from __future__ import annotations

import numpy as np
import pandas as pd

TRADING_DAYS_PER_YEAR = 252


def calculate_returns(prices: pd.DataFrame | pd.Series, periods: int = 1, dropna: bool = True):
    """Calculate simple percentage returns from prices."""

    if isinstance(prices, pd.Series):
        returns = prices.dropna().pct_change(periods=periods, fill_method=None)
    else:
        returns = prices.apply(
            lambda column: column.dropna().pct_change(periods=periods, fill_method=None)
        )

    return returns.dropna(how="all") if dropna else returns


def cumulative_returns(returns: pd.DataFrame | pd.Series):
    """Convert periodic returns into cumulative returns."""

    return (1 + returns).cumprod() - 1


def annualized_return(
    returns: pd.DataFrame | pd.Series,
    periods_per_year: int = TRADING_DAYS_PER_YEAR,
) -> pd.Series | float:
    """Calculate annualized geometric return."""

    if isinstance(returns, pd.Series):
        return _annualized_return_series(returns, periods_per_year)

    return returns.apply(_annualized_return_series, periods_per_year=periods_per_year)


def annualized_volatility(
    returns: pd.DataFrame | pd.Series,
    periods_per_year: int = TRADING_DAYS_PER_YEAR,
) -> pd.Series | float:
    """Calculate annualized volatility."""

    return returns.std() * np.sqrt(periods_per_year)


def sharpe_ratio(
    returns: pd.DataFrame | pd.Series,
    risk_free_rate: float = 0.0,
    periods_per_year: int = TRADING_DAYS_PER_YEAR,
) -> pd.Series | float:
    """Calculate annualized Sharpe ratio from periodic returns."""

    periodic_rf = risk_free_rate / periods_per_year
    excess_returns = returns - periodic_rf
    volatility = returns.std()
    sharpe = excess_returns.mean() / volatility * np.sqrt(periods_per_year)
    return sharpe.replace([np.inf, -np.inf], np.nan) if isinstance(sharpe, pd.Series) else sharpe


def drawdown_series(prices: pd.DataFrame | pd.Series):
    """Calculate drawdown series from prices."""

    return prices / prices.cummax() - 1


def max_drawdown(prices: pd.DataFrame | pd.Series):
    """Calculate maximum drawdown."""

    return drawdown_series(prices).min()


def performance_summary(
    prices: pd.DataFrame,
    risk_free_rate: float = 0.0,
    periods_per_year: int = TRADING_DAYS_PER_YEAR,
) -> pd.DataFrame:
    """Create a compact risk/return table for a price DataFrame."""

    returns = calculate_returns(prices)
    summary = pd.DataFrame(
        {
            "total_return": total_return(prices),
            "annualized_return": annualized_return(returns, periods_per_year),
            "annualized_volatility": annualized_volatility(returns, periods_per_year),
            "sharpe_ratio": sharpe_ratio(returns, risk_free_rate, periods_per_year),
            "max_drawdown": max_drawdown(prices),
        }
    )
    return summary.sort_values("sharpe_ratio", ascending=False)


def total_return(prices: pd.DataFrame | pd.Series) -> pd.Series | float:
    """Calculate total return from first to last valid price."""

    if isinstance(prices, pd.Series):
        return _total_return_series(prices)

    return prices.apply(_total_return_series)


def rolling_returns(prices: pd.DataFrame, window: int = 252) -> pd.DataFrame:
    """Calculate rolling returns over a fixed number of observations."""

    return prices / prices.shift(window) - 1


def rolling_volatility(
    returns: pd.DataFrame,
    window: int = 63,
    periods_per_year: int = TRADING_DAYS_PER_YEAR,
) -> pd.DataFrame:
    """Calculate annualized rolling volatility."""

    return returns.rolling(window).std() * np.sqrt(periods_per_year)


def correlation_matrix(returns: pd.DataFrame) -> pd.DataFrame:
    """Calculate asset return correlations."""

    return returns.corr()


def _annualized_return_series(returns: pd.Series, periods_per_year: int) -> float:
    clean_returns = returns.dropna()
    if clean_returns.empty:
        return np.nan

    total_growth = (1 + clean_returns).prod()
    years = clean_returns.shape[0] / periods_per_year
    if years <= 0:
        return np.nan

    return total_growth ** (1 / years) - 1


def _total_return_series(prices: pd.Series) -> float:
    clean_prices = prices.dropna()
    if clean_prices.empty:
        return np.nan

    return clean_prices.iloc[-1] / clean_prices.iloc[0] - 1
