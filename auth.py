from __future__ import annotations

import streamlit as st

PASSWORD = "AhmedRostom"


def require_password() -> None:
    if st.session_state.get("authenticated", False):
        return

    st.title("War Shock Monitor")
    st.caption("Enter the password to view this page.")

    entered_password = st.text_input("Password", type="password")

    if st.button("Unlock"):
        if entered_password == PASSWORD:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Incorrect password.")

    st.stop()
