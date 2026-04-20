# components/cards.py

from __future__ import annotations

from typing import Any, Dict, Optional

import pandas as pd
import streamlit as st

from config import INDICATOR_COMPARISON_POLICY, DATA_STATUS_LABELS


# =========================================================
# LOW-LEVEL FORMATTERS
# =========================================================
def format_number(value: Optional[float], decimals: int = 2) -> str:
    if value is None or pd.isna(value):
        return "N/A"
    return f"{value:,.{decimals}f}"


def format_percent(value: Optional[float], decimals: int = 2, signed: bool = False) -> str:
    if value is None or pd.isna(value):
        return "N/A"
    if signed:
        return f"{value:+,.{decimals}f}%"
    return f"{value:,.{decimals}f}%"


def format_change_value(value: Optional[float], decimals: int = 2, suffix: str = "") -> str:
    if value is None or pd.isna(value):
        return "N/A"
    return f"{value:+,.{decimals}f}{suffix}"


def format_main_value(value: Optional[float], unit: str, decimals: int = 2) -> str:
    if value is None or pd.isna(value):
        return "N/A"
    if unit == "%":
        return f"{value:,.{decimals}f}%"
    return f"{value:,.{decimals}f}"


def get_delta_class(value: Optional[float], inverse_good: bool = False) -> str:
    if value is None or pd.isna(value):
        return "neutral"
    if inverse_good:
        if value < 0:
            return "positive"
        if value > 0:
            return "negative"
        return "neutral"
    if value > 0:
        return "positive"
    if value < 0:
        return "negative"
    return "neutral"


def get_assessment_class(level: str) -> str:
    mapping = {
        "Low": "assessment-low",
        "Medium": "assessment-medium",
        "High": "assessment-high",
    }
    return mapping.get(level, "assessment-medium")


# =========================================================
# BADGES / META
# =========================================================
def render_badge(text: str, kind: str = "default") -> str:
    kind_class = {
        "tag": "badge-tag",
        "frequency": "badge-frequency",
        "source": "badge-source",
        "status": "badge-status",
        "default": "badge-default",
    }.get(kind, "badge-default")
    return f'<span class="dashboard-badge {kind_class}">{text}</span>'


def render_badge_row(
    tag: Optional[str] = None,
    frequency: Optional[str] = None,
    source: Optional[str] = None,
) -> str:
    parts = []
    if tag:
        parts.append(render_badge(tag, "tag"))
    if frequency:
        parts.append(render_badge(frequency, "frequency"))
    if source:
        parts.append(render_badge(source, "source"))
    return " ".join(parts)


def render_reference_line(reference_period: Optional[str], previous_period: Optional[str]) -> str:
    if reference_period and previous_period:
        return f"Latest: {reference_period} · Prev: {previous_period}"
    if reference_period:
        return f"Latest: {reference_period}"
    return "Reference period unavailable"




def render_yoy_line(indicator: Dict[str, Any], decimals: int = 2) -> str:
    yoy_value = indicator.get("yoy_value")
    yoy_period = indicator.get("yoy_period")
    yoy_change_value = indicator.get("yoy_change_value")
    yoy_change_pct = indicator.get("yoy_change_pct")
    unit = indicator.get("unit", "")

    if yoy_period is None and (yoy_value is None or pd.isna(yoy_value)):
        return "YoY: N/A"

    if yoy_value is None or pd.isna(yoy_value):
        return f"YoY vs {yoy_period or 'same period last year'}: N/A"

    base_text = format_main_value(yoy_value, unit=unit, decimals=decimals)

    if yoy_change_value is None or pd.isna(yoy_change_value):
        return f"YoY base ({yoy_period or 'same period last year'}): {base_text}"

    suffix = "%" if unit == "%" else ""
    delta_text = format_change_value(yoy_change_value, decimals=decimals, suffix=suffix)

    if yoy_change_pct is None or pd.isna(yoy_change_pct):
        return f"YoY vs {yoy_period or 'same period last year'}: {base_text} · {delta_text}"

    return f"YoY vs {yoy_period or 'same period last year'}: {base_text} · {delta_text} ({yoy_change_pct:+.2f}%)"



def render_status_line(indicator: Dict[str, Any]) -> str:
    status = str(indicator.get("data_status", "placeholder"))
    label = DATA_STATUS_LABELS.get(status, status.replace("_", " ").title())
    return f"Data status: {label}"


