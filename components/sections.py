from __future__ import annotations

from typing import Any, Dict, List, Optional, Callable

import pandas as pd
import streamlit as st

from config import (
    DATA_TAGS,
    EXECUTIVE_STRESS_ITEMS,
    FOOTER_LIMITATIONS,
    FOOTER_SOURCE_GUIDE,
    HOUSEHOLD_SAVINGS_CONFIG,
    BUDGET_SAVINGS_CONFIG,
    INSIGHT_BARS,
    INTERNATIONAL_RESPONSE_BUCKETS,
    MITIGATION_CONFIG,
    PAGE_SUBTITLE,
    PAGE_TITLE,
    SCENARIO_CONFIG,
    SCENARIO_LABEL_STRIP,
    SECTION_INDICATORS,
    SECTION_TITLES,
    TRANSMISSION_BUCKETS,
    TRANSMISSION_FLOW,
)
from components.cards import (
    render_assessment_card,
    render_commentary_panel,
    render_insight_bar,
    render_live_card,
    render_official_card,
    render_policy_card,
    render_scenario_card,
    render_simple_stat_panel,
)
from components.charts import (
    build_category_snapshot_chart,
    build_cpi_mom_chart,
    build_inflation_composition_chart,
    build_official_trend_chart,
    build_reserves_chart,
    build_sparkline,
    build_top_categories_table_df,
    build_trade_balance_chart,
)


