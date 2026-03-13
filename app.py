import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt
from datetime import datetime

st.set_page_config(
    page_title="Macro Indicators and Risk Identification Dashboard",
    layout="wide"
)

# ===================================================
# CONFIGURATION
# ===================================================
WINDOW_OPTIONS = {
    "1 Month": {"lookback": 21},
    "3 Months": {"lookback": 63},
    "6 Months": {"lookback": 126},
    "1 Year": {"lookback": 252},
}

MAX_FETCH_PERIOD = "2y"
DEFAULT_STALE_THRESHOLD_BDAYS = 3
APP_CACHE_VERSION = "v2_critical_upgrades"

RISK_BADGES = {
    "Normal": "🟢 Normal",
    "Watch": "🟠 Watch",
    "Elevated": "🔴 Elevated",
    "Unrated": "⚪ Unrated",
    "No signal": "⚪ No signal",
}

RISK_ORDER = {
    "Normal": 0,
    "Watch": 1,
    "Elevated": 2,
}

# ===================================================
# INDICATOR CONFIG
# ===================================================
STOCK_MARKETS_EGYPT = {
    "EGX30": {
        "ticker": "^CASE30",
        "unit": "index points",
        "decimals": 2,
        "show_chart": False,
        "show_delta": False,
        "special_mode": "egx30_auto_ytd",
        "description": "Broad benchmark for the Egyptian stock market.",
        "source": "Yahoo Finance via yfinance",
        "source_type": "Convenience market data",
        "risk_note": "A weaker EGX30 can signal softer domestic market sentiment and tighter local risk appetite.",
        "risk_rules": {
            "metric": "ytd_pct",
            "direction": "lower_is_riskier",
            "amber": -3.0,
            "red": -8.0,
        },
    },
    "Commercial International Bank (CIB)": {
        "ticker": "COMI.CA",
        "unit": "EGP per share",
        "decimals": 2,
        "show_chart": True,
        "show_delta": True,
        "description": "Largest listed Egyptian bank and a major driver of EGX30 sentiment.",
        "source": "Yahoo Finance via yfinance",
        "source_type": "Convenience market data",
        "risk_note": "CIB is often a quick read on local equity sentiment and perceptions of financial-sector strength.",
        "risk_rules": {
            "metric": "delta_pct",
            "direction": "lower_is_riskier",
            "amber": -5.0,
            "red": -10.0,
        },
    },
}

STOCK_MARKETS_US = {
    "S&P 500": {
        "ticker": "^GSPC",
        "unit": "index points",
        "decimals": 2,
        "show_chart": True,
        "show_delta": True,
        "description": "Large-cap U.S. equities.",
        "source": "Yahoo Finance via yfinance",
        "source_type": "Convenience market data",
        "risk_note": "Broad U.S. equity weakness can signal worsening global risk sentiment.",
        "risk_rules": {
            "metric": "delta_pct",
            "direction": "lower_is_riskier",
            "amber": -3.0,
            "red": -7.0,
        },
    },
    "Dow Jones": {
        "ticker": "^DJI",
        "unit": "index points",
        "decimals": 2,
        "show_chart": True,
        "show_delta": True,
        "description": "Blue-chip U.S. equities.",
        "source": "Yahoo Finance via yfinance",
        "source_type": "Convenience market data",
        "risk_note": "Blue-chip weakness can reinforce broader concerns around global growth and risk appetite.",
        "risk_rules": {
            "metric": "delta_pct",
            "direction": "lower_is_riskier",
            "amber": -3.0,
            "red": -7.0,
        },
    },
}

STOCK_MARKETS_EUROPE = {
    "DAX": {
        "ticker": "^GDAXI",
        "unit": "index points",
        "decimals": 2,
        "show_chart": True,
        "show_delta": True,
        "description": "Leading German equities.",
        "source": "Yahoo Finance via yfinance",
        "source_type": "Convenience market data",
        "risk_note": "European equity weakness can point to softer industrial demand and external headwinds.",
        "risk_rules": {
            "metric": "delta_pct",
            "direction": "lower_is_riskier",
            "amber": -3.0,
            "red": -7.0,
        },
    },
    "FTSE 100": {
        "ticker": "^FTSE",
        "unit": "index points",
        "decimals": 2,
        "show_chart": True,
        "show_delta": True,
        "description": "Major listed companies in the UK market.",
        "source": "Yahoo Finance via yfinance",
        "source_type": "Convenience market data",
        "risk_note": "Useful as another read on broader developed-market sentiment.",
        "risk_rules": {
            "metric": "delta_pct",
            "direction": "lower_is_riskier",
            "amber": -3.0,
            "red": -7.0,
        },
    },
}

STOCK_MARKETS_GLOBAL = {
    "MSCI World (URTH ETF proxy)": {
        "ticker": "URTH",
        "unit": "USD per share",
        "decimals": 2,
        "show_chart": True,
        "show_delta": True,
        "description": "Proxy for developed global equities.",
        "source": "Yahoo Finance via yfinance",
        "source_type": "Convenience market data",
        "risk_note": "Helps read the direction of broad developed-market equities.",
        "risk_rules": {
            "metric": "delta_pct",
            "direction": "lower_is_riskier",
            "amber": -3.0,
            "red": -7.0,
        },
    },
    "MSCI Emerging Markets (EEM ETF proxy)": {
        "ticker": "EEM",
        "unit": "USD per share",
        "decimals": 2,
        "show_chart": True,
        "show_delta": True,
        "description": "Proxy for broad emerging market equities.",
        "source": "Yahoo Finance via yfinance",
        "source_type": "Convenience market data",
        "risk_note": "EM weakness can signal tighter external financing conditions for emerging markets.",
        "risk_rules": {
            "metric": "delta_pct",
            "direction": "lower_is_riskier",
            "amber": -3.0,
            "red": -7.0,
        },
    },
}

