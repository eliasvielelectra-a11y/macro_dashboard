# manual_series.py

# =========================================================
# NOTE
# =========================================================
# Manual v1 series extracted from uploaded official/statistical decks.
# All series are stored as lists of dicts with:
# - period: ISO-like string for month/quarter/year
# - value: numeric
# - source_note: optional
#
# Period conventions:
# - Monthly: YYYY-MM
# - Quarterly: YYYY-QN
# - Annual calendar: YYYY
# - Fiscal year: YYYY/YYYY

# =========================================================
# EGYPT REACTION
# =========================================================
HEADLINE_INFLATION_MONTHLY = [
    {"period": "2025-01", "value": 23.2},
    {"period": "2025-02", "value": 12.5},
    {"period": "2025-03", "value": 13.1},
    {"period": "2025-04", "value": 13.5},
    {"period": "2025-05", "value": 16.5},
    {"period": "2025-06", "value": 14.4},
    {"period": "2025-07", "value": 13.1},
    {"period": "2025-08", "value": 11.2},
    {"period": "2025-09", "value": 10.3},
    {"period": "2025-10", "value": 10.1},
    {"period": "2025-11", "value": 10.0},
    {"period": "2025-12", "value": 10.3},
    {"period": "2026-01", "value": 10.1},
    {"period": "2026-02", "value": 11.5},
    {"period": "2026-03", "value": 13.5},
]

# Placeholder until exact official monthly series is supplied.
CORE_INFLATION_MONTHLY = [
    {"period": "2026-03", "value": None, "source_note": "To be filled from official CBE series"},
]

OVERNIGHT_DEPOSIT_RATE_SERIES = [
    {"period": "2026-03", "value": None, "source_note": "To be filled from current official/CBE feed"},
]

OVERNIGHT_LENDING_RATE_SERIES = [
    {"period": "2026-03", "value": None, "source_note": "To be filled from current official/CBE feed"},
]

MAIN_OPERATION_RATE_SERIES = [
    {"period": "2026-03", "value": None, "source_note": "To be filled from current official/CBE feed"},
]

CONIA_MONTHLY = [
    {"period": "2026-03", "value": None, "source_note": "To be filled from current official/CBE series"},
]

# =========================================================
# EXTERNAL INFLOWS
# =========================================================
# From CAPMAS deck monthly panels / annual context where visible.

TOURIST_ARRIVALS_MONTHLY = [
    {"period": "2026-03", "value": 1.40, "source_note": "Mar 2026 from crisis presentation"},
    {"period": "2025-03", "value": 1.19, "source_note": "Mar 2025 comparison from crisis presentation"},
]

TOURISM_NIGHTS_MONTHLY = [
    # Draft from CAPMAS monthly chart can be completed precisely from source table if needed.
    {"period": "2026-02", "value": 13.3},
    {"period": "2026-01", "value": 16.5},
    {"period": "2025-12", "value": 14.7},
    {"period": "2025-11", "value": 16.1},
    {"period": "2025-10", "value": 17.2},
    {"period": "2025-09", "value": 18.3},
    {"period": "2025-08", "value": 23.1},
    {"period": "2025-07", "value": 17.3},
    {"period": "2025-06", "value": 14.8},
    {"period": "2025-05", "value": 14.6},
    {"period": "2025-04", "value": 15.5},
    {"period": "2025-03", "value": 13.4},
    {"period": "2025-02", "value": 12.5},
]

SUEZ_REVENUES_MONTHLY_EGP = [
    {"period": "2025-02", "value": 13.1},
    {"period": "2025-03", "value": 16.8},
    {"period": "2025-04", "value": 16.8},
    {"period": "2025-05", "value": 16.8},
    {"period": "2025-06", "value": 15.6},
    {"period": "2025-07", "value": 17.5},
    {"period": "2025-08", "value": 17.5},
    {"period": "2025-09", "value": 18.8},
    {"period": "2025-10", "value": 17.7},
    {"period": "2025-11", "value": 18.0},
    {"period": "2025-12", "value": 18.8},
    {"period": "2026-01", "value": 17.3},
    {"period": "2026-02", "value": 17.4},
]

# Dollar-denominated March comparison from crisis presentation.
SUEZ_REVENUES_MARCH_USD = [
    {"period": "2025-03", "value": 332.8, "unit": "million USD"},
    {"period": "2026-03", "value": 410.3, "unit": "million USD"},
]

REMITTANCES_QUARTERLY = [
    {"period": "2023-Q1", "value": 7.5},
    {"period": "2023-Q2", "value": 5.0},
    {"period": "2023-Q3", "value": 4.9},
    {"period": "2023-Q4", "value": 4.5},
    {"period": "2024-Q1", "value": 10.0},
    {"period": "2024-Q2", "value": 9.4},
    {"period": "2024-Q3", "value": 8.7},
    {"period": "2024-Q4", "value": 8.3},
    {"period": "2025-Q1", "value": 8.3, "source_note": "Filled manually by user"},
    {"period": "2025-Q2", "value": 8.7, "source_note": "Filled manually by user"},
    {"period": "2025-Q3", "value": 9.4, "source_note": "Filled manually by user"},
    {"period": "2025-Q4", "value": 10.0, "source_note": "Filled manually by user"},
]

