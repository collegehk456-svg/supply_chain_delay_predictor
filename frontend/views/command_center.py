"""
SmartShip AI — Live Command Center
Futuristic real-time anomaly detection and monitoring dashboard.
"""

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import time
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")


def render():
    # ── Page CSS ──────────────────────────────────────────────────────────────
    st.markdown("""
    <style>
    /* Animated ticker */
    @keyframes ticker-scroll {
        0%   { transform: translateX(100%); }
        100% { transform: translateX(-100%); }
    }
    .ticker-wrap {
        background: rgba(0,0,0,0.4);
        border: 1px solid rgba(0,212,255,0.2);
        border-radius: 8px;
        overflow: hidden;
        padding: 0.5rem 0;
        margin-bottom: 1.5rem;
    }
    .ticker-inner {
        display: flex; gap: 3rem;
        animation: ticker-scroll 28s linear infinite;
        white-space: nowrap;
    }
    .ticker-item { font-size: 0.82rem; font-weight: 600; font-family: 'Inter', monospace; }
    .ticker-crit { color: #ef4444; }
    .ticker-high { color: #f97316; }
    .ticker-med  { color: #eab308; }
    .ticker-low  { color: #22c55e; }
    .ticker-sep  { color: #334155; }

    /* Risk badge */
    .risk-badge {
        display: inline-flex; align-items: center; gap: 5px;
        border-radius: 6px; padding: 0.2rem 0.65rem;
        font-size: 0.75rem; font-weight: 700; text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .risk-CRITICAL { background: rgba(239,68,68,0.18); color: #ef4444; border: 1px solid rgba(239,68,68,0.35); }
    .risk-HIGH     { background: rgba(249,115,22,0.18); color: #f97316; border: 1px solid rgba(249,115,22,0.35); }
    .risk-MEDIUM   { background: rgba(234,179,8,0.18);  color: #eab308; border: 1px solid rgba(234,179,8,0.35); }
    .risk-LOW      { background: rgba(34,197,94,0.18);  color: #22c55e; border: 1px solid rgba(34,197,94,0.35); }

    /* Shipment card */
    .shipment-card {
        background: rgba(15,23,42,0.65);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px; padding: 0.85rem 1rem;
        margin-bottom: 0.55rem;
        transition: border-color 0.2s;
    }
    .shipment-card:hover { border-color: rgba(0,212,255,0.25); }
    .ship-id   { font-size: 0.78rem; font-weight: 700; color: #00d4ff; font-family: monospace; }
    .ship-route { font-size: 0.82rem; color: #cbd5e1; margin: 0.15rem 0; }
    .ship-meta  { font-size: 0.72rem; color: #64748b; }

    /* Executive summary card */
    .exec-card {
        background: linear-gradient(135deg, rgba(0,212,255,0.06) 0%, rgba(168,85,247,0.06) 100%);
        border: 1px solid rgba(0,212,255,0.15);
        border-radius: 16px; padding: 1.5rem;
        margin-bottom: 1.5rem;
    }
    .exec-headline { font-size: 1.05rem; font-weight: 700; color: #f1f5f9; margin-bottom: 0.75rem; }
    .exec-body { font-size: 0.88rem; color: #94a3b8; line-height: 1.6; }

    /* Warehouse block */
    .wh-block {
        background: rgba(15,23,42,0.7);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 12px; padding: 1rem;
        text-align: center;
    }
    .wh-label  { font-size: 0.7rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.35rem; }
    .wh-name   { font-size: 1.5rem; font-weight: 800; margin-bottom: 0.3rem; }
    .wh-rate   { font-size: 0.82rem; font-weight: 600; }
    .wh-active { font-size: 0.72rem; color: #64748b; margin-top: 0.25rem; }

    /* Alert card */
    .alert-item {
        display: flex; align-items: flex-start; gap: 0.65rem;
        background: rgba(15,23,42,0.5);
        border-radius: 10px; padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
    }
    .alert-icon { font-size: 1rem; margin-top: 0.1rem; }
    .alert-msg { font-size: 0.83rem; color: #cbd5e1; }
    .alert-time { font-size: 0.68rem; color: #475569; margin-top: 0.2rem; }

    /* Pulse animation */
    @keyframes pulse-dot { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:0.6;transform:scale(1.3)} }
    .pulse-live {
        display: inline-flex; align-items: center; gap: 6px;
        font-size: 0.75rem; font-weight: 700; color: #22c55e;
        text-transform: uppercase; letter-spacing: 0.08em;
    }
    .pulse-dot {
        width: 8px; height: 8px; border-radius: 50%; background: #22c55e;
        animation: pulse-dot 1.4s ease-in-out infinite;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Header ─────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="hero-banner">
        <div style="display:flex;align-items:center;justify-content:space-between;">
            <div>
                <div class="hero-title">⚡ AI Command Center</div>
                <div class="hero-subtitle">Real-time shipment monitoring · Anomaly detection · Live risk intelligence</div>
            </div>
            <div class="pulse-live"><div class="pulse-dot"></div>LIVE FEED</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Fetch live data ─────────────────────────────────────────────────────────
    @st.cache_data(ttl=8)
    def fetch_stream():
        try:
            r = requests.get(f"{API_URL}/api/v1/anomaly/stream?n=18", timeout=8)
            if r.status_code == 200:
                return r.json().get("shipments", [])
        except Exception:
            pass
        return []

    @st.cache_data(ttl=12)
    def fetch_summary():
        try:
            r = requests.get(f"{API_URL}/api/v1/anomaly/executive-summary", timeout=8)
            if r.status_code == 200:
                return r.json()
        except Exception:
            pass
        return None

    @st.cache_data(ttl=15)
    def fetch_warehouse_risk():
        try:
            r = requests.get(f"{API_URL}/api/v1/anomaly/warehouse-risk", timeout=8)
            if r.status_code == 200:
                return r.json().get("warehouse_blocks", [])
        except Exception:
            pass
        return []

    stream    = fetch_stream()
    summary   = fetch_summary()
    wh_blocks = fetch_warehouse_risk()

    # ── Live Ticker ─────────────────────────────────────────────────────────────
    if stream:
        level_class = {"CRITICAL": "ticker-crit", "HIGH": "ticker-high", "MEDIUM": "ticker-med", "LOW": "ticker-low"}
        items = []
        for s in stream[:12]:
            cls  = level_class.get(s.get("risk_level", "LOW"), "ticker-low")
            sid  = s.get("shipment_id", "SHP-?")
            orig = s.get("origin", "—")
            dest = s.get("destination", "—")
            risk = s.get("risk_score", 0)
            lvl  = s.get("risk_level", "LOW")
            items.append(f'<span class="ticker-item {cls}">[{lvl}] {sid} · {orig} → {dest} · Risk: {risk:.0f}%</span>')
            items.append('<span class="ticker-sep">|</span>')
        st.markdown(
            f'<div class="ticker-wrap"><div class="ticker-inner">{"".join(items)}</div></div>',
            unsafe_allow_html=True
        )

    # ── Executive Summary ───────────────────────────────────────────────────────
    if summary:
        st.markdown(f"""
        <div class="exec-card">
            <div class="exec-headline">{summary.get('headline','')}</div>
            <div class="exec-body">{summary.get('summary','')}</div>
        </div>
        """, unsafe_allow_html=True)

    # ── KPI Row ─────────────────────────────────────────────────────────────────
    if summary:
        c  = summary.get("critical_count", 0)
        h  = summary.get("high_count", 0)
        m  = summary.get("medium_count", 0)
        lo = summary.get("low_count", 0)
        ar = summary.get("avg_risk_score", 0)
        tot = summary.get("total_monitored", 0)

        st.markdown(f"""
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-icon">🔴</div>
                <div class="kpi-value" style="background:linear-gradient(135deg,#ef4444,#dc2626);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">{c}</div>
                <div class="kpi-label">Critical Alerts</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-icon">🟠</div>
                <div class="kpi-value" style="background:linear-gradient(135deg,#f97316,#ea580c);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">{h}</div>
                <div class="kpi-label">High Risk</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-icon">🟡</div>
                <div class="kpi-value" style="background:linear-gradient(135deg,#eab308,#ca8a04);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">{m}</div>
                <div class="kpi-label">Medium Risk</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-icon">✅</div>
                <div class="kpi-value" style="background:linear-gradient(135deg,#22c55e,#16a34a);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">{lo}</div>
                <div class="kpi-label">Healthy</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-icon">📊</div>
                <div class="kpi-value">{ar:.0f}%</div>
                <div class="kpi-label">Avg Risk Score</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-icon">📦</div>
                <div class="kpi-value">{tot}</div>
                <div class="kpi-label">Monitored</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Charts Row ──────────────────────────────────────────────────────────────
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown("### 📡 Live Risk Distribution")
        if stream:
            df = pd.DataFrame(stream)
            risk_order = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
            colors_map = {"CRITICAL": "#ef4444", "HIGH": "#f97316", "MEDIUM": "#eab308", "LOW": "#22c55e"}
            counts = {lvl: (df["risk_level"] == lvl).sum() for lvl in risk_order}
            fig = go.Figure(data=[go.Bar(
                x=list(counts.keys()),
                y=list(counts.values()),
                marker_color=[colors_map[k] for k in counts],
                marker_line_color="rgba(255,255,255,0.1)",
                marker_line_width=1,
            )])
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#94a3b8", family="Inter"),
                xaxis=dict(showgrid=False, color="#64748b"),
                yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)", color="#64748b"),
                margin=dict(l=0, r=0, t=10, b=0), height=240,
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)

            # Risk score scatter
            st.markdown("### 🔍 Risk Score Timeline")
            df["idx"] = range(len(df))
            fig2 = go.Figure()
            for lvl, col in colors_map.items():
                mask = df["risk_level"] == lvl
                fig2.add_trace(go.Scatter(
                    x=df[mask]["idx"], y=df[mask]["risk_score"],
                    mode="markers", name=lvl,
                    marker=dict(color=col, size=10, line=dict(color="rgba(255,255,255,0.3)", width=1)),
                ))
            fig2.add_hline(y=70, line_dash="dot", line_color="#ef4444", opacity=0.6,
                           annotation_text="Critical threshold", annotation_font_color="#ef4444")
            fig2.add_hline(y=45, line_dash="dot", line_color="#f97316", opacity=0.5,
                           annotation_text="High threshold", annotation_font_color="#f97316")
            fig2.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#94a3b8", family="Inter"),
                xaxis=dict(showgrid=False, color="#64748b", title="Shipment #"),
                yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)", color="#64748b", title="Risk Score %"),
                margin=dict(l=0, r=0, t=10, b=0), height=260,
                legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8")),
            )
            st.plotly_chart(fig2, use_container_width=True)

    with col_right:
        st.markdown("### 🏭 Warehouse Risk Map")
        if wh_blocks:
            risk_colors = {0: "#22c55e", 1: "#eab308", 2: "#f97316", 3: "#ef4444"}
            for blk in wh_blocks:
                delay = blk.get("delay_rate", 50)
                active = blk.get("active_shipments", 0)
                rs = blk.get("risk_score", 0)
                if delay >= 68:   color = "#ef4444"
                elif delay >= 63: color = "#f97316"
                elif delay >= 58: color = "#eab308"
                else:             color = "#22c55e"

                bar_pct = min(int(delay), 100)
                st.markdown(f"""
                <div class="wh-block" style="margin-bottom:0.6rem;">
                    <div class="wh-label">Warehouse Block</div>
                    <div class="wh-name" style="color:{color};">{blk['block']}</div>
                    <div style="background:rgba(255,255,255,0.05);border-radius:4px;height:6px;margin:0.4rem 0;">
                        <div style="width:{bar_pct}%;height:100%;background:{color};border-radius:4px;transition:width 0.5s;"></div>
                    </div>
                    <div class="wh-rate" style="color:{color};">Delay Rate: {delay:.1f}%</div>
                    <div class="wh-active">🚀 {active} active shipments</div>
                </div>
                """, unsafe_allow_html=True)

        # Pie chart
        if wh_blocks:
            st.markdown("### 📊 Volume Distribution")
            labels = [b["block"] for b in wh_blocks]
            values = [b.get("volume", 1000) for b in wh_blocks]
            fig3 = go.Figure(data=[go.Pie(
                labels=[f"Block {l}" for l in labels],
                values=values,
                hole=0.6,
                marker=dict(colors=["#00d4ff","#a855f7","#22c55e","#f97316","#eab308","#ef4444"],
                            line=dict(color="rgba(0,0,0,0.3)", width=2)),
            )])
            fig3.update_traces(textposition="outside", textfont_size=11,
                               textfont_color="#94a3b8")
            fig3.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#94a3b8", family="Inter"),
                margin=dict(l=0, r=0, t=10, b=0), height=260,
                legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8", size=11)),
                showlegend=True,
            )
            st.plotly_chart(fig3, use_container_width=True)

    # ── Live Shipment Stream ────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🚢 Live Shipment Intelligence Feed")

    col_refresh, col_info = st.columns([1, 5])
    with col_refresh:
        if st.button("🔄 Refresh Feed"):
            st.cache_data.clear()
            st.rerun()
    with col_info:
        st.markdown(
            '<div class="stat-badge" style="margin-top:0.35rem;">Isolation Forest + Statistical Rules · Auto-refresh every 8s</div>',
            unsafe_allow_html=True
        )

    if stream:
        sorted_stream = sorted(stream, key=lambda x: x.get("risk_score", 0), reverse=True)
        col_a, col_b = st.columns(2)
        for i, ship in enumerate(sorted_stream[:16]):
            col = col_a if i % 2 == 0 else col_b
            with col:
                lvl       = ship.get("risk_level", "LOW")
                sid       = ship.get("shipment_id", "—")
                orig      = ship.get("origin", "—")
                dest      = ship.get("destination", "—")
                risk_sc   = ship.get("risk_score", 0)
                alert     = ship.get("alert", {})
                alert_msg = alert.get("message", "")
                alert_icon = alert.get("icon", "")
                flags     = ship.get("statistical_flags", [])
                s_data    = ship.get("shipment", {})
                mode      = s_data.get("mode_of_shipment", "—")
                discount  = s_data.get("discount_offered", 0)
                weight    = s_data.get("weight_in_gms", 0)

                flags_html = ""
                for f in flags[:2]:
                    flags_html += f'<div class="alert-item"><span class="alert-icon">⚡</span><div class="alert-msg">{f}</div></div>'

                st.markdown(f"""
                <div class="shipment-card">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.4rem;">
                        <div class="ship-id">{sid}</div>
                        <div class="risk-badge risk-{lvl}">{lvl} · {risk_sc:.0f}%</div>
                    </div>
                    <div class="ship-route">✈ {orig} → {dest}</div>
                    <div class="ship-meta" style="margin:0.3rem 0;">
                        {mode} &nbsp;·&nbsp; Discount: {discount:.0f}% &nbsp;·&nbsp; Weight: {weight:.0f}g
                    </div>
                    {f'<div style="margin-top:0.4rem;font-size:0.78rem;color:#94a3b8;">{alert_icon} {alert_msg}</div>' if alert_msg else ''}
                    {flags_html}
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("📡 Connecting to live feed… Ensure the Backend API workflow is running.")

    # ── Top Anomalies ───────────────────────────────────────────────────────────
    if summary and summary.get("top_anomalies"):
        st.markdown("---")
        st.markdown("### 🚨 Top Anomalies Requiring Immediate Attention")
        for anom in summary["top_anomalies"]:
            lvl   = anom.get("risk_level", "HIGH")
            sid   = anom.get("shipment_id", "—")
            score = anom.get("risk_score", 0)
            flags = anom.get("statistical_flags", [])
            alert = anom.get("alert", {})
            color_map = {"CRITICAL": "#ef4444", "HIGH": "#f97316", "MEDIUM": "#eab308", "LOW": "#22c55e"}
            col = color_map.get(lvl, "#94a3b8")
            flags_str = " · ".join(flags[:3]) if flags else alert.get("message", "")
            st.markdown(f"""
            <div style="background:rgba(15,23,42,0.7);border:1px solid {col}33;
                        border-left:3px solid {col};border-radius:12px;
                        padding:1rem 1.25rem;margin-bottom:0.6rem;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.3rem;">
                    <span style="font-weight:700;color:{col};">{alert.get('icon','')} {sid}</span>
                    <span class="risk-badge risk-{lvl}">{lvl} · {score:.0f}% Risk</span>
                </div>
                <div style="font-size:0.83rem;color:#94a3b8;">{flags_str}</div>
            </div>
            """, unsafe_allow_html=True)