def render_section_header(title: str, subtitle: Optional[str] = None) -> None:
    st.markdown(
        f"""
        <div class="section-header-wrap">
            <div class="section-header-title">{title}</div>
            {f'<div class="section-header-subtitle">{subtitle}</div>' if subtitle else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_badge_strip(items: List[str]) -> None:
    html = "".join([f'<span class="dashboard-badge badge-tag">{item}</span>' for item in items])
    st.markdown(f'<div class="badge-strip">{html}</div>', unsafe_allow_html=True)


def get_indicator(indicators: Dict[str, Dict[str, Any]], key: str) -> Dict[str, Any]:
    return indicators.get(key, {})


def safe_df_from_indicator(indicator: Dict[str, Any], key: str = "series") -> pd.DataFrame:
    value = indicator.get(key)
    if isinstance(value, pd.DataFrame):
        return value
    return pd.DataFrame()


def render_reference_table(df: pd.DataFrame, value_col: str, title: str) -> None:
    if df is None or df.empty:
        st.caption(f"{title}: no data available")
        return

    show_df = df.copy()
    if value_col in show_df.columns:
        show_df[value_col] = show_df[value_col].map(lambda x: f"{x:,.2f}" if pd.notna(x) else "N/A")
    st.markdown(f"**{title}**")
    st.dataframe(show_df, width="stretch", hide_index=True)


def _render_live_indicator_row(keys: List[str], live_data: Dict[str, Dict[str, Any]], ncols: int, chart_height: int = 105) -> None:
    cols = st.columns(ncols, gap="medium")
    for col, key in zip(cols, keys):
        indicator = get_indicator(live_data, key)
        spark_df = indicator.get("sparkline_df", pd.DataFrame())
        avg = indicator.get("average_value")
        pos = None if indicator.get("change_value") is None else indicator["change_value"] >= 0

        chart = build_sparkline(
            chart_df=spark_df,
            average_value=avg,
            positive=pos,
            value_col="Close",
            date_col="Date",
            height=chart_height,
        )
        with col:
            render_live_card(
                indicator=indicator,
                sparkline_chart=chart,
                decimals=indicator.get("decimals", 2),
            )


def _render_official_indicator_row(
    keys: List[str],
    official_data: Dict[str, Dict[str, Any]],
    ncols: int,
    chart_height: int = 120,
    as_bar_map: Optional[Dict[str, bool]] = None,
) -> None:
    cols = st.columns(ncols, gap="medium")
    for col, key in zip(cols, keys):
        indicator = get_indicator(official_data, key)
        chart = build_official_trend_chart(
            series_df=safe_df_from_indicator(indicator),
            height=chart_height,
            as_bar=(as_bar_map or {}).get(key, False),
            value_format=",.2f",
        )
        with col:
            render_official_card(indicator=indicator, trend_chart=chart, decimals=2)


def _render_box_row(items: List[Dict[str, Any]], ncols: int, renderer: Callable[[Dict[str, Any]], None]) -> None:
    cols = st.columns(ncols, gap="medium")
    for col, item in zip(cols, items):
        with col:
            renderer(item)


def render_header(selected_window_label: str) -> None:
    left, right = st.columns([6, 2])

    with left:
        st.title(PAGE_TITLE)
        st.caption(PAGE_SUBTITLE)
        st.markdown(
            """
            <div class="header-framing-line">
                Hybrid dashboard using live markets, official Egypt indicators,
                assessment blocks, scenario framing, and policy options.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
            f"""
            <div class="header-controls-card">
                <div><strong>Last updated</strong></div>
                <div>{pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}</div>
                <div style="margin-top:0.5rem;"><strong>Sparkline window</strong></div>
                <div>{selected_window_label}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    render_badge_strip(DATA_TAGS)


def render_executive_stress_strip(assessment_items: Dict[str, Dict[str, Any]]) -> None:
    render_section_header("Executive Stress Strip", "A quick synthesis of the main pressure points.")
    for start in range(0, len(EXECUTIVE_STRESS_ITEMS), 3):
        row_keys = EXECUTIVE_STRESS_ITEMS[start:start + 3]
        cols = st.columns(len(row_keys), gap="medium")
        for col, key in zip(cols, row_keys):
            with col:
                render_assessment_card(assessment_items.get(key, {
                    "title": key,
                    "tag": "Assessment",
                    "level": "Medium",
                    "direction": "Stable",
                    "reason": "No assessment available.",
                }))
    st.divider()


def render_immediate_shock_section(live_data: Dict[str, Dict[str, Any]]) -> None:
    render_section_header(SECTION_TITLES["immediate_shock"], "External market signals shaping the shock environment.")
    _render_live_indicator_row(SECTION_INDICATORS["immediate_shock"], live_data, ncols=6, chart_height=105)
    st.divider()


def render_egypt_reaction_section(reaction_data: Dict[str, Dict[str, Any]]) -> None:
    render_section_header(SECTION_TITLES["egypt_reaction"], "How Egyptian markets and macro indicators are reacting.")

    row1 = SECTION_INDICATORS["egypt_reaction_row1"]
    live_keys = [k for k in row1 if get_indicator(reaction_data, k).get("tag") == "Live"]
    official_keys = [k for k in row1 if get_indicator(reaction_data, k).get("tag") != "Live"]

    if live_keys:
        _render_live_indicator_row(live_keys, reaction_data, ncols=len(live_keys), chart_height=105)
    if official_keys:
        _render_official_indicator_row(official_keys, reaction_data, ncols=len(official_keys), chart_height=120)

    if SECTION_INDICATORS["egypt_reaction_row2"]:
        _render_official_indicator_row(
            SECTION_INDICATORS["egypt_reaction_row2"],
            reaction_data,
            ncols=max(1, len(SECTION_INDICATORS["egypt_reaction_row2"])),
            chart_height=120,
        )
    st.divider()


def render_transmission_section() -> None:
    render_section_header(SECTION_TITLES["transmission_map"], "How the regional shock travels into the Egyptian economy.")
    flow_html = " <span class='flow-arrow'>→</span> ".join([f"<span class='flow-node'>{node}</span>" for node in TRANSMISSION_FLOW])
    st.markdown(f'<div class="transmission-flow">{flow_html}</div>', unsafe_allow_html=True)

    cols = st.columns(4, gap="medium")
    for col, bucket in zip(cols, TRANSMISSION_BUCKETS):
        with col:
            st.markdown(
                f"""
                <div class="transmission-bucket">
                    <div class="transmission-bucket-title">{bucket['title']}</div>
                    <div class="transmission-bucket-text">{bucket['summary']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    st.divider()


def render_external_inflows_section(inflow_data: Dict[str, Dict[str, Any]]) -> None:
    render_section_header(SECTION_TITLES["external_inflows"], "The clearest direct channels through which the crisis can affect Egypt.")
    _render_official_indicator_row(SECTION_INDICATORS["external_inflows"], inflow_data, ncols=4, chart_height=125)
    render_insight_bar(INSIGHT_BARS["external_inflows"], tag="Assessment")
    st.divider()


def _render_external_balance_top_row(balance_data: Dict[str, Dict[str, Any]]) -> None:
    _render_official_indicator_row(SECTION_INDICATORS["external_balance"], balance_data, ncols=4, chart_height=125)


def _render_external_balance_detail_panel(balance_data: Dict[str, Dict[str, Any]]) -> None:
    lower_left, lower_right = st.columns([2, 1], gap="large")

    exports_df = safe_df_from_indicator(balance_data.get("exports", {}))
    imports_df = safe_df_from_indicator(balance_data.get("imports", {}))
    trade_df = safe_df_from_indicator(balance_data.get("trade_balance", {}))
    reserves_df = safe_df_from_indicator(balance_data.get("net_reserves", {}))

    with lower_left:
        st.markdown("**External Balance Trend**")
        trade_chart = build_trade_balance_chart(exports_df=exports_df, imports_df=imports_df, trade_balance_df=trade_df, height=260)
        st.altair_chart(trade_chart, width="stretch")

        if not reserves_df.empty:
            st.markdown("**Reserves Trend**")
            reserves_chart = build_reserves_chart(reserves_df, height=220)
            st.altair_chart(reserves_chart, width="stretch")

    with lower_right:
        render_commentary_panel(
            "Balance Commentary",
            bullets=[
                "Monitor whether import pressure is outpacing export adjustment.",
                "Trade balance gives the clearest short-cycle external stress signal.",
                "Reserves provide the main official resilience buffer.",
            ],
            tag="Assessment",
        )


def render_external_balance_section(balance_data: Dict[str, Dict[str, Any]]) -> None:
    render_section_header(SECTION_TITLES["external_balance"], "Trade and reserves indicators showing external resilience and strain.")
    _render_external_balance_top_row(balance_data)
    _render_external_balance_detail_panel(balance_data)
    st.divider()


def render_business_activity_section(business_data: Dict[str, Dict[str, Any]]) -> None:
    render_section_header(SECTION_TITLES["business_activity"], "Confidence, investment appetite, and domestic private-sector activity.")
    _render_official_indicator_row(
        SECTION_INDICATORS["business_activity"],
        business_data,
        ncols=3,
        chart_height=130,
        as_bar_map={"companies_established": True, "issued_capital": True},
    )
    render_insight_bar(INSIGHT_BARS["business_activity"], tag="Assessment")
    st.divider()


def render_domestic_price_pressure_section(price_data: Dict[str, Any]) -> None:
    render_section_header(SECTION_TITLES["domestic_price_pressure"], "How external shocks are filtering into domestic inflation structure.")

    left, middle, right = st.columns([1, 1, 2], gap="medium")
    food_indicator = price_data.get("food_inflation", {})
    cpi_weights_df = price_data.get("cpi_weights", pd.DataFrame())
    category_snapshot_df = price_data.get("category_inflation_snapshot", pd.DataFrame())
    cpi_mom_df = price_data.get("cpi_monthly_mom", pd.DataFrame())

    with left:
        chart = build_official_trend_chart(series_df=safe_df_from_indicator(food_indicator), height=125, as_bar=False, value_format=",.2f")
        render_official_card(indicator=food_indicator, trend_chart=chart, decimals=2)

    with middle:
        st.markdown("**Category Inflation Snapshot**")
        snapshot_chart = build_category_snapshot_chart(snapshot_df=category_snapshot_df, value_col="mar_2026", height=240)
        st.altair_chart(snapshot_chart, width="stretch")
        top_df = build_top_categories_table_df(snapshot_df=category_snapshot_df, sort_col="mar_2026", top_n=3)
        render_reference_table(top_df, "mar_2026", "Top 3 categories")

    with right:
        st.markdown("**Inflation Composition**")
        composition_chart = build_inflation_composition_chart(weights_df=cpi_weights_df, snapshot_df=category_snapshot_df, height=300)
        st.altair_chart(composition_chart, width="stretch")
        if isinstance(cpi_mom_df, pd.DataFrame) and not cpi_mom_df.empty:
            st.markdown("**Monthly CPI Momentum**")
            mom_chart = build_cpi_mom_chart(cpi_mom_df, height=180)
            st.altair_chart(mom_chart, width="stretch")

    render_insight_bar(INSIGHT_BARS["domestic_price_pressure"], tag="Assessment")
    st.divider()


def render_scenario_snapshot_section() -> None:
    render_section_header(SECTION_TITLES["scenario_snapshot"], "Structured scenario framing based on the uploaded crisis deck.")
    _render_box_row(SCENARIO_CONFIG, 4, render_scenario_card)
    label_html = "".join([f'<span class="scenario-strip-label">{label}</span>' for label in SCENARIO_LABEL_STRIP])
    st.markdown(f'<div class="scenario-label-strip">{label_html}</div>', unsafe_allow_html=True)
    st.divider()


def _render_policy_response_boxes() -> None:
    st.markdown("**International Response Patterns**")
    cols = st.columns(4, gap="medium")
    for col, item in zip(cols, INTERNATIONAL_RESPONSE_BUCKETS):
        with col:
            st.markdown(
                f"""
                <div class="policy-response-box">
                    <div class="policy-response-title">{item['title']}</div>
                    <div class="policy-response-text">{item['summary']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def _render_policy_scenarios() -> None:
    st.markdown("**Remote-Work Mitigation Scenarios**")
    _render_box_row(MITIGATION_CONFIG, 5, render_policy_card)


def _render_policy_stats() -> None:
    left, right = st.columns(2, gap="large")

    with left:
        stats = {
            "Private car commuter / month": f"EGP {HOUSEHOLD_SAVINGS_CONFIG['private_car']['monthly_cost_egp']:,.0f}",
            "One-day saving": f"EGP {HOUSEHOLD_SAVINGS_CONFIG['private_car']['one_day_savings_egp']:,.0f}",
            "Two-day saving": f"EGP {HOUSEHOLD_SAVINGS_CONFIG['private_car']['two_day_savings_egp']:,.0f}",
            "Public transport / month": f"EGP {HOUSEHOLD_SAVINGS_CONFIG['public_transport']['monthly_cost_egp']:,.0f}",
            "One-day PT saving": f"EGP {HOUSEHOLD_SAVINGS_CONFIG['public_transport']['one_day_savings_egp']:,.0f}",
            "Two-day PT saving": f"EGP {HOUSEHOLD_SAVINGS_CONFIG['public_transport']['two_day_savings_egp']:,.0f}",
        }
        render_simple_stat_panel(title="Household Savings", stats=stats, tag="Policy", subtitle=HOUSEHOLD_SAVINGS_CONFIG.get("summary_note"))

    with right:
        budget_stats = {
            "Period": BUDGET_SAVINGS_CONFIG["period"],
            "One-day remote-work saving": f"EGP {BUDGET_SAVINGS_CONFIG['one_day_savings_mn_egp']:,.0f} mn",
            "Two-day remote-work saving": f"EGP {BUDGET_SAVINGS_CONFIG['two_day_savings_mn_egp']:,.0f} mn",
        }
        render_simple_stat_panel(
            title=BUDGET_SAVINGS_CONFIG["title"],
            stats=budget_stats,
            tag=BUDGET_SAVINGS_CONFIG["tag"],
            subtitle="Estimated savings for public-sector fuel-related spending.",
        )


def render_policy_section() -> None:
    render_section_header(SECTION_TITLES["policy_mitigation"], "International response patterns and potential mitigation options for Egypt.")
    _render_policy_response_boxes()
    st.markdown("")
    _render_policy_scenarios()
    st.markdown("")
    _render_policy_stats()
    st.divider()


def render_footer() -> None:
    cols = st.columns(3, gap="large")
    with cols[0]:
        st.markdown("**Source Guide**")
        for item in FOOTER_SOURCE_GUIDE:
            st.markdown(f"- {item}")
    with cols[1]:
        st.markdown("**Data Tag Guide**")
        for item in DATA_TAGS:
            st.markdown(f"- {item}")
    with cols[2]:
        st.markdown("**Limitations**")
        for item in FOOTER_LIMITATIONS:
            st.markdown(f"- {item}")


def render_full_dashboard(
    selected_window_label: str,
    assessment_items: Dict[str, Dict[str, Any]],
    live_immediate_shock_data: Dict[str, Dict[str, Any]],
    egypt_reaction_data: Dict[str, Dict[str, Any]],
    inflow_data: Dict[str, Dict[str, Any]],
    balance_data: Dict[str, Dict[str, Any]],
    business_data: Dict[str, Dict[str, Any]],
    price_data: Dict[str, Any],
) -> None:
    render_header(selected_window_label)
    render_executive_stress_strip(assessment_items)
    render_immediate_shock_section(live_immediate_shock_data)
    render_egypt_reaction_section(egypt_reaction_data)
    render_transmission_section()
    render_external_inflows_section(inflow_data)
    render_external_balance_section(balance_data)
    render_business_activity_section(business_data)
    render_domestic_price_pressure_section(price_data)
    render_scenario_snapshot_section()
    render_policy_section()
    render_footer()
