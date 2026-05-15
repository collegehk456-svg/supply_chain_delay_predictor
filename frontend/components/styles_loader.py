"""Load shared CSS theme into Streamlit."""

from pathlib import Path

import streamlit as st


def inject_theme() -> None:
    theme_path = Path(__file__).parent.parent / "styles" / "theme.css"
    if theme_path.exists():
        css = theme_path.read_text(encoding="utf-8")
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
