from __future__ import annotations

import streamlit as st

from config import (
    PAGE_LAYOUT,
    PAGE_TITLE,
    SPARKLINE_OPTIONS,
    DEFAULT_SPARKLINE_WINDOW,
)
from market_data import (
    load_live_egypt_reaction_market_data,
    load_immediate_shock_data,
    merge_reaction_data,
)
from assessments import build_assessment_items
from components.sections import render_full_dashboard
from auth import require_password
from ui_styles import inject_styles
from data_loaders import (
    get_live_immediate_shock_data,
    get_live_egypt_reaction_market_data,
    get_official_egypt_reaction_data,
    get_external_inflows_data,
    get_external_balance_data,
    get_business_activity_data,
    get_domestic_price_pressure_data,
)


st.set_page_config(
    page_title=PAGE_TITLE,
    layout=PAGE_LAYOUT,
)


def render_sidebar_controls() -> str:
    st.sidebar.header("Controls")

    selected_window_label = st.sidebar.selectbox(
        "Sparkline window",
        options=list(SPARKLINE_OPTIONS.keys()),
        index=list(SPARKLINE_OPTIONS.keys()).index(DEFAULT_SPARKLINE_WINDOW),
    )

    if st.sidebar.button("Refresh"):
        st.cache_data.clear()
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.subheader("View")
    st.sidebar.caption("Single long-form dashboard")
    st.sidebar.caption("Mixed data types: Live, Official, Assessment, Scenario, Policy")

    return selected_window_label


def main() -> None:
    require_password()
    inject_styles()

    selected_window_label = render_sidebar_controls()

    live_immediate_shock_data = get_live_immediate_shock_data(selected_window_label)
    live_egypt_reaction_market_data = get_live_egypt_reaction_market_data(selected_window_label)

    official_egypt_reaction_data = get_official_egypt_reaction_data()
    inflow_data = get_external_inflows_data()
    balance_data = get_external_balance_data()
    business_data = get_business_activity_data()
    price_data = get_domestic_price_pressure_data()

    egypt_reaction_data = merge_reaction_data(
        live_market_data=live_egypt_reaction_market_data,
        official_reaction_data=official_egypt_reaction_data,
    )

    assessment_items = build_assessment_items(
        live_data={**live_immediate_shock_data, **live_egypt_reaction_market_data},
        egypt_reaction_data=official_egypt_reaction_data,
        inflow_data=inflow_data,
        balance_data=balance_data,
        business_data=business_data,
    )

    render_full_dashboard(
        selected_window_label=selected_window_label,
        assessment_items=assessment_items,
        live_immediate_shock_data=live_immediate_shock_data,
        egypt_reaction_data=egypt_reaction_data,
        inflow_data=inflow_data,
        balance_data=balance_data,
        business_data=business_data,
        price_data=price_data,
    )


if __name__ == "__main__":
    main()
