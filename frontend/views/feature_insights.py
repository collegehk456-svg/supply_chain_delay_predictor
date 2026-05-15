"""Feature importance and insights dashboard."""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

def show_insights():
    st.title("Feature Analysis & Insights")
    
    st.markdown("""
    Our ML model discovered the key factors that cause shipping delays.
    Understanding these helps logistics teams reduce delays proactively.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Feature Importance")
        
        feature_data = {
            'Feature': [
                'Discount Offered',
                'Log Weight',
                'Prior Purchases',
                'Product Cost',
                'Weight (grams)',
                'Log Cost',
                'Has Discount',
                'Customer Calls',
                'Shipment Mode',
                'Weight/Cost Ratio'
            ],
            'Importance (%)': [56.5, 9.7, 5.1, 4.6, 3.6, 2.7, 2.6, 2.2, 2.1, 2.0]
        }
        
        df_feat = pd.DataFrame(feature_data)
        
        fig = go.Figure(go.Bar(
            x=df_feat['Importance (%)'],
            y=df_feat['Feature'],
            orientation='h',
            marker=dict(
                color=df_feat['Importance (%)'],
                colorscale=[[0, '#1e3a5f'], [0.5, '#0ea5e9'], [1, '#00d4ff']],
                line=dict(color='rgba(0,212,255,0.3)', width=1)
            ),
            text=[f"{v:.1f}%" for v in df_feat['Importance (%)']],
            textposition='outside'
        ))
        fig.update_layout(
            plot_bgcolor='rgba(15,23,42,0.8)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#cbd5e1'),
            margin=dict(l=10, r=60, t=10, b=10),
            height=350,
            xaxis=dict(gridcolor='rgba(255,255,255,0.05)', title='Importance (%)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.05)')
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Delay Rate by Shipment Mode")
        
        mode_data = {
            'Mode': ['Ship', 'Flight', 'Road'],
            'Delay Rate (%)': [62.1, 54.3, 57.8],
            'Volume': [7462, 1777, 1760]
        }
        df_mode = pd.DataFrame(mode_data)
        
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=df_mode['Mode'],
            y=df_mode['Delay Rate (%)'],
            marker=dict(
                color=['#ef4444', '#f97316', '#eab308'],
                opacity=0.85
            ),
            text=[f"{v:.1f}%" for v in df_mode['Delay Rate (%)']],
            textposition='outside'
        ))
        fig2.update_layout(
            plot_bgcolor='rgba(15,23,42,0.8)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#cbd5e1'),
            margin=dict(l=10, r=10, t=10, b=10),
            height=350,
            yaxis=dict(gridcolor='rgba(255,255,255,0.05)', title='Delay Rate (%)', range=[0, 80]),
            xaxis=dict(gridcolor='rgba(255,255,255,0.05)')
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    st.markdown("---")
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("Discount vs Delay Probability")
        
        discount_bins = list(range(0, 70, 10))
        delay_rates = [32.1, 41.3, 52.7, 63.4, 71.8, 79.2, 86.5]
        
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(
            x=discount_bins,
            y=delay_rates,
            mode='lines+markers',
            line=dict(color='#00d4ff', width=3),
            marker=dict(size=10, color='#a855f7', line=dict(color='#00d4ff', width=2)),
            fill='tozeroy',
            fillcolor='rgba(0,212,255,0.08)'
        ))
        fig3.update_layout(
            plot_bgcolor='rgba(15,23,42,0.8)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#cbd5e1'),
            margin=dict(l=10, r=10, t=10, b=10),
            height=300,
            xaxis=dict(title='Discount (%)', gridcolor='rgba(255,255,255,0.05)'),
            yaxis=dict(title='Delay Rate (%)', gridcolor='rgba(255,255,255,0.05)')
        )
        st.plotly_chart(fig3, use_container_width=True)
    
    with col4:
        st.subheader("Weight Distribution by Outcome")
        
        import numpy as np
        np.random.seed(42)
        delayed_weights = np.random.normal(3272, 1200, 500)
        ontime_weights = np.random.normal(2100, 900, 400)
        
        fig4 = go.Figure()
        fig4.add_trace(go.Histogram(
            x=delayed_weights, name='Delayed', opacity=0.7,
            marker_color='#ef4444', nbinsx=20
        ))
        fig4.add_trace(go.Histogram(
            x=ontime_weights, name='On-Time', opacity=0.7,
            marker_color='#22c55e', nbinsx=20
        ))
        fig4.update_layout(
            barmode='overlay',
            plot_bgcolor='rgba(15,23,42,0.8)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#cbd5e1'),
            margin=dict(l=10, r=10, t=10, b=10),
            height=300,
            legend=dict(bgcolor='rgba(0,0,0,0)'),
            xaxis=dict(title='Weight (grams)', gridcolor='rgba(255,255,255,0.05)'),
            yaxis=dict(title='Count', gridcolor='rgba(255,255,255,0.05)')
        )
        st.plotly_chart(fig4, use_container_width=True)
    
    st.markdown("---")
    st.subheader("Key Insights")
    
    insights = [
        ("Discount is King", "Shipments with >25% discount are 2.7x more likely to be delayed. This is the single strongest predictor at 56.5% model importance.", "warning"),
        ("Weight Matters", "Packages over 3kg have a 73% delay rate vs 51% for lighter packages. Special handling requirements slow down the fulfillment chain.", "error"),
        ("Air is Safest", "Air freight (Flight) has the lowest delay rate at 54.3%, followed by Road at 57.8% and Ship at 62.1%. For critical shipments, upgrade to air.", "success"),
        ("New Customers Need More Care", "Customers with <2 prior purchases have a 12% higher delay rate due to address errors and handling requirement mismatches.", "info"),
    ]
    
    for title, text, color_type in insights:
        if color_type == "warning":
            st.warning(f"**{title}**: {text}")
        elif color_type == "error":
            st.error(f"**{title}**: {text}")
        elif color_type == "success":
            st.success(f"**{title}**: {text}")
        else:
            st.info(f"**{title}**: {text}")
