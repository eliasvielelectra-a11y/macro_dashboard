# market_data.py

from __future__ import annotations

from typing import Any, Dict, Optional

import pandas as pd
import yfinance as yf

from config import (
    CACHE_TTL_SECONDS,
    DEFAULT_SPARKLINE_WINDOW,
    LIVE_MARKET_CONFIG,
    SPARKLINE_OPTIONS,
)


# =========================================================
# NORMALIZATION HELPERS
# =========================================================
def normalize_history(df: Optional[pd.DataFrame]) -> pd.DataFrame:
    """
    Normalize yfinance history output into a clean single-index dataframe.

    Expected columns after normalization:
    - Open, High, Low, Close, Adj Close, Volume (where available)
    """
    if df is None or df.empty:
        return pd.DataFrame()

    out = df.copy()

    if isinstance(out.columns, pd.MultiIndex):
        out.columns = out.columns.get_level_values(0)

    if isinstance(out.index, pd.DatetimeIndex) and out.index.tz is not None:
        out.index = out.index.tz_localize(None)

    out = out.sort_index()

    if "Close" in out.columns:
        out = out.dropna(subset=["Close"])

    return out


def safe_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
        return float(value)
    except Exception:
        return None


# =========================================================
# RAW FETCH
# =========================================================
def fetch_history(ticker: str, period: str) -> pd.DataFrame:
    """
    Download daily history from Yahoo Finance.
    """
    try:
        df = yf.download(
            ticker,
            period=period,
            interval="1d",
            auto_adjust=False,
            progress=False,
            threads=False,
        )

        if df is None or df.empty:
            df = yf.Ticker(ticker).history(
                period=period,
                interval="1d",
                auto_adjust=False,
            )

        return normalize_history(df)

    except Exception:
        return pd.DataFrame()


# =========================================================
# SERIES PREP
# =========================================================
def build_close_series(
    history_df: pd.DataFrame,
    multiplier: float = 1.0,
) -> pd.DataFrame:
    """
    Convert normalized price history into a standard Date/Close dataframe.
    """
    if history_df is None or history_df.empty or "Close" not in history_df.columns:
        return pd.DataFrame(columns=["Date", "Close"])

    out = history_df[["Close"]].copy()

    if multiplier != 1.0:
        out["Close"] = out["Close"] * multiplier

    out = out.dropna().reset_index()

    # Standardize date column name
    if out.columns[0] != "Date":
        out = out.rename(columns={out.columns[0]: "Date"})

    return out[["Date", "Close"]]


def build_sparkline_df(
    close_df: pd.DataFrame,
    points: int,
) -> pd.DataFrame:
    """
    Return the tail portion used in live card sparklines.
    """
    if close_df is None or close_df.empty:
        return pd.DataFrame(columns=["Date", "Close"])

    out = close_df.tail(points).copy().reset_index(drop=True)
    return out


# =========================================================
# METRIC CALCULATION
# =========================================================
def evaluate_market_series(
    close_df: pd.DataFrame,
    sparkline_points: int,
) -> Dict[str, Any]:
    """
    Compute latest/previous/change/sparkline/average from Date/Close dataframe.
    """
    if close_df is None or close_df.empty or "Close" not in close_df.columns:
        return {
            "latest_value": None,
            "previous_value": None,
            "change_value": None,
            "change_pct": None,
            "reference_period": None,
            "previous_period": None,
            "sparkline_df": pd.DataFrame(columns=["Date", "Close"]),
            "average_value": None,
        }

    closes = close_df["Close"].dropna()
    if closes.empty:
        return {
            "latest_value": None,
            "previous_value": None,
            "change_value": None,
            "change_pct": None,
            "reference_period": None,
            "previous_period": None,
            "sparkline_df": pd.DataFrame(columns=["Date", "Close"]),
            "average_value": None,
        }

    latest_idx = closes.index[-1]
    latest_value = safe_float(closes.loc[latest_idx])

    previous_value = None
    previous_period = None
    if len(closes) >= 2:
        previous_idx = closes.index[-2]
        previous_value = safe_float(closes.loc[previous_idx])
        previous_period = str(pd.to_datetime(close_df.loc[previous_idx, "Date"]).date())

    change_value = None
    change_pct = None
    if latest_value is not None and previous_value is not None:
        change_value = latest_value - previous_value
        if previous_value != 0:
            change_pct = (change_value / previous_value) * 100.0

    reference_period = str(pd.to_datetime(close_df.loc[latest_idx, "Date"]).date())

    sparkline_df = build_sparkline_df(close_df, sparkline_points)
    average_value = safe_float(sparkline_df["Close"].mean()) if not sparkline_df.empty else None

    return {
        "latest_value": latest_value,
        "previous_value": previous_value,
        "change_value": change_value,
        "change_pct": change_pct,
        "reference_period": reference_period,
        "previous_period": previous_period,
        "sparkline_df": sparkline_df,
        "average_value": average_value,
    }