CURRENCIES_EGYPT = {
    "USD / EGP": {
        "ticker": "EGP=X",
        "unit": "EGP per USD",
        "decimals": 4,
        "show_chart": True,
        "show_delta": True,
        "description": "Egyptian pound per U.S. dollar.",
        "source": "Yahoo Finance via yfinance",
        "source_type": "Convenience market data",
        "risk_note": "A higher USD/EGP can indicate FX pressure and broader external vulnerability.",
        "risk_rules": {
            "metric": "delta_pct",
            "direction": "higher_is_riskier",
            "amber": 1.5,
            "red": 3.0,
        },
    }
}

CURRENCIES_GLOBAL = {
    "DXY": {
        "ticker": "DX-Y.NYB",
        "unit": "index level",
        "decimals": 2,
        "show_chart": True,
        "show_delta": True,
        "description": "U.S. dollar strength against a basket of major currencies.",
        "source": "Yahoo Finance via yfinance",
        "source_type": "Convenience market data",
        "risk_note": "A stronger dollar can tighten financing conditions for emerging markets.",
        "risk_rules": {
            "metric": "delta_pct",
            "direction": "higher_is_riskier",
            "amber": 1.5,
            "red": 3.0,
        },
    },
    "USD / JPY": {
        "ticker": "JPY=X",
        "unit": "JPY per USD",
        "decimals": 3,
        "show_chart": True,
        "show_delta": True,
        "description": "Dollar-yen exchange rate.",
        "source": "Yahoo Finance via yfinance",
        "source_type": "Convenience market data",
        "risk_note": "Useful as a global market stress cross-check, though not a direct Egypt risk indicator.",
        "risk_rules": {
            "metric": "delta_pct",
            "direction": "higher_is_riskier",
            "amber": 2.0,
            "red": 4.0,
        },
    },
}

RATES_CREDIT_GLOBAL = {
    "U.S. 5Y Treasury Yield": {
        "ticker": "^FVX",
        "unit": "%",
        "decimals": 2,
        "value_divisor": 10,
        "show_chart": True,
        "show_delta": True,
        "description": "Intermediate U.S. Treasury yield.",
        "source": "Yahoo Finance via yfinance",
        "source_type": "Convenience market data",
        "risk_note": "Higher U.S. yields can tighten global financial conditions.",
        "risk_rules": {
            "metric": "latest",
            "direction": "higher_is_riskier",
            "amber": 4.00,
            "red": 4.50,
        },
    },
    "U.S. 10Y Treasury Yield": {
        "ticker": "^TNX",
        "unit": "%",
        "decimals": 2,
        "value_divisor": 10,
        "show_chart": True,
        "show_delta": True,
        "description": "Benchmark U.S. long-term rate.",
        "source": "Yahoo Finance via yfinance",
        "source_type": "Convenience market data",
        "risk_note": "Higher long-end U.S. yields can pressure emerging-market funding conditions.",
        "risk_rules": {
            "metric": "latest",
            "direction": "higher_is_riskier",
            "amber": 4.25,
            "red": 4.75,
        },
    },
    "EMB (EM Sovereign Bond ETF proxy)": {
        "ticker": "EMB",
        "unit": "USD per share",
        "decimals": 2,
        "show_chart": True,
        "show_delta": True,
        "description": "Proxy for emerging-market sovereign external debt.",
        "source": "Yahoo Finance via yfinance",
        "source_type": "Convenience market data",
        "risk_note": "A weaker EMB can indicate broader pressure on EM sovereign spreads and funding sentiment.",
        "risk_rules": {
            "metric": "delta_pct",
            "direction": "lower_is_riskier",
            "amber": -1.5,
            "red": -4.0,
        },
    },
    "U.S. High Yield (HYG proxy)": {
        "ticker": "HYG",
        "unit": "USD per share",
        "decimals": 2,
        "show_chart": True,
        "show_delta": True,
        "description": "Proxy for global credit risk appetite.",
        "source": "Yahoo Finance via yfinance",
        "source_type": "Convenience market data",
        "risk_note": "High-yield weakness often reflects worsening risk appetite and tighter credit conditions.",
        "risk_rules": {
            "metric": "delta_pct",
            "direction": "lower_is_riskier",
            "amber": -1.5,
            "red": -4.0,
        },
    },
}

VOLATILITY_GLOBAL = {
    "VIX": {
        "ticker": "^VIX",
        "unit": "index level",
        "decimals": 2,
        "show_chart": True,
        "show_delta": True,
        "description": "Implied volatility for U.S. equities.",
        "source": "Yahoo Finance via yfinance",
        "source_type": "Convenience market data",
        "risk_note": "A higher VIX signals broader global risk aversion.",
        "risk_rules": {
            "metric": "latest",
            "direction": "higher_is_riskier",
            "amber": 18.0,
            "red": 25.0,
        },
    },
    "MOVE": {
        "ticker": "^MOVE",
        "unit": "index level",
        "decimals": 2,
        "show_chart": True,
        "show_delta": True,
        "description": "Bond market volatility.",
        "source": "Yahoo Finance via yfinance",
        "source_type": "Convenience market data",
        "risk_note": "Higher Treasury volatility can indicate stress in the global rates complex.",
        "risk_rules": {
            "metric": "latest",
            "direction": "higher_is_riskier",
            "amber": 110.0,
            "red": 130.0,
        },
    },
}

COMMODITIES_ENERGY = {
    "Brent": {
        "ticker": "BZ=F",
        "unit": "USD per barrel",
        "decimals": 2,
        "show_chart": True,
        "show_delta": True,
        "description": "Global oil benchmark.",
        "source": "Yahoo Finance via yfinance",
        "source_type": "Convenience market data",
        "risk_note": "Higher oil prices can increase Egypt’s import bill and inflation pressure.",
        "risk_rules": {
            "metric": "delta_pct",
            "direction": "higher_is_riskier",
            "amber": 5.0,
            "red": 10.0,
        },
    },
    "Natural Gas": {
        "ticker": "NG=F",
        "unit": "USD per MMBtu",
        "decimals": 3,
        "show_chart": True,
        "show_delta": True,
        "description": "Key global energy input.",
        "source": "Yahoo Finance via yfinance",
        "source_type": "Convenience market data",
        "risk_note": "Gas spikes can matter for energy costs and broader imported inflation.",
        "risk_rules": {
            "metric": "delta_pct",
            "direction": "higher_is_riskier",
            "amber": 8.0,
            "red": 15.0,
        },
    },
}

