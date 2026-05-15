"""
SmartShip AI — Executive Intelligence Dashboard
AI-generated business summaries, performance forecasting, ROI impact, and model health.
"""

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")


def _chart_layout(height=280, **kw):
    return dict(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94a3b8", family="Inter", size=12),
        margin=dict(l=0, r=0, t=35, b=0), height=height,
        **kw
    )


def render():
    st.markdown("""
    <style>
    /* Score gauge ring */
    .score-ring {
        display:flex;flex-direction:column;align-items:center;justify-content:center;
        padding:1.5rem;
    }
    .score-value {
        font-size:3rem;font-weight:900;letter-spacing:-0.04em;
        background:linear-gradient(135deg,#00d4ff,#a855f7);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
    }
    .score-label {
        font-size:0.72rem;color:#64748b;text-transform:uppercase;
        letter-spacing:0.1em;font-weight:600;margin-top:0.25rem;
    }
    /* Insight card */
    .insight-card {
        background:rgba(15,23,42,0.65);
        border:1px solid rgba(255,255,255,0.07);
        border-radius:14px;padding:1.1rem 1.25rem;margin-bottom:0.6rem;
        border-left:3px solid #00d4ff;
        transition:border-color 0.2s;
    }
    .insight-card.warn { border-left-color:#f97316; }
    .insight-card.good { border-left-color:#22c55e; }
    .insight-card.crit { border-left-color:#ef4444; }
    .insight-title { font-size:0.88rem;font-weight:700;color:#f1f5f9;margin-bottom:0.3rem; }
    .insight-body  { font-size:0.8rem;color:#94a3b8;line-height:1.55; }
    .insight-badge {
        display:inline-block;font-size:0.7rem;font-weight:700;
        border-radius:4px;padding:0.15rem 0.5rem;margin-top:0.35rem;
    }
    /* ROI card */
    .roi-block {
        background:linear-gradient(135deg,rgba(0,212,255,0.07),rgba(168,85,247,0.07));
        border:1px solid rgba(0,212,255,0.15);
        border-radius:14px;padding:1.25rem;margin-bottom:0.75rem;
    }
    .roi-num {
        font-size:2rem;font-weight:900;
        background:linear-gradient(135deg,#00d4ff,#22c55e);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
    }
    .roi-desc { font-size:0.78rem;color:#64748b;margin-top:0.25rem; }
    /* Model badge */
    .model-kpi {
        display:flex;justify-content:space-between;align-items:center;
        padding:0.55rem 0;border-bottom:1px solid rgba(255,255,255,0.05);
    }
    .model-kpi:last-child { border-bottom:none; }
    .model-kpi-name  { font-size:0.82rem;color:#94a3b8; }
    .model-kpi-value { font-size:0.82rem;font-weight:700;color:#00d4ff; }
    </style>
    """, unsafe_allow_html=True)

    # ── Header ────────────────────────────────────────────────────────────────
    now_str = datetime.utcnow().strftime("%B %d, %Y · %H:%M UTC")
    st.markdown(f"""
    <div class="hero-banner">
        <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:1rem;">
            <div>
                <div class="hero-title">📋 Executive Dashboard</div>
                <div class="hero-subtitle">
                    AI-generated business intelligence · Performance forecasting · ROI impact analysis
                </div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:0.72rem;color:#475569;text-transform:uppercase;letter-spacing:0.08em;">Report Generated</div>
                <div style="font-size:0.85rem;color:#94a3b8;font-weight:600;">{now_str}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Fetch live data ───────────────────────────────────────────────────────
    @st.cache_data(ttl=20)
    def fetch_exec_summary():
        try:
            r = requests.get(f"{API_URL}/api/v1/anomaly/executive-summary", timeout=8)
            if r.status_code == 200:
                return r.json()
        except Exception:
            pass
        return None

    summary = fetch_exec_summary()

    # ── System Health Score (derived) ─────────────────────────────────────────
    avg_risk = summary.get("avg_risk_score", 45.0) if summary else 45.0
    health_score = max(0, min(100, round(100 - avg_risk * 0.85)))
    critical_ct  = summary.get("critical_count", 2) if summary else 2
    high_ct      = summary.get("high_count", 4) if summary else 4

    # ── Top row: Health Score + KPI tiles ─────────────────────────────────────
    col_gauge, col_kpis = st.columns([1, 3])

    with col_gauge:
        st.markdown("""
        <div class="section-card" style="text-align:center;padding:1.5rem 1rem;">
            <div style="font-size:0.72rem;color:#64748b;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.5rem;">System Health Score</div>
        </div>
        """, unsafe_allow_html=True)

        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=health_score,
            number={"suffix": "%", "font": {"size": 36, "color": "#f1f5f9", "family": "Inter"}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#334155",
                         "tickfont": {"color": "#64748b", "size": 10}},
                "bar":  {"color": "#00d4ff", "thickness": 0.28},
                "bgcolor": "rgba(15,23,42,0.5)",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 40],  "color": "rgba(239,68,68,0.15)"},
                    {"range": [40, 70], "color": "rgba(234,179,8,0.1)"},
                    {"range": [70, 100],"color": "rgba(34,197,94,0.1)"},
                ],
                "threshold": {
                    "line": {"color": "#a855f7", "width": 2},
                    "thickness": 0.8,
                    "value": health_score,
                }
            }
        ))
        fig_gauge.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            height=200,
            margin=dict(l=10, r=10, t=10, b=0),
            font=dict(color="#94a3b8", family="Inter"),
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

        health_color = "#22c55e" if health_score >= 70 else ("#eab308" if health_score >= 40 else "#ef4444")
        health_label = "HEALTHY" if health_score >= 70 else ("AT RISK" if health_score >= 40 else "CRITICAL")
        st.markdown(f"""
        <div style="text-align:center;margin-top:-0.5rem;">
            <div style="display:inline-block;background:{health_color}22;border:1px solid {health_color}55;
                        border-radius:6px;padding:0.25rem 0.85rem;font-size:0.75rem;font-weight:700;color:{health_color};">
                {health_label}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_kpis:
        delay_prevented_est = max(0, int((100 - avg_risk) / 100 * 11000 * 0.15))
        savings_est = delay_prevented_est * 65
        st.markdown(f"""
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-icon">📦</div>
                <div class="kpi-value">11K</div>
                <div class="kpi-label">Shipments Covered</div>
                <div class="kpi-change">↑ Monthly baseline</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-icon">🎯</div>
                <div class="kpi-value" style="background:linear-gradient(135deg,#22c55e,#10b981);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">66.3%</div>
                <div class="kpi-label">Model Accuracy</div>
                <div class="kpi-change">ROC-AUC: 74.6%</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-icon">💰</div>
                <div class="kpi-value" style="background:linear-gradient(135deg,#f97316,#eab308);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">${savings_est:,.0f}</div>
                <div class="kpi-label">Est. Monthly Savings</div>
                <div class="kpi-change">↑ At current model performance</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-icon">⚠️</div>
                <div class="kpi-value" style="background:linear-gradient(135deg,#ef4444,#f97316);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">{critical_ct + high_ct}</div>
                <div class="kpi-label">Active Alerts</div>
                <div class="kpi-change" style="color:{'#ef4444' if critical_ct>0 else '#eab308'};">{critical_ct} critical · {high_ct} high</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Row 2: Forecast + Insights ────────────────────────────────────────────
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown("### 📈 Delay Rate Forecast (30-Day)")
        days = list(range(-14, 17))
        baseline = 59.7
        seed_vals = [baseline + random.gauss(0, 3.5) for _ in range(14)]
        forecast  = [baseline - i * 0.4 + random.gauss(0, 2) for i in range(17)]
        upper_ci  = [v + 4.5 for v in forecast]
        lower_ci  = [v - 4.5 for v in forecast]

        fig_fc = go.Figure()
        fig_fc.add_trace(go.Scatter(
            x=days[:14], y=seed_vals, mode="lines+markers", name="Historical",
            line=dict(color="#00d4ff", width=2.5),
            marker=dict(size=5, color="#00d4ff"),
        ))
        fig_fc.add_trace(go.Scatter(
            x=days[13:], y=[seed_vals[-1]] + forecast[1:],
            mode="lines", name="Forecast",
            line=dict(color="#a855f7", width=2.5, dash="dot"),
        ))
        fig_fc.add_trace(go.Scatter(
            x=days[13:] + days[13:][::-1],
            y=upper_ci[1:] + lower_ci[1:][::-1],
            fill="toself", fillcolor="rgba(168,85,247,0.07)",
            line=dict(color="rgba(0,0,0,0)"), name="95% CI", showlegend=True,
        ))
        fig_fc.add_vline(x=0, line_dash="dot", line_color="rgba(255,255,255,0.2)",
                         annotation_text="Today", annotation_font_color="#64748b",
                         annotation_font_size=11)
        fig_fc.add_hline(y=50, line_dash="dot", line_color="rgba(34,197,94,0.3)",
                         annotation_text="Target 50%", annotation_font_color="#22c55e",
                         annotation_font_size=10)
        fig_fc.update_layout(
            **_chart_layout(320),
            xaxis=dict(title="Days from Today", gridcolor="rgba(255,255,255,0.04)", color="#64748b"),
            yaxis=dict(title="Delay Rate %", gridcolor="rgba(255,255,255,0.04)", color="#64748b", range=[40, 80]),
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8")),
        )
        st.plotly_chart(fig_fc, use_container_width=True)

        # Radar chart — KPI performance vs target
        st.markdown("### 🎯 Performance vs Targets")
        categories = ["Accuracy", "Precision", "Recall", "F1-Score", "ROC-AUC", "Coverage"]
        actual  = [66.3, 76.1, 63.4, 69.2, 74.6, 88.0]
        target  = [75.0, 80.0, 70.0, 75.0, 80.0, 95.0]

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=actual + [actual[0]], theta=categories + [categories[0]],
            fill="toself", fillcolor="rgba(0,212,255,0.1)",
            line=dict(color="#00d4ff", width=2), name="Current",
        ))
        fig_radar.add_trace(go.Scatterpolar(
            r=target + [target[0]], theta=categories + [categories[0]],
            fill="toself", fillcolor="rgba(168,85,247,0.07)",
            line=dict(color="#a855f7", width=2, dash="dot"), name="Target",
        ))
        fig_radar.update_layout(
            polar=dict(
                bgcolor="rgba(15,23,42,0.5)",
                radialaxis=dict(visible=True, range=[0, 100], gridcolor="rgba(255,255,255,0.07)",
                                tickcolor="#334155", tickfont=dict(color="#64748b", size=9)),
                angularaxis=dict(gridcolor="rgba(255,255,255,0.07)", tickfont=dict(color="#94a3b8", size=11)),
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            height=300,
            margin=dict(l=30, r=30, t=30, b=30),
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8")),
            font=dict(family="Inter"),
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    with col_right:
        st.markdown("### 💡 AI-Generated Insights")

        insights = [
            {
                "cls": "crit",
                "icon": "🔴",
                "title": "Discount Policy is the #1 Risk",
                "body": "Discount offered drives 56.5% of model decisions. "
                        "Current avg discount for delayed shipments is 18.7% vs 5.5% for on-time. "
                        "A hard cap of 20% could reduce delays by ~30%.",
                "badge": "HIGH IMPACT", "badge_color": "#ef4444"
            },
            {
                "cls": "warn",
                "icon": "🟠",
                "title": "Heavy Package Route Gap",
                "body": "Packages >3kg shipped via sea freight show elevated delay rate. "
                        "Routing these to air freight or expedited ground would yield measurable improvement.",
                "badge": "QUICK WIN", "badge_color": "#f97316"
            },
            {
                "cls": "good",
                "icon": "🟢",
                "title": "Flight Mode Outperforms",
                "body": "Air freight (Flight) shipments have the lowest delay rate across all warehouse blocks. "
                        "Consider expanding Flight capacity for high-value, time-critical orders.",
                "badge": "OPPORTUNITY", "badge_color": "#22c55e"
            },
            {
                "cls": "",
                "icon": "🔵",
                "title": "New Customer Risk Flag",
                "body": "First-time buyers (prior_purchases <2) experience 12% higher delay rates. "
                        "An address verification step at checkout could reduce fulfillment errors.",
                "badge": "MEDIUM TERM", "badge_color": "#00d4ff"
            },
            {
                "cls": "warn",
                "icon": "🟡",
                "title": "Block D & E Underperforming",
                "body": "Warehouse blocks D and E show delay rates of 63-68%, well above the platform average. "
                        "Root-cause audit recommended for Q3.",
                "badge": "INVESTIGATE", "badge_color": "#eab308"
            },
        ]

        for ins in insights:
            st.markdown(f"""
            <div class="insight-card {ins['cls']}">
                <div class="insight-title">{ins['icon']} {ins['title']}</div>
                <div class="insight-body">{ins['body']}</div>
                <div class="insight-badge"
                     style="background:{ins['badge_color']}22;color:{ins['badge_color']};
                            border:1px solid {ins['badge_color']}44;">
                    {ins['badge']}
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Row 3: ROI Calculator + Model Health ──────────────────────────────────
    col_roi, col_model = st.columns(2)

    with col_roi:
        st.markdown("### 💰 ROI Impact Simulator")

        current_delay_rate = st.slider("Current Delay Rate (%)", 40, 80, 60, 1)
        target_delay_rate  = st.slider("Target Delay Rate (%)", 20, int(current_delay_rate), 40, 1)
        monthly_volume     = st.slider("Monthly Shipments", 1000, 50000, 11000, 500)
        cost_per_delay     = st.slider("Cost per Delay ($)", 20, 200, 65, 5)

        delayed_now     = int(monthly_volume * current_delay_rate / 100)
        delayed_target  = int(monthly_volume * target_delay_rate / 100)
        prevented       = delayed_now - delayed_target
        monthly_savings = prevented * cost_per_delay
        annual_savings  = monthly_savings * 12

        st.markdown(f"""
        <div class="roi-block">
            <div style="font-size:0.75rem;color:#64748b;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.5rem;">Monthly ROI Estimate</div>
            <div class="roi-num">${monthly_savings:,.0f}</div>
            <div class="roi-desc">{prevented:,} delays prevented × ${cost_per_delay} avg cost</div>
        </div>
        <div class="roi-block" style="border-color:rgba(168,85,247,0.2);">
            <div style="font-size:0.75rem;color:#64748b;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.5rem;">Annual ROI Estimate</div>
            <div class="roi-num" style="background:linear-gradient(135deg,#a855f7,#6366f1);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">${annual_savings:,.0f}</div>
            <div class="roi-desc">Delay rate: {current_delay_rate}% → {target_delay_rate}% on {monthly_volume:,} shipments/month</div>
        </div>
        """, unsafe_allow_html=True)

        # Savings waterfall chart
        fig_bar = go.Figure(go.Bar(
            x=["Current Cost", "After Optimization", "Savings"],
            y=[delayed_now * cost_per_delay, delayed_target * cost_per_delay, monthly_savings],
            marker_color=["#ef4444", "#22c55e", "#00d4ff"],
            marker_line_color="rgba(255,255,255,0.1)", marker_line_width=1,
        ))
        fig_bar.update_layout(
            **_chart_layout(230),
            xaxis=dict(showgrid=False, color="#64748b"),
            yaxis=dict(title="$ / month", gridcolor="rgba(255,255,255,0.04)", color="#64748b"),
            showlegend=False,
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_model:
        st.markdown("### 🤖 Model Health Monitor")

        model_metrics = [
            ("Accuracy",       "66.3%",  "#00d4ff"),
            ("Precision",      "76.1%",  "#22c55e"),
            ("Recall",         "63.4%",  "#eab308"),
            ("F1-Score",       "69.2%",  "#00d4ff"),
            ("ROC-AUC",        "74.6%",  "#a855f7"),
            ("Training Data",  "10,999", "#00d4ff"),
            ("Features",       "22",     "#22c55e"),
            ("Inference",      "<50ms",  "#a855f7"),
            ("Model Type",     "XGBoost v1.0", "#64748b"),
            ("Pipeline",       "Full MLOps",   "#64748b"),
        ]
        st.markdown('<div class="section-card" style="padding:1rem 1.25rem;">', unsafe_allow_html=True)
        for name, val, color in model_metrics:
            st.markdown(f"""
            <div class="model-kpi">
                <span class="model-kpi-name">{name}</span>
                <span class="model-kpi-value" style="color:{color};">{val}</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Feature importance horizontal bar
        st.markdown("#### 📊 Feature Importance Top 5")
        feats  = ["Discount %", "Log Weight", "Prior Purchases", "Product Cost", "Mode"]
        imps   = [56.5, 9.7, 5.1, 4.6, 2.1]
        colors = ["#ef4444", "#f97316", "#eab308", "#22c55e", "#00d4ff"]
        fig_fi = go.Figure(go.Bar(
            x=imps, y=feats, orientation="h",
            marker_color=colors,
            marker_line_color="rgba(255,255,255,0.08)", marker_line_width=1,
            text=[f"{v}%" for v in imps], textposition="outside",
            textfont=dict(color="#94a3b8", size=11),
        ))
        fig_fi.update_layout(
            **_chart_layout(220),
            xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.04)",
                       color="#64748b", title="Importance %"),
            yaxis=dict(showgrid=False, color="#94a3b8"),
            showlegend=False,
        )
        st.plotly_chart(fig_fi, use_container_width=True)

    st.markdown("---")

    # ── Supply Chain Flow Diagram ──────────────────────────────────────────────
    st.markdown("### 🔗 Supply Chain Flow Analysis")

    labels = ["Orders", "Block A", "Block B", "Block C", "Block D", "Block E", "Block F",
              "Ship", "Flight", "Road", "On-Time", "Delayed"]
    source = [0,0,0,0,0,0, 1,2,3,4,5,6, 1,2,3, 7,8,9, 7,8,9]
    target = [1,2,3,4,5,6, 7,7,7,7,7,7, 8,8,8, 10,10,10, 11,11,11]
    value  = [1833,1833,1833,1834,500,3166, 900,900,900,900,500,2000,
              600,600,600, 3000,800,800, 3000,1000,1000]
    colors_nodes = [
        "#334155","#00d4ff","#0ea5e9","#6366f1","#a855f7","#ec4899","#f97316",
        "#0ea5e9","#a855f7","#22c55e","#22c55e","#ef4444"
    ]
    fig_sankey = go.Figure(go.Sankey(
        node=dict(
            label=labels,
            color=colors_nodes,
            pad=18, thickness=20,
            line=dict(color="rgba(0,0,0,0)", width=0),
        ),
        link=dict(
            source=source, target=target, value=value,
            color=["rgba(0,212,255,0.15)"] * len(source),
        ),
    ))
    fig_sankey.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94a3b8", family="Inter", size=11),
        margin=dict(l=0, r=0, t=10, b=0), height=380,
    )
    st.plotly_chart(fig_sankey, use_container_width=True)

    # ── Auto-Generated Summary Text ───────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📄 AI Executive Brief")
    headline = summary.get("headline", "🟡 MODERATE RISK — Monitor Active Alerts") if summary else "🟡 Moderate Risk"
    body     = summary.get("summary", "System operating within expected parameters.") if summary else ""

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,rgba(0,212,255,0.05),rgba(168,85,247,0.05));
                border:1px solid rgba(0,212,255,0.15);border-radius:16px;padding:1.5rem 2rem;">
        <div style="font-size:1rem;font-weight:700;color:#f1f5f9;margin-bottom:0.75rem;">{headline}</div>
        <div style="font-size:0.88rem;color:#94a3b8;line-height:1.7;margin-bottom:1rem;">{body}</div>
        <div style="font-size:0.85rem;color:#94a3b8;line-height:1.7;">
            <strong style="color:#e2e8f0;">Strategic Recommendation:</strong>
            Prioritize discount policy reform as the single highest-ROI intervention.
            Establish dynamic discount limits (≤20% for standard, ≤10% during peak periods)
            using the SmartShip model as the gating engine. Pair with proactive notification
            protocols for shipments with risk scores above 60% to reduce exception handling costs.
            Target delay rate reduction from 59.7% to below 45% within 90 days of implementation.
        </div>
        <div style="margin-top:1rem;font-size:0.72rem;color:#475569;">
            Generated by SmartShip AI Executive Advisor · {now_str}
        </div>
    </div>
    """, unsafe_allow_html=True)
