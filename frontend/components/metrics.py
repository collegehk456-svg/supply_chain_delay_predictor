import streamlit as st
from datetime import datetime
import time

def animated_counter(target: int, label: str, duration: float = 1.0, icon: str = "📊"):
    """
    Animated counter that counts up to target value.
    """
    placeholder = st.empty()
    
    start_time = time.time()
    while time.time() - start_time < duration:
        progress = (time.time() - start_time) / duration
        current_value = int(target * progress)
        
        placeholder.metric(label, f"{current_value:,}", delta=None)
        time.sleep(0.01)
    
    placeholder.metric(label, f"{target:,}", delta=None)


def create_metrics_row(metrics: list):
    """
    Create a row of metric cards with equal spacing.
    metrics: list of dicts with 'label', 'value', 'change', 'icon'
    """
    cols = st.columns(len(metrics))
    
    for idx, col in enumerate(cols):
        with col:
            metric = metrics[idx]
            st.metric(
                label=metric.get('label', ''),
                value=metric.get('value', 0),
                delta=metric.get('change', None)
            )


def kpi_display(title: str, value: str, subtitle: str = "", 
               trend: str = None, trend_color: str = "green"):
    """
    Premium KPI display component.
    """
    st.markdown(f"""
        <style>
        .kpi-display-{id(title)} {{
            background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(168, 85, 247, 0.1) 100%);
            border: 1px solid rgba(0, 212, 255, 0.3);
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
            animation: slideInUp 0.5s ease-out;
        }}
        
        .kpi-title {{
            font-size: 0.85rem;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.5rem;
            font-weight: 600;
        }}
        
        .kpi-value {{
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #00d4ff 0%, #a855f7 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.5rem;
        }}
        
        .kpi-subtitle {{
            font-size: 0.9rem;
            color: #cbd5e1;
            margin-bottom: 0.75rem;
        }}
        
        .kpi-trend {{
            font-size: 0.85rem;
            color: {trend_color};
            font-weight: 600;
        }}
        </style>
        
        <div class="kpi-display-{id(title)}">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value}</div>
            {f'<div class="kpi-subtitle">{subtitle}</div>' if subtitle else ''}
            {f'<div class="kpi-trend">{trend}</div>' if trend else ''}
        </div>
    """, unsafe_allow_html=True)
