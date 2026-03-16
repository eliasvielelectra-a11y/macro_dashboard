import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt
from datetime import datetime

from cbe_data import fetch_cbe_stats


# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Market Board",
    layout="wide",
)

# =========================================================
# STYLING
# =========================================================
st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1.00rem;
            padding-bottom: 1.35rem;
            max-width: 1450px;
        }

        .section-title {
            font-size: 1.04rem;
            font-weight: 700;
            margin-top: 0.6rem;
            margin-bottom: 0.65rem;
        }

        .market-card {
            border: 1px solid rgba(128, 128, 128, 0.20);
            border-bottom: none;
            border-radius: 14px 14px 0 0;
            padding: 10px 12px 7px 12px;
            min-height: 170px;
            background: transparent;
        }

        .market-name {
            font-size: 0.95rem;
            font-weight: 700;
            margin-bottom: 0.08rem;
        }

        .market-desc {
            font-size: 0.75rem;
            line-height: 1.18;
            color: #6b7280;
            margin-bottom: 0.32rem;
        }

        .market-price {
            font-size: 1.50rem;
            font-weight: 800;
            line-height: 1.02;
            margin-bottom: 0.12rem;
        }

        .market-change {
            font-size: 0.88rem;
            font-weight: 700;
            margin-bottom: 0.01rem;
        }

        .market-change-label {
            font-size: 0.71rem;
            color: #6b7280;
            margin-bottom: 0.06rem;
        }

        .market-period-change {
            font-size: 0.80rem;
            font-weight: 600;
            margin-top: 0.08rem;
            margin-bottom: 0.01rem;
        }

        .market-period-label {
            font-size: 0.71rem;
            color: #6b7280;
            margin-bottom: 0.08rem;
        }

        .market-meta {
            font-size: 0.70rem;
            color: #6b7280;
            line-height: 1.2;
            margin-top: 0.06rem;
        }

        .positive {
            color: #16a34a;
        }

        .negative {
            color: #dc2626;
        }

        .neutral {
            color: #6b7280;
        }

        .chart-wrap {
            border: 1px solid rgba(128, 128, 128, 0.20);
            border-top: none;
            border-radius: 0 0 14px 14px;
            padding: 2px 6px 8px 6px;
            margin-top: 0;
            background: transparent;
        }

        div[data-testid="stTabs"] button {
            font-weight: 600;
        }

        div[data-testid="stHorizontalBlock"] > div {
            align-self: stretch !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# CONFIG
# =========================================================
CACHE_TTL_SECONDS = 4 * 60 * 60
DEFAULT_SPARKLINE_WINDOW = "3 Months"

SPARKLINE_OPTIONS = {
    "3 Months": {"period": "3mo", "points": 60},
    "6 Months": {"period": "6mo", "points": 120},
}

MINISTRY_LOGO_URL = "https://orchtech.com/wp-content/uploads/2021/09/mped-logo-black.png"

DEFAULT_MARKET_SOURCE = "Yahoo Finance via yfinance"
DEFAULT_CBE_SOURCE = "Central Bank of Egypt"

EGX30_TICKER = "^CASE30"
USD_EGP_TICKER = "EGP=X"
EGX30_YTD_ANCHOR = 41828.97

MARKET_GROUPS = {
    "Stock Markets": {
        "US": {
            "VIX": {
                "ticker": "^VIX",
                "decimals": 2,
                "description": "U.S. equity volatility benchmark.",
                "why": "Included as a quick read on market fear and risk appetite.",
                "source": DEFAULT_MARKET_SOURCE,
            },
            "S&P 500": {
                "ticker": "^GSPC",
                "decimals": 2,
                "description": "Broad U.S. large-cap equities.",
                "why": "Included as the main benchmark for U.S. market direction.",
                "source": DEFAULT_MARKET_SOURCE,
            },
            "Dow 30": {
                "ticker": "^DJI",
                "decimals": 2,
                "description": "Blue-chip U.S. industrial stocks.",
                "why": "Included as a simple read on major mature U.S. corporates.",
                "source": DEFAULT_MARKET_SOURCE,
            },
            "Nasdaq": {
                "ticker": "^IXIC",
                "decimals": 2,
                "description": "Tech-heavy U.S. equity benchmark.",
                "why": "Included for growth, tech, and duration-sensitive sentiment.",
                "source": DEFAULT_MARKET_SOURCE,
            },
            "Russell 2000": {
                "ticker": "^RUT",
                "decimals": 2,
                "description": "U.S. small-cap equities.",
                "why": "Included as a read on smaller domestic-facing U.S. firms.",
                "source": DEFAULT_MARKET_SOURCE,
            },
        },
        "Europe": {
            "FTSE 100": {
                "ticker": "^FTSE",
                "decimals": 2,
                "description": "Large listed companies in the UK.",
                "why": "Included as a quick UK large-cap market benchmark.",
                "source": DEFAULT_MARKET_SOURCE,
            },
            "CAC 40": {
                "ticker": "^FCHI",
                "decimals": 2,
                "description": "Leading French equities.",
                "why": "Included to track French and core Euro-area equity tone.",
                "source": DEFAULT_MARKET_SOURCE,
            },
            "DAX": {
                "ticker": "^GDAXI",
                "decimals": 2,
                "description": "Major German listed companies.",
                "why": "Included as a key read on Europe’s industrial core.",
                "source": DEFAULT_MARKET_SOURCE,
            },
            "Euronext 100": {
                "ticker": "^N100",
                "decimals": 2,
                "description": "Large Eurozone listed firms.",
                "why": "Included for a broader cross-country Euro-area view.",
                "source": DEFAULT_MARKET_SOURCE,
            },
        },
        "Asia": {
            "SSE Composite": {
                "ticker": "000001.SS",
                "decimals": 2,
                "description": "Main Shanghai equity benchmark.",
                "why": "Included as a basic read on mainland China equities.",
                "source": DEFAULT_MARKET_SOURCE,
            },
            "Nikkei 225": {
                "ticker": "^N225",
                "decimals": 2,
                "description": "Japanese blue-chip equities.",
                "why": "Included as a flagship benchmark for Japan’s market.",
                "source": DEFAULT_MARKET_SOURCE,
            },
            "Hang Seng": {
                "ticker": "^HSI",
                "decimals": 2,
                "description": "Key Hong Kong market index.",
                "why": "Included for Hong Kong and China-linked market sentiment.",
                "source": DEFAULT_MARKET_SOURCE,
            },
            "Asia Dow": {
                "ticker": "^AXDJ",
                "decimals": 2,
                "description": "Regional Asia-Pacific blue-chip basket.",
                "why": "Included for a broader regional Asia-Pacific snapshot.",
                "source": DEFAULT_MARKET_SOURCE,
            },
        },
    },
    "Bitcoin": {
        "Crypto": {
            "Bitcoin": {
                "ticker": "BTC-USD",
                "decimals": 2,
                "description": "Largest cryptocurrency by market value.",
                "why": "Included as the headline crypto risk asset.",
                "source": DEFAULT_MARKET_SOURCE,
            },
            "Ethereum": {
                "ticker": "ETH-USD",
                "decimals": 2,
                "description": "Major smart-contract crypto asset.",
                "why": "Included as a second major crypto benchmark.",
                "source": DEFAULT_MARKET_SOURCE,
            },
        }
    },
    "Rates": {
        "US Rates": {
            "MOVE Index": {
                "ticker": "^MOVE",
                "decimals": 2,
                "description": "U.S. Treasury volatility benchmark.",
                "why": "Included to track stress and volatility in rates markets.",
                "source": DEFAULT_MARKET_SOURCE,
            },
            "13-Week Bond": {
                "ticker": "^IRX",
                "decimals": 2,
                "multiplier": 10,
                "description": "Short-end U.S. Treasury yield.",
                "why": "Included as a quick read on the front end of the curve.",
                "source": DEFAULT_MARKET_SOURCE,
            },
            "5-Year Bond": {
                "ticker": "^FVX",
                "decimals": 2,
                "multiplier": 10,
                "description": "Intermediate U.S. Treasury yield.",
                "why": "Included to track medium-term rate expectations.",
                "source": DEFAULT_MARKET_SOURCE,
            },
            "10-Year Bond": {
                "ticker": "^TNX",
                "decimals": 2,
                "multiplier": 10,
                "description": "Benchmark U.S. Treasury yield.",
                "why": "Included as the core global long-rate reference.",
                "source": DEFAULT_MARKET_SOURCE,
            },
            "30-Year Bond": {
                "ticker": "^TYX",
                "decimals": 2,
                "multiplier": 10,
                "description": "Long-end U.S. Treasury yield.",
                "why": "Included to watch long-duration bond market pressure.",
                "source": DEFAULT_MARKET_SOURCE,
            },
        }
    },
    "Currencies": {
        "FX": {
            "DXY": {
                "ticker": "^NYICDX",
                "decimals": 2,
                "description": "U.S. dollar against major peers.",
                "why": "Included as a standard broad-dollar barometer.",
                "source": DEFAULT_MARKET_SOURCE,
            },
            "EUR/USD": {
                "ticker": "EURUSD=X",
                "decimals": 4,
                "description": "Euro-dollar exchange rate.",
                "why": "Included as the world’s most-watched major FX pair.",
                "source": DEFAULT_MARKET_SOURCE,
            },
            "USD/JPY": {
                "ticker": "JPY=X",
                "decimals": 3,
                "description": "Dollar-yen exchange rate.",
                "why": "Included as a key macro and rates-sensitive FX pair.",
                "source": DEFAULT_MARKET_SOURCE,
            },
        }
    },
    "Commodities": {
        "Commodities": {
            "Brent Crude Oil": {
                "ticker": "BZ=F",
                "decimals": 2,
                "description": "Global oil benchmark.",
                "why": "Included as the main global crude reference.",
                "source": DEFAULT_MARKET_SOURCE,
            },
            "Gold": {
                "ticker": "GC=F",
                "decimals": 2,
                "description": "Traditional safe-haven metal.",
                "why": "Included as a classic defensive asset gauge.",
                "source": DEFAULT_MARKET_SOURCE,
            },
            "Silver": {
                "ticker": "SI=F",
                "decimals": 2,
                "description": "Precious metal with industrial uses.",
                "why": "Included for both precious-metal and industrial demand tone.",
                "source": DEFAULT_MARKET_SOURCE,
            },
            "Copper": {
                "ticker": "HG=F",
                "decimals": 3,
                "description": "Industrial metal tied to growth.",
                "why": "Included as a rough global activity signal.",
                "source": DEFAULT_MARKET_SOURCE,
            },
            "Natural Gas": {
                "ticker": "NG=F",
                "decimals": 3,
                "description": "Key global energy commodity.",
                "why": "Included to monitor energy-market swings beyond oil.",
                "source": DEFAULT_MARKET_SOURCE,
            },
            "Wheat": {
                "ticker": "ZW=F",
                "decimals": 2,
                "description": "Major global grain benchmark.",
                "why": "Included as a simple read on food commodity pressure.",
                "source": DEFAULT_MARKET_SOURCE,
            },
        }
    },
}

EGYPT_MACRO_CONFIG = {
    "Overnight Deposit Rate": {
        "key": "overnight_deposit_rate",
        "decimals": 2,
        "description": "CBE policy corridor floor.",
        "why": "Included as a core read on monetary-policy stance.",
        "ticker_label": "Official CBE statistic",
        "source": DEFAULT_CBE_SOURCE,
    },
    "Overnight Lending Rate": {
        "key": "overnight_lending_rate",
        "decimals": 2,
        "description": "CBE policy corridor ceiling.",
        "why": "Included to track the upper bound of the policy corridor.",
        "ticker_label": "Official CBE statistic",
        "source": DEFAULT_CBE_SOURCE,
    },
    "Main Operation": {
        "key": "main_operation",
        "decimals": 2,
        "description": "Main policy operation rate.",
        "why": "Included as the central operating policy reference.",
        "ticker_label": "Official CBE statistic",
        "source": DEFAULT_CBE_SOURCE,
    },
    "CONIA": {
        "key": "conia",
        "decimals": 3,
        "description": "Cairo overnight interbank average.",
        "why": "Included as the live money-market reference.",
        "ticker_label": "Official CBE statistic",
        "source": DEFAULT_CBE_SOURCE,
    },
    "Core Inflation": {
        "key": "core_inflation_rate",
        "decimals": 3,
        "description": "Underlying inflation excluding volatile items.",
        "why": "Included to track the underlying inflation trend.",
        "ticker_label": "Official CBE statistic",
        "source": DEFAULT_CBE_SOURCE,
    },
    "Headline Inflation": {
        "key": "headline_inflation_rate",
        "decimals": 3,
        "description": "Broad consumer inflation rate.",
        "why": "Included as the main inflation pulse.",
        "ticker_label": "Official CBE statistic",
        "source": DEFAULT_CBE_SOURCE,
    },
    "EGX30": {
        "ticker": EGX30_TICKER,
        "decimals": 2,
        "description": "Main Egyptian equity benchmark.",
        "why": "Included as a quick read on domestic market sentiment.",
        "source": DEFAULT_MARKET_SOURCE,
    },
    "USD/EGP": {
        "ticker": USD_EGP_TICKER,
        "decimals": 4,
        "description": "Egyptian pound per U.S. dollar.",
        "why": "Included as a basic read on FX conditions.",
        "source": DEFAULT_MARKET_SOURCE,
    },
}

# =========================================================
# HELPERS
# =========================================================
def format_value(value, decimals=2):
    if value is None or pd.isna(value):
        return "N/A"
    return f"{value:,.{decimals}f}"


def normalize_history(df):
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


def collect_unique_tickers(groups):
    tickers = []
    for sections in groups.values():
        for instruments in sections.values():
            for meta in instruments.values():
                ticker = meta.get("ticker")
                if ticker:
                    tickers.append(ticker)
    return sorted(set(tickers))


@st.cache_data(ttl=CACHE_TTL_SECONDS)
def fetch_history(ticker, period):
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


def transform_close_series(df, multiplier=1.0):
    if df.empty or "Close" not in df.columns:
        return pd.DataFrame()

    out = df[["Close"]].copy()

    if multiplier and multiplier != 1:
        out["Close"] = out["Close"] * multiplier

    return out.dropna()


def evaluate_ticker(df, sparkline_points):
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


def evaluate_egx30_ytd(df, anchor_value):
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


def get_delta_class(change):
    if change is None or pd.isna(change):
        return "neutral"
    if change > 0:
        return "positive"
    if change < 0:
        return "negative"
    return "neutral"


def get_day_label(change):
    if change is None or pd.isna(change):
        return "Flat / unavailable on the day"
    if change > 0:
        return "Up on the day"
    if change < 0:
        return "Down on the day"
    return "Flat on the day"


def build_sparkline(chart_df, positive, average_value):
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
                    scale=alt.Scale(domain=[y_min, y_max], zero=False)
                )
            )
        )
        layers.append(avg_line)

    return alt.layer(*layers).properties(height=125)


