from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st
import altair as alt

from cbe_data import fetch_cbe_stats


EGX30_TICKER = "^CASE30"
USD_EGP_TICKER = "EGP=X"

# Replace this with your chosen year-start anchor for EGX30.
EGX30_YTD_ANCHOR = 41828.97

EGYPT_MACRO_CARD_ORDER = [
    "overnight_deposit_rate",
    "overnight_lending_rate",
    "main_operation",
    "conia",
    "core_inflation_rate",
    "headline_inflation_rate",
    "inflation_target_text",
]

EGYPT_MACRO_META = {
    "overnight_deposit_rate": {
        "label": "Overnight Deposit Rate",
        "description": "CBE policy corridor floor.",
        "why": "Included as a core read on monetary-policy stance.",
        "display_type": "percent",
        "decimals": 2,
    },
    "overnight_lending_rate": {
        "label": "Overnight Lending Rate",
        "description": "CBE policy corridor ceiling.",
        "why": "Included to track the upper bound of the policy corridor.",
        "display_type": "percent",
        "decimals": 2,
    },
    "main_operation": {
        "label": "Main Operation",
        "description": "Main policy operation rate.",
        "why": "Included as the central operating policy reference.",
        "display_type": "percent",
        "decimals": 2,
    },
    "conia": {
        "label": "CONIA",
        "description": "Cairo overnight interbank average.",
        "why": "Included as the live money-market reference.",
        "display_type": "percent",
        "decimals": 3,
    },
    "core_inflation_rate": {
        "label": "Core Inflation",
        "description": "Underlying inflation excluding volatile items.",
        "why": "Included to track the underlying inflation trend.",
        "display_type": "percent",
        "decimals": 3,
    },
    "headline_inflation_rate": {
        "label": "Headline Inflation",
        "description": "Broad consumer inflation rate.",
        "why": "Included as the main inflation pulse.",
        "display_type": "percent",
        "decimals": 3,
    },
    "inflation_target_text": {
        "label": "Inflation Target",
        "description": "CBE stated target.",
        "why": "Included as the benchmark for inflation convergence.",
        "display_type": "text",
        "decimals": None,
    },
    "egx30_ytd": {
        "label": "EGX30",
        "description": "Main Egyptian equity benchmark.",
        "why": "Included as a quick read on domestic market sentiment.",
        "display_type": "market_ytd",
        "decimals": 2,
    },
    "usd_egp": {
        "label": "USD/EGP",
        "description": "Egyptian pound per U.S. dollar.",
        "why": "Included as a basic read on FX conditions.",
        "display_type": "market_daily",
        "decimals": 4,
    },
}


def format_value(value: float | None, decimals: int = 2) -> str:
    if value is None or pd.isna(value):
        return "N/A"
    return f"{value:,.{decimals}f}"


def normalize_history(df: pd.DataFrame) -> pd.DataFrame:
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


def transform_close_series(df: pd.DataFrame, multiplier: float = 1.0) -> pd.DataFrame:
    if df.empty or "Close" not in df.columns:
        return pd.DataFrame()

    out = df[["Close"]].copy()

    if multiplier and multiplier != 1:
        out["Close"] = out["Close"] * multiplier

    return out.dropna()


def evaluate_market_ticker(df: pd.DataFrame, sparkline_points: int) -> dict[str, Any]:
    if df.empty or "Close" not in df.columns:
        return {
            "latest": None,
            "change": None,
            "change_pct": None,
            "period_change": None,
            "period_change_pct": None,
            "sparkline": pd.DataFrame(),
            "average": None,
        }

    closes = df["Close"].dropna()

    if closes.empty:
        return {
            "latest": None,
            "change": None,
            "change_pct": None,
            "period_change": None,
            "period_change_pct": None,
            "sparkline": pd.DataFrame(),
            "average": None,
        }

    latest = float(closes.iloc[-1])
    previous = float(closes.iloc[-2]) if len(closes) >= 2 else None

    if previous is not None:
        change = latest - previous
        change_pct = (change / previous * 100) if previous != 0 else None
    else:
        change = None
        change_pct = None

    spark = closes.tail(sparkline_points).reset_index()
    spark.columns = ["Date", "Close"]

    if len(spark) >= 2:
        period_start = float(spark["Close"].iloc[0])
        period_end = float(spark["Close"].iloc[-1])
        period_change = period_end - period_start
        period_change_pct = (period_change / period_start * 100) if period_start != 0 else None
    else:
        period_change = None
        period_change_pct = None

    average = float(spark["Close"].mean()) if not spark.empty else None

    return {
        "latest": latest,
        "change": change,
        "change_pct": change_pct,
        "period_change": period_change,
        "period_change_pct": period_change_pct,
        "sparkline": spark,
        "average": average,
    }


