# egypt_data.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import re

import pandas as pd

from config import OFFICIAL_INDICATOR_CONFIG
from cbe_data import fetch_cbe_stats
from manual_series import (
    HEADLINE_INFLATION_MONTHLY,
    CORE_INFLATION_MONTHLY,
    OVERNIGHT_DEPOSIT_RATE_SERIES,
    OVERNIGHT_LENDING_RATE_SERIES,
    MAIN_OPERATION_RATE_SERIES,
    CONIA_MONTHLY,
    SUEZ_REVENUES_MONTHLY_EGP,
    TOURIST_ARRIVALS_MONTHLY,
    TOURISM_NIGHTS_MONTHLY,
    REMITTANCES_QUARTERLY,
    EXPORTS_MONTHLY,
    IMPORTS_MONTHLY,
    TRADE_BALANCE_MONTHLY,
    NET_RESERVES_MONTHLY,
    FDI_QUARTERLY,
    COMPANIES_ESTABLISHED_MONTHLY,
    ISSUED_CAPITAL_MONTHLY,
    FOOD_INFLATION_ANNUAL,
    CPI_WEIGHTS,
    CATEGORY_INFLATION_SNAPSHOT_MAR_2026,
    CPI_MONTHLY_MOM,
    MARCH_2026_EXTERNAL_FX_SNAPSHOT,
)


# =========================================================
# STANDARD RECORD SHAPE
# =========================================================
@dataclass
class IndicatorRecord:
    id: str
    title: str
    tag: str
    frequency: str
    source: str
    unit: str
    section: str
    description: str
    latest_value: Optional[float]
    previous_value: Optional[float]
    change_value: Optional[float]
    change_pct: Optional[float]
    reference_period: Optional[str]
    previous_period: Optional[str]
    yoy_value: Optional[float]
    yoy_period: Optional[str]
    yoy_change_value: Optional[float]
    yoy_change_pct: Optional[float]
    data_status: str
    current_snapshot_value: Optional[float]
    current_snapshot_asof: Optional[str]
    current_snapshot_note: Optional[str]
    series: pd.DataFrame
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "tag": self.tag,
            "frequency": self.frequency,
            "source": self.source,
            "unit": self.unit,
            "section": self.section,
            "description": self.description,
            "latest_value": self.latest_value,
            "previous_value": self.previous_value,
            "change_value": self.change_value,
            "change_pct": self.change_pct,
            "reference_period": self.reference_period,
            "previous_period": self.previous_period,
            "yoy_value": self.yoy_value,
            "yoy_period": self.yoy_period,
            "yoy_change_value": self.yoy_change_value,
            "yoy_change_pct": self.yoy_change_pct,
            "data_status": self.data_status,
            "current_snapshot_value": self.current_snapshot_value,
            "current_snapshot_asof": self.current_snapshot_asof,
            "current_snapshot_note": self.current_snapshot_note,
            "series": self.series,
            "notes": self.notes,
        }