# =========================================================
# INDICATOR RECORD BUILDER
# =========================================================
def make_live_indicator_record(
    indicator_id: str,
    selected_window_label: str = DEFAULT_SPARKLINE_WINDOW,
) -> Dict[str, Any]:
    """
    Build one normalized live market indicator record from config + yfinance.
    """
    if indicator_id not in LIVE_MARKET_CONFIG:
        raise KeyError(f"Missing live market config for '{indicator_id}'.")

    cfg = LIVE_MARKET_CONFIG[indicator_id]
    ticker = cfg["ticker"]

    window_cfg = SPARKLINE_OPTIONS[selected_window_label]
    history_period = window_cfg["period"]
    sparkline_points = window_cfg["points"]

    raw_history = fetch_history(ticker=ticker, period=history_period)
    close_df = build_close_series(
        history_df=raw_history,
        multiplier=cfg.get("multiplier", 1.0),
    )
    metrics = evaluate_market_series(
        close_df=close_df,
        sparkline_points=sparkline_points,
    )

    return {
        "id": indicator_id,
        "title": cfg["title"],
        "ticker": ticker,
        "tag": cfg["tag"],
        "frequency": cfg["frequency"],
        "source": cfg["source"],
        "unit": cfg["unit"],
        "section": cfg["section"],
        "description": cfg.get("description", ""),
        "decimals": cfg.get("decimals", 2),
        "latest_value": metrics["latest_value"],
        "previous_value": metrics["previous_value"],
        "change_value": metrics["change_value"],
        "change_pct": metrics["change_pct"],
        "reference_period": metrics["reference_period"],
        "previous_period": metrics["previous_period"],
        "sparkline_df": metrics["sparkline_df"],
        "average_value": metrics["average_value"],
        "raw_history": raw_history,
        "series": close_df.rename(columns={"Date": "period", "Close": "value"}),
    }


# =========================================================
# BULK LOADERS
# =========================================================
def load_live_market_data(
    selected_window_label: str = DEFAULT_SPARKLINE_WINDOW,
) -> Dict[str, Dict[str, Any]]:
    """
    Load all live indicators defined in LIVE_MARKET_CONFIG.
    """
    return {
        indicator_id: make_live_indicator_record(
            indicator_id=indicator_id,
            selected_window_label=selected_window_label,
        )
        for indicator_id in LIVE_MARKET_CONFIG.keys()
    }


def load_immediate_shock_data(
    selected_window_label: str = DEFAULT_SPARKLINE_WINDOW,
) -> Dict[str, Dict[str, Any]]:
    """
    Load only section=immediate_shock live indicators.
    """
    out = {}
    for indicator_id, cfg in LIVE_MARKET_CONFIG.items():
        if cfg.get("section") == "immediate_shock":
            out[indicator_id] = make_live_indicator_record(
                indicator_id=indicator_id,
                selected_window_label=selected_window_label,
            )
    return out


def load_live_egypt_reaction_market_data(
    selected_window_label: str = DEFAULT_SPARKLINE_WINDOW,
) -> Dict[str, Dict[str, Any]]:
    """
    Load only live indicators used in the Egypt Reaction section.
    """
    out = {}
    for indicator_id, cfg in LIVE_MARKET_CONFIG.items():
        if cfg.get("section") == "egypt_reaction":
            out[indicator_id] = make_live_indicator_record(
                indicator_id=indicator_id,
                selected_window_label=selected_window_label,
            )
    return out


# =========================================================
# ASSEMBLY HELPERS
# =========================================================
def merge_reaction_data(
    live_market_data: Dict[str, Dict[str, Any]],
    official_reaction_data: Dict[str, Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    """
    Merge live and official Egypt reaction indicators into one dictionary.
    Live USD/EGP and EGX30 + official inflation/rates/CONIA.
    """
    out: Dict[str, Dict[str, Any]] = {}
    out.update(live_market_data)
    out.update(official_reaction_data)
    return out