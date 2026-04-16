# assessments.py

from __future__ import annotations

from typing import Any, Dict, Optional

import pandas as pd

from config import EXECUTIVE_STRESS_TITLES, ASSESSMENT_THRESHOLDS


# =========================================================
# BASIC HELPERS
# =========================================================
def safe_num(value: Any) -> Optional[float]:
    try:
        if value is None or pd.isna(value):
            return None
        return float(value)
    except Exception:
        return None


def classify_three_band(
    value: Optional[float],
    low_threshold: float,
    high_threshold: float,
    inverse: bool = False,
) -> str:
    """
    Classify into Low / Medium / High.

    Normal mode:
      low value   -> Low
      mid value   -> Medium
      high value  -> High

    inverse mode:
      low value   -> High
      mid value   -> Medium
      high value  -> Low
    """
    if value is None:
        return "Medium"

    if not inverse:
        if value >= high_threshold:
            return "High"
        if value >= low_threshold:
            return "Medium"
        return "Low"

    if value <= low_threshold:
        return "High"
    if value <= high_threshold:
        return "Medium"
    return "Low"


def direction_from_change(
    change: Optional[float],
    inverse_good: bool = False,
    deadband: float = 0.05,
) -> str:
    """
    improving / stable / worsening based on change.
    inverse_good=True means lower is better.
    """
    if change is None:
        return "Stable"

    if abs(change) <= deadband:
        return "Stable"

    if not inverse_good:
        return "Worsening" if change > 0 else "Improving"

    return "Improving" if change > 0 else "Worsening"


def build_assessment_item(
    key: str,
    level: str,
    direction: str,
    reason: str,
) -> Dict[str, str]:
    return {
        "id": key,
        "title": EXECUTIVE_STRESS_TITLES.get(key, key),
        "tag": "Assessment",
        "level": level,
        "direction": direction,
        "reason": reason,
    }


def latest_value(indicator: Optional[Dict[str, Any]]) -> Optional[float]:
    if not indicator:
        return None
    return safe_num(indicator.get("latest_value"))


def change_value(indicator: Optional[Dict[str, Any]]) -> Optional[float]:
    if not indicator:
        return None
    return safe_num(indicator.get("change_value"))


def yoy_change_value(indicator: Optional[Dict[str, Any]]) -> Optional[float]:
    if not indicator:
        return None
    return safe_num(indicator.get("yoy_change_value"))


def yoy_change_pct(indicator: Optional[Dict[str, Any]]) -> Optional[float]:
    if not indicator:
        return None
    return safe_num(indicator.get("yoy_change_pct"))


def snapshot_value(indicator: Optional[Dict[str, Any]]) -> Optional[float]:
    if not indicator:
        return None
    return safe_num(indicator.get("current_snapshot_value"))


def data_status(indicator: Optional[Dict[str, Any]]) -> str:
    if not indicator:
        return "placeholder"
    return str(indicator.get("data_status", "placeholder"))


