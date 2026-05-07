"""Streamlit dashboard for MacroQuant Lab."""

from __future__ import annotations

from datetime import date
from pathlib import Path
import sys

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from macroquant_lab.config import EXTENDED_ASSET_TICKERS, FRED_SERIES
from macroquant_lab.data_loader import download_fred_series, download_prices, monthly_prices
from macroquant_lab.macro import (
    build_macro_features,
    classify_macro_regimes,
    summarize_returns_by_regime,
)
from macroquant_lab.metrics import calculate_returns, performance_summary
from macroquant_lab.visualization import (
    plot_correlation_heatmap,
    plot_cumulative_returns,
    plot_drawdowns,
    plot_macro_series,
    plot_prices,
    plot_regime_asset_returns,
)


st.set_page_config(page_title="MacroQuant Lab", layout="wide")
st.title("MacroQuant Lab")

asset_labels = list(EXTENDED_ASSET_TICKERS.keys())
default_assets = ["S&P 500", "Nasdaq 100", "Gold", "US Long Bonds", "Bitcoin"]

with st.sidebar:
    selected_assets = st.multiselect("Assets", asset_labels, default=default_assets)
    start_date = st.date_input("Start date", value=date(2015, 1, 1))


@st.cache_data(show_spinner=False)
def load_prices(selected: tuple[str, ...], start: str):
    tickers = {label: EXTENDED_ASSET_TICKERS[label] for label in selected}
    return download_prices(tickers, start=start)


@st.cache_data(show_spinner=False)
def load_macro(start: str):
    raw_macro = download_fred_series(FRED_SERIES, start=start)
    return classify_macro_regimes(build_macro_features(raw_macro))


if not selected_assets:
    st.stop()

prices = load_prices(tuple(selected_assets), str(start_date))
returns = calculate_returns(prices)
summary = performance_summary(prices)

metric_columns = st.columns(min(4, len(summary)))
for column, asset in zip(metric_columns, summary.index):
    column.metric(
        asset,
        f"{summary.loc[asset, 'annualized_return']:.1%}",
        f"Sharpe {summary.loc[asset, 'sharpe_ratio']:.2f}",
    )

tab_prices, tab_returns, tab_drawdown, tab_corr, tab_macro, tab_regimes, tab_table = st.tabs(
    ["Prices", "Cumulative", "Drawdown", "Correlation", "Macro", "Regimes", "Metrics"]
)

with tab_prices:
    st.plotly_chart(plot_prices(prices), use_container_width=True)

with tab_returns:
    st.plotly_chart(plot_cumulative_returns(returns), use_container_width=True)

with tab_drawdown:
    st.plotly_chart(plot_drawdowns(prices), use_container_width=True)

with tab_corr:
    st.plotly_chart(plot_correlation_heatmap(returns), use_container_width=True)

with tab_macro:
    try:
        macro_features = load_macro(str(start_date))
        macro_columns = [
            column
            for column in ["Inflation YoY", "Fed Funds Rate", "Yield Curve 10Y-2Y", "GDP YoY", "VIX"]
            if column in macro_features
        ]
        latest_regime = macro_features.dropna(how="all").iloc[-1]
        st.metric("Latest macro regime", latest_regime["macro_regime"])
        st.plotly_chart(
            plot_macro_series(macro_features, macro_columns),
            use_container_width=True,
        )
        st.dataframe(macro_features.tail(12), use_container_width=True)
    except Exception as exc:
        st.warning(f"Macro data could not be loaded: {exc}")

with tab_regimes:
    try:
        macro_features = load_macro(str(start_date))
        monthly_returns = calculate_returns(monthly_prices(prices))
        regime_summary = summarize_returns_by_regime(monthly_returns, macro_features)
        if regime_summary.empty:
            st.info("There is not enough aligned macro and market data yet.")
        else:
            st.plotly_chart(plot_regime_asset_returns(regime_summary), use_container_width=True)
            st.dataframe(
                regime_summary.style.format(
                    {
                        "mean_monthly_return": "{:.2%}",
                        "annualized_return": "{:.1%}",
                        "annualized_volatility": "{:.1%}",
                    }
                ),
                use_container_width=True,
            )
    except Exception as exc:
        st.warning(f"Macro regimes could not be calculated: {exc}")

with tab_table:
    st.dataframe(
        summary.style.format(
            {
                "total_return": "{:.1%}",
                "annualized_return": "{:.1%}",
                "annualized_volatility": "{:.1%}",
                "sharpe_ratio": "{:.2f}",
                "max_drawdown": "{:.1%}",
            }
        ),
        use_container_width=True,
    )
