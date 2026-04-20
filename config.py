# config.py

from collections import OrderedDict

# =========================================================
# PAGE
# =========================================================
PAGE_TITLE = "War Shock Monitor"
PAGE_SUBTITLE = (
    "Tracking how regional conflict transmits into Egypt through energy, inflation, "
    "external inflows, trade, FX, and policy response."
)

PAGE_LAYOUT = "wide"
MAX_CONTENT_WIDTH_PX = 1500

DATA_TAGS = ["Live", "Official", "Assessment", "Scenario", "Policy"]

SPARKLINE_OPTIONS = OrderedDict({
    "3 Months": {"period": "3mo", "points": 60},
    "6 Months": {"period": "6mo", "points": 120},
})

DEFAULT_SPARKLINE_WINDOW = "3 Months"
CACHE_TTL_SECONDS = 4 * 60 * 60

DEFAULT_MARKET_SOURCE = "Yahoo Finance via yfinance"
DEFAULT_OFFICIAL_SOURCE = "Official Egypt sources"
DEFAULT_SCENARIO_SOURCE = "Scenario deck"
DEFAULT_POLICY_SOURCE = "Policy / mitigation deck"

# =========================================================
# DISPLAY / BADGES
# =========================================================
TAG_STYLES = {
    "Live": {"label": "Live"},
    "Official": {"label": "Official"},
    "Assessment": {"label": "Assessment"},
    "Scenario": {"label": "Scenario"},
    "Policy": {"label": "Policy"},
}

FREQUENCY_STYLES = {
    "Daily": {"label": "Daily"},
    "Monthly": {"label": "Monthly"},
    "Quarterly": {"label": "Quarterly"},
    "Annual": {"label": "Annual"},
    "Event-based": {"label": "Event-based"},
}

ASSESSMENT_LEVELS = ["Low", "Medium", "High"]
ASSESSMENT_DIRECTIONS = ["Improving", "Stable", "Worsening"]



# =========================================================
# INDICATOR COMPARISON POLICY
# =========================================================
INDICATOR_COMPARISON_POLICY = {
    "headline_inflation": {
        "comparison_mode": "mixed",
        "show_previous_period": True,
        "show_yoy": True,
        "show_snapshot": True,
    },
    "suez_revenues": {
        "comparison_mode": "mixed",
        "show_previous_period": True,
        "show_yoy": True,
        "show_snapshot": False,
    },
    "tourist_arrivals": {
        "comparison_mode": "mixed",
        "show_previous_period": True,
        "show_yoy": True,
        "show_snapshot": False,
    },
    "tourism_nights": {
        "comparison_mode": "mixed",
        "show_previous_period": True,
        "show_yoy": True,
        "show_snapshot": False,
    },
    "remittances": {
        "comparison_mode": "mixed",
        "show_previous_period": True,
        "show_yoy": True,
        "show_snapshot": False,
    },
    "exports": {
        "comparison_mode": "mixed",
        "show_previous_period": True,
        "show_yoy": True,
        "show_snapshot": False,
    },
    "imports": {
        "comparison_mode": "mixed",
        "show_previous_period": True,
        "show_yoy": True,
        "show_snapshot": False,
    },
    "trade_balance": {
        "comparison_mode": "mixed",
        "show_previous_period": True,
        "show_yoy": True,
        "show_snapshot": False,
    },
    "net_reserves": {
        "comparison_mode": "mixed",
        "show_previous_period": True,
        "show_yoy": True,
        "show_snapshot": False,
    },
    "fdi": {
        "comparison_mode": "mixed",
        "show_previous_period": True,
        "show_yoy": True,
        "show_snapshot": False,
    },
    "companies_established": {
        "comparison_mode": "mixed",
        "show_previous_period": True,
        "show_yoy": True,
        "show_snapshot": False,
    },
    "issued_capital": {
        "comparison_mode": "mixed",
        "show_previous_period": True,
        "show_yoy": True,
        "show_snapshot": False,
    },
    "food_inflation": {
        "comparison_mode": "mixed",
        "show_previous_period": True,
        "show_yoy": True,
        "show_snapshot": False,
    },
}

# =========================================================
# DATA STATUS DISPLAY
# =========================================================
DATA_STATUS_LABELS = {
    "complete": "Complete series",
    "partial": "Partial series",
    "placeholder": "Placeholder only",
    "snapshot_only": "Snapshot only",
    "fallback_used": "Fallback used",
}

