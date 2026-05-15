"""
SmartShip AI - Production-Grade Supply Chain Intelligence Platform
Futuristic Streamlit dashboard with glassmorphism design.
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import os
import uuid

st.set_page_config(
    page_title="SmartShip AI",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_URL = os.getenv("API_URL", "http://localhost:8000")

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, sans-serif !important;
}

/* Dark background */
.stApp {
    background: linear-gradient(135deg, #020817 0%, #0a1628 50%, #0d1f3c 100%) !important;
}
.stApp > header { background: transparent !important; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a0e27 0%, #0f172a 100%) !important;
    border-right: 1px solid rgba(0,212,255,0.12) !important;
}
section[data-testid="stSidebar"] .stRadio label {
    color: #94a3b8 !important;
    font-weight: 500;
    font-size: 0.9rem;
    padding: 6px 0;
    transition: color 0.2s;
}
section[data-testid="stSidebar"] .stRadio label:hover { color: #00d4ff !important; }

/* Main content padding */
.block-container { padding: 1.5rem 2rem 3rem 2rem !important; max-width: 1400px; }

/* Page hero banner */
.hero-banner {
    background: linear-gradient(135deg, rgba(0,212,255,0.08) 0%, rgba(168,85,247,0.08) 100%);
    border: 1px solid rgba(0,212,255,0.15);
    border-radius: 20px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.hero-banner::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; bottom: 0;
    background: radial-gradient(ellipse at top left, rgba(0,212,255,0.06) 0%, transparent 60%);
    pointer-events: none;
}
.hero-title {
    font-size: 2.4rem; font-weight: 800; letter-spacing: -0.03em;
    background: linear-gradient(135deg, #00d4ff 0%, #a855f7 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; margin: 0 0 0.4rem 0;
}
.hero-subtitle { color: #94a3b8; font-size: 1rem; margin: 0; font-weight: 400; }

/* Metric cards */
.kpi-grid { display: flex; gap: 1rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
.kpi-card {
    flex: 1; min-width: 160px;
    background: rgba(15,23,42,0.7);
    border: 1px solid rgba(0,212,255,0.15);
    border-radius: 16px; padding: 1.25rem 1.5rem;
    backdrop-filter: blur(10px);
    transition: all 0.25s cubic-bezier(0.4,0,0.2,1);
    position: relative; overflow: hidden;
}
.kpi-card:hover {
    border-color: rgba(0,212,255,0.4);
    box-shadow: 0 8px 32px rgba(0,212,255,0.12);
    transform: translateY(-3px);
}
.kpi-icon { font-size: 1.4rem; margin-bottom: 0.6rem; }
.kpi-value {
    font-size: 2rem; font-weight: 800; letter-spacing: -0.02em;
    background: linear-gradient(135deg, #00d4ff 0%, #0ea5e9 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; margin-bottom: 0.25rem;
}
.kpi-label { font-size: 0.75rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.08em; font-weight: 600; }
.kpi-change { font-size: 0.8rem; color: #22c55e; font-weight: 600; margin-top: 0.4rem; }

/* Section cards */
.section-card {
    background: rgba(15,23,42,0.6);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px; padding: 1.5rem;
    backdrop-filter: blur(10px);
    margin-bottom: 1rem;
}

/* Prediction result cards */
.pred-delayed {
    background: linear-gradient(135deg, rgba(239,68,68,0.12) 0%, rgba(239,68,68,0.04) 100%);
    border: 1px solid rgba(239,68,68,0.35);
    border-radius: 16px; padding: 1.5rem; text-align: center;
}
.pred-ontime {
    background: linear-gradient(135deg, rgba(34,197,94,0.12) 0%, rgba(34,197,94,0.04) 100%);
    border: 1px solid rgba(34,197,94,0.35);
    border-radius: 16px; padding: 1.5rem; text-align: center;
}
.pred-label { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; color: #94a3b8; font-weight: 600; margin-bottom: 0.5rem; }
.pred-value-delayed { font-size: 1.8rem; font-weight: 800; color: #ef4444; }
.pred-value-ontime { font-size: 1.8rem; font-weight: 800; color: #22c55e; }
.pred-value-neutral { font-size: 1.8rem; font-weight: 800; color: #00d4ff; }

/* Factor pills */
.factor-pill {
    display: inline-block;
    background: rgba(0,212,255,0.1);
    border: 1px solid rgba(0,212,255,0.25);
    color: #00d4ff; border-radius: 20px;
    padding: 0.3rem 0.9rem; font-size: 0.82rem; font-weight: 600;
    margin: 0.2rem; transition: all 0.2s;
}

/* Chat bubbles */
.chat-container {
    display: flex; flex-direction: column; gap: 0.75rem;
    max-height: 460px; overflow-y: auto; padding: 1rem 0;
}
.chat-msg-user {
    background: linear-gradient(135deg, rgba(0,212,255,0.15) 0%, rgba(14,165,233,0.1) 100%);
    border: 1px solid rgba(0,212,255,0.25);
    border-radius: 16px 16px 4px 16px;
    padding: 0.85rem 1.1rem; align-self: flex-end;
    max-width: 80%; color: #e2e8f0; font-size: 0.9rem; line-height: 1.5;
}
.chat-msg-assistant {
    background: rgba(15,23,42,0.8);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px 16px 16px 4px;
    padding: 0.85rem 1.1rem; align-self: flex-start;
    max-width: 85%; color: #cbd5e1; font-size: 0.9rem; line-height: 1.6;
}
.chat-avatar { font-size: 1.1rem; margin-bottom: 0.25rem; }
.chat-timestamp { font-size: 0.7rem; color: #475569; margin-top: 0.3rem; }

/* Suggestion chips */
.suggestion-chip {
    display: inline-block;
    background: rgba(168,85,247,0.1);
    border: 1px solid rgba(168,85,247,0.3);
    color: #c084fc; border-radius: 20px;
    padding: 0.3rem 0.85rem; font-size: 0.8rem;
    margin: 0.2rem; cursor: pointer;
    transition: all 0.2s;
}
.suggestion-chip:hover {
    background: rgba(168,85,247,0.2);
    border-color: rgba(168,85,247,0.5);
}

/* Rec cards */
.rec-card {
    background: rgba(15,23,42,0.5);
    border-left: 3px solid #00d4ff;
    border-radius: 0 12px 12px 0;
    padding: 1rem 1.25rem; margin-bottom: 0.75rem;
}
.rec-card.high { border-left-color: #ef4444; }
.rec-card.medium { border-left-color: #f97316; }
.rec-action { font-size: 0.9rem; font-weight: 600; color: #f1f5f9; margin-bottom: 0.3rem; }
.rec-reason { font-size: 0.82rem; color: #94a3b8; margin-bottom: 0.3rem; }
.rec-impact { font-size: 0.78rem; color: #22c55e; font-weight: 600; }

/* Stat badges */
.stat-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(0,212,255,0.08);
    border: 1px solid rgba(0,212,255,0.2);
    border-radius: 8px; padding: 0.4rem 0.75rem;
    font-size: 0.82rem; color: #94a3b8; font-weight: 500;
}
.stat-badge span { color: #00d4ff; font-weight: 700; }

/* Scrollbar */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: rgba(255,255,255,0.02); }
::-webkit-scrollbar-thumb { background: rgba(0,212,255,0.25); border-radius: 3px; }

/* Streamlit element overrides */
.stButton > button {
    background: linear-gradient(135deg, #00d4ff 0%, #0ea5e9 100%) !important;
    color: #020817 !important; font-weight: 700 !important;
    border: none !important; border-radius: 10px !important;
    padding: 0.6rem 1.5rem !important;
    box-shadow: 0 4px 15px rgba(0,212,255,0.25) !important;
    transition: all 0.2s !important; font-size: 0.9rem !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 25px rgba(0,212,255,0.35) !important;
}
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
    background: rgba(15,23,42,0.8) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    color: #e2e8f0 !important; border-radius: 10px !important;
}
.stTextInput > div > div > input:focus {
    border-color: rgba(0,212,255,0.5) !important;
    box-shadow: 0 0 0 2px rgba(0,212,255,0.1) !important;
}
.stSlider > div > div > div { color: #00d4ff !important; }
.stMetric { background: rgba(15,23,42,0.5); border-radius: 12px; padding: 0.75rem; }
.stMetric label { color: #64748b !important; font-size: 0.75rem !important; text-transform: uppercase !important; letter-spacing: 0.06em !important; }
.stMetric [data-testid="metric-container"] > div { color: #f1f5f9 !important; }
div[data-testid="stMarkdownContainer"] p { color: #94a3b8; }
hr { border-color: rgba(255,255,255,0.07) !important; }
.stAlert { border-radius: 12px !important; }
.stDataFrame { border-radius: 12px !important; overflow: hidden; }
.stFileUploader { background: rgba(15,23,42,0.5) !important; border: 1px dashed rgba(0,212,255,0.3) !important; border-radius: 12px !important; }
</style>
""", unsafe_allow_html=True)