COMMODITIES_METALS = {
    "Gold": {
        "ticker": "GC=F",
        "unit": "USD per troy ounce",
        "decimals": 2,
        "show_chart": True,
        "show_delta": True,
        "description": "Traditional safe-haven asset.",
        "source": "Yahoo Finance via yfinance",
        "source_type": "Convenience market data",
        "risk_note": "A stronger gold price can reflect rising caution and defensive positioning.",
        "risk_rules": {
            "metric": "delta_pct",
            "direction": "higher_is_riskier",
            "amber": 3.0,
            "red": 6.0,
        },
    },
    "Copper": {
        "ticker": "HG=F",
        "unit": "USD per pound",
        "decimals": 3,
        "show_chart": True,
        "show_delta": True,
        "description": "Industrial metal and global growth signal.",
        "source": "Yahoo Finance via yfinance",
        "source_type": "Convenience market data",
        "risk_note": "Weak copper can signal softer global industrial momentum.",
        "risk_rules": {
            "metric": "delta_pct",
            "direction": "lower_is_riskier",
            "amber": -3.0,
            "red": -6.0,
        },
    },
}

COMMODITIES_FOOD = {
    "Wheat": {
        "ticker": "ZW=F",
        "unit": "U.S. cents per bushel",
        "decimals": 2,
        "show_chart": True,
        "show_delta": True,
        "description": "Global grain benchmark.",
        "source": "Yahoo Finance via yfinance",
        "source_type": "Convenience market data",
        "risk_note": "Higher wheat prices can matter for food import pressure and inflation sensitivity.",
        "risk_rules": {
            "metric": "delta_pct",
            "direction": "higher_is_riskier",
            "amber": 5.0,
            "red": 10.0,
        },
    },
}

ALL_CONFIG_BLOCKS = [
    STOCK_MARKETS_EGYPT,
    STOCK_MARKETS_US,
    STOCK_MARKETS_EUROPE,
    STOCK_MARKETS_GLOBAL,
    CURRENCIES_EGYPT,
    CURRENCIES_GLOBAL,
    RATES_CREDIT_GLOBAL,
    VOLATILITY_GLOBAL,
    COMMODITIES_ENERGY,
    COMMODITIES_METALS,
    COMMODITIES_FOOD,
]

PULSE_GROUPS = {
    "External Financing Pressure": {
        "members": [
            "USD / EGP",
            "DXY",
            "MSCI Emerging Markets (EEM ETF proxy)",
            "EMB (EM Sovereign Bond ETF proxy)",
        ],
        "note": "Combines FX pressure with broader emerging-market financing tone.",
    },
    "Energy & Food Import Pressure": {
        "members": [
            "Brent",
            "Natural Gas",
            "Wheat",
        ],
        "note": "Tracks imported energy and food cost pressure.",
    },
    "Global Risk Aversion": {
        "members": [
            "VIX",
            "MOVE",
            "Gold",
        ],
        "note": "Monitors cross-asset risk-off behavior.",
    },
    "Egypt Market Sentiment": {
        "members": [
            "EGX30",
            "Commercial International Bank (CIB)",
        ],
        "note": "A quick read on local market mood.",
    },
}

# ===================================================
# SIDEBAR
# ===================================================
st.sidebar.header("Controls")

chart_window_label = st.sidebar.selectbox(
    "Chart window",
    options=list(WINDOW_OPTIONS.keys()),
    index=2
)

change_window_label = st.sidebar.selectbox(
    "Change / risk reference window",
    options=list(WINDOW_OPTIONS.keys()),
    index=2
)

selected_chart_lookback = WINDOW_OPTIONS[chart_window_label]["lookback"]
selected_change_lookback = WINDOW_OPTIONS[change_window_label]["lookback"]

show_diagnostics = st.sidebar.checkbox("Show fetch diagnostics", value=False)

if st.sidebar.button("Refresh data"):
    st.cache_data.clear()

st.sidebar.markdown("---")
st.sidebar.markdown("**Risk legend**")
st.sidebar.caption("🟢 Normal")
st.sidebar.caption("🟠 Watch")
st.sidebar.caption("🔴 Elevated")
st.sidebar.caption("Signals are simple rule-based flags for monitoring, not formal risk ratings.")

# ===================================================
# HELPERS
# ===================================================
def format_value(value, decimals=2):
    if value is None or pd.isna(value):
        return "N/A"
    return f"{value:,.{decimals}f}"


def format_date(dt_value):
    if dt_value is None or pd.isna(dt_value):
        return "N/A"
    return pd.Timestamp(dt_value).strftime("%Y-%m-%d")


def normalize_index(df):
    if df is None or df.empty:
        return pd.DataFrame()

    out = df.copy()

    if isinstance(out.columns, pd.MultiIndex):
        out.columns = out.columns.get_level_values(0)

    if isinstance(out.index, pd.DatetimeIndex) and out.index.tz is not None:
        out.index = out.index.tz_localize(None)

    out = out.sort_index()
    return out


def business_days_lag(last_date):
    if last_date is None or pd.isna(last_date):
        return None

    today = pd.Timestamp(datetime.now().date())
    last_day = pd.Timestamp(last_date).normalize()

    if last_day >= today:
        return 0

    return max(len(pd.bdate_range(last_day + pd.Timedelta(days=1), today)), 0)