# =========================================================
# EXTERNAL BALANCE
# =========================================================
EXPORTS_MONTHLY = [
    {"period": "2024-12", "value": 4.0},
    {"period": "2025-01", "value": 4.6},
    {"period": "2025-02", "value": 4.2},
    {"period": "2025-03", "value": 4.9},
    {"period": "2025-04", "value": 4.0},
    {"period": "2025-05", "value": 4.2},
    {"period": "2025-06", "value": 4.0},
    {"period": "2025-07", "value": 3.7},
    {"period": "2025-08", "value": 3.6},
    {"period": "2025-09", "value": 4.4},
    {"period": "2025-10", "value": 4.2},
    {"period": "2025-11", "value": 4.8},
    {"period": "2025-12", "value": 4.7},
]

IMPORTS_MONTHLY = [
    {"period": "2024-12", "value": 9.5},
    {"period": "2025-01", "value": 8.7},
    {"period": "2025-02", "value": 8.8},
    {"period": "2025-03", "value": 8.2},
    {"period": "2025-04", "value": 8.7},
    {"period": "2025-05", "value": 9.0},
    {"period": "2025-06", "value": 8.2},
    {"period": "2025-07", "value": 8.1},
    {"period": "2025-08", "value": 8.2},
    {"period": "2025-09", "value": 7.9},
    {"period": "2025-10", "value": 7.4},
    {"period": "2025-11", "value": 8.7},
    {"period": "2025-12", "value": 8.7},
]

TRADE_BALANCE_MONTHLY = [
    {"period": "2024-12", "value": -4.9},
    {"period": "2025-01", "value": -4.7},
    {"period": "2025-02", "value": -4.6},
    {"period": "2025-03", "value": -3.3},
    {"period": "2025-04", "value": -4.7},
    {"period": "2025-05", "value": -5.2},
    {"period": "2025-06", "value": -4.7},
    {"period": "2025-07", "value": -3.7},
    {"period": "2025-08", "value": -3.9},
    {"period": "2025-09", "value": -3.1},
    {"period": "2025-10", "value": -2.7},
    {"period": "2025-11", "value": -4.2},
    {"period": "2025-12", "value": -4.4},
]

NET_RESERVES_MONTHLY = [
    {"period": "2025-02", "value": 47.4},
    {"period": "2025-03", "value": 47.8},
    {"period": "2025-04", "value": 48.1},
    {"period": "2025-05", "value": 48.5},
    {"period": "2025-06", "value": 48.7},
    {"period": "2025-07", "value": 49.0},
    {"period": "2025-08", "value": 49.3},
    {"period": "2025-09", "value": 49.5},
    {"period": "2025-10", "value": 50.1},
    {"period": "2025-11", "value": 50.2},
    {"period": "2025-12", "value": 51.5},
    {"period": "2026-01", "value": 52.6},
    {"period": "2026-02", "value": 52.7},
]

# =========================================================
# BUSINESS ACTIVITY
# =========================================================
FDI_QUARTERLY = [
    {"period": "2022-Q1", "value": 2.4},
    {"period": "2022-Q2", "value": 3.8},
    {"period": "2022-Q3", "value": 3.3},
    {"period": "2022-Q4", "value": 2.7},
    {"period": "2023-Q1", "value": 18.2},
    {"period": "2023-Q2", "value": 3.2},
    {"period": "2023-Q3", "value": 2.1},
    {"period": "2023-Q4", "value": 2.2},
    {"period": "2024-Q1", "value": 2.4},
    {"period": "2024-Q2", "value": 2.3},
    {"period": "2024-Q3", "value": 3.3},
    {"period": "2024-Q4", "value": 1.6},
    {"period": "2025-Q1", "value": 4.1},
    {"period": "2025-Q2", "value": 1.6},
    {"period": "2025-Q3", "value": 1.7},
    {"period": "2025-Q4", "value": 2.4, "source_note": "Filled manually by user"},
]

COMPANIES_ESTABLISHED_MONTHLY = [
    {"period": "2025-02", "value": 4475},
    {"period": "2025-03", "value": 3242},
    {"period": "2025-04", "value": 2711},
    {"period": "2025-05", "value": 4018},
    {"period": "2025-06", "value": 3425},
    {"period": "2025-07", "value": 3904},
    {"period": "2025-08", "value": 3259},
    {"period": "2025-09", "value": 3676},
    {"period": "2025-10", "value": 4320},
    {"period": "2025-11", "value": 3839},
    {"period": "2025-12", "value": 5210},
    {"period": "2026-01", "value": 4746},
    {"period": "2026-02", "value": 3756},
]

