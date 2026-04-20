from __future__ import annotations

import streamlit as st

from config import CACHE_TTL_SECONDS
from market_data import (
    load_immediate_shock_data,
    load_live_egypt_reaction_market_data,
)
from egypt_data import (
    load_business_activity_data,
    load_domestic_price_pressure_data,
    load_egypt_reaction_data,
    load_external_balance_data,
    load_external_inflows_data,
)


@st.cache_data(ttl=CACHE_TTL_SECONDS)
def get_live_immediate_shock_data(selected_window_label: str):
    return load_immediate_shock_data(selected_window_label)


@st.cache_data(ttl=CACHE_TTL_SECONDS)
def get_live_egypt_reaction_market_data(selected_window_label: str):
    return load_live_egypt_reaction_market_data(selected_window_label)


@st.cache_data(ttl=CACHE_TTL_SECONDS)
def get_official_egypt_reaction_data():
    return load_egypt_reaction_data()


@st.cache_data(ttl=CACHE_TTL_SECONDS)
def get_external_inflows_data():
    return load_external_inflows_data()


@st.cache_data(ttl=CACHE_TTL_SECONDS)
def get_external_balance_data():
    return load_external_balance_data()


@st.cache_data(ttl=CACHE_TTL_SECONDS)
def get_business_activity_data():
    return load_business_activity_data()


@st.cache_data(ttl=CACHE_TTL_SECONDS)
def get_domestic_price_pressure_data():
    return load_domestic_price_pressure_data()