def build_freshness_label(last_date, stale_threshold):
    lag = business_days_lag(last_date)

    if lag is None:
        return lag, False, "Unknown freshness"

    is_stale = lag > stale_threshold

    if is_stale:
        label = f"Possibly stale ({lag} business-day lag, approximate)"
    else:
        label = f"Fresh by business-day check ({lag} lag, approximate)"

    return lag, is_stale, label


def apply_series_transforms(df, meta):
    if df is None or df.empty:
        return pd.DataFrame()

    out = df.copy()

    if "Close" in out.columns:
        divisor = meta.get("value_divisor", 1)
        multiplier = meta.get("value_multiplier", 1)

        if divisor == 0:
            divisor = 1

        out["Close"] = out["Close"] * multiplier / divisor

    return out


def get_previous_year_close(df):
    if df is None or df.empty or "Close" not in df.columns:
        return None, None

    closes = df["Close"].dropna()
    if closes.empty:
        return None, None

    latest_date = closes.index[-1]
    previous_year = latest_date.year - 1

    previous_year_data = closes[closes.index.year == previous_year]
    if previous_year_data.empty:
        return None, None

    anchor_date = previous_year_data.index[-1]
    anchor_value = float(previous_year_data.iloc[-1])
    return anchor_value, anchor_date


def signal_badge(status):
    return RISK_BADGES.get(status, "⚪ Unrated")


def get_metric_label(metric_key):
    labels = {
        "latest": "latest level",
        "delta_pct": f"{change_window_label} change",
        "ytd_pct": "YTD change",
    }
    return labels.get(metric_key, metric_key)


def classify_risk(meta, result):
    rules = meta.get("risk_rules")
    if not rules:
        return {
            "status": "Unrated",
            "reason": "No rule-based signal configured.",
            "metric_used": None,
            "threshold_amber": None,
            "threshold_red": None,
        }

    metric_key = rules.get("metric", "latest")
    metric_value = result.get(metric_key)

    if metric_value is None or pd.isna(metric_value):
        if metric_key == "ytd_pct" and meta.get("special_mode") == "egx30_auto_ytd":
            reason = "YTD signal unavailable because prior-year anchor was not found in the fetched window."
        else:
            reason = "Insufficient data for the configured rule."
        return {
            "status": "No signal",
            "reason": reason,
            "metric_used": metric_key,
            "threshold_amber": rules.get("amber"),
            "threshold_red": rules.get("red"),
        }

    direction = rules.get("direction", "higher_is_riskier")
    amber = rules.get("amber")
    red = rules.get("red")

    if amber is None or red is None:
        return {
            "status": "Unrated",
            "reason": "Risk rule thresholds are incomplete.",
            "metric_used": metric_key,
            "threshold_amber": amber,
            "threshold_red": red,
        }

    if direction == "higher_is_riskier":
        if metric_value >= red:
            status = "Elevated"
        elif metric_value >= amber:
            status = "Watch"
        else:
            status = "Normal"
    elif direction == "lower_is_riskier":
        if metric_value <= red:
            status = "Elevated"
        elif metric_value <= amber:
            status = "Watch"
        else:
            status = "Normal"
    else:
        return {
            "status": "Unrated",
            "reason": "Risk rule direction is invalid.",
            "metric_used": metric_key,
            "threshold_amber": amber,
            "threshold_red": red,
        }

    metric_label = get_metric_label(metric_key)

    if direction == "higher_is_riskier":
        if status == "Elevated":
            reason = f"{metric_label.capitalize()} is {metric_value:.2f}, above the Elevated threshold of {red:.2f}."
        elif status == "Watch":
            reason = f"{metric_label.capitalize()} is {metric_value:.2f}, above the Watch threshold of {amber:.2f}."
        else:
            reason = f"{metric_label.capitalize()} is {metric_value:.2f}, below the Watch threshold of {amber:.2f}."
    else:
        if status == "Elevated":
            reason = f"{metric_label.capitalize()} is {metric_value:.2f}, below the Elevated threshold of {red:.2f}."
        elif status == "Watch":
            reason = f"{metric_label.capitalize()} is {metric_value:.2f}, below the Watch threshold of {amber:.2f}."
        else:
            reason = f"{metric_label.capitalize()} is {metric_value:.2f}, above the Watch threshold of {amber:.2f}."

    return {
        "status": status,
        "reason": reason,
        "metric_used": metric_key,
        "threshold_amber": amber,
        "threshold_red": red,
    }


def build_chart(close_df, title, decimals=2):
    chart_data = close_df.reset_index().copy()
    chart_data.columns = ["Date", "Close"]

    y_min = float(chart_data["Close"].min())
    y_max = float(chart_data["Close"].max())

    if y_min == y_max:
        y_min -= 1
        y_max += 1
    else:
        padding = (y_max - y_min) * 0.08
        y_min -= padding
        y_max += padding

    return (
        alt.Chart(chart_data)
        .mark_line()
        .encode(
            x=alt.X("Date:T", title=None),
            y=alt.Y(
                "Close:Q",
                title=None,
                scale=alt.Scale(domain=[y_min, y_max], zero=False)
            ),
            tooltip=[
                alt.Tooltip("Date:T", title="Date"),
                alt.Tooltip("Close:Q", title=title, format=f",.{decimals}f")
            ]
        )
        .properties(height=240)
        .interactive()
    )


def render_anchor(anchor_id):
    st.markdown(f"<div id='{anchor_id}'></div>", unsafe_allow_html=True)


def render_subsection_header(title):
    st.markdown(
        f"<div style='font-size:24px; font-weight:700; margin-top:14px; margin-bottom:8px;'>{title}</div>",
        unsafe_allow_html=True
    )


def render_tab_index(items):
    st.markdown("#### Jump within this tab")
    links = " | ".join([f"[{label}](#{anchor})" for label, anchor in items])
    st.markdown(links)
    st.markdown("")


