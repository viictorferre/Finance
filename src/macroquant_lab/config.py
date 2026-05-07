"""Project configuration: tickers, labels and macro series."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Asset:
    """Financial asset metadata used across notebooks and dashboards."""

    label: str
    ticker: str
    category: str


CORE_ASSETS: tuple[Asset, ...] = (
    Asset("S&P 500", "SPY", "Equity"),
    Asset("Nasdaq 100", "QQQ", "Equity"),
    Asset("Gold", "GLD", "Commodity"),
    Asset("US Long Bonds", "TLT", "Fixed Income"),
    Asset("Bitcoin", "BTC-USD", "Crypto"),
)

EXTENDED_ASSETS: tuple[Asset, ...] = (
    *CORE_ASSETS,
    Asset("Oil", "USO", "Commodity"),
    Asset("US Dollar", "UUP", "Currency"),
    Asset("Apple", "AAPL", "Single Stock"),
    Asset("Microsoft", "MSFT", "Single Stock"),
    Asset("Nvidia", "NVDA", "Single Stock"),
    Asset("Santander", "SAN.MC", "Single Stock"),
    Asset("Inditex", "ITX.MC", "Single Stock"),
)

CORE_ASSET_TICKERS: dict[str, str] = {asset.label: asset.ticker for asset in CORE_ASSETS}
EXTENDED_ASSET_TICKERS: dict[str, str] = {asset.label: asset.ticker for asset in EXTENDED_ASSETS}

FRED_SERIES: dict[str, str] = {
    "US CPI": "CPIAUCSL",
    "Fed Funds Rate": "FEDFUNDS",
    "US Unemployment": "UNRATE",
    "US Real GDP": "GDPC1",
    "US 10Y Yield": "DGS10",
    "US 2Y Yield": "DGS2",
    "US 10Y Real Yield": "DFII10",
    "US Money Supply M2": "M2SL",
    "VIX": "VIXCLS",
}
