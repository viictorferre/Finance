"""Plotly visualizations for research notebooks and Streamlit."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from macroquant_lab.metrics import cumulative_returns, drawdown_series


def plot_prices(prices: pd.DataFrame) -> go.Figure:
    fig = px.line(prices, title="Price evolution")
    fig.update_layout(yaxis_title="Price", xaxis_title=None, legend_title_text=None)
    return fig


def plot_cumulative_returns(returns: pd.DataFrame) -> go.Figure:
    cumulative = cumulative_returns(returns)
    fig = px.line(cumulative, title="Cumulative return")
    fig.update_layout(yaxis_tickformat=".0%", xaxis_title=None, legend_title_text=None)
    return fig


def plot_drawdowns(prices: pd.DataFrame) -> go.Figure:
    drawdowns = drawdown_series(prices)
    fig = px.line(drawdowns, title="Drawdown")
    fig.update_layout(yaxis_tickformat=".0%", xaxis_title=None, legend_title_text=None)
    return fig


def plot_correlation_heatmap(returns: pd.DataFrame) -> go.Figure:
    corr = returns.corr()
    fig = px.imshow(
        corr,
        text_auto=".2f",
        zmin=-1,
        zmax=1,
        color_continuous_scale="RdBu",
        title="Return correlation",
    )
    fig.update_layout(xaxis_title=None, yaxis_title=None)
    return fig


def plot_macro_series(macro_features: pd.DataFrame, columns: list[str] | None = None) -> go.Figure:
    """Plot selected macro indicators through time."""

    selected = macro_features[columns] if columns else macro_features
    fig = px.line(selected, title="Macro indicators")
    fig.update_layout(yaxis_title="Value", xaxis_title=None, legend_title_text=None)
    return fig


def plot_regime_asset_returns(regime_summary: pd.DataFrame) -> go.Figure:
    """Plot asset annualized returns grouped by macro regime."""

    heatmap_data = regime_summary.pivot(
        index="macro_regime",
        columns="asset",
        values="annualized_return",
    )
    fig = px.imshow(
        heatmap_data,
        text_auto=".1%",
        color_continuous_scale="RdYlGn",
        title="Annualized return by macro regime",
    )
    fig.update_layout(xaxis_title=None, yaxis_title=None)
    return fig