# ── Session state ─────────────────────────────────────────────────────────────
defaults = {
    'predictions_history': [],
    'chat_messages': [],
    'session_id': str(uuid.uuid4())[:8],
    'chat_input': '',
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ── Helper: API check ─────────────────────────────────────────────────────────
def api_healthy() -> bool:
    try:
        r = requests.get(f"{API_URL}/health", timeout=3)
        return r.status_code == 200 and r.json().get("model_loaded", False)
    except Exception:
        return False


def fmt_time(ts: str) -> str:
    try:
        return datetime.fromisoformat(ts).strftime("%H:%M")
    except Exception:
        return ""


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:1rem 0 0.5rem 0;">
        <div style="font-size:1.6rem;font-weight:900;background:linear-gradient(135deg,#00d4ff,#a855f7);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
            SmartShip AI
        </div>
        <div style="font-size:0.75rem;color:#475569;margin-top:0.2rem;font-weight:500;">
            Supply Chain Intelligence
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    healthy = api_healthy()
    status_color = "#22c55e" if healthy else "#ef4444"
    status_text  = "API Connected" if healthy else "API Offline"
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:8px;padding:0.5rem 0;margin-bottom:0.75rem;">
        <div style="width:8px;height:8px;border-radius:50%;background:{status_color};
                    box-shadow:0 0 8px {status_color};flex-shrink:0;"></div>
        <span style="font-size:0.8rem;color:{status_color};font-weight:600;">{status_text}</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div style="height:1px;background:rgba(255,255,255,0.06);margin-bottom:1rem;"></div>', unsafe_allow_html=True)
    
    page = st.radio(
        "Navigation",
        ["🏠 Home", "⚡ Command Center", "🔮 Single Prediction", "📦 Batch Predictions",
         "📊 Feature Analysis", "📈 Analytics", "🤖 AI Assistant", "ℹ️ About"],
        label_visibility="collapsed"
    )
    
    st.markdown('<div style="height:1px;background:rgba(255,255,255,0.06);margin:1rem 0;"></div>', unsafe_allow_html=True)
    
    total = len(st.session_state.predictions_history)
    if total > 0:
        delayed = sum(1 for p in st.session_state.predictions_history if p.get('prediction') == 1)
        st.markdown(f"""
        <div style="font-size:0.72rem;color:#475569;text-transform:uppercase;letter-spacing:0.08em;font-weight:600;margin-bottom:0.6rem;">
            Session Stats
        </div>
        <div style="display:flex;flex-direction:column;gap:6px;">
            <div class="stat-badge">Predictions <span>{total}</span></div>
            <div class="stat-badge">Delayed <span style="color:#ef4444;">{delayed}</span></div>
            <div class="stat-badge">On-Time <span style="color:#22c55e;">{total-delayed}</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    chat_count = len(st.session_state.chat_messages)
    if chat_count > 0:
        st.markdown(f"""
        <div style="margin-top:0.75rem;">
            <div class="stat-badge">Chat Messages <span>{chat_count}</span></div>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# HOME PAGE
# ═══════════════════════════════════════════════════════════════════════════════
if page == "⚡ Command Center":
    from frontend.pages.command_center import render as render_cc
    render_cc()

elif page == "🏠 Home":
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title">SmartShip AI Platform</div>
        <div class="hero-subtitle">
            AI-powered supply chain delay prediction · Real-time insights · Production-grade MLOps
        </div>
    </div>
    """, unsafe_allow_html=True)

    total = len(st.session_state.predictions_history)
    delayed = sum(1 for p in st.session_state.predictions_history if p.get('prediction') == 1) if total > 0 else 0
    delay_rate = f"{(delayed/total*100):.1f}%" if total > 0 else "—"
    avg_prob = sum(p.get('probability_delayed', 0) for p in st.session_state.predictions_history) / max(total, 1)
    
    st.markdown(f"""
    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-icon">🎯</div>
            <div class="kpi-value">{total}</div>
            <div class="kpi-label">Total Predictions</div>
            <div class="kpi-change">↑ This session</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon">⚠️</div>
            <div class="kpi-value" style="background:linear-gradient(135deg,#ef4444,#f97316);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">{delay_rate}</div>
            <div class="kpi-label">Delay Rate</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon">🤖</div>
            <div class="kpi-value" style="background:linear-gradient(135deg,#22c55e,#10b981);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">74.6%</div>
            <div class="kpi-label">Model ROC-AUC</div>
            <div class="kpi-change">↑ XGBoost v1.0</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon">⚡</div>
            <div class="kpi-value" style="background:linear-gradient(135deg,#a855f7,#6366f1);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">&lt;50ms</div>
            <div class="kpi-label">Inference Speed</div>
            <div class="kpi-change">↑ FastAPI + XGBoost</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon">📦</div>
            <div class="kpi-value">11K</div>
            <div class="kpi-label">Training Shipments</div>
            <div class="kpi-change">↑ 22 features</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="section-card">
            <div style="font-size:1.05rem;font-weight:700;color:#f1f5f9;margin-bottom:1rem;">Platform Capabilities</div>
        </div>
        """, unsafe_allow_html=True)
        feats = [
            ("🔮", "Single Prediction", "Instant delay probability with SHAP explanations and actionable recommendations"),
            ("📦", "Batch Processing", "Upload CSV files to predict delays for hundreds of shipments at once"),
            ("📊", "Feature Analysis", "Understand the exact factors driving delays with interactive charts"),
            ("🤖", "AI Assistant", "Chat with the AI about supply chain optimization and delay prevention"),
            ("📈", "Analytics", "Track prediction history and visualize delay trends in real time"),
        ]
        for icon, title, desc in feats:
            st.markdown(f"""
            <div style="display:flex;gap:12px;padding:0.75rem 0;border-bottom:1px solid rgba(255,255,255,0.05);">
                <div style="font-size:1.3rem;flex-shrink:0;">{icon}</div>
                <div>
                    <div style="font-size:0.88rem;font-weight:600;color:#e2e8f0;">{title}</div>
                    <div style="font-size:0.8rem;color:#64748b;margin-top:2px;">{desc}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="section-card">
            <div style="font-size:1.05rem;font-weight:700;color:#f1f5f9;margin-bottom:1rem;">Top Delay Drivers</div>
        </div>
        """, unsafe_allow_html=True)
        
        drivers = [
            ("Discount Offered", 56.5, "#00d4ff"),
            ("Package Weight", 9.7, "#0ea5e9"),
            ("Prior Purchases", 5.1, "#6366f1"),
            ("Product Cost", 4.6, "#a855f7"),
            ("Shipment Mode", 2.1, "#ec4899"),
        ]
        for name, pct, color in drivers:
            st.markdown(f"""
            <div style="margin-bottom:0.85rem;">
                <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                    <span style="font-size:0.82rem;color:#cbd5e1;font-weight:500;">{name}</span>
                    <span style="font-size:0.82rem;color:{color};font-weight:700;">{pct}%</span>
                </div>
                <div style="height:6px;background:rgba(255,255,255,0.06);border-radius:3px;overflow:hidden;">
                    <div style="width:{pct}%;height:100%;background:{color};border-radius:3px;
                                box-shadow:0 0 8px {color}40;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="margin-top:1rem;padding:0.85rem;background:rgba(0,212,255,0.06);
                    border:1px solid rgba(0,212,255,0.15);border-radius:10px;">
            <div style="font-size:0.8rem;color:#94a3b8;">
                <span style="color:#00d4ff;font-weight:600;">Key Finding:</span>
                Shipments with &gt;25% discount are <strong style="color:#f1f5f9;">2.7× more likely to be delayed</strong>.
                Discount is the single strongest predictor at 56.5% model importance.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-top:1.5rem;padding:1.25rem 1.5rem;
                background:linear-gradient(135deg,rgba(0,212,255,0.06),rgba(168,85,247,0.06));
                border:1px solid rgba(0,212,255,0.12);border-radius:16px;">
        <div style="font-size:0.9rem;font-weight:700;color:#f1f5f9;margin-bottom:0.6rem;">
            Quick Start Guide
        </div>
        <div style="display:flex;gap:1.5rem;flex-wrap:wrap;">
            <div style="font-size:0.82rem;color:#94a3b8;">
                <span style="color:#00d4ff;font-weight:600;">Step 1</span> → Single Prediction
            </div>
            <div style="font-size:0.82rem;color:#94a3b8;">
                <span style="color:#a855f7;font-weight:600;">Step 2</span> → Review SHAP Explanation
            </div>
            <div style="font-size:0.82rem;color:#94a3b8;">
                <span style="color:#22c55e;font-weight:600;">Step 3</span> → Act on Recommendations
            </div>
            <div style="font-size:0.82rem;color:#94a3b8;">
                <span style="color:#f97316;font-weight:600;">Step 4</span> → Track in Analytics
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# SINGLE PREDICTION PAGE
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🔮 Single Prediction":
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title" style="font-size:1.9rem;">Single Shipment Prediction</div>
        <div class="hero-subtitle">Fill in shipment details to get an instant AI-powered delay prediction with SHAP explanations.</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown('<div style="font-size:0.82rem;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.75rem;">Shipment Details</div>', unsafe_allow_html=True)
        warehouse_block = st.selectbox("Warehouse Block", ["A", "B", "C", "D", "E", "F"])
        mode_of_shipment = st.selectbox("Mode of Shipment", ["Ship", "Flight", "Road"])
        customer_care_calls = st.number_input("Customer Care Calls", min_value=0, max_value=10, value=2)
        customer_rating = st.slider("Customer Rating", min_value=1.0, max_value=5.0, value=3.5, step=0.5)
        cost_of_product = st.number_input("Product Cost ($)", min_value=100, max_value=100000, value=5000, step=100)

    with col2:
        st.markdown('<div style="font-size:0.82rem;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.75rem;">Customer & Product Info</div>', unsafe_allow_html=True)
        prior_purchases = st.number_input("Prior Purchases", min_value=0, max_value=20, value=3)
        product_importance = st.selectbox("Product Importance", ["Low", "Medium", "High"])
        gender = st.selectbox("Customer Gender", ["M", "F"])
        discount_offered = st.slider("Discount Offered (%)", min_value=0.0, max_value=65.0, value=10.0, step=1.0)
        weight_in_gms = st.number_input("Weight (grams)", min_value=100, max_value=10000, value=2500, step=50)

    st.markdown("<br>", unsafe_allow_html=True)
    predict_btn = st.button("🔮 Predict Delay Probability", use_container_width=True, type="primary")

    if predict_btn:
        if not api_healthy():
            st.error("Backend API is offline. Please ensure it is running on port 8000.")
        else:
            payload = {
                "warehouse_block": warehouse_block,
                "mode_of_shipment": mode_of_shipment,
                "customer_care_calls": int(customer_care_calls),
                "customer_rating": float(customer_rating),
                "cost_of_the_product": float(cost_of_product),
                "prior_purchases": int(prior_purchases),
                "product_importance": product_importance,
                "gender": gender,
                "discount_offered": float(discount_offered),
                "weight_in_gms": float(weight_in_gms),
            }

            with st.spinner("Running AI prediction pipeline…"):
                try:
                    resp = requests.post(
                        f"{API_URL}/api/v1/predict-with-explanation",
                        json=payload, timeout=15
                    )
                    if resp.status_code == 200:
                        result = resp.json()
                        st.session_state.predictions_history.append(result)

                        is_delayed = result['prediction'] == 1
                        probability = result['probability_delayed']
                        confidence = max(probability, 1 - probability)

                        st.markdown("---")
                        st.markdown('<div style="font-size:1rem;font-weight:700;color:#f1f5f9;margin-bottom:1rem;">Prediction Results</div>', unsafe_allow_html=True)

                        c1, c2, c3 = st.columns(3)
                        with c1:
                            if is_delayed:
                                st.markdown('<div class="pred-delayed"><div class="pred-label">Prediction</div><div class="pred-value-delayed">DELAYED</div></div>', unsafe_allow_html=True)
                            else:
                                st.markdown('<div class="pred-ontime"><div class="pred-label">Prediction</div><div class="pred-value-ontime">ON-TIME</div></div>', unsafe_allow_html=True)
                        with c2:
                            prob_color = "#ef4444" if probability > 0.5 else "#22c55e"
                            st.markdown(f'<div class="section-card" style="text-align:center;"><div class="pred-label">Delay Probability</div><div class="pred-value-neutral" style="color:{prob_color};">{probability*100:.1f}%</div></div>', unsafe_allow_html=True)
                        with c3:
                            st.markdown(f'<div class="section-card" style="text-align:center;"><div class="pred-label">Confidence</div><div class="pred-value-neutral">{confidence*100:.1f}%</div></div>', unsafe_allow_html=True)

                        st.markdown("<br>", unsafe_allow_html=True)
                        col_left, col_right = st.columns([1.2, 1])

                        with col_left:
                            st.markdown('<div style="font-size:0.9rem;font-weight:700;color:#f1f5f9;margin-bottom:0.75rem;">Top Contributing Factors</div>', unsafe_allow_html=True)
                            factors_df = pd.DataFrame(result.get('top_factors', []))
                            if not factors_df.empty:
                                factors_df = factors_df.sort_values('importance', ascending=True)
                                fig = go.Figure(go.Bar(
                                    x=factors_df['importance'],
                                    y=factors_df['feature'],
                                    orientation='h',
                                    marker=dict(
                                        color=factors_df['importance'],
                                        colorscale=[[0, '#0ea5e9'], [1, '#00d4ff']],
                                        line=dict(color='rgba(0,212,255,0.3)', width=1)
                                    ),
                                    text=[f"{v:.3f}" for v in factors_df['importance']],
                                    textposition='outside'
                                ))
                                fig.update_layout(
                                    plot_bgcolor='rgba(15,23,42,0)', paper_bgcolor='rgba(0,0,0,0)',
                                    font=dict(color='#94a3b8', size=12),
                                    margin=dict(l=0, r=60, t=0, b=0), height=220,
                                    xaxis=dict(gridcolor='rgba(255,255,255,0.05)', showgrid=True),
                                    yaxis=dict(gridcolor='rgba(255,255,255,0)', showgrid=False)
                                )
                                st.plotly_chart(fig, use_container_width=True)

                        with col_right:
                            st.markdown('<div style="font-size:0.9rem;font-weight:700;color:#f1f5f9;margin-bottom:0.75rem;">AI Explanation</div>', unsafe_allow_html=True)
                            exp_text = result.get('explanation_text', '')
                            st.markdown(f'<div style="background:rgba(15,23,42,0.7);border:1px solid rgba(255,255,255,0.08);border-radius:12px;padding:1rem;font-size:0.85rem;color:#94a3b8;line-height:1.6;">{exp_text}</div>', unsafe_allow_html=True)

                        recs = result.get('recommendations', [])
                        if recs:
                            st.markdown("<br>", unsafe_allow_html=True)
                            st.markdown('<div style="font-size:0.9rem;font-weight:700;color:#f1f5f9;margin-bottom:0.75rem;">Actionable Recommendations</div>', unsafe_allow_html=True)
                            for i, rec in enumerate(recs[:4], 1):
                                priority = "high" if i == 1 else "medium"
                                badge_color = "#ef4444" if i == 1 else "#f97316"
                                badge_text = "HIGH" if i == 1 else "MEDIUM"
                                st.markdown(f"""
                                <div class="rec-card {priority}">
                                    <div style="display:flex;align-items:center;gap:8px;margin-bottom:0.4rem;">
                                        <span style="font-size:0.68rem;font-weight:700;background:{badge_color};color:white;
                                                     border-radius:4px;padding:1px 6px;">{badge_text}</span>
                                        <div class="rec-action">{rec}</div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.error(f"Prediction error (HTTP {resp.status_code}): {resp.text[:200]}")
                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to API. Ensure the Backend API workflow is running.")
                except Exception as e:
                    st.error(f"Unexpected error: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# BATCH PREDICTIONS PAGE
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📦 Batch Predictions":
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title" style="font-size:1.9rem;">Batch Predictions</div>
        <div class="hero-subtitle">Upload a CSV file to predict delays for multiple shipments simultaneously.</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background:rgba(0,212,255,0.06);border:1px solid rgba(0,212,255,0.15);
                border-radius:12px;padding:1rem 1.25rem;margin-bottom:1.5rem;">
        <div style="font-size:0.85rem;font-weight:600;color:#00d4ff;margin-bottom:0.4rem;">Required CSV Columns</div>
        <div style="font-size:0.8rem;color:#64748b;font-family:monospace;">
            warehouse_block, mode_of_shipment, customer_care_calls, customer_rating,
            cost_of_the_product, prior_purchases, product_importance, gender,
            discount_offered, weight_in_gms
        </div>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Drop CSV file here or click to browse", type="csv")

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.markdown(f'<div style="font-size:0.85rem;color:#94a3b8;margin-bottom:0.5rem;">{len(df)} shipments loaded</div>', unsafe_allow_html=True)
            st.dataframe(df.head(5), use_container_width=True)

            if st.button("🚀 Run Batch Prediction", type="primary", use_container_width=True):
                if not api_healthy():
                    st.error("Backend API is offline.")
                else:
                    with st.spinner(f"Processing {len(df)} shipments…"):
                        try:
                            col_map = {
                                'Warehouse_block': 'warehouse_block',
                                'Mode_of_Shipment': 'mode_of_shipment',
                                'Customer_care_calls': 'customer_care_calls',
                                'Customer_rating': 'customer_rating',
                                'Cost_of_the_Product': 'cost_of_the_product',
                                'Prior_purchases': 'prior_purchases',
                                'Product_importance': 'product_importance',
                                'Gender': 'gender',
                                'Discount_offered': 'discount_offered',
                                'Weight_in_gms': 'weight_in_gms',
                            }
                            df_renamed = df.rename(columns=col_map)
                            needed = ['warehouse_block','mode_of_shipment','customer_care_calls',
                                      'customer_rating','cost_of_the_product','prior_purchases',
                                      'product_importance','gender','discount_offered','weight_in_gms']
                            missing = [c for c in needed if c not in df_renamed.columns]
                            if missing:
                                st.error(f"Missing required columns: {missing}")
                            else:
                                shipments = df_renamed[needed].to_dict('records')
                                resp = requests.post(
                                    f"{API_URL}/api/v1/predict/batch",
                                    json={"shipments": shipments}, timeout=60
                                )
                                if resp.status_code == 200:
                                    results = resp.json()
                                    preds = results['predictions']
                                    total_p = results['total_predictions']
                                    time_ms = results['processing_time_ms']

                                    delayed_n = sum(1 for p in preds if p['prediction'] == 1)
                                    ontime_n = total_p - delayed_n

                                    c1, c2, c3, c4 = st.columns(4)
                                    c1.metric("Total Processed", total_p)
                                    c2.metric("Delayed", delayed_n)
                                    c3.metric("On-Time", ontime_n)
                                    c4.metric("Processing Time", f"{time_ms:.0f}ms")

                                    out_df = pd.DataFrame([{
                                        'Prediction': 'Delayed' if p['prediction'] == 1 else 'On-Time',
                                        'Delay Probability': f"{p['probability_delayed']*100:.1f}%",
                                        'Confidence': f"{p['confidence']*100:.1f}%",
                                    } for p in preds])

                                    st.dataframe(out_df, use_container_width=True)

                                    fig = go.Figure(data=[go.Pie(
                                        labels=['On-Time', 'Delayed'],
                                        values=[ontime_n, delayed_n],
                                        hole=0.5,
                                        marker=dict(colors=['#22c55e', '#ef4444'])
                                    )])
                                    fig.update_layout(
                                        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                                        font=dict(color='#94a3b8'), height=280,
                                        margin=dict(l=0,r=0,t=0,b=0),
                                        legend=dict(bgcolor='rgba(0,0,0,0)')
                                    )
                                    st.plotly_chart(fig, use_container_width=True)

                                    csv_out = out_df.to_csv(index=False)
                                    st.download_button("📥 Download Results CSV", csv_out,
                                                       "smartship_predictions.csv", "text/csv")
                                else:
                                    st.error(f"Batch error: {resp.text[:300]}")
                        except Exception as e:
                            st.error(f"Error: {e}")
        except Exception as e:
            st.error(f"Error reading CSV: {e}")
    else:
        st.markdown("""
        <div style="text-align:center;padding:3rem 2rem;background:rgba(15,23,42,0.4);
                    border:1px dashed rgba(0,212,255,0.2);border-radius:16px;margin-top:1rem;">
            <div style="font-size:2.5rem;margin-bottom:0.75rem;">📂</div>
            <div style="font-size:0.95rem;color:#64748b;">Upload a CSV file to begin batch prediction</div>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# FEATURE ANALYSIS PAGE
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📊 Feature Analysis":
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title" style="font-size:1.9rem;">Feature Analysis & Insights</div>
        <div class="hero-subtitle">Deep-dive into the ML model's feature importance and what drives shipment delays.</div>
    </div>
    """, unsafe_allow_html=True)
    from frontend.pages.feature_insights import show_insights
    show_insights()


# ═══════════════════════════════════════════════════════════════════════════════
# ANALYTICS PAGE
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📈 Analytics":
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title" style="font-size:1.9rem;">Analytics Dashboard</div>
        <div class="hero-subtitle">Real-time session analytics and prediction trend visualization.</div>
    </div>
    """, unsafe_allow_html=True)

    history = st.session_state.predictions_history

    if len(history) == 0:
        st.markdown("""
        <div style="text-align:center;padding:4rem 2rem;background:rgba(15,23,42,0.4);
                    border:1px dashed rgba(0,212,255,0.15);border-radius:16px;">
            <div style="font-size:3rem;margin-bottom:1rem;">📈</div>
            <div style="font-size:1rem;color:#64748b;margin-bottom:0.5rem;">No predictions yet</div>
            <div style="font-size:0.85rem;color:#475569;">Make predictions on the Single Prediction page to see analytics here.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        total_p = len(history)
        delayed_p = sum(1 for p in history if p.get('prediction') == 1)
        ontime_p = total_p - delayed_p
        avg_prob = sum(p.get('probability_delayed', 0) for p in history) / total_p
        avg_conf = sum(p.get('confidence', max(p.get('probability_delayed',0.5), 1-p.get('probability_delayed',0.5))) for p in history) / total_p

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Predictions", total_p)
        c2.metric("Delayed", delayed_p, delta=f"{delayed_p/total_p*100:.1f}%")
        c3.metric("On-Time", ontime_p, delta=f"{ontime_p/total_p*100:.1f}%")
        c4.metric("Avg Delay Prob", f"{avg_prob*100:.1f}%")

        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)

        with col1:
            fig_pie = go.Figure(data=[go.Pie(
                labels=['On-Time', 'Delayed'],
                values=[ontime_p, delayed_p],
                hole=0.55,
                marker=dict(colors=['#22c55e', '#ef4444'], line=dict(color='rgba(0,0,0,0)', width=2)),
                textinfo='label+percent'
            )])
            fig_pie.update_layout(
                title=dict(text='Prediction Distribution', font=dict(color='#f1f5f9', size=14)),
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#94a3b8'), height=280,
                margin=dict(l=0,r=0,t=40,b=0),
                legend=dict(bgcolor='rgba(0,0,0,0)')
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with col2:
            probs = [p.get('probability_delayed', 0.5) for p in history]
            fig_hist = px.histogram(
                x=probs, nbins=min(15, len(history)),
                title='Delay Probability Distribution',
                labels={'x': 'Delay Probability', 'y': 'Count'},
                color_discrete_sequence=['#00d4ff']
            )
            fig_hist.update_layout(
                plot_bgcolor='rgba(15,23,42,0.5)', paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#94a3b8'), height=280,
                margin=dict(l=0,r=0,t=40,b=0),
                xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                yaxis=dict(gridcolor='rgba(255,255,255,0.05)')
            )
            st.plotly_chart(fig_hist, use_container_width=True)

        if len(history) >= 3:
            probs_seq = [p.get('probability_delayed', 0.5) for p in history]
            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(
                x=list(range(1, len(probs_seq)+1)), y=[p*100 for p in probs_seq],
                mode='lines+markers', name='Delay Prob',
                line=dict(color='#00d4ff', width=2.5),
                marker=dict(size=7, color=['#ef4444' if p>0.5 else '#22c55e' for p in probs_seq],
                            line=dict(color='#00d4ff', width=1.5)),
                fill='tozeroy', fillcolor='rgba(0,212,255,0.06)'
            ))
            fig_line.add_hline(y=50, line_dash='dash', line_color='rgba(239,68,68,0.4)',
                               annotation_text='50% threshold')
            fig_line.update_layout(
                title=dict(text='Delay Probability Over Predictions', font=dict(color='#f1f5f9', size=14)),
                plot_bgcolor='rgba(15,23,42,0.5)', paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#94a3b8'), height=280,
                margin=dict(l=0,r=0,t=40,b=0),
                xaxis=dict(title='Prediction #', gridcolor='rgba(255,255,255,0.05)'),
                yaxis=dict(title='Delay Prob (%)', gridcolor='rgba(255,255,255,0.05)')
            )
            st.plotly_chart(fig_line, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# AI ASSISTANT PAGE
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🤖 AI Assistant":
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title" style="font-size:1.9rem;">🤖 Multi-Agent AI System</div>
        <div class="hero-subtitle">
            5 specialized AI agents collaborate to answer your supply chain questions.
            Risk Analyst · Delay Predictor · Operations Advisor · Data Analyst · Executive Advisor
        </div>
    </div>
    <div style="display:flex;gap:0.6rem;flex-wrap:wrap;margin-bottom:1rem;">
        <div style="background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.25);border-radius:20px;padding:0.3rem 0.85rem;font-size:0.78rem;color:#ef4444;font-weight:600;">⚠️ Risk Analyst</div>
        <div style="background:rgba(168,85,247,0.1);border:1px solid rgba(168,85,247,0.25);border-radius:20px;padding:0.3rem 0.85rem;font-size:0.78rem;color:#a855f7;font-weight:600;">🔮 Delay Predictor</div>
        <div style="background:rgba(234,179,8,0.1);border:1px solid rgba(234,179,8,0.25);border-radius:20px;padding:0.3rem 0.85rem;font-size:0.78rem;color:#eab308;font-weight:600;">💡 Ops Advisor</div>
        <div style="background:rgba(0,212,255,0.1);border:1px solid rgba(0,212,255,0.25);border-radius:20px;padding:0.3rem 0.85rem;font-size:0.78rem;color:#00d4ff;font-weight:600;">📊 Data Analyst</div>
        <div style="background:rgba(34,197,94,0.1);border:1px solid rgba(34,197,94,0.25);border-radius:20px;padding:0.3rem 0.85rem;font-size:0.78rem;color:#22c55e;font-weight:600;">📋 Exec Advisor</div>
    </div>
    """, unsafe_allow_html=True)

    suggestions = [
        "What causes the most delays?",
        "Give me an executive summary",
        "How can I reduce delays by 30%?",
        "What anomalies should I watch?",
        "Analyze the discount relationship",
        "Top operations recommendations",
    ]

    st.markdown('<div style="margin-bottom:0.75rem;font-size:0.78rem;color:#475569;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;">Quick Questions</div>', unsafe_allow_html=True)
    cols = st.columns(3)
    for i, sug in enumerate(suggestions):
        with cols[i % 3]:
            if st.button(sug, key=f"sug_{i}", use_container_width=True):
                st.session_state['pending_chat'] = sug

    st.markdown("---")

    if st.session_state.chat_messages:
        chat_html = '<div class="chat-container">'
        for msg in st.session_state.chat_messages[-20:]:
            ts = fmt_time(msg.get('timestamp', ''))
            if msg['role'] == 'user':
                chat_html += f"""
                <div style="display:flex;flex-direction:column;align-items:flex-end;">
                    <div class="chat-msg-user">{msg['content']}</div>
                    <div class="chat-timestamp">{ts}</div>
                </div>
                """
            else:
                import re as _re
                content = msg['content']
                content = _re.sub(r'\*\*(.*?)\*\*', r'<strong style="color:#e2e8f0;">\1</strong>', content)
                content = content.replace('\n', '<br>')
                agent    = msg.get('agent') or {}
                a_icon   = agent.get('icon', '🤖')
                a_name   = agent.get('name', 'SmartShip AI')
                a_role   = agent.get('role', 'AI Assistant')
                sources_html = ""
                if msg.get('sources'):
                    srcs = " · ".join(s['topic'].title() for s in msg['sources'][:2])
                    sources_html = f'<div style="font-size:0.7rem;color:#334155;margin-top:6px;">📚 {srcs}</div>'
                agent_tag = f'<div style="font-size:0.7rem;color:#a855f7;font-weight:700;margin-bottom:4px;">{a_icon} {a_name} <span style="color:#475569;font-weight:400;">· {a_role}</span></div>'
                chat_html += f"""
                <div style="display:flex;flex-direction:column;align-items:flex-start;">
                    <div class="chat-msg-assistant">{agent_tag}{content}{sources_html}</div>
                    <div class="chat-timestamp">{ts}</div>
                </div>
                """
        chat_html += '</div>'
        st.markdown(chat_html, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    col_input, col_btn = st.columns([5, 1])
    with col_input:
        user_input = st.text_input(
            "Ask the AI Assistant…",
            value=st.session_state.get('pending_chat', ''),
            placeholder="e.g. What is the main cause of shipment delays?",
            label_visibility="collapsed",
            key="chat_text_input"
        )
    with col_btn:
        send_btn = st.button("Send →", type="primary", use_container_width=True)

    if 'pending_chat' in st.session_state:
        del st.session_state['pending_chat']

    should_send = send_btn and user_input.strip()

    if should_send:
        message = user_input.strip()
        ts_now = datetime.utcnow().isoformat()

        st.session_state.chat_messages.append({
            'role': 'user', 'content': message, 'timestamp': ts_now
        })

        if not api_healthy():
            reply = {
                "response": (
                    "I'm having trouble connecting to the backend API right now. "
                    "Please ensure the Backend API workflow is running, then try again. "
                    "In the meantime, I can tell you that the #1 cause of shipment delays "
                    "is high discount (>25%), which accounts for 56.5% of model importance."
                ),
                "sources": [],
                "timestamp": ts_now
            }
        else:
            try:
                resp = requests.post(
                    f"{API_URL}/api/v1/chat",
                    json={"message": message, "session_id": st.session_state.session_id},
                    timeout=10
                )
                if resp.status_code == 200:
                    reply = resp.json()
                else:
                    reply = {
                        "response": "I encountered an error processing your request. Please try again.",
                        "sources": [], "timestamp": ts_now
                    }
            except Exception as e:
                reply = {
                    "response": f"Connection error: {str(e)[:100]}. Please check the backend is running.",
                    "sources": [], "timestamp": ts_now
                }

        st.session_state.chat_messages.append({
            'role': 'assistant',
            'content': reply.get('response', ''),
            'sources': reply.get('sources', []),
            'agent': reply.get('agent'),
            'timestamp': reply.get('timestamp', ts_now)
        })
        st.rerun()

    if not st.session_state.chat_messages:
        st.markdown("""
        <div style="text-align:center;padding:3rem 2rem;background:rgba(15,23,42,0.4);
                    border:1px dashed rgba(168,85,247,0.2);border-radius:16px;margin-top:1rem;">
            <div style="font-size:3rem;margin-bottom:1rem;">🤖</div>
            <div style="font-size:1rem;color:#64748b;margin-bottom:0.5rem;">Your AI Assistant is ready</div>
            <div style="font-size:0.85rem;color:#475569;">
                Click a quick question above or type your own to start chatting.
            </div>
        </div>
        """, unsafe_allow_html=True)

    if st.session_state.chat_messages:
        if st.button("Clear Conversation", use_container_width=False):
            st.session_state.chat_messages = []
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# ABOUT PAGE
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "ℹ️ About":
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title" style="font-size:1.9rem;">About SmartShip AI</div>
        <div class="hero-subtitle">Production-grade MLOps platform for supply chain delay prediction.</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="section-card">
            <div style="font-size:1rem;font-weight:700;color:#f1f5f9;margin-bottom:1rem;">Platform Overview</div>
            <div style="font-size:0.85rem;color:#94a3b8;line-height:1.8;">
                <strong style="color:#00d4ff;">SmartShip AI</strong> is an end-to-end MLOps platform
                that predicts shipment delays using XGBoost and SHAP explanations.<br><br>
                The system processes 10 shipment features through a 22-feature engineering pipeline,
                delivering real-time predictions with &lt;50ms inference latency.<br><br>
                Built for logistics teams who need actionable, explainable AI — not black-box predictions.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="section-card" style="margin-top:1rem;">
            <div style="font-size:1rem;font-weight:700;color:#f1f5f9;margin-bottom:1rem;">Model Performance</div>
        </div>
        """, unsafe_allow_html=True)
        
        metrics = [("Accuracy", "66.3%"), ("Precision", "76.1%"),
                   ("Recall", "63.4%"), ("F1-Score", "69.2%"),
                   ("ROC-AUC", "74.6%"), ("Inference", "<50ms")]
        for name, val in metrics:
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;padding:0.5rem 0;
                        border-bottom:1px solid rgba(255,255,255,0.05);">
                <span style="font-size:0.85rem;color:#94a3b8;">{name}</span>
                <span style="font-size:0.85rem;color:#00d4ff;font-weight:700;">{val}</span>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="section-card">
            <div style="font-size:1rem;font-weight:700;color:#f1f5f9;margin-bottom:1rem;">Technology Stack</div>
        </div>
        """, unsafe_allow_html=True)
        
        stack = [
            ("🧠", "ML Model", "XGBoost + SHAP Explanations"),
            ("⚡", "Backend", "FastAPI + Async Python"),
            ("📊", "Frontend", "Streamlit + Plotly"),
            ("🔄", "MLOps", "Custom Pipeline + Joblib"),
            ("🗄️", "Data", "Pandas + NumPy + Scikit-learn"),
            ("🤖", "AI Chat", "RAG + TF-IDF Semantic Search"),
        ]
        for icon, cat, detail in stack:
            st.markdown(f"""
            <div style="display:flex;gap:12px;padding:0.65rem 0;border-bottom:1px solid rgba(255,255,255,0.05);">
                <div style="font-size:1.3rem;flex-shrink:0;">{icon}</div>
                <div>
                    <div style="font-size:0.82rem;font-weight:600;color:#e2e8f0;">{cat}</div>
                    <div style="font-size:0.78rem;color:#64748b;">{detail}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div class="section-card" style="margin-top:1rem;">
            <div style="font-size:1rem;font-weight:700;color:#f1f5f9;margin-bottom:1rem;">MLOps Pipeline</div>
            <div style="font-size:0.82rem;color:#94a3b8;line-height:2;">
                Data Ingestion → Validation → Preprocessing<br>
                → Feature Engineering (22 features) → XGBoost Training<br>
                → Cross-validation → Model Registry → FastAPI Serving<br>
                → Streamlit Dashboard → SHAP Explanations
            </div>
        </div>
        """, unsafe_allow_html=True)