def collect_unique_tickers(config_blocks):
    tickers = []
    for block in config_blocks:
        for meta in block.values():
            ticker = meta.get("ticker")
            if ticker:
                tickers.append(ticker)
    return tuple(sorted(set(tickers)))


def build_meta_lookup(config_blocks):
    meta_lookup = {}
    for block in config_blocks:
        for name, meta in block.items():
            meta_lookup[name] = meta
    return meta_lookup


@st.cache_data(ttl=1800)
def fetch_yf_history(ticker, period, cache_version):
    diagnostic = {
        "ticker": ticker,
        "fetch_status": "unknown",
        "rows": 0,
        "latest_date": None,
        "used_fallback": False,
        "error_note": "",
    }

    try:
        df = yf.download(
            ticker,
            period=period,
            interval="1d",
            auto_adjust=False,
            progress=False,
            threads=False
        )

        if df is None or df.empty:
            diagnostic["used_fallback"] = True
            df = yf.Ticker(ticker).history(
                period=period,
                interval="1d",
                auto_adjust=False
            )

        df = normalize_index(df)

        if df.empty:
            diagnostic["fetch_status"] = "empty"
            diagnostic["error_note"] = "No rows returned."
            return pd.DataFrame(), diagnostic

        if "Close" not in df.columns:
            diagnostic["fetch_status"] = "invalid"
            diagnostic["error_note"] = "Returned data has no Close column."
            return pd.DataFrame(), diagnostic

        df = df.dropna(subset=["Close"])

        if df.empty:
            diagnostic["fetch_status"] = "invalid"
            diagnostic["error_note"] = "All Close values are missing."
            return pd.DataFrame(), diagnostic

        diagnostic["fetch_status"] = "ok"
        diagnostic["rows"] = len(df)
        diagnostic["latest_date"] = df.index[-1]

        return df, diagnostic

    except Exception as e:
        diagnostic["fetch_status"] = "error"
        diagnostic["error_note"] = str(e)
        return pd.DataFrame(), diagnostic


def load_data_store(unique_tickers, period, cache_version):
    store = {}
    diagnostics = []

    for ticker in unique_tickers:
        df, diag = fetch_yf_history(ticker, period, cache_version)
        store[ticker] = df
        diagnostics.append(diag)

    diagnostics_df = pd.DataFrame(diagnostics)
    if not diagnostics_df.empty and "latest_date" in diagnostics_df.columns:
        diagnostics_df["latest_date"] = diagnostics_df["latest_date"].apply(format_date)

    return store, diagnostics_df


def evaluate_indicator(name, meta, raw_df, chart_lookback, change_lookback):
    ticker = meta.get("ticker")
    data = apply_series_transforms(raw_df, meta)

    base_result = {
        "name": name,
        "ticker": ticker,
        "latest": None,
        "latest_date": None,
        "delta_pct": None,
        "chart_df": pd.DataFrame(),
        "business_lag": None,
        "is_stale": None,
        "freshness_label": "Unknown freshness",
        "data_status": "no_data",
        "fetch_status": "unknown",
        "ytd_pct": None,
        "ytd_anchor": None,
        "ytd_anchor_date": None,
        "ytd_note": None,
    }

    if data.empty or "Close" not in data.columns:
        result = base_result.copy()
        result["data_status"] = "no_data"
        result["signal"] = classify_risk(meta, result)
        return result

    closes = data["Close"].dropna()
    if closes.empty:
        result = base_result.copy()
        result["data_status"] = "invalid_close"
        result["signal"] = classify_risk(meta, result)
        return result

    latest = float(closes.iloc[-1])
    latest_date = closes.index[-1]

    if len(closes) >= change_lookback + 1:
        reference = float(closes.iloc[-(change_lookback + 1)])
        delta_pct = ((latest - reference) / reference * 100) if reference != 0 else 0.0
    elif len(closes) >= 2:
        reference = float(closes.iloc[0])
        delta_pct = ((latest - reference) / reference * 100) if reference != 0 else 0.0
    else:
        delta_pct = None

    stale_threshold = meta.get("stale_threshold_days", DEFAULT_STALE_THRESHOLD_BDAYS)
    bday_lag, is_stale, freshness_label = build_freshness_label(latest_date, stale_threshold)

    chart_df = data[["Close"]].dropna().tail(chart_lookback + 1).copy()

    result = {
        "name": name,
        "ticker": ticker,
        "latest": latest,
        "latest_date": latest_date,
        "delta_pct": delta_pct,
        "chart_df": chart_df,
        "business_lag": bday_lag,
        "is_stale": is_stale,
        "freshness_label": freshness_label,
        "data_status": "ok",
        "fetch_status": "ok",
        "ytd_pct": None,
        "ytd_anchor": None,
        "ytd_anchor_date": None,
        "ytd_note": None,
    }

    if meta.get("special_mode") == "egx30_auto_ytd":
        anchor_value, anchor_date = get_previous_year_close(data)
        result["ytd_anchor"] = anchor_value
        result["ytd_anchor_date"] = anchor_date

        if anchor_value not in (None, 0):
            result["ytd_pct"] = ((latest / anchor_value) - 1) * 100
        else:
            result["ytd_note"] = "YTD unavailable because prior-year anchor was not found in the fetched window."

    result["signal"] = classify_risk(meta, result)
    return result


def build_results_by_name(config_blocks, data_store, chart_lookback, change_lookback):
    results = {}
    for block in config_blocks:
        for name, meta in block.items():
            raw_df = data_store.get(meta.get("ticker"), pd.DataFrame())
            results[name] = evaluate_indicator(
                name=name,
                meta=meta,
                raw_df=raw_df,
                chart_lookback=chart_lookback,
                change_lookback=change_lookback
            )
    return results


def attach_fetch_status_to_results(results_by_name, diagnostics_df):
    if diagnostics_df.empty:
        return results_by_name

    diag_lookup = diagnostics_df.set_index("ticker").to_dict(orient="index")

    for result in results_by_name.values():
        ticker = result.get("ticker")
        diag = diag_lookup.get(ticker)
        if diag:
            result["fetch_status"] = diag.get("fetch_status", "unknown")

    return results_by_name