DATA_STATUS_BADGE_KIND = {
    "complete": "status",
    "partial": "frequency",
    "placeholder": "default",
    "snapshot_only": "source",
    "fallback_used": "default",
}

# =========================================================
# ASSESSMENT THRESHOLDS
# =========================================================
ASSESSMENT_THRESHOLDS = {
    "energy_shock_pressure": {
        "brent_change_high": 1.5,
        "brent_change_medium": 0.0,
        "gas_change_high": 0.15,
        "gas_change_medium": 0.0,
        "brent_level_high": 100.0,
        "brent_level_medium": 90.0,
        "score_high": 5,
        "score_medium": 2,
    },
    "imported_inflation_pressure": {
        "wheat_change_high": 15.0,
        "wheat_change_medium": 0.0,
        "brent_change_high": 1.5,
        "brent_change_medium": 0.0,
        "fx_change_high": 0.15,
        "fx_change_medium": 0.0,
        "headline_yoy_change_high": 1.0,
        "headline_yoy_change_medium": 0.2,
        "headline_level_high": 20.0,
        "headline_level_medium": 12.0,
        "score_high": 6,
        "score_medium": 3,
    },
    "trade_pressure": {
        "imports_yoy_high": 0.3,
        "imports_yoy_medium": 0.0,
        "exports_yoy_high_negative": -0.3,
        "exports_yoy_medium_negative": 0.0,
        "trade_balance_level_high": -4.5,
        "trade_balance_level_medium": -3.0,
        "score_high": 5,
        "score_medium": 2,
    },
    "fx_pressure": {
        "fx_change_high": 0.2,
        "fx_change_medium": 0.0,
        "reserves_yoy_high_negative": -0.5,
        "reserves_yoy_medium_negative": 0.0,
        "score_high": 3,
        "score_medium": 1,
    },
    "domestic_activity_pressure": {
        "egx_change_high_negative": -250.0,
        "fdi_yoy_high_negative": -0.5,
        "companies_yoy_high_negative": -250.0,
        "capital_yoy_high_negative": -1.0,
        "score_high": 5,
        "score_medium": 2,
    },
}

# =========================================================
# LIVE MARKET INDICATORS
# =========================================================
LIVE_MARKET_CONFIG = OrderedDict({
    "brent": {
        "title": "Brent Crude",
        "ticker": "BZ=F",
        "decimals": 2,
        "tag": "Live",
        "frequency": "Daily",
        "source": DEFAULT_MARKET_SOURCE,
        "unit": "USD/bbl",
        "section": "immediate_shock",
        "description": "Global oil benchmark",
    },
    "natural_gas": {
        "title": "Natural Gas",
        "ticker": "NG=F",
        "decimals": 3,
        "tag": "Live",
        "frequency": "Daily",
        "source": DEFAULT_MARKET_SOURCE,
        "unit": "USD/mmBtu",
        "section": "immediate_shock",
        "description": "Energy and LNG pressure proxy",
    },
    "gold": {
        "title": "Gold",
        "ticker": "GC=F",
        "decimals": 2,
        "tag": "Live",
        "frequency": "Daily",
        "source": DEFAULT_MARKET_SOURCE,
        "unit": "USD/oz",
        "section": "immediate_shock",
        "description": "Safe-haven stress indicator",
    },
    "wheat": {
        "title": "Wheat",
        "ticker": "ZW=F",
        "decimals": 2,
        "tag": "Live",
        "frequency": "Daily",
        "source": DEFAULT_MARKET_SOURCE,
        "unit": "US cents/bushel",
        "section": "immediate_shock",
        "description": "Imported food pressure proxy",
    },
    "dxy": {
        "title": "DXY",
        "ticker": "^NYICDX",
        "decimals": 2,
        "tag": "Live",
        "frequency": "Daily",
        "source": DEFAULT_MARKET_SOURCE,
        "unit": "index",
        "section": "immediate_shock",
        "description": "Broad dollar strength",
    },
    "vix": {
        "title": "VIX",
        "ticker": "^VIX",
        "decimals": 2,
        "tag": "Live",
        "frequency": "Daily",
        "source": DEFAULT_MARKET_SOURCE,
        "unit": "index",
        "section": "immediate_shock",
        "description": "Risk-off / volatility proxy",
    },
    "usd_egp": {
        "title": "USD/EGP",
        "ticker": "EGP=X",
        "decimals": 4,
        "tag": "Live",
        "frequency": "Daily",
        "source": DEFAULT_MARKET_SOURCE,
        "unit": "EGP per USD",
        "section": "egypt_reaction",
        "description": "FX pressure indicator",
    },
    "egx30": {
        "title": "EGX30",
        "ticker": "^CASE30",
        "decimals": 2,
        "tag": "Live",
        "frequency": "Daily",
        "source": DEFAULT_MARKET_SOURCE,
        "unit": "index",
        "section": "egypt_reaction",
        "description": "Domestic market sentiment",
    },
})