def evaluate_egx30_ytd(raw_df: pd.DataFrame, anchor_value: float = EGX30_YTD_ANCHOR) -> dict[str, Any]:
    df = normalize_history(raw_df)

    if df.empty or "Close" not in df.columns:
        return {
            "latest": None,
            "ytd_change_pct": None,
            "anchor_value": anchor_value,
        }

    closes = df["Close"].dropna()

    if closes.empty:
        return {
            "latest": None,
            "ytd_change_pct": None,
            "anchor_value": anchor_value,
        }

    latest = float(closes.iloc[-1])

    if anchor_value and anchor_value != 0:
        ytd_change_pct = ((latest - anchor_value) / anchor_value) * 100
    else:
        ytd_change_pct = None

    return {
        "latest": latest,
        "ytd_change_pct": ytd_change_pct,
        "anchor_value": anchor_value,
    }


def get_delta_class(change: float | None) -> str:
    if change is None or pd.isna(change):
        return "neutral"
    if change > 0:
        return "positive"
    if change < 0:
        return "negative"
    return "neutral"


def get_day_label(change: float | None) -> str:
    if change is None or pd.isna(change):
        return "Flat / unavailable on the day"
    if change > 0:
        return "Up on the day"
    if change < 0:
        return "Down on the day"
    return "Flat on the day"


def build_sparkline(chart_df: pd.DataFrame, positive: bool | None, average_value: float | None):
    if chart_df is None or chart_df.empty:
        return None

    line_color = "#16a34a" if positive else "#dc2626"
    if positive is None:
        line_color = "#6b7280"

    y_min = float(chart_df["Close"].min())
    y_max = float(chart_df["Close"].max())

    if average_value is not None:
        y_min = min(y_min, average_value)
        y_max = max(y_max, average_value)

    if y_min == y_max:
        y_min -= 1
        y_max += 1
    else:
        pad = (y_max - y_min) * 0.14
        y_min -= pad
        y_max += pad

    price_line = (
        alt.Chart(chart_df)
        .mark_line(strokeWidth=2.2, color=line_color)
        .encode(
            x=alt.X("Date:T", axis=None),
            y=alt.Y(
                "Close:Q",
                axis=None,
                scale=alt.Scale(domain=[y_min, y_max], zero=False),
            ),
            tooltip=[
                alt.Tooltip("Date:T", title="Date"),
                alt.Tooltip("Close:Q", title="Close", format=",.4f"),
            ],
        )
    )

    layers = [price_line]

    if average_value is not None:
        avg_df = pd.DataFrame({"Average": [average_value]})
        avg_line = (
            alt.Chart(avg_df)
            .mark_rule(strokeDash=[4, 4], color="#9ca3af", strokeWidth=1.1)
            .encode(
                y=alt.Y(
                    "Average:Q",
                    scale=alt.Scale(domain=[y_min, y_max], zero=False),
                )
            )
        )
        layers.append(avg_line)

    return alt.layer(*layers).properties(height=125)