def aggregate_signal(member_names, results_by_name):
    statuses = []
    drivers = []

    for member in member_names:
        if member in results_by_name:
            member_status = results_by_name[member]["signal"]["status"]
            drivers.append(f"{member}: {member_status}")
            if member_status in RISK_ORDER:
                statuses.append(RISK_ORDER[member_status])

    if not statuses:
        return "No signal", drivers

    max_score = max(statuses)
    inverse_map = {v: k for k, v in RISK_ORDER.items()}
    return inverse_map[max_score], drivers


def build_snapshot_table(results_by_name, config_blocks):
    rows = []
    meta_lookup = build_meta_lookup(config_blocks)

    for name, result in results_by_name.items():
        meta = meta_lookup.get(name, {})
        rules = meta.get("risk_rules", {})

        rows.append({
            "Indicator": name,
            "Ticker": meta.get("ticker"),
            "Description": meta.get("description"),
            "Latest": result.get("latest"),
            "Delta %": result.get("delta_pct"),
            "YTD %": result.get("ytd_pct"),
            "YTD Note": result.get("ytd_note"),
            "Risk Status": result.get("signal", {}).get("status"),
            "Risk Reason": result.get("signal", {}).get("reason"),
            "Rule Metric": result.get("signal", {}).get("metric_used"),
            "Rule Direction": rules.get("direction"),
            "Amber Threshold": result.get("signal", {}).get("threshold_amber"),
            "Red Threshold": result.get("signal", {}).get("threshold_red"),
            "Latest Data Date": format_date(result.get("latest_date")),
            "Business-Day Lag (Approx)": result.get("business_lag"),
            "Freshness": result.get("freshness_label"),
            "Data Status": result.get("data_status"),
            "Fetch Status": result.get("fetch_status"),
            "Unit": meta.get("unit"),
            "Source": meta.get("source"),
            "Source Type": meta.get("source_type"),
            "Risk Note": meta.get("risk_note"),
        })

    return pd.DataFrame(rows)


# ===================================================
# RENDER FUNCTIONS
# ===================================================
def render_dashboard_header(results_by_name):
    all_results = list(results_by_name.values())
    valid_results = [r for r in all_results if r.get("latest") is not None]
    latest_dates = [r.get("latest_date") for r in valid_results if r.get("latest_date") is not None]

    latest_loaded_date = max(latest_dates) if latest_dates else None
    stale_count = sum(1 for r in valid_results if r.get("is_stale"))
    total_live = len(valid_results)

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Dashboard refreshed", datetime.now().strftime("%Y-%m-%d %H:%M"))
    with c2:
        st.metric("Latest data point loaded", format_date(latest_loaded_date))
    with c3:
        st.metric("Live series loaded", str(total_live))
    with c4:
        st.metric("Possibly stale series", str(stale_count))

    st.caption(
        f"Chart window: {chart_window_label}. "
        f"Change / risk reference window: {change_window_label}. "
        "Freshness checks are approximate and use business-day gaps rather than exchange-specific holiday calendars."
    )


def render_risk_pulse(results_by_name):
    st.markdown("## Risk Pulse")

    cols = st.columns(4)

    for idx, (pulse_name, pulse_meta) in enumerate(PULSE_GROUPS.items()):
        status, drivers = aggregate_signal(pulse_meta["members"], results_by_name)

        with cols[idx]:
            st.markdown(f"**{pulse_name}**")
            st.markdown(signal_badge(status))
            st.caption(pulse_meta["note"])
            if drivers:
                st.caption("Drivers: " + " | ".join(drivers))


def render_standard_indicator(name, meta, result):
    decimals = meta.get("decimals", 2)

    st.markdown(
        f"<div style='font-size:30px; font-weight:700; margin-top:8px; margin-bottom:6px;'>{name}</div>",
        unsafe_allow_html=True
    )

    if meta.get("description"):
        st.caption(meta["description"])

    if result["latest"] is None:
        st.warning("No data available.")
        st.caption(f"Data status: {result.get('data_status', 'unknown')}")
        st.caption(f"Unit: {meta.get('unit', 'N/A')}")
        if meta.get("source"):
            st.caption(f"Source: {meta['source']}")
        return

    if meta.get("show_delta", True) and result["delta_pct"] is not None:
        st.metric(
            label="Latest Value",
            value=format_value(result["latest"], decimals),
            delta=f"{result['delta_pct']:+.2f}%"
        )
        st.caption(f"Delta shown versus selected {change_window_label.lower()} reference window.")
    else:
        st.metric(
            label="Latest Value",
            value=format_value(result["latest"], decimals)
        )

    if meta.get("show_chart", False) and not result["chart_df"].empty:
        st.altair_chart(
            build_chart(result["chart_df"], name, decimals=decimals),
            use_container_width=True
        )

    st.markdown(f"**Risk status:** {signal_badge(result['signal']['status'])}")
    st.caption(result["signal"]["reason"])
    st.caption(f"Latest data date: {format_date(result['latest_date'])} | Freshness: {result['freshness_label']}")

    if meta.get("risk_note"):
        st.caption(f"Why it matters: {meta['risk_note']}")

    st.caption(f"Unit: {meta.get('unit', 'N/A')}")
    if meta.get("source"):
        st.caption(f"Source: {meta['source']}")