# =========================================================
# LOW-LEVEL HELPERS
# =========================================================
def series_to_dataframe(raw_series: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Convert a manual list-of-dicts series into a standard dataframe.
    Expected minimally: period, value
    Optional fields: source_note, unit, etc.
    """
    df = pd.DataFrame(raw_series).copy()

    if df.empty:
        return pd.DataFrame(columns=["period", "value"])

    if "period" not in df.columns or "value" not in df.columns:
        raise ValueError("Series must include 'period' and 'value' fields.")

    df = df.sort_values("period").reset_index(drop=True)
    return df


def latest_valid_rows(series_df: pd.DataFrame) -> pd.DataFrame:
    """
    Keep only rows with non-null values, preserving order.
    """
    if series_df.empty:
        return series_df.copy()

    if "value" not in series_df.columns:
        raise ValueError("Series dataframe must contain a 'value' column.")

    return series_df[series_df["value"].notna()].copy().reset_index(drop=True)


def compute_latest_and_previous(series_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Return latest/previous values and periods from a standard series dataframe.
    """
    valid = latest_valid_rows(series_df)

    if valid.empty:
        return {
            "latest_value": None,
            "previous_value": None,
            "reference_period": None,
            "previous_period": None,
        }

    latest_row = valid.iloc[-1]
    previous_row = valid.iloc[-2] if len(valid) >= 2 else None

    return {
        "latest_value": float(latest_row["value"]) if pd.notna(latest_row["value"]) else None,
        "previous_value": float(previous_row["value"]) if previous_row is not None and pd.notna(previous_row["value"]) else None,
        "reference_period": str(latest_row["period"]),
        "previous_period": str(previous_row["period"]) if previous_row is not None else None,
    }


def compute_change(latest_value: Optional[float], previous_value: Optional[float]) -> Dict[str, Optional[float]]:
    if latest_value is None or previous_value is None:
        return {"change_value": None, "change_pct": None}

    change_value = latest_value - previous_value
    change_pct = None if previous_value == 0 else (change_value / previous_value) * 100.0

    return {
        "change_value": change_value,
        "change_pct": change_pct,
    }



def infer_yoy_period(period: Optional[str]) -> Optional[str]:
    if not period:
        return None

    monthly = re.match(r"^(\d{4})-(\d{2})$", str(period))
    if monthly:
        year, month = monthly.groups()
        return f"{int(year) - 1:04d}-{month}"

    quarterly = re.match(r"^(\d{4})-Q([1-4])$", str(period))
    if quarterly:
        year, quarter = quarterly.groups()
        return f"{int(year) - 1:04d}-Q{quarter}"

    annual = re.match(r"^(\d{4})$", str(period))
    if annual:
        return f"{int(annual.group(1)) - 1:04d}"

    fiscal = re.match(r"^(\d{4})/(\d{4})$", str(period))
    if fiscal:
        a, b = fiscal.groups()
        return f"{int(a) - 1:04d}/{int(b) - 1:04d}"

    return None


def compute_yoy(series_df: pd.DataFrame, reference_period: Optional[str], latest_value: Optional[float]) -> Dict[str, Any]:
    if latest_value is None or reference_period is None or series_df.empty:
        return {
            "yoy_value": None,
            "yoy_period": None,
            "yoy_change_value": None,
            "yoy_change_pct": None,
        }

    yoy_period = infer_yoy_period(reference_period)
    if yoy_period is None:
        return {
            "yoy_value": None,
            "yoy_period": None,
            "yoy_change_value": None,
            "yoy_change_pct": None,
        }

    valid = latest_valid_rows(series_df)
    match = valid[valid["period"].astype(str) == yoy_period]
    if match.empty:
        return {
            "yoy_value": None,
            "yoy_period": yoy_period,
            "yoy_change_value": None,
            "yoy_change_pct": None,
        }

    yoy_value = float(match.iloc[-1]["value"])
    yoy_change_value = latest_value - yoy_value
    yoy_change_pct = None if yoy_value == 0 else (yoy_change_value / yoy_value) * 100.0

    return {
        "yoy_value": yoy_value,
        "yoy_period": yoy_period,
        "yoy_change_value": yoy_change_value,
        "yoy_change_pct": yoy_change_pct,
    }


def determine_data_status(series_df: pd.DataFrame) -> str:
    if series_df.empty:
        return "placeholder"

    if "value" not in series_df.columns:
        return "placeholder"

    total_rows = len(series_df)
    valid_rows = int(series_df["value"].notna().sum())

    if valid_rows == 0:
        return "placeholder"
    if valid_rows < total_rows:
        return "partial"
    return "complete"


def build_snapshot_fields(
    use_snapshot: bool,
    snapshot_value: Optional[float],
    snapshot_asof: Optional[str],
    snapshot_note: Optional[str],
) -> Dict[str, Any]:
    if not use_snapshot:
        return {
            "current_snapshot_value": None,
            "current_snapshot_asof": None,
            "current_snapshot_note": None,
        }

    return {
        "current_snapshot_value": snapshot_value,
        "current_snapshot_asof": snapshot_asof,
        "current_snapshot_note": snapshot_note,
    }


def make_indicator_record(
    indicator_id: str,
    raw_series: List[Dict[str, Any]],
    notes: Optional[str] = None,
    current_snapshot_value: Optional[float] = None,
    current_snapshot_asof: Optional[str] = None,
    current_snapshot_note: Optional[str] = None,
) -> IndicatorRecord:
    """
    Build a normalized IndicatorRecord from config + manual series.
    """
    if indicator_id not in OFFICIAL_INDICATOR_CONFIG:
        raise KeyError(f"Missing indicator config for '{indicator_id}'.")

    cfg = OFFICIAL_INDICATOR_CONFIG[indicator_id]
    df = series_to_dataframe(raw_series)

    stats = compute_latest_and_previous(df)
    delta = compute_change(stats["latest_value"], stats["previous_value"])
    yoy = compute_yoy(df, stats["reference_period"], stats["latest_value"])
    data_status = determine_data_status(df)

    return IndicatorRecord(
        id=indicator_id,
        title=cfg["title"],
        tag=cfg["tag"],
        frequency=cfg["frequency"],
        source=cfg["source"],
        unit=cfg["unit"],
        section=cfg["section"],
        description=cfg["description"],
        latest_value=stats["latest_value"],
        previous_value=stats["previous_value"],
        change_value=delta["change_value"],
        change_pct=delta["change_pct"],
        reference_period=stats["reference_period"],
        previous_period=stats["previous_period"],
        yoy_value=yoy["yoy_value"],
        yoy_period=yoy["yoy_period"],
        yoy_change_value=yoy["yoy_change_value"],
        yoy_change_pct=yoy["yoy_change_pct"],
        data_status=data_status,
        current_snapshot_value=current_snapshot_value,
        current_snapshot_asof=current_snapshot_asof,
        current_snapshot_note=current_snapshot_note,
        series=df,
        notes=notes,
    )




# =========================================================
# SECTION LOADERS
# =========================================================
def load_egypt_reaction_data() -> Dict[str, Dict[str, Any]]:
    """
    Official indicators used in the Egypt Reaction section.

    Historical released series stay separate from the current CBE homepage snapshot.
    The dashboard can display both, but snapshot values are not injected into the
    stored monthly history.
    """
    cbe_result = fetch_cbe_stats()
    cbe_stats = cbe_result.stats

    snapshot_asof = cbe_result.fetched_at_utc
    snapshot_note = (
        f"Current CBE homepage snapshot. Fetch status: {cbe_result.fetch_status}. "
        f"Fallback keys: {', '.join(cbe_result.used_fallback_keys) if cbe_result.used_fallback_keys else 'none'}."
    )
    if cbe_result.notes:
        snapshot_note += " " + " | ".join(cbe_result.notes)

    records = {
        "headline_inflation": make_indicator_record(
            "headline_inflation",
            HEADLINE_INFLATION_MONTHLY,
            notes=f"Historical monthly release series. Inflation target: {cbe_stats.get('inflation_target_text', 'N/A')}",
            current_snapshot_value=cbe_stats.get("headline_inflation_rate"),
            current_snapshot_asof=snapshot_asof,
            current_snapshot_note=snapshot_note,
        ),
        "core_inflation": make_indicator_record(
            "core_inflation",
            CORE_INFLATION_MONTHLY,
            notes="Historical monthly release series.",
            current_snapshot_value=cbe_stats.get("core_inflation_rate"),
            current_snapshot_asof=snapshot_asof,
            current_snapshot_note=snapshot_note,
        ),
        "overnight_deposit": make_indicator_record(
            "overnight_deposit",
            OVERNIGHT_DEPOSIT_RATE_SERIES,
            notes="Historical released rate series, if available.",
            current_snapshot_value=cbe_stats.get("overnight_deposit_rate"),
            current_snapshot_asof=snapshot_asof,
            current_snapshot_note=snapshot_note,
        ),
        "overnight_lending": make_indicator_record(
            "overnight_lending",
            OVERNIGHT_LENDING_RATE_SERIES,
            notes="Historical released rate series, if available.",
            current_snapshot_value=cbe_stats.get("overnight_lending_rate"),
            current_snapshot_asof=snapshot_asof,
            current_snapshot_note=snapshot_note,
        ),
        "main_operation": make_indicator_record(
            "main_operation",
            MAIN_OPERATION_RATE_SERIES,
            notes="Historical released rate series, if available.",
            current_snapshot_value=cbe_stats.get("main_operation"),
            current_snapshot_asof=snapshot_asof,
            current_snapshot_note=snapshot_note,
        ),
        "conia": make_indicator_record(
            "conia",
            CONIA_MONTHLY,
            notes="Historical released CONIA series, if available.",
            current_snapshot_value=cbe_stats.get("conia"),
            current_snapshot_asof=snapshot_asof,
            current_snapshot_note=snapshot_note,
        ),
    }
    return {k: v.to_dict() for k, v in records.items()}


def load_external_inflows_data() -> Dict[str, Dict[str, Any]]:
    """
    Official external inflow indicators.
    """
    records = {
        "suez_revenues": make_indicator_record("suez_revenues", SUEZ_REVENUES_MONTHLY_EGP),
        "tourist_arrivals": make_indicator_record("tourist_arrivals", TOURIST_ARRIVALS_MONTHLY),
        "tourism_nights": make_indicator_record("tourism_nights", TOURISM_NIGHTS_MONTHLY),
        "remittances": make_indicator_record("remittances", REMITTANCES_QUARTERLY),
    }
    return {k: v.to_dict() for k, v in records.items()}


def load_external_balance_data() -> Dict[str, Dict[str, Any]]:
    """
    Official external balance indicators.
    """
    records = {
        "exports": make_indicator_record("exports", EXPORTS_MONTHLY),
        "imports": make_indicator_record("imports", IMPORTS_MONTHLY),
        "trade_balance": make_indicator_record("trade_balance", TRADE_BALANCE_MONTHLY),
        "net_reserves": make_indicator_record("net_reserves", NET_RESERVES_MONTHLY),
    }
    return {k: v.to_dict() for k, v in records.items()}


def load_business_activity_data() -> Dict[str, Dict[str, Any]]:
    """
    Official investment / business activity indicators.
    """
    records = {
        "fdi": make_indicator_record("fdi", FDI_QUARTERLY),
        "companies_established": make_indicator_record("companies_established", COMPANIES_ESTABLISHED_MONTHLY),
        "issued_capital": make_indicator_record("issued_capital", ISSUED_CAPITAL_MONTHLY),
    }
    return {k: v.to_dict() for k, v in records.items()}


def load_domestic_price_pressure_data() -> Dict[str, Any]:
    """
    Mixed data for domestic price pressure section.
    This includes one normalized indicator plus supporting chart/table data.
    """
    food_inflation_record = make_indicator_record(
        "food_inflation",
        FOOD_INFLATION_ANNUAL,
        notes="Annual food inflation series currently loaded; monthly food inflation can be substituted later if available."
    )

    return {
        "food_inflation": food_inflation_record.to_dict(),
        "cpi_weights": pd.DataFrame(CPI_WEIGHTS),
        "category_inflation_snapshot": pd.DataFrame(CATEGORY_INFLATION_SNAPSHOT_MAR_2026),
        "cpi_monthly_mom": pd.DataFrame(CPI_MONTHLY_MOM),
        "external_fx_snapshot": MARCH_2026_EXTERNAL_FX_SNAPSHOT,
    }


# =========================================================
# AGGREGATED LOADER
# =========================================================
def load_all_egypt_official_data() -> Dict[str, Any]:
    """
    Convenience loader for the whole official-data layer.
    """
    return {
        "egypt_reaction": load_egypt_reaction_data(),
        "external_inflows": load_external_inflows_data(),
        "external_balance": load_external_balance_data(),
        "business_activity": load_business_activity_data(),
        "domestic_price_pressure": load_domestic_price_pressure_data(),
    }