def render_market_card(
    name: str,
    description: str,
    why: str,
    latest: float | None,
    change: float | None,
    change_pct: float | None,
    period_change: float | None,
    period_change_pct: float | None,
    sparkline_df: pd.DataFrame,
    average_value: float | None,
    sparkline_window_label: str,
    decimals: int = 2,
):
    subtitle = description if not why else f"{description} · {why}"

    if latest is None:
        st.markdown(
            f"""
            <div class="market-card">
                <div class="market-name">{name}</div>
                <div class="market-desc">{subtitle}</div>
                <div class="market-price">N/A</div>
                <div class="market-change neutral">N/A</div>
                <div class="market-change-label">Daily move</div>
                <div class="market-period-change neutral">N/A</div>
                <div class="market-period-label">{sparkline_window_label} change</div>
            </div>
            <div class="chart-wrap"></div>
            """,
            unsafe_allow_html=True,
        )
        return

    delta_class = get_delta_class(change)
    period_class = get_delta_class(period_change)
    day_label = get_day_label(change)

    if change is None or change_pct is None:
        change_text = "N/A"
        spark_positive = None
    else:
        change_text = f"{change:+,.{decimals}f} ({change_pct:+.2f}%)"
        spark_positive = change >= 0

    if period_change is None or period_change_pct is None:
        period_change_text = "N/A"
    else:
        period_change_text = f"{period_change:+,.{decimals}f} ({period_change_pct:+.2f}%)"

    st.markdown(
        f"""
        <div class="market-card">
            <div class="market-name">{name}</div>
            <div class="market-desc">{subtitle}</div>
            <div class="market-price">{format_value(latest, decimals)}</div>
            <div class="market-change {delta_class}">{change_text}</div>
            <div class="market-change-label">{day_label}</div>
            <div class="market-period-change {period_class}">{period_change_text}</div>
            <div class="market-period-label">{sparkline_window_label} change</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
    chart = build_sparkline(
        chart_df=sparkline_df,
        positive=spark_positive,
        average_value=average_value,
    )
    if chart is not None:
        st.altair_chart(chart, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


def render_egx30_ytd_card(raw_df: pd.DataFrame, sparkline_points: int, sparkline_window_label: str):
    meta = EGYPT_MACRO_META["egx30_ytd"]
    market_eval = evaluate_market_ticker(normalize_history(raw_df), sparkline_points=sparkline_points)
    ytd_eval = evaluate_egx30_ytd(raw_df, anchor_value=EGX30_YTD_ANCHOR)

    description = meta["description"]
    why = meta["why"]
    subtitle = f"{description} · {why}"

    latest = ytd_eval["latest"]
    ytd_change_pct = ytd_eval["ytd_change_pct"]
    anchor_value = ytd_eval["anchor_value"]

    if latest is None:
        st.markdown(
            f"""
            <div class="market-card">
                <div class="market-name">{meta['label']}</div>
                <div class="market-desc">{subtitle}</div>
                <div class="market-price">N/A</div>
                <div class="market-change neutral">N/A</div>
                <div class="market-change-label">YTD move</div>
                <div class="market-period-change neutral">N/A</div>
                <div class="market-period-label">{sparkline_window_label} change</div>
            </div>
            <div class="chart-wrap"></div>
            """,
            unsafe_allow_html=True,
        )
        return

    ytd_class = get_delta_class(ytd_change_pct)
    if ytd_change_pct is None:
        ytd_text = "N/A"
        ytd_label = "YTD move"
    else:
        ytd_text = f"{ytd_change_pct:+.2f}%"
        ytd_label = f"YTD move · anchor {anchor_value:,.2f}"

    period_change = market_eval["period_change"]
    period_change_pct = market_eval["period_change_pct"]
    period_class = get_delta_class(period_change)

    if period_change is None or period_change_pct is None:
        period_text = "N/A"
    else:
        period_text = f"{period_change:+,.2f} ({period_change_pct:+.2f}%)"

    spark_positive = None if period_change is None else period_change >= 0

    st.markdown(
        f"""
        <div class="market-card">
            <div class="market-name">{meta['label']}</div>
            <div class="market-desc">{subtitle}</div>
            <div class="market-price">{format_value(latest, meta['decimals'])}</div>
            <div class="market-change {ytd_class}">{ytd_text}</div>
            <div class="market-change-label">{ytd_label}</div>
            <div class="market-period-change {period_class}">{period_text}</div>
            <div class="market-period-label">{sparkline_window_label} change</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
    chart = build_sparkline(
        chart_df=market_eval["sparkline"],
        positive=spark_positive,
        average_value=market_eval["average"],
    )
    if chart is not None:
        st.altair_chart(chart, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


def render_usd_egp_card(raw_df: pd.DataFrame, sparkline_points: int, sparkline_window_label: str):
    meta = EGYPT_MACRO_META["usd_egp"]
    market_eval = evaluate_market_ticker(normalize_history(raw_df), sparkline_points=sparkline_points)

    render_market_card(
        name=meta["label"],
        description=meta["description"],
        why=meta["why"],
        latest=market_eval["latest"],
        change=market_eval["change"],
        change_pct=market_eval["change_pct"],
        period_change=market_eval["period_change"],
        period_change_pct=market_eval["period_change_pct"],
        sparkline_df=market_eval["sparkline"],
        average_value=market_eval["average"],
        sparkline_window_label=sparkline_window_label,
        decimals=meta["decimals"],
    )


def render_cbe_stat_card(key: str, stats: dict[str, Any]):
    meta = EGYPT_MACRO_META[key]
    value = stats.get(key)
    subtitle = f"{meta['description']} · {meta['why']}"

    if meta["display_type"] == "text":
        display_value = value if value else "N/A"
    elif value is None:
        display_value = "N/A"
    else:
        display_value = f"{float(value):,.{meta['decimals']}f}%"

    st.markdown(
        f"""
        <div class="market-card" style="border-bottom: 1px solid rgba(128, 128, 128, 0.20); border-radius: 14px;">
            <div class="market-name">{meta['label']}</div>
            <div class="market-desc">{subtitle}</div>
            <div class="market-price">{display_value}</div>
            <div class="market-change-label">Official CBE statistic</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_egypt_macro_tab(
    fetch_history_func,
    selected_period: str,
    sparkline_points: int,
    sparkline_window_label: str,
):
    cbe_result = fetch_cbe_stats()
    cbe_stats = cbe_result.stats

    egx30_df = fetch_history_func(EGX30_TICKER, selected_period)
    usd_egp_df = fetch_history_func(USD_EGP_TICKER, selected_period)

    st.markdown("<div class='section-title'>Policy & Inflation</div>", unsafe_allow_html=True)

    policy_keys = EGYPT_MACRO_CARD_ORDER
    for i in range(0, len(policy_keys), 3):
        row_keys = policy_keys[i:i + 3]
        cols = st.columns(3, gap="medium")
        for col, key in zip(cols, row_keys):
            with col:
                render_cbe_stat_card(key, cbe_stats)

    st.markdown("")
    st.markdown("<div class='section-title'>Markets</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="medium")
    with col1:
        render_egx30_ytd_card(
            raw_df=egx30_df,
            sparkline_points=sparkline_points,
            sparkline_window_label=sparkline_window_label,
        )
    with col2:
        render_usd_egp_card(
            raw_df=usd_egp_df,
            sparkline_points=sparkline_points,
            sparkline_window_label=sparkline_window_label,
        )

    st.markdown("")
    st.markdown("<div class='section-title'>Source & Usage</div>", unsafe_allow_html=True)
    st.caption("Official Egypt policy, CONIA, inflation, and target: Central Bank of Egypt.")
    st.caption("EGX30 and USD/EGP: convenience market data via Yahoo Finance / yfinance.")
    st.caption("Internal monitoring and briefing support only. Verify before formal circulation.")
    st.caption("CBE source: " + cbe_result.source_label)
    st.caption("CBE URL: " + cbe_result.source_url)
    st.caption("CBE fetch status: " + cbe_result.fetch_status)

    if cbe_result.notes:
        for note in cbe_result.notes:
            st.caption("Note: " + note)