def render_card_header(
    title: str,
    tag: Optional[str] = None,
    frequency: Optional[str] = None,
    source: Optional[str] = None,
    subtitle: Optional[str] = None,
) -> None:
    badge_row = render_badge_row(tag=tag, frequency=frequency, source=source)
    st.markdown(
        f"""
        <div class="card-header">
            <div class="card-title">{title}</div>
            <div class="card-badges">{badge_row}</div>
            {f'<div class="card-subtitle">{subtitle}</div>' if subtitle else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# LIVE CARD
# =========================================================
def render_live_card(
    indicator: Dict[str, Any],
    sparkline_chart=None,
    decimals: Optional[int] = None,
    inverse_good: bool = False,
) -> None:
    title = indicator.get("title", "Untitled")
    tag = indicator.get("tag", "Live")
    frequency = indicator.get("frequency", "Daily")
    source = indicator.get("source")
    unit = indicator.get("unit", "")
    latest_value = indicator.get("latest_value")
    change_value = indicator.get("change_value")
    change_pct = indicator.get("change_pct")
    description = indicator.get("description")
    reference_period = indicator.get("reference_period")

    d = decimals if decimals is not None else indicator.get("decimals", 2)
    delta_class = get_delta_class(change_value, inverse_good=inverse_good)

    latest_text = format_main_value(latest_value, unit=unit, decimals=d)

    if change_value is None or pd.isna(change_value) or change_pct is None or pd.isna(change_pct):
        change_text = "N/A"
    else:
        suffix = "%" if unit == "%" else ""
        change_text = f"{format_change_value(change_value, decimals=d, suffix=suffix)} ({change_pct:+.2f}%)"

    with st.container(border=True):
        render_card_header(
            title=title,
            tag=tag,
            frequency=frequency,
            source=source,
            subtitle=description,
        )
        st.markdown(
            f"""
            <div class="card-main-value">{latest_text}</div>
            <div class="card-secondary {delta_class}">{change_text}</div>
            <div class="card-meta">{reference_period or "Latest available"}</div>
            """,
            unsafe_allow_html=True,
        )
        if sparkline_chart is not None:
            st.altair_chart(sparkline_chart, width="stretch")
        else:
            st.markdown('<div class="card-chart-placeholder">No chart available</div>', unsafe_allow_html=True)


# =========================================================
# OFFICIAL CARD
# =========================================================
def render_official_card(
    indicator: Dict[str, Any],
    trend_chart=None,
    decimals: int = 2,
    inverse_good: bool = False,
) -> None:
    title = indicator.get("title", "Untitled")
    indicator_id = indicator.get("id", "")
    policy = INDICATOR_COMPARISON_POLICY.get(indicator_id, {})
    tag = indicator.get("tag", "Official")
    frequency = indicator.get("frequency")
    source = indicator.get("source")
    unit = indicator.get("unit", "")
    latest_value = indicator.get("latest_value")
    previous_value = indicator.get("previous_value")
    change_value = indicator.get("change_value")
    change_pct = indicator.get("change_pct")
    reference_period = indicator.get("reference_period")
    previous_period = indicator.get("previous_period")
    description = indicator.get("description")
    notes = indicator.get("notes")
    snapshot_note = None

    delta_class = get_delta_class(change_value, inverse_good=inverse_good)
    main_text = format_main_value(latest_value, unit=unit, decimals=decimals)

    compare_text = ""
    if previous_value is not None and pd.notna(previous_value):
        prev_text = format_main_value(previous_value, unit=unit, decimals=decimals)
        if change_value is None or pd.isna(change_value):
            compare_text = f"Prev: {prev_text}"
        else:
            compare_text = f"Prev: {prev_text} · {format_change_value(change_value, decimals=decimals)}"

    pct_text = ""
    if compare_text and change_pct is not None and pd.notna(change_pct):
        pct_text = f" ({change_pct:+.2f}%)"

    meta_lines = [f'<div class="card-meta">{render_reference_line(reference_period, previous_period)}</div>']

    if policy.get("show_yoy", False):
        yoy_line = render_yoy_line(indicator, decimals=decimals)
        if yoy_line and "N/A" not in yoy_line:
            meta_lines.append(f'<div class="card-meta">{yoy_line}</div>')

    status_line = render_status_line(indicator)
    if status_line:
        meta_lines.append(f'<div class="card-meta">{status_line}</div>')

    with st.container(border=True):
        render_card_header(
            title=title,
            tag=tag,
            frequency=frequency,
            source=source,
            subtitle=description,
        )
        st.markdown(
            f"""
            <div class="card-main-value">{main_text}</div>
            {f'<div class="card-secondary {delta_class}">{compare_text}{pct_text}</div>' if compare_text else ''}
            {''.join(meta_lines)}
            """,
            unsafe_allow_html=True,
        )
        if trend_chart is not None:
            st.altair_chart(trend_chart, width="stretch")
        else:
            st.markdown('<div class="card-chart-placeholder">No trend chart available</div>', unsafe_allow_html=True)

        if notes:
            st.markdown(f'<div class="card-note">{notes}</div>', unsafe_allow_html=True)


# =========================================================
# ASSESSMENT CARD
# =========================================================
def render_assessment_card(item: Dict[str, Any]) -> None:
    title = item.get("title", "Untitled")
    level = item.get("level", "Medium")
    direction = item.get("direction", "Stable")
    reason = item.get("reason", "")
    tag = item.get("tag", "Assessment")
    assessment_class = get_assessment_class(level)

    with st.container(border=True):
        render_card_header(title=title, tag=tag)
        st.markdown(
            f"""
            <div class="{assessment_class}">
                <div class="assessment-main-row">
                    <div class="assessment-level">{level}</div>
                    <div class="assessment-direction">{direction}</div>
                </div>
                <div class="assessment-reason">{reason}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# =========================================================
# SCENARIO CARD
# =========================================================
def render_scenario_card(item: Dict[str, Any]) -> None:
    title = item.get("title", "Scenario")
    subtitle = item.get("subtitle", "")
    tag = item.get("tag", "Scenario")

    closest_badge = ""
    if item.get("closest_to_current_path"):
        closest_badge = render_badge("Closest to current path", "status")

    with st.container(border=True):
        render_card_header(
            title=title,
            tag=tag,
            subtitle=subtitle,
        )
        st.markdown(
            f"""
            <div class="scenario-highlight">{closest_badge}</div>
            <div class="scenario-grid">
                <div><strong>Oil:</strong> ${item.get("oil_price", "N/A")}</div>
                <div><strong>Wheat:</strong> {format_percent(item.get("wheat_change_pct"), 0, signed=True)}</div>
                <div><strong>FX:</strong> {format_percent(item.get("fx_change_pct"), 0, signed=True)}</div>
                <div><strong>Tourism:</strong> {format_percent(item.get("tourism_change_pct"), 0, signed=True)}</div>
                <div><strong>Remittances:</strong> {format_percent(item.get("remittances_change_pct"), 0, signed=True)}</div>
                <div><strong>Growth impact:</strong> {item.get("growth_impact_pp", "N/A")} pp</div>
                <div><strong>Growth result:</strong> {item.get("growth_result_pct", "N/A")}%</div>
            </div>
            <div class="scenario-note">{item.get("inflation_effect_text", "")}</div>
            <div class="scenario-note secondary">{item.get("inflation_peak_text", "")}</div>
            """,
            unsafe_allow_html=True,
        )


# =========================================================
# POLICY CARD
# =========================================================
def render_policy_card(item: Dict[str, Any]) -> None:
    title = item.get("title", "Policy Case")
    tag = item.get("tag", "Policy")
    one_day = item.get("one_day_savings_pct")
    two_day = item.get("two_day_savings_pct")

    with st.container(border=True):
        render_card_header(
            title=title,
            tag=tag,
            subtitle="Estimated fuel savings under remote-work assumptions",
        )
        st.markdown(
            f"""
            <div class="policy-metric-row">
                <div class="policy-metric-label">One day remote work</div>
                <div class="policy-metric-value">{format_percent(one_day, 2)}</div>
            </div>
            <div class="policy-metric-row">
                <div class="policy-metric-label">Two days remote work</div>
                <div class="policy-metric-value">{format_percent(two_day, 2)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# =========================================================
# NARRATIVE / SUPPORT CARDS
# =========================================================
def render_insight_bar(text: str, tag: str = "Assessment") -> None:
    st.markdown(
        f"""
        <div class="insight-bar">
            <div class="insight-bar-badge">{render_badge(tag, "tag")}</div>
            <div class="insight-bar-text">{text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_commentary_panel(title: str, bullets: list[str], tag: str = "Assessment") -> None:
    bullet_html = "".join(f"<li>{b}</li>" for b in bullets[:3])

    with st.container(border=True):
        render_card_header(title=title, tag=tag)
        st.markdown(
            f"""
            <div class="commentary-list">
                <ul>{bullet_html}</ul>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_simple_stat_panel(
    title: str,
    stats: Dict[str, Any],
    tag: str = "Policy",
    subtitle: Optional[str] = None,
) -> None:
    rows = []
    for label, value in stats.items():
        rows.append(
            f"""
            <div class="stat-panel-row">
                <div class="stat-panel-label">{label}</div>
                <div class="stat-panel-value">{value}</div>
            </div>
            """
        )

    with st.container(border=True):
        render_card_header(
            title=title,
            tag=tag,
            subtitle=subtitle,
        )
        st.markdown("".join(rows), unsafe_allow_html=True)