def render_egx30_indicator(name, meta, result):
    decimals = meta.get("decimals", 2)

    st.markdown(
        f"<div style='font-size:30px; font-weight:700; margin-top:8px; margin-bottom:6px;'>{name}</div>",
        unsafe_allow_html=True
    )

    if meta.get("description"):
        st.caption(meta["description"])

    if result["latest"] is None:
        st.warning("No data available.")
        st.caption(f"Data status: {result.get('data_status', 'unknown')}")
        st.caption(f"Unit: {meta.get('unit', 'N/A')}")
        if meta.get("source"):
            st.caption(f"Source: {meta['source']}")
        return

    c1, c2 = st.columns(2)
    with c1:
        st.metric("Latest Value", format_value(result["latest"], decimals))
    with c2:
        if result["ytd_pct"] is not None:
            st.metric("YTD %", f"{result['ytd_pct']:+.2f}%")
        else:
            st.metric("YTD %", "N/A")

    st.markdown(f"**Risk status:** {signal_badge(result['signal']['status'])}")
    st.caption(result["signal"]["reason"])
    st.caption(f"Latest data date: {format_date(result['latest_date'])} | Freshness: {result['freshness_label']}")

    if result["ytd_anchor"] is not None:
        st.caption(
            f"YTD anchor: {format_value(result['ytd_anchor'], decimals)} "
            f"on {format_date(result['ytd_anchor_date'])}"
        )
    elif result.get("ytd_note"):
        st.caption(result["ytd_note"])

    if meta.get("risk_note"):
        st.caption(f"Why it matters: {meta['risk_note']}")

    st.caption(f"Unit: {meta.get('unit', 'N/A')}")
    if meta.get("source"):
        st.caption(f"Source: {meta['source']}")


def render_indicator(name, meta, result):
    if meta.get("special_mode") == "egx30_auto_ytd":
        render_egx30_indicator(name, meta, result)
    else:
        render_standard_indicator(name, meta, result)


def render_config_block(config, results_by_name):
    items = list(config.items())
    n = len(items)
    i = 0

    while i < n:
        if i == n - 1:
            _, center, _ = st.columns([1, 2, 1], gap="large")
            name, meta = items[i]
            with center:
                render_indicator(name, meta, results_by_name[name])
            i += 1
        else:
            col1, col2 = st.columns(2, gap="large")
            name1, meta1 = items[i]
            name2, meta2 = items[i + 1]

            with col1:
                render_indicator(name1, meta1, results_by_name[name1])
            with col2:
                render_indicator(name2, meta2, results_by_name[name2])

            i += 2


def render_domestic_macro_pending():
    st.markdown("### Domestic Macro (Pending Validated Sources)")
    st.write(
        "This section is intentionally held back from live display until the dashboard migrates "
        "key Egypt macro series to validated official or licensed feeds."
    )

    pending_df = pd.DataFrame([
        {
            "Series": "Headline CPI inflation",
            "Suggested source": "CAPMAS / CBE / official statistical release",
            "Reason not yet live": "Should come from an official domestic source, not a convenience market feed."
        },
        {
            "Series": "CBE policy rates",
            "Suggested source": "Central Bank of Egypt",
            "Reason not yet live": "Needs validated policy-rate sourcing and update logic."
        },
        {
            "Series": "Net international reserves",
            "Suggested source": "Central Bank of Egypt",
            "Reason not yet live": "Best displayed from official reserve releases."
        },
        {
            "Series": "Egypt T-bill / bond yields",
            "Suggested source": "MOF / CBE / licensed market data",
            "Reason not yet live": "Domestic fixed-income series require stronger validation and licensing review."
        },
        {
            "Series": "PMI",
            "Suggested source": "Licensed provider / official release",
            "Reason not yet live": "May require a licensed distribution workflow."
        },
        {
            "Series": "External sector metrics",
            "Suggested source": "CBE / IMF / official releases",
            "Reason not yet live": "Should be sourced from validated macro publications rather than market proxies."
        },
    ])

    st.dataframe(pending_df, use_container_width=True)
    st.info(
        "Recommended next step: integrate official or licensed feeds for Egypt domestic macro and fixed-income series, "
        "then use the same rendering framework already built for the live market tabs."
    )


def render_methodology():
    render_anchor("methodology-purpose")
    st.markdown("### Purpose")
    st.write(
        "This dashboard is designed as a monitoring and briefing tool for macro-financial risk identification. "
        "Egypt is shown first where relevant, with global indicators used as contextual comparators."
    )

    render_anchor("methodology-sources")
    st.markdown("### Sources")
    st.write(
        "Most live market series are currently pulled from Yahoo Finance through the yfinance Python package. "
        "Each indicator includes its source beneath the metric or chart."
    )
    st.write(
        "Domestic macro and Egypt fixed-income series are intentionally not yet live where stronger official or licensed sourcing is preferable."
    )

    render_anchor("methodology-transformations")
    st.markdown("### Transformations")
    st.write(
        "The chart window and change/risk reference window are selected separately in the sidebar."
    )
    st.write(
        "EGX30 YTD is calculated automatically using the last available trading close from the previous calendar year in the fetched series."
    )
    st.write(
        "Certain Yahoo Finance Treasury yield tickers are displayed on a divided-by-10 basis so that values appear as standard percentages."
    )

    render_anchor("methodology-risk")
    st.markdown("### Risk Signal Logic")
    st.write(
        "Risk flags are simple rule-based monitoring signals. Each configured indicator can be classified as Normal, Watch, or Elevated "
        "based on either its latest level, its selected-window change, or its YTD change."
    )
    st.write(
        "These signals are intended for directional monitoring and prioritization, not as official risk ratings or forecasting models."
    )

    render_anchor("methodology-freshness")
    st.markdown("### Data Freshness")
    st.write(
        "Each series displays its latest available data date and a freshness label. "
        "Freshness is approximated using business-day gaps rather than exchange-specific calendars."
    )
    st.write(
        "Accordingly, a series marked as possibly stale should be reviewed before concluding that a true data problem exists."
    )

    render_anchor("methodology-due-diligence")
    st.markdown("### Due Diligence")
    st.write(
        "This dashboard is intended for internal monitoring, briefing support, and structured discussion. "
        "It is not a trading terminal or an official market data platform."
    )
    st.write(
        "Any number intended for publication, formal briefing, or external circulation should be cross-checked against the relevant official or licensed source."
    )

    render_anchor("methodology-licensing")
    st.markdown("### Licensing and Usage Caution")
    st.write(
        "Yahoo Finance and data accessed via yfinance should be treated as convenience data for internal analytical monitoring."
    )
    st.write(
        "This dashboard does not claim official redistribution rights, exchange licensing rights, or suitability for commercial resale."
    )
    st.write(
        "If deployed more broadly, key series should be migrated to official, licensed, or institutionally approved feeds as appropriate."
    )

    render_anchor("methodology-next")
    st.markdown("### Recommended Next Data Upgrades")
    st.write(
        "The next priority should be to add validated Egypt domestic macro, domestic rates, and sovereign-risk series "
        "using official or licensed sources, while preserving the current config-driven rendering structure."
    )