# =========================================================
# INDIVIDUAL ASSESSMENTS
# =========================================================
def assess_energy_shock(live_data: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
    thresholds = ASSESSMENT_THRESHOLDS["energy_shock_pressure"]
    brent = live_data.get("brent", {})
    gas = live_data.get("natural_gas", {})

    brent_chg = change_value(brent)
    gas_chg = change_value(gas)
    brent_lvl = latest_value(brent)
    gas_lvl = latest_value(gas)

    score = 0

    if brent_chg is not None:
        if brent_chg > thresholds["brent_change_high"]:
            score += 2
        elif brent_chg > thresholds["brent_change_medium"]:
            score += 1

    if gas_chg is not None:
        if gas_chg > thresholds["gas_change_high"]:
            score += 2
        elif gas_chg > thresholds["gas_change_medium"]:
            score += 1

    if brent_lvl is not None:
        if brent_lvl >= thresholds["brent_level_high"]:
            score += 2
        elif brent_lvl >= thresholds["brent_level_medium"]:
            score += 1

    level = "Low"
    if score >= thresholds["score_high"]:
        level = "High"
    elif score >= thresholds["score_medium"]:
        level = "Medium"

    net_change = sum(v for v in [brent_chg, gas_chg] if v is not None) if any(v is not None for v in [brent_chg, gas_chg]) else None
    direction = direction_from_change(net_change, inverse_good=False, deadband=0.1)

    reason_parts = []
    if brent_lvl is not None:
        reason_parts.append(f"Brent at {brent_lvl:,.1f}")
    if gas_lvl is not None:
        reason_parts.append(f"gas at {gas_lvl:,.2f}")
    reason = ", ".join(reason_parts) if reason_parts else "Energy pricing signals are mixed."

    return build_assessment_item(
        "energy_shock_pressure",
        level,
        direction,
        reason,
    )


def assess_imported_inflation(
    live_data: Dict[str, Dict[str, Any]],
    egypt_reaction_data: Dict[str, Dict[str, Any]],
) -> Dict[str, str]:
    thresholds = ASSESSMENT_THRESHOLDS["imported_inflation_pressure"]
    wheat = live_data.get("wheat", {})
    brent = live_data.get("brent", {})
    usd_egp = live_data.get("usd_egp", {})
    headline = egypt_reaction_data.get("headline_inflation", {})

    wheat_chg = change_value(wheat)
    brent_chg = change_value(brent)
    fx_chg = change_value(usd_egp)
    headline_lvl = latest_value(headline)
    headline_chg = yoy_change_value(headline)

    score = 0

    for val, high_cut, med_cut in [
        (wheat_chg, thresholds["wheat_change_high"], thresholds["wheat_change_medium"]),
        (brent_chg, thresholds["brent_change_high"], thresholds["brent_change_medium"]),
        (fx_chg, thresholds["fx_change_high"], thresholds["fx_change_medium"]),
        (headline_chg, thresholds["headline_yoy_change_high"], thresholds["headline_yoy_change_medium"]),
    ]:
        if val is None:
            continue
        if val > high_cut:
            score += 2
        elif val > med_cut:
            score += 1

    if headline_lvl is not None:
        if headline_lvl >= thresholds["headline_level_high"]:
            score += 2
        elif headline_lvl >= thresholds["headline_level_medium"]:
            score += 1

    level = "Low"
    if score >= thresholds["score_high"]:
        level = "High"
    elif score >= thresholds["score_medium"]:
        level = "Medium"

    signal_sum = sum(v for v in [wheat_chg, brent_chg, fx_chg, headline_chg] if v is not None) if any(v is not None for v in [wheat_chg, brent_chg, fx_chg, headline_chg]) else None
    direction = direction_from_change(signal_sum, inverse_good=False, deadband=0.2)

    reason = "YoY inflation pass-through signals are "
    if level == "High":
        reason += "jointly pointing to elevated imported inflation pressure."
    elif level == "Medium":
        reason += "showing moderate pass-through risk."
    else:
        reason += "not showing broad pass-through stress."

    return build_assessment_item(
        "imported_inflation_pressure",
        level,
        direction,
        reason,
    )


def assess_external_inflows(
    inflow_data: Dict[str, Dict[str, Any]],
) -> Dict[str, str]:
    suez = inflow_data.get("suez_revenues", {})
    tourists = inflow_data.get("tourist_arrivals", {})
    nights = inflow_data.get("tourism_nights", {})
    remittances = inflow_data.get("remittances", {})

    deltas = [
        yoy_change_value(suez),
        yoy_change_value(tourists),
        yoy_change_value(nights),
        yoy_change_value(remittances),
    ]

    negative_count = sum(1 for d in deltas if d is not None and d < 0)
    positive_count = sum(1 for d in deltas if d is not None and d > 0)

    if negative_count >= 3:
        level = "High"
    elif negative_count >= 1:
        level = "Medium"
    elif positive_count >= 2:
        level = "Low"
    else:
        level = "Medium"

    net_change = sum(d for d in deltas if d is not None) if any(d is not None for d in deltas) else None
    direction = direction_from_change(net_change, inverse_good=True, deadband=0.05)

    reason = "Based on Suez, tourism, and remittance readings."
    if level == "High":
        reason = "Multiple external inflow channels are weakening at the same time."
    elif level == "Medium":
        reason = "External inflow channels are mixed and need monitoring."
    elif level == "Low":
        reason = "Recent inflow readings look relatively resilient."

    return build_assessment_item(
        "external_inflows_pressure",
        level,
        direction,
        reason,
    )


def assess_trade_pressure(
    balance_data: Dict[str, Dict[str, Any]],
) -> Dict[str, str]:
    thresholds = ASSESSMENT_THRESHOLDS["trade_pressure"]
    imports = balance_data.get("imports", {})
    exports = balance_data.get("exports", {})
    trade_balance = balance_data.get("trade_balance", {})

    imports_chg = yoy_change_value(imports)
    exports_chg = yoy_change_value(exports)
    tb_latest = latest_value(trade_balance)
    tb_chg = yoy_change_value(trade_balance)

    score = 0

    if imports_chg is not None:
        if imports_chg > thresholds["imports_yoy_high"]:
            score += 2
        elif imports_chg > thresholds["imports_yoy_medium"]:
            score += 1

    if exports_chg is not None:
        if exports_chg < thresholds["exports_yoy_high_negative"]:
            score += 2
        elif exports_chg < thresholds["exports_yoy_medium_negative"]:
            score += 1

    if tb_latest is not None:
        if tb_latest <= thresholds["trade_balance_level_high"]:
            score += 2
        elif tb_latest <= thresholds["trade_balance_level_medium"]:
            score += 1

    level = "Low"
    if score >= thresholds["score_high"]:
        level = "High"
    elif score >= thresholds["score_medium"]:
        level = "Medium"

    direction = direction_from_change(tb_chg, inverse_good=True, deadband=0.05)

    if level == "High":
        reason = "Import pressure and trade-balance weakness are elevated."
    elif level == "Medium":
        reason = "Trade dynamics are manageable but still under pressure."
    else:
        reason = "Trade data does not currently imply severe strain."

    return build_assessment_item(
        "trade_pressure",
        level,
        direction,
        reason,
    )


def assess_fx_pressure(
    live_data: Dict[str, Dict[str, Any]],
    balance_data: Dict[str, Dict[str, Any]],
) -> Dict[str, str]:
    thresholds = ASSESSMENT_THRESHOLDS["fx_pressure"]
    usd_egp = live_data.get("usd_egp", {})
    reserves = balance_data.get("net_reserves", {})

    fx_chg = change_value(usd_egp)
    fx_lvl = latest_value(usd_egp)
    reserves_chg = yoy_change_value(reserves)

    score = 0

    if fx_chg is not None:
        if fx_chg > thresholds["fx_change_high"]:
            score += 2
        elif fx_chg > thresholds["fx_change_medium"]:
            score += 1

    if reserves_chg is not None:
        if reserves_chg < thresholds["reserves_yoy_high_negative"]:
            score += 2
        elif reserves_chg < thresholds["reserves_yoy_medium_negative"]:
            score += 1
        elif reserves_chg > 0:
            score -= 1

    level = "Low"
    if score >= thresholds["score_high"]:
        level = "High"
    elif score >= thresholds["score_medium"]:
        level = "Medium"

    composite_change = 0.0
    have_signal = False
    if fx_chg is not None:
        composite_change += fx_chg
        have_signal = True
    if reserves_chg is not None:
        composite_change -= reserves_chg
        have_signal = True

    direction = direction_from_change(composite_change if have_signal else None, inverse_good=False, deadband=0.05)

    reason = f"USD/EGP at {fx_lvl:,.2f}." if fx_lvl is not None else "FX signals are mixed."
    if reserves_chg is not None:
        reason += f" YoY reserves change: {reserves_chg:+.2f}."

    return build_assessment_item(
        "fx_pressure",
        level,
        direction,
        reason,
    )


def assess_domestic_activity(
    live_data: Dict[str, Dict[str, Any]],
    business_data: Dict[str, Dict[str, Any]],
) -> Dict[str, str]:
    thresholds = ASSESSMENT_THRESHOLDS["domestic_activity_pressure"]
    egx30 = live_data.get("egx30", {})
    fdi = business_data.get("fdi", {})
    companies = business_data.get("companies_established", {})
    capital = business_data.get("issued_capital", {})

    egx_chg = change_value(egx30)
    fdi_chg = yoy_change_value(fdi)
    companies_chg = yoy_change_value(companies)
    capital_chg = yoy_change_value(capital)

    weakness_score = 0

    for val, threshold in [
        (egx_chg, thresholds["egx_change_high_negative"]),
        (fdi_chg, thresholds["fdi_yoy_high_negative"]),
        (companies_chg, thresholds["companies_yoy_high_negative"]),
        (capital_chg, thresholds["capital_yoy_high_negative"]),
    ]:
        if val is None:
            continue
        if val <= threshold:
            weakness_score += 2
        elif val < 0:
            weakness_score += 1

    level = "Low"
    if weakness_score >= 5:
        level = "High"
    elif weakness_score >= 2:
        level = "Medium"

    signal_sum = sum(v for v in [egx_chg, fdi_chg, companies_chg, capital_chg] if v is not None) if any(v is not None for v in [egx_chg, fdi_chg, companies_chg, capital_chg]) else None
    direction = direction_from_change(signal_sum, inverse_good=True, deadband=0.1)

    if level == "High":
        reason = "Business and market indicators suggest weakening domestic activity."
    elif level == "Medium":
        reason = "Domestic activity signals are mixed and need monitoring."
    else:
        reason = "Business and market indicators look relatively resilient."

    return build_assessment_item(
        "domestic_activity_pressure",
        level,
        direction,
        reason,
    )


# =========================================================
# AGGREGATOR
# =========================================================
def build_assessment_items(
    live_data: Dict[str, Dict[str, Any]],
    egypt_reaction_data: Dict[str, Dict[str, Any]],
    inflow_data: Dict[str, Dict[str, Any]],
    balance_data: Dict[str, Dict[str, Any]],
    business_data: Dict[str, Dict[str, Any]],
) -> Dict[str, Dict[str, str]]:
    """
    Build all six executive-strip assessment items.
    """
    items = {
        "energy_shock_pressure": assess_energy_shock(live_data),
        "imported_inflation_pressure": assess_imported_inflation(live_data, egypt_reaction_data),
        "external_inflows_pressure": assess_external_inflows(inflow_data),
        "trade_pressure": assess_trade_pressure(balance_data),
        "fx_pressure": assess_fx_pressure(live_data, balance_data),
        "domestic_activity_pressure": assess_domestic_activity(live_data, business_data),
    }
    return items