# components/charts.py

from __future__ import annotations

from typing import Any, Dict, Optional

import altair as alt
import pandas as pd


# =========================================================
# SHARED HELPERS
# =========================================================
def _empty_chart(height: int = 120, message: str = "No data available") -> alt.Chart:
    df = pd.DataFrame({"x": [0], "y": [0], "label": [message]})
    text = alt.Chart(df).mark_text(align="center", baseline="middle", color="#9ca3af").encode(
        x=alt.value(120),
        y=alt.value(max(30, height // 2)),
        text="label:N",
    )
    return text.properties(height=height)


def _prepare_period_df(series_df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize period/value dataframe for plotting.
    Expected columns: period, value
    """
    if series_df is None or series_df.empty:
        return pd.DataFrame(columns=["period", "value"])

    if "period" not in series_df.columns or "value" not in series_df.columns:
        return pd.DataFrame(columns=["period", "value"])

    out = series_df.copy()
    out = out[out["value"].notna()].copy()
    out["period"] = out["period"].astype(str)
    return out.reset_index(drop=True)


def _prepare_time_df(series_df: pd.DataFrame) -> pd.DataFrame:
    """
    Attempt to convert period strings to a datetime field for monthly/date-like charts.
    Falls back to period strings if parsing is not possible.
    """
    df = _prepare_period_df(series_df)
    if df.empty:
        return df

    dt = pd.to_datetime(df["period"], errors="coerce")
    if dt.notna().sum() >= max(1, len(df) // 2):
        df["period_dt"] = dt
    else:
        df["period_dt"] = pd.NaT

    return df




def build_official_yoy_comparison_chart(
    latest_df: pd.DataFrame,
    comparison_df: pd.DataFrame,
    latest_label: str = "Latest",
    comparison_label: str = "YoY base",
    height: int = 220,
) -> alt.Chart:
    ldf = _prepare_period_df(latest_df)
    cdf = _prepare_period_df(comparison_df)

    if ldf.empty and cdf.empty:
        return _empty_chart(height=height, message="No comparison data")

    ldf = ldf.copy()
    ldf["series"] = latest_label
    cdf = cdf.copy()
    cdf["series"] = comparison_label

    df = pd.concat([ldf, cdf], ignore_index=True)
    df["period_dt"] = pd.to_datetime(df["period"], errors="coerce")

    use_time = df["period_dt"].notna().sum() > 0
    x = alt.X("period_dt:T", title=None) if use_time else alt.X("period:N", sort=None, title=None)

    return alt.Chart(df).mark_line(point=True, strokeWidth=2.0).encode(
        x=x,
        y=alt.Y("value:Q", title=None),
        color=alt.Color("series:N", title=None),
        tooltip=[
            alt.Tooltip("period:N", title="Period"),
            alt.Tooltip("series:N", title="Series"),
            alt.Tooltip("value:Q", title="Value", format=",.2f"),
        ],
    ).properties(height=height)


def build_snapshot_vs_history_chart(
    history_df: pd.DataFrame,
    snapshot_value: Optional[float],
    height: int = 180,
) -> alt.Chart:
    hdf = _prepare_time_df(history_df)
    if hdf.empty and snapshot_value is None:
        return _empty_chart(height=height, message="No snapshot or history")

    layers = []
    if not hdf.empty:
        y_domain = _compute_y_domain(hdf["value"])
        use_time = hdf["period_dt"].notna().sum() > 0
        x = alt.X("period_dt:T", axis=alt.Axis(title=None, labels=False, ticks=False)) if use_time else alt.X("period:N", sort=None, axis=alt.Axis(title=None, labels=False, ticks=False))
        layers.append(
            alt.Chart(hdf).mark_line(point=True, strokeWidth=2.0).encode(
                x=x,
                y=alt.Y("value:Q", axis=None, scale=alt.Scale(domain=y_domain, zero=False) if y_domain else alt.Scale(zero=False)),
                tooltip=[alt.Tooltip("period:N", title="Period"), alt.Tooltip("value:Q", title="Value", format=",.2f")],
            )
        )

    if snapshot_value is not None:
        sdf = pd.DataFrame({"snapshot": [snapshot_value]})
        layers.append(
            alt.Chart(sdf).mark_rule(strokeDash=[5, 3], color="#9ca3af", strokeWidth=1.4).encode(
                y=alt.Y("snapshot:Q")
            )
        )

    return alt.layer(*layers).properties(height=height)

def _compute_y_domain(values: pd.Series, pad_ratio: float = 0.12) -> Optional[list[float]]:
    values = values.dropna()
    if values.empty:
        return None

    y_min = float(values.min())
    y_max = float(values.max())

    if y_min == y_max:
        return [y_min - 1, y_max + 1]

    pad = (y_max - y_min) * pad_ratio
    return [y_min - pad, y_max + pad]


# =========================================================
# LIVE SPARKLINE
# =========================================================
def build_sparkline(
    chart_df: pd.DataFrame,
    average_value: Optional[float] = None,
    positive: Optional[bool] = None,
    value_col: str = "Close",
    date_col: str = "Date",
    height: int = 110,
) -> alt.Chart:
    """
    Build a compact sparkline for live market cards.

    Expected chart_df columns:
    - Date
    - Close
    """
    if chart_df is None or chart_df.empty or value_col not in chart_df.columns:
        return _empty_chart(height=height, message="No data available")

    df = chart_df.copy()
    df = df[[date_col, value_col]].dropna().copy()

    if df.empty:
        return _empty_chart(height=height, message="No data available")

    y_domain = _compute_y_domain(df[value_col])

    line_color = "#6b7280"
    if positive is True:
        line_color = "#16a34a"
    elif positive is False:
        line_color = "#dc2626"

    base = alt.Chart(df)

    line = base.mark_line(
        strokeWidth=2.2,
        color=line_color,
    ).encode(
        x=alt.X(f"{date_col}:T", axis=None),
        y=alt.Y(
            f"{value_col}:Q",
            axis=None,
            scale=alt.Scale(domain=y_domain, zero=False) if y_domain else alt.Scale(zero=False),
        ),
        tooltip=[
            alt.Tooltip(f"{date_col}:T", title="Date"),
            alt.Tooltip(f"{value_col}:Q", title="Value", format=",.4f"),
        ],
    )

    layers = [line]

    if average_value is not None:
        avg_df = pd.DataFrame({"avg": [average_value]})
        avg_rule = alt.Chart(avg_df).mark_rule(
            strokeDash=[4, 4],
            color="#9ca3af",
            strokeWidth=1.0,
        ).encode(
            y=alt.Y(
                "avg:Q",
                scale=alt.Scale(domain=y_domain, zero=False) if y_domain else alt.Scale(zero=False),
            )
        )
        layers.append(avg_rule)

    return alt.layer(*layers).properties(height=height)


# =========================================================
# OFFICIAL TREND CHARTS
# =========================================================
def build_official_trend_chart(
    series_df: pd.DataFrame,
    title: Optional[str] = None,
    height: int = 150,
    as_bar: bool = False,
    value_format: str = ",.2f",
) -> alt.Chart:
    """
    Standard compact trend chart for official indicator cards.
    Works for monthly/quarterly/annual series.

    Input columns:
    - period
    - value
    """
    df = _prepare_time_df(series_df)
    if df.empty:
        return _empty_chart(height=height, message="No data available")

    y_domain = _compute_y_domain(df["value"])

    use_time = df["period_dt"].notna().sum() > 0

    if use_time:
        x = alt.X("period_dt:T", axis=alt.Axis(title=None, labels=False, ticks=False))
        tooltip_period = alt.Tooltip("period:N", title="Period")
    else:
        x = alt.X("period:N", sort=None, axis=alt.Axis(title=None, labels=False, ticks=False))
        tooltip_period = alt.Tooltip("period:N", title="Period")

    base = alt.Chart(df)

    if as_bar:
        chart = base.mark_bar(cornerRadiusTopLeft=2, cornerRadiusTopRight=2).encode(
            x=x,
            y=alt.Y(
                "value:Q",
                axis=None,
                scale=alt.Scale(domain=y_domain, zero=False) if y_domain else alt.Scale(zero=False),
            ),
            tooltip=[
                tooltip_period,
                alt.Tooltip("value:Q", title="Value", format=value_format),
            ],
        )
    else:
        chart = base.mark_line(point=True, strokeWidth=2.0).encode(
            x=x,
            y=alt.Y(
                "value:Q",
                axis=None,
                scale=alt.Scale(domain=y_domain, zero=False) if y_domain else alt.Scale(zero=False),
            ),
            tooltip=[
                tooltip_period,
                alt.Tooltip("value:Q", title="Value", format=value_format),
            ],
        )

    if title:
        chart = chart.properties(title=title)

    return chart.properties(height=height)


def build_dual_series_chart(
    left_df: pd.DataFrame,
    right_df: pd.DataFrame,
    left_label: str = "Left",
    right_label: str = "Right",
    height: int = 220,
) -> alt.Chart:
    """
    General-purpose dual-series line chart for comparable official series.
    Both inputs must contain: period, value
    """
    ldf = _prepare_period_df(left_df)
    rdf = _prepare_period_df(right_df)

    if ldf.empty and rdf.empty:
        return _empty_chart(height=height, message="No data available")

    ldf = ldf.copy()
    ldf["series"] = left_label
    rdf = rdf.copy()
    rdf["series"] = right_label

    df = pd.concat([ldf, rdf], ignore_index=True)
    df["period_dt"] = pd.to_datetime(df["period"], errors="coerce")

    use_time = df["period_dt"].notna().sum() > 0

    if use_time:
        x = alt.X("period_dt:T", title=None)
        tooltip_period = alt.Tooltip("period:N", title="Period")
    else:
        x = alt.X("period:N", sort=None, title=None)
        tooltip_period = alt.Tooltip("period:N", title="Period")

    return alt.Chart(df).mark_line(point=True, strokeWidth=2.0).encode(
        x=x,
        y=alt.Y("value:Q", title=None),
        color=alt.Color("series:N", title=None),
        tooltip=[
            tooltip_period,
            alt.Tooltip("series:N", title="Series"),
            alt.Tooltip("value:Q", title="Value", format=",.2f"),
        ],
    ).properties(height=height)


# =========================================================
# EXTERNAL BALANCE CHARTS
# =========================================================
def build_trade_balance_chart(
    exports_df: pd.DataFrame,
    imports_df: pd.DataFrame,
    trade_balance_df: Optional[pd.DataFrame] = None,
    height: int = 240,
) -> alt.Chart:
    """
    Comparison chart for exports vs imports, with optional trade balance overlay.
    """
    edf = _prepare_period_df(exports_df)
    idf = _prepare_period_df(imports_df)

    if edf.empty and idf.empty:
        return _empty_chart(height=height, message="No data available")

    edf = edf.copy()
    edf["series"] = "Exports"

    idf = idf.copy()
    idf["series"] = "Imports"

    combined = pd.concat([edf, idf], ignore_index=True)
    combined["period_dt"] = pd.to_datetime(combined["period"], errors="coerce")
    use_time = combined["period_dt"].notna().sum() > 0

    if use_time:
        x = alt.X("period_dt:T", title=None)
        tooltip_period = alt.Tooltip("period:N", title="Period")
    else:
        x = alt.X("period:N", sort=None, title=None)
        tooltip_period = alt.Tooltip("period:N", title="Period")

    bars = alt.Chart(combined).mark_bar(opacity=0.85).encode(
        x=x,
        y=alt.Y("value:Q", title="Exports / Imports"),
        color=alt.Color("series:N", title=None),
        xOffset="series:N",
        tooltip=[
            tooltip_period,
            alt.Tooltip("series:N", title="Series"),
            alt.Tooltip("value:Q", title="Value", format=",.2f"),
        ],
    )

    layers = [bars]

    if trade_balance_df is not None:
        tdf = _prepare_period_df(trade_balance_df)
        if not tdf.empty:
            tdf["period_dt"] = pd.to_datetime(tdf["period"], errors="coerce")

            trade_x = alt.X("period_dt:T", title=None) if use_time else alt.X("period:N", sort=None, title=None)

            trade_line = alt.Chart(tdf).mark_line(
                point=True,
                strokeWidth=2.0,
                strokeDash=[5, 3],
            ).encode(
                x=trade_x,
                y=alt.Y("value:Q", title="Trade Balance"),
                tooltip=[
                    alt.Tooltip("period:N", title="Period"),
                    alt.Tooltip("value:Q", title="Trade Balance", format=",.2f"),
                ],
            )
            layers.append(trade_line)

    return alt.layer(*layers).resolve_scale(y="independent").properties(height=height)


def build_reserves_chart(series_df: pd.DataFrame, height: int = 220) -> alt.Chart:
    """
    Simple reserves trend chart.
    """
    return build_official_trend_chart(
        series_df=series_df,
        height=height,
        as_bar=False,
        value_format=",.1f",
    )


# =========================================================
# INFLATION / CATEGORY CHARTS
# =========================================================
def build_inflation_composition_chart(
    weights_df: pd.DataFrame,
    snapshot_df: Optional[pd.DataFrame] = None,
    height: int = 280,
) -> alt.Chart:
    """
    Main chart for the Domestic Price Pressure section.

    If snapshot_df is provided and includes:
    - category
    - mar_2026
    - weight_pct
    then chart category inflation with size/context from weights.

    Otherwise, fall back to CPI weights only.
    """
    if snapshot_df is not None and not snapshot_df.empty:
        df = snapshot_df.copy()

        if "category" in df.columns and "mar_2026" in df.columns:
            sort_order = list(df.sort_values("weight_pct", ascending=False)["category"])

            bars = alt.Chart(df).mark_bar().encode(
                x=alt.X("mar_2026:Q", title="Inflation (%)"),
                y=alt.Y("category:N", sort=sort_order, title=None),
                tooltip=[
                    alt.Tooltip("category:N", title="Category"),
                    alt.Tooltip("mar_2026:Q", title="Mar 2026", format=",.2f"),
                    alt.Tooltip("mar_2025:Q", title="Mar 2025", format=",.2f"),
                    alt.Tooltip("weight_pct:Q", title="Weight", format=",.2f"),
                ],
            )

            text = alt.Chart(df).mark_text(
                align="left",
                baseline="middle",
                dx=4,
            ).encode(
                x="mar_2026:Q",
                y=alt.Y("category:N", sort=sort_order),
                text=alt.Text("mar_2026:Q", format=",.1f"),
            )

            return alt.layer(bars, text).properties(height=height)

    if weights_df is None or weights_df.empty:
        return _empty_chart(height=height, message="No data available")

    df = weights_df.copy()
    sort_order = list(df.sort_values("weight_pct", ascending=False)["category"])

    return alt.Chart(df).mark_bar().encode(
        x=alt.X("weight_pct:Q", title="Weight (%)"),
        y=alt.Y("category:N", sort=sort_order, title=None),
        tooltip=[
            alt.Tooltip("category:N", title="Category"),
            alt.Tooltip("weight_pct:Q", title="Weight", format=",.2f"),
        ],
    ).properties(height=height)


def build_category_snapshot_chart(
    snapshot_df: pd.DataFrame,
    value_col: str = "mar_2026",
    height: int = 220,
) -> alt.Chart:
    """
    Compact ranked bar chart for top category inflation snapshot.
    """
    if snapshot_df is None or snapshot_df.empty or value_col not in snapshot_df.columns:
        return _empty_chart(height=height, message="No data available")

    df = snapshot_df.copy()
    df = df[df[value_col].notna()].copy()
    df = df.sort_values(value_col, ascending=False)

    return alt.Chart(df).mark_bar().encode(
        x=alt.X(f"{value_col}:Q", title="Inflation (%)"),
        y=alt.Y("category:N", sort="-x", title=None),
        tooltip=[
            alt.Tooltip("category:N", title="Category"),
            alt.Tooltip(f"{value_col}:Q", title="Value", format=",.2f"),
            alt.Tooltip("weight_pct:Q", title="Weight", format=",.2f"),
        ],
    ).properties(height=height)


def build_cpi_mom_chart(series_df: pd.DataFrame, height: int = 200) -> alt.Chart:
    """
    Month-on-month CPI chart.
    """
    return build_official_trend_chart(
        series_df=series_df,
        height=height,
        as_bar=True,
        value_format=",.2f",
    )


# =========================================================
# SMALL TABLE-LIKE CHART OPTION
# =========================================================
def build_top_categories_table_df(
    snapshot_df: pd.DataFrame,
    sort_col: str = "mar_2026",
    top_n: int = 3,
) -> pd.DataFrame:
    """
    Returns a compact dataframe suitable for display in a table-like component.
    """
    if snapshot_df is None or snapshot_df.empty or sort_col not in snapshot_df.columns:
        return pd.DataFrame(columns=["category", sort_col, "weight_pct"])

    df = snapshot_df.copy()
    df = df[df[sort_col].notna()].copy()
    df = df.sort_values(sort_col, ascending=False).head(top_n)
    return df[["category", sort_col, "weight_pct"]].reset_index(drop=True)