def render_fetch_diagnostics(diagnostics_df):
    st.markdown("## Fetch Diagnostics")

    if diagnostics_df.empty:
        st.info("No diagnostics available.")
        return

    st.caption("Useful for debugging empty or inconsistent Yahoo Finance responses.")
    st.dataframe(diagnostics_df, use_container_width=True)


# ===================================================
# PAGE TITLE
# ===================================================
st.title("Macro Indicators and Risk Identification Dashboard")

# ===================================================
# DATA LOAD
# ===================================================
unique_tickers = collect_unique_tickers(ALL_CONFIG_BLOCKS)
data_store, diagnostics_df = load_data_store(unique_tickers, MAX_FETCH_PERIOD, APP_CACHE_VERSION)
results_by_name = build_results_by_name(
    ALL_CONFIG_BLOCKS,
    data_store,
    selected_chart_lookback,
    selected_change_lookback
)
results_by_name = attach_fetch_status_to_results(results_by_name, diagnostics_df)

# ===================================================
# TOP SUMMARY
# ===================================================
render_dashboard_header(results_by_name)
render_risk_pulse(results_by_name)

snapshot_df = build_snapshot_table(results_by_name, ALL_CONFIG_BLOCKS)
snapshot_csv = snapshot_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download latest snapshot (CSV)",
    data=snapshot_csv,
    file_name="macro_risk_dashboard_snapshot.csv",
    mime="text/csv"
)

if show_diagnostics:
    render_fetch_diagnostics(diagnostics_df)

st.markdown("---")

# ===================================================
# TABS
# ===================================================
stock_tab, fx_tab, rates_tab, vol_tab, comm_tab, domestic_tab, methodology_tab = st.tabs(
    ["Stock Markets", "Currencies", "Rates & Credit", "Volatility", "Commodities", "Domestic Macro", "Methodology"]
)

with stock_tab:
    render_tab_index([
        ("Egypt", "stock-egypt"),
        ("United States", "stock-us"),
        ("Europe", "stock-europe"),
        ("Global", "stock-global"),
    ])

    render_anchor("stock-egypt")
    render_subsection_header("Egypt")
    render_config_block(STOCK_MARKETS_EGYPT, results_by_name)

    render_anchor("stock-us")
    render_subsection_header("United States")
    render_config_block(STOCK_MARKETS_US, results_by_name)

    render_anchor("stock-europe")
    render_subsection_header("Europe")
    render_config_block(STOCK_MARKETS_EUROPE, results_by_name)

    render_anchor("stock-global")
    render_subsection_header("Global")
    render_config_block(STOCK_MARKETS_GLOBAL, results_by_name)

with fx_tab:
    render_tab_index([
        ("Egypt", "fx-egypt"),
        ("Global", "fx-global"),
    ])

    render_anchor("fx-egypt")
    render_subsection_header("Egypt")
    render_config_block(CURRENCIES_EGYPT, results_by_name)

    render_anchor("fx-global")
    render_subsection_header("Global")
    render_config_block(CURRENCIES_GLOBAL, results_by_name)

with rates_tab:
    render_tab_index([
        ("Global", "rates-global"),
        ("Egypt - Pending Validated Sources", "rates-egypt-pending"),
    ])

    render_anchor("rates-global")
    render_subsection_header("Global")
    render_config_block(RATES_CREDIT_GLOBAL, results_by_name)

    render_anchor("rates-egypt-pending")
    render_subsection_header("Egypt - Pending Validated Sources")
    st.info(
        "Egypt domestic fixed-income and sovereign-risk series are intentionally pending "
        "validated official or licensed sourcing before being added as live indicators."
    )

with vol_tab:
    render_tab_index([
        ("Global", "vol-global"),
    ])

    render_anchor("vol-global")
    render_subsection_header("Global")
    render_config_block(VOLATILITY_GLOBAL, results_by_name)

with comm_tab:
    render_tab_index([
        ("Energy", "comm-energy"),
        ("Metals", "comm-metals"),
        ("Food", "comm-food"),
    ])

    render_anchor("comm-energy")
    render_subsection_header("Energy")
    render_config_block(COMMODITIES_ENERGY, results_by_name)

    render_anchor("comm-metals")
    render_subsection_header("Metals")
    render_config_block(COMMODITIES_METALS, results_by_name)

    render_anchor("comm-food")
    render_subsection_header("Food")
    render_config_block(COMMODITIES_FOOD, results_by_name)

with domestic_tab:
    render_tab_index([
        ("Pending Validated Sources", "domestic-pending"),
    ])
    render_anchor("domestic-pending")
    render_domestic_macro_pending()

with methodology_tab:
    render_tab_index([
        ("Purpose", "methodology-purpose"),
        ("Sources", "methodology-sources"),
        ("Transformations", "methodology-transformations"),
        ("Risk Signal Logic", "methodology-risk"),
        ("Data Freshness", "methodology-freshness"),
        ("Due Diligence", "methodology-due-diligence"),
        ("Licensing", "methodology-licensing"),
        ("Next Data Upgrades", "methodology-next"),
    ])
    render_methodology()