# =========================================================
# OFFICIAL INDICATORS
# =========================================================
OFFICIAL_INDICATOR_CONFIG = OrderedDict({
    # Egypt reaction
    "headline_inflation": {
        "title": "Headline Inflation",
        "tag": "Official",
        "frequency": "Monthly",
        "source": "CAPMAS / CBE",
        "unit": "%",
        "section": "egypt_reaction",
        "description": "Broad CPI inflation",
    },

    # External inflows
    "suez_revenues": {
        "title": "Suez Canal Revenues",
        "tag": "Official",
        "frequency": "Monthly",
        "source": "CAPMAS / Suez Canal Authority",
        "unit": "billion EGP",
        "section": "external_inflows",
        "description": "Key external FX inflow channel",
    },
    "tourist_arrivals": {
        "title": "Tourist Arrivals",
        "tag": "Official",
        "frequency": "Monthly",
        "source": "CAPMAS",
        "unit": "million tourists",
        "section": "external_inflows",
        "description": "Tourism inflow indicator",
    },
    "tourism_nights": {
        "title": "Tourism Nights",
        "tag": "Official",
        "frequency": "Monthly",
        "source": "CAPMAS",
        "unit": "million nights",
        "section": "external_inflows",
        "description": "Tourism activity indicator",
    },
    "remittances": {
        "title": "Remittances",
        "tag": "Official",
        "frequency": "Quarterly",
        "source": "CAPMAS / CBE",
        "unit": "billion USD",
        "section": "external_inflows",
        "description": "Household external inflow support",
    },

    # External balance
    "exports": {
        "title": "Exports",
        "tag": "Official",
        "frequency": "Monthly",
        "source": "CAPMAS",
        "unit": "billion USD",
        "section": "external_balance",
        "description": "Goods exports",
    },
    "imports": {
        "title": "Imports",
        "tag": "Official",
        "frequency": "Monthly",
        "source": "CAPMAS",
        "unit": "billion USD",
        "section": "external_balance",
        "description": "Goods imports",
    },
    "trade_balance": {
        "title": "Trade Balance",
        "tag": "Official",
        "frequency": "Monthly",
        "source": "CAPMAS",
        "unit": "billion USD",
        "section": "external_balance",
        "description": "Monthly trade balance",
    },
    "net_reserves": {
        "title": "Net International Reserves",
        "tag": "Official",
        "frequency": "Monthly",
        "source": "CAPMAS / CBE",
        "unit": "billion USD",
        "section": "external_balance",
        "description": "External resilience buffer",
    },

    # Business activity
    "fdi": {
        "title": "FDI",
        "tag": "Official",
        "frequency": "Quarterly",
        "source": "CAPMAS / CBE",
        "unit": "billion USD",
        "section": "business_activity",
        "description": "Foreign direct investment",
    },
    "companies_established": {
        "title": "Companies Established",
        "tag": "Official",
        "frequency": "Monthly",
        "source": "CAPMAS / GAFI",
        "unit": "count",
        "section": "business_activity",
        "description": "Business formation activity",
    },
    "issued_capital": {
        "title": "Issued Capital of New Companies",
        "tag": "Official",
        "frequency": "Monthly",
        "source": "CAPMAS / GAFI",
        "unit": "billion EGP",
        "section": "business_activity",
        "description": "Capital committed by new firms",
    },

    # Domestic price pressure
    "food_inflation": {
        "title": "Food Inflation",
        "tag": "Official",
        "frequency": "Monthly",
        "source": "CAPMAS",
        "unit": "%",
        "section": "domestic_price_pressure",
        "description": "Food and beverage inflation",
    },
})

# =========================================================
# PAGE SECTION ORDER
# =========================================================
SECTION_ORDER = [
    "header",
    "executive_stress_strip",
    "immediate_shock",
    "egypt_reaction",
    "transmission_map",
    "external_inflows",
    "external_balance",
    "business_activity",
    "domestic_price_pressure",
    "scenario_snapshot",
    "policy_mitigation",
    "footer",
]

