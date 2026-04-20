# components/__init__.py

from .cards import (
    render_assessment_card,
    render_commentary_panel,
    render_insight_bar,
    render_live_card,
    render_official_card,
    render_policy_card,
    render_scenario_card,
    render_simple_stat_panel,
)

from .charts import (
    build_category_snapshot_chart,
    build_cpi_mom_chart,
    build_dual_series_chart,
    build_inflation_composition_chart,
    build_official_trend_chart,
    build_reserves_chart,
    build_sparkline,
    build_top_categories_table_df,
    build_trade_balance_chart,
)

from .sections import (
    render_badge_strip,
    render_business_activity_section,
    render_domestic_price_pressure_section,
    render_egypt_reaction_section,
    render_executive_stress_strip,
    render_external_balance_section,
    render_external_inflows_section,
    render_footer,
    render_full_dashboard,
    render_header,
    render_immediate_shock_section,
    render_policy_section,
    render_scenario_snapshot_section,
    render_section_header,
    render_transmission_section,
)

__all__ = [
    # cards
    "render_assessment_card",
    "render_commentary_panel",
    "render_insight_bar",
    "render_live_card",
    "render_official_card",
    "render_policy_card",
    "render_scenario_card",
    "render_simple_stat_panel",

    # charts
    "build_category_snapshot_chart",
    "build_cpi_mom_chart",
    "build_dual_series_chart",
    "build_inflation_composition_chart",
    "build_official_trend_chart",
    "build_reserves_chart",
    "build_sparkline",
    "build_top_categories_table_df",
    "build_trade_balance_chart",

    # sections
    "render_badge_strip",
    "render_business_activity_section",
    "render_domestic_price_pressure_section",
    "render_egypt_reaction_section",
    "render_executive_stress_strip",
    "render_external_balance_section",
    "render_external_inflows_section",
    "render_footer",
    "render_full_dashboard",
    "render_header",
    "render_immediate_shock_section",
    "render_policy_section",
    "render_scenario_snapshot_section",
    "render_section_header",
    "render_transmission_section",
]