ISSUED_CAPITAL_MONTHLY = [
    {"period": "2025-02", "value": 18.6},
    {"period": "2025-03", "value": 12.6},
    {"period": "2025-04", "value": 11.5},
    {"period": "2025-05", "value": 14.4},
    {"period": "2025-06", "value": 11.3},
    {"period": "2025-07", "value": 15.9},
    {"period": "2025-08", "value": 14.4},
    {"period": "2025-09", "value": 13.2},
    {"period": "2025-10", "value": 21.0},
    {"period": "2025-11", "value": 11.9},
    {"period": "2025-12", "value": 20.3},
    {"period": "2026-01", "value": 16.7},
    {"period": "2026-02", "value": 14.5},
]

# =========================================================
# DOMESTIC PRICE PRESSURE
# =========================================================
FOOD_INFLATION_ANNUAL = [
    {"period": "2015", "value": 10.9},
    {"period": "2016", "value": 17.4},
    {"period": "2017", "value": 39.3},
    {"period": "2018", "value": 13.1},
    {"period": "2019", "value": 6.2},
    {"period": "2020", "value": -0.6},
    {"period": "2021", "value": 5.2},
    {"period": "2022", "value": 25.2},
    {"period": "2023", "value": 63.5},
    {"period": "2024", "value": 31.6},
    {"period": "2025", "value": 4.8},
]

CPI_WEIGHTS = [
    {"category": "Food & Beverages", "weight_pct": 35.872},
    {"category": "Housing, Water, Electricity, Gas & Fuel", "weight_pct": 18.049},
    {"category": "Health", "weight_pct": 9.042},
    {"category": "Transport", "weight_pct": 6.051},
    {"category": "Clothing & Footwear", "weight_pct": 4.671},
    {"category": "Alcoholic Beverages & Tobacco", "weight_pct": 4.634},
    {"category": "Misc. Goods & Services", "weight_pct": 4.517},
    {"category": "Education", "weight_pct": 4.395},
    {"category": "Restaurants & Hotels", "weight_pct": 4.271},
    {"category": "Furniture & Household Equipment", "weight_pct": 4.074},
    {"category": "Communications", "weight_pct": 2.321},
    {"category": "Culture & Recreation", "weight_pct": 2.104},
]

CATEGORY_INFLATION_SNAPSHOT_MAR_2026 = [
    {"category": "Food & Beverages", "mar_2026": 6.32, "mar_2025": 6.5, "weight_pct": 35.9},
    {"category": "Housing / Utilities / Fuel", "mar_2026": 27.85, "mar_2025": 17.4, "weight_pct": 18.05},
    {"category": "Health", "mar_2026": 17.04, "mar_2025": 25.5, "weight_pct": 9.04},
    {"category": "Transport", "mar_2026": 29.17, "mar_2025": 29.5, "weight_pct": 6.05},
    {"category": "Clothing & Footwear", "mar_2026": 14.03, "mar_2025": 18.3, "weight_pct": 4.67},
    {"category": "Alcoholic Beverages & Tobacco", "mar_2026": 15.29, "mar_2025": 26.2, "weight_pct": 4.63},
    {"category": "Education", "mar_2026": 20.05, "mar_2025": 10.0, "weight_pct": 4.4},
    {"category": "Restaurants & Hotels", "mar_2026": 13.6, "mar_2025": 11.3, "weight_pct": 4.27},
]

CPI_MONTHLY_MOM = [
    {"period": "2025-01", "value": 1.6},
    {"period": "2025-02", "value": 1.4},
    {"period": "2025-03", "value": 1.5},
    {"period": "2025-04", "value": 1.3},
    {"period": "2025-05", "value": 1.8},
    {"period": "2025-06", "value": -0.1},
    {"period": "2025-07", "value": -0.6},
    {"period": "2025-08", "value": 0.1},
    {"period": "2025-09", "value": 1.5},
    {"period": "2025-10", "value": 1.3},
    {"period": "2025-11", "value": -0.2},
    {"period": "2025-12", "value": 0.1},
    {"period": "2026-01", "value": 1.5},
    {"period": "2026-02", "value": 2.7},
    {"period": "2026-03", "value": 3.3},
]

# =========================================================
# MARCH 2026 EXTERNAL FX SNAPSHOT
# =========================================================
MARCH_2026_EXTERNAL_FX_SNAPSHOT = {
    "tourists_million": {"2025-03": 1.19, "2026-03": 1.40},
    "suez_fees_million_usd": {"2025-03": 332.8, "2026-03": 410.3},
    "ships_thousand": {"2025-03": 1.071, "2026-03": 1.191},
    "cargo_million_tons": {"2025-03": 42.3, "2026-03": 51.51},
}