SECTION_TITLES = {
    "immediate_shock": "Immediate Shock",
    "egypt_reaction": "Egypt Reaction",
    "transmission_map": "Crisis Transmission Map",
    "external_inflows": "Egypt Exposure: External Inflows",
    "external_balance": "Egypt Exposure: External Balance",
    "business_activity": "Egypt Exposure: Investment & Business Activity",
    "domestic_price_pressure": "Domestic Price Pressure",
    "scenario_snapshot": "Scenario Snapshot",
    "policy_mitigation": "Policy / Mitigation Options",
}

SECTION_INDICATORS = {
    "immediate_shock": [
        "brent", "natural_gas", "gold", "wheat", "dxy", "vix"
    ],
    "egypt_reaction_row1": [
        "usd_egp", "egx30", "headline_inflation"
    ],
    "egypt_reaction_row2": [],
    "external_inflows": [
        "suez_revenues", "tourist_arrivals", "tourism_nights", "remittances"
    ],
    "external_balance": [
        "exports", "imports", "trade_balance", "net_reserves"
    ],
    "business_activity": [
        "fdi", "companies_established", "issued_capital"
    ],
    "domestic_price_pressure_cards": [
        "food_inflation"
    ],
}

# =========================================================
# EXECUTIVE STRESS STRIP CONFIG
# =========================================================
EXECUTIVE_STRESS_ITEMS = [
    "energy_shock_pressure",
    "imported_inflation_pressure",
    "external_inflows_pressure",
    "trade_pressure",
    "fx_pressure",
    "domestic_activity_pressure",
]

EXECUTIVE_STRESS_TITLES = {
    "energy_shock_pressure": "Energy Shock Pressure",
    "imported_inflation_pressure": "Imported Inflation Pressure",
    "external_inflows_pressure": "External Inflows Pressure",
    "trade_pressure": "Trade Pressure",
    "fx_pressure": "FX Pressure",
    "domestic_activity_pressure": "Domestic Activity Pressure",
}

# =========================================================
# SCENARIO SNAPSHOT
# =========================================================
SCENARIO_CONFIG = [
    {
        "id": "scenario_1",
        "title": "Scenario 1",
        "subtitle": "Oil at $100",
        "oil_price": 100,
        "wheat_change_pct": 15,
        "fx_change_pct": 15,
        "tourism_change_pct": -15,
        "remittances_change_pct": -10,
        "growth_impact_pp": -0.4,
        "growth_result_pct": 4.8,
        "inflation_effect_text": "Average annual inflation ~17–18%",
        "inflation_peak_text": "Peak around Aug 2026: ~20–21%",
        "tag": "Scenario",
        "closest_to_current_path": True,
    },
    {
        "id": "scenario_2",
        "title": "Scenario 2",
        "subtitle": "Oil at $125",
        "oil_price": 125,
        "wheat_change_pct": 15,
        "fx_change_pct": 15,
        "tourism_change_pct": -15,
        "remittances_change_pct": -10,
        "growth_impact_pp": -1.3,
        "growth_result_pct": 3.9,
        "inflation_effect_text": "Average annual inflation ~17–18%",
        "inflation_peak_text": "Peak around Aug 2026: ~20–21%",
        "tag": "Scenario",
        "closest_to_current_path": False,
    },
    {
        "id": "scenario_3",
        "title": "Scenario 3",
        "subtitle": "Oil at $150",
        "oil_price": 150,
        "wheat_change_pct": 15,
        "fx_change_pct": 15,
        "tourism_change_pct": -15,
        "remittances_change_pct": -10,
        "growth_impact_pp": -1.5,
        "growth_result_pct": 3.7,
        "inflation_effect_text": "Average annual inflation ~17–18%",
        "inflation_peak_text": "Peak around Aug 2026: ~20–21%",
        "tag": "Scenario",
        "closest_to_current_path": False,
    },
    {
        "id": "scenario_4",
        "title": "Scenario 4",
        "subtitle": "Oil at $200",
        "oil_price": 200,
        "wheat_change_pct": 15,
        "fx_change_pct": 15,
        "tourism_change_pct": -15,
        "remittances_change_pct": -10,
        "growth_impact_pp": -1.9,
        "growth_result_pct": 3.3,
        "inflation_effect_text": "Average annual inflation ~17–18%",
        "inflation_peak_text": "Peak around Aug 2026: ~20–21%",
        "tag": "Scenario",
        "closest_to_current_path": False,
    },
]

SCENARIO_LABEL_STRIP = [
    "Closest to current path",
    "Higher-stress cases",
    "Less likely under de-escalation",
]