def render_market_card(name, meta, result, sparkline_window_label):
    decimals = meta.get("decimals", 2)
    latest = result["latest"]
    change = result["change"]
    change_pct = result["change_pct"]
    period_change = result["period_change"]
    period_change_pct = result["period_change_pct"]

    description = meta.get("description", "")
    why = meta.get("why", "")
    subtitle = description if not why else f"{description} · {why}"
    ticker_text = meta.get("ticker", "N/A")
    source_text = meta.get("source", DEFAULT_MARKET_SOURCE)

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
                <div class="market-meta">Ticker: {ticker_text}</div>
                <div class="market-meta">Source: {source_text}</div>
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
            <div class="market-meta">Ticker: {ticker_text}</div>
            <div class="market-meta">Source: {source_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
    chart = build_sparkline(
        chart_df=result["sparkline"],
        positive=spark_positive,
        average_value=result["average"],
    )
    if chart is not None:
        st.altair_chart(chart, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


def render_cbe_stat_card(name, meta, cbe_stats):
    value = cbe_stats.get(meta["key"])
    subtitle = f"{meta['description']} · {meta['why']}"
    ticker_text = meta.get("ticker_label", "Official CBE statistic")
    source_text = meta.get("source", DEFAULT_CBE_SOURCE)

    display_value = "N/A" if value is None else f"{float(value):,.{meta['decimals']}f}%"

    st.markdown(
        f"""
        <div class="market-card" style="border-bottom: 1px solid rgba(128, 128, 128, 0.20); border-radius: 14px;">
            <div class="market-name">{name}</div>
            <div class="market-desc">{subtitle}</div>
            <div class="market-price">{display_value}</div>
            <div class="market-change-label">Official CBE statistic</div>
            <div class="market-meta">Ticker: {ticker_text}</div>
            <div class="market-meta">Source: {source_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_egx30_ytd_card(raw_df, sparkline_points, sparkline_window_label):
    meta = EGYPT_MACRO_CONFIG["EGX30"]
    market_eval = evaluate_ticker(normalize_history(raw_df), sparkline_points=sparkline_points)
    ytd_eval = evaluate_egx30_ytd(raw_df, anchor_value=EGX30_YTD_ANCHOR)

    subtitle = f"{meta['description']} · {meta['why']}"
    latest = ytd_eval["latest"]
    ytd_change_pct = ytd_eval["ytd_change_pct"]
    anchor_value = ytd_eval["anchor_value"]
    period_change = market_eval["period_change"]
    period_change_pct = market_eval["period_change_pct"]

    if latest is None:
        st.markdown(
            f"""
            <div class="market-card">
                <div class="market-name">EGX30</div>
                <div class="market-desc">{subtitle}</div>
                <div class="market-price">N/A</div>
                <div class="market-change neutral">N/A</div>
                <div class="market-change-label">YTD move</div>
                <div class="market-period-change neutral">N/A</div>
                <div class="market-period-label">{sparkline_window_label} change</div>
                <div class="market-meta">Ticker: {meta['ticker']}</div>
                <div class="market-meta">Source: {meta['source']}</div>
            </div>
            <div class="chart-wrap"></div>
            """,
            unsafe_allow_html=True,
        )
        return

    ytd_class = get_delta_class(ytd_change_pct)
    ytd_text = "N/A" if ytd_change_pct is None else f"{ytd_change_pct:+.2f}%"
    ytd_label = f"YTD move · anchor {anchor_value:,.2f}"

    period_class = get_delta_class(period_change)
    if period_change is None or period_change_pct is None:
        period_text = "N/A"
        spark_positive = None
    else:
        period_text = f"{period_change:+,.2f} ({period_change_pct:+.2f}%)"
        spark_positive = period_change >= 0

    st.markdown(
        f"""
        <div class="market-card">
            <div class="market-name">EGX30</div>
            <div class="market-desc">{subtitle}</div>
            <div class="market-price">{format_value(latest, meta['decimals'])}</div>
            <div class="market-change {ytd_class}">{ytd_text}</div>
            <div class="market-change-label">{ytd_label}</div>
            <div class="market-period-change {period_class}">{period_text}</div>
            <div class="market-period-label">{sparkline_window_label} change</div>
            <div class="market-meta">Ticker: {meta['ticker']}</div>
            <div class="market-meta">Source: {meta['source']}</div>
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


def render_usd_egp_card(raw_df, sparkline_points, sparkline_window_label):
    meta = EGYPT_MACRO_CONFIG["USD/EGP"]
    result = evaluate_ticker(normalize_history(raw_df), sparkline_points=sparkline_points)
    render_market_card("USD/EGP", meta, result, sparkline_window_label)


def render_instrument_grid(instruments, data_store, sparkline_points, sparkline_window_label):
    items = list(instruments.items())

    for i in range(0, len(items), 3):
        row = items[i:i + 3]
        cols = st.columns(3, gap="medium")

        for col, (name, meta) in zip(cols, row):
            with col:
                raw_df = data_store.get(meta["ticker"], pd.DataFrame())
                multiplier = meta.get("multiplier", 1)
                df = transform_close_series(raw_df, multiplier=multiplier)
                result = evaluate_ticker(df, sparkline_points=sparkline_points)
                render_market_card(name, meta, result, sparkline_window_label)


def render_egypt_macro_tab(data_store, sparkline_points, sparkline_window_label):
    cbe_result = fetch_cbe_stats()
    cbe_stats = cbe_result.stats

    st.markdown("<div class='section-title'>Policy & Inflation</div>", unsafe_allow_html=True)

    policy_names = [
        "Overnight Deposit Rate",
        "Overnight Lending Rate",
        "Main Operation",
        "CONIA",
        "Core Inflation",
        "Headline Inflation",
    ]

    for i in range(0, len(policy_names), 3):
        row_names = policy_names[i:i + 3]
        cols = st.columns(3, gap="medium")
        for col, name in zip(cols, row_names):
            with col:
                render_cbe_stat_card(name, EGYPT_MACRO_CONFIG[name], cbe_stats)

    st.markdown("")
    st.markdown("<div class='section-title'>Markets</div>", unsafe_allow_html=True)

    egx30_df = data_store.get(EGX30_TICKER, pd.DataFrame())
    usd_egp_df = data_store.get(USD_EGP_TICKER, pd.DataFrame())

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
    st.markdown("<div class='section-title'>Source & Notes</div>", unsafe_allow_html=True)
    st.caption("Official Egypt policy, CONIA, and inflation statistics: Central Bank of Egypt.")
    st.caption("EGX30 and USD/EGP: convenience market data via Yahoo Finance / yfinance.")
    st.caption(f"CBE fetch status: {cbe_result.fetch_status}")
    if cbe_result.notes:
        for note in cbe_result.notes:
            st.caption("Note: " + note)

# =========================================================
# SIDEBAR CONTROLS
# =========================================================
st.sidebar.header("Controls")

sparkline_window_label = st.sidebar.selectbox(
    "Sparkline window",
    options=list(SPARKLINE_OPTIONS.keys()),
    index=list(SPARKLINE_OPTIONS.keys()).index(DEFAULT_SPARKLINE_WINDOW),
)

if st.sidebar.button("Refresh"):
    st.cache_data.clear()
    st.rerun()

selected_period = SPARKLINE_OPTIONS[sparkline_window_label]["period"]
selected_points = SPARKLINE_OPTIONS[sparkline_window_label]["points"]

st.sidebar.markdown("---")
st.sidebar.subheader("Source Guide")
st.sidebar.caption("Egypt policy, CONIA, and inflation: Central Bank of Egypt.")
st.sidebar.caption("Market prices and benchmarks: Yahoo Finance via yfinance.")

st.sidebar.subheader("Licensing & Use")
st.sidebar.caption("Internal monitoring and briefing support.")
st.sidebar.caption("Market series are convenience data unless moved to a licensed institutional feed.")
st.sidebar.caption("Verify official figures before formal circulation or publication.")

st.sidebar.subheader("Branding Note")
st.sidebar.caption("Ministry of Planning logo displayed for internal dashboard context.")

# =========================================================
# DATA LOAD
# =========================================================
all_tickers = collect_unique_tickers(MARKET_GROUPS)
all_tickers = sorted(set(all_tickers + [EGX30_TICKER, USD_EGP_TICKER]))
data_store = {ticker: fetch_history(ticker, selected_period) for ticker in all_tickers}

# =========================================================
# HEADER
# =========================================================
header_left, header_right = st.columns([6, 1])

with header_left:
    st.title("Market Board")
    st.caption(
        f"Last refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M')} · "
        f"Sparkline: rolling {sparkline_window_label.lower()} · "
        "Dashed line: period average · "
        "Colored daily number: up/down on the day"
    )

with header_right:
    st.image(MINISTRY_LOGO_URL, width=150)

st.markdown("")

# =========================================================
# TABS
# =========================================================
tab_names = ["Egypt Macro"] + list(MARKET_GROUPS.keys())
tabs = st.tabs(tab_names)

with tabs[0]:
    render_egypt_macro_tab(
        data_store=data_store,
        sparkline_points=selected_points,
        sparkline_window_label=sparkline_window_label,
    )

for tab_obj, tab_name in zip(tabs[1:], list(MARKET_GROUPS.keys())):
    with tab_obj:
        for section_name, instruments in MARKET_GROUPS[tab_name].items():
            st.markdown(f"<div class='section-title'>{section_name}</div>", unsafe_allow_html=True)
            render_instrument_grid(
                instruments=instruments,
                data_store=data_store,
                sparkline_points=selected_points,
                sparkline_window_label=sparkline_window_label,
            )
            st.markdown("")