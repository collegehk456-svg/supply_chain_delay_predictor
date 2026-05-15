import streamlit as st
from typing import List, Dict, Any
import json
from datetime import datetime

def init_session_state():
    """
    Initialize all session state variables.
    """
    if "page" not in st.session_state:
        st.session_state.page = "home"
    
    if "predictions_history" not in st.session_state:
        st.session_state.predictions_history = []
    
    if "theme_dark" not in st.session_state:
        st.session_state.theme_dark = True
    
    if "user_preferences" not in st.session_state:
        st.session_state.user_preferences = {
            "show_advanced": False,
            "notifications": True,
            "auto_refresh": False,
        }


def load_css_files():
    """
    Load all CSS files and inject into Streamlit.
    """
    css_files = [
        "frontend/styles/theme.css",
        "frontend/styles/animations.css",
        "frontend/styles/global.css",
    ]
    
    css_content = ""
    
    for css_file in css_files:
        try:
            with open(css_file, "r") as f:
                css_content += f.read() + "\n"
        except FileNotFoundError:
            pass
    
    if css_content:
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)


def format_number(value: float, decimals: int = 2) -> str:
    """
    Format number with abbreviations (K, M, B).
    """
    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.{decimals}f}B"
    elif value >= 1_000_000:
        return f"{value / 1_000_000:.{decimals}f}M"
    elif value >= 1_000:
        return f"{value / 1_000:.{decimals}f}K"
    else:
        return f"{value:.{decimals}f}"


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Format percentage value.
    """
    return f"{value:.{decimals}f}%"


def get_color_by_value(value: float, low: float = 0, high: float = 100) -> str:
    """
    Get color based on value range.
    """
    percentage = (value - low) / (high - low)
    
    if percentage < 0.33:
        return "#ef4444"  # Red
    elif percentage < 0.66:
        return "#fb923c"  # Orange
    else:
        return "#22c55e"  # Green


def add_to_history(prediction: Dict[str, Any]):
    """
    Add prediction to history.
    """
    prediction["timestamp"] = datetime.now().isoformat()
    st.session_state.predictions_history.append(prediction)
    
    # Keep only last 100 predictions
    if len(st.session_state.predictions_history) > 100:
        st.session_state.predictions_history = st.session_state.predictions_history[-100:]


def get_history() -> List[Dict[str, Any]]:
    """
    Get prediction history.
    """
    return st.session_state.predictions_history