# =========================================================
# POLICY / MITIGATION
# =========================================================
INTERNATIONAL_RESPONSE_BUCKETS = [
    {
        "title": "Targeted Energy Support",
        "summary": "Support to shield vulnerable groups from fuel and energy-price spikes.",
    },
    {
        "title": "Supply Security",
        "summary": "Emergency sourcing, fuel diversification, and fertilizer/food supply support.",
    },
    {
        "title": "Remote Work / Rationing",
        "summary": "Work-from-home, energy-saving, and fuel-rationing measures.",
    },
    {
        "title": "Trade / Commercial Measures",
        "summary": "Operational and trade actions to reduce shock transmission.",
    },
]

MITIGATION_CONFIG = [
    {
        "id": "public_only",
        "title": "Public Sector Only",
        "one_day_savings_pct": 0.75,
        "two_day_savings_pct": 1.50,
        "tag": "Policy",
    },
    {
        "id": "public_private_30",
        "title": "Public + Private 30%",
        "one_day_savings_pct": 1.08,
        "two_day_savings_pct": 2.50,
        "tag": "Policy",
    },
    {
        "id": "public_private_50",
        "title": "Public + Private 50%",
        "one_day_savings_pct": 1.31,
        "two_day_savings_pct": 3.18,
        "tag": "Policy",
    },
    {
        "id": "public_private_70",
        "title": "Public + Private 70%",
        "one_day_savings_pct": 1.53,
        "two_day_savings_pct": 3.86,
        "tag": "Policy",
    },
    {
        "id": "public_private_100",
        "title": "Public + Private 100%",
        "one_day_savings_pct": 1.87,
        "two_day_savings_pct": 4.87,
        "tag": "Policy",
    },
]

HOUSEHOLD_SAVINGS_CONFIG = {
    "private_car": {
        "title": "Private Car Commuter",
        "monthly_cost_egp": 2673,
        "one_day_savings_egp": 535,
        "two_day_savings_egp": 1069,
    },
    "public_transport": {
        "title": "Public Transport Commuter",
        "monthly_cost_egp": 1100,
        "one_day_savings_egp": 220,
        "two_day_savings_egp": 440,
    },
    "summary_note": (
        "Presentation text also cites a typical monthly transport saving of roughly "
        "EGP 360 for one day remote work and EGP 720 for two days under a simplified "
        "employee transport budget framing."
    ),
}

BUDGET_SAVINGS_CONFIG = {
    "title": "Public Budget Savings",
    "period": "Mar–Jun 2026",
    "one_day_savings_mn_egp": 697,
    "two_day_savings_mn_egp": 1400,
    "tag": "Policy",
}

# =========================================================
# NARRATIVE TEXT BLOCKS
# =========================================================
TRANSMISSION_FLOW = [
    "Regional escalation",
    "Energy / shipping / supply shock",
    "Higher import costs",
    "Pressure on Suez / tourism / inflows",
    "FX stress",
    "Higher inflation",
    "Slower growth / fiscal strain",
]

TRANSMISSION_BUCKETS = [
    {
        "title": "Prices",
        "summary": "Energy and imported goods pressures raise production and consumer costs."
    },
    {
        "title": "Trade",
        "summary": "Shipping disruption and higher freight costs distort import-export dynamics."
    },
    {
        "title": "Income",
        "summary": "Tourism, Suez, and household inflows may face pressure under prolonged stress."
    },
    {
        "title": "External flows",
        "summary": "FX, reserves, FDI, and broader capital confidence become more sensitive."
    },
]

INSIGHT_BARS = {
    "external_inflows": (
        "External inflows are the clearest direct Egypt transmission channel in this crisis."
    ),
    "business_activity": (
        "Business activity indicators provide a confidence and private-sector resilience layer."
    ),
    "domestic_price_pressure": (
        "Recent inflation acceleration reflects the interaction of energy, import, and supply-chain channels."
    ),
}

# =========================================================
# FOOTER
# =========================================================
FOOTER_SOURCE_GUIDE = [
    "Live market data via Yahoo Finance / yfinance.",
    "Official Egypt indicators compiled from CAPMAS, CBE, Suez Canal Authority, and GAFI series.",
    "Scenario and mitigation framing from the April 9, 2026 crisis presentation.",
]

FOOTER_LIMITATIONS = [
    "This dashboard mixes daily, monthly, quarterly, and event-based indicators.",
    "Assessment blocks are synthesized judgments, not direct observations.",
    "Scenario blocks are indicative briefing scenarios, not a forecast engine.",
]