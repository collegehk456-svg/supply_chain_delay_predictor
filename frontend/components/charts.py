import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Any
import pandas as pd

def create_premium_chart_layout():
    """
    Returns a premium chart layout configuration for Plotly.
    """
    return dict(
        template="plotly_dark",
        paper_bgcolor="rgba(15, 23, 42, 0.5)",
        plot_bgcolor="rgba(15, 23, 42, 0.3)",
        font=dict(
            family="-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto'",
            size=12,
            color="#cbd5e1"
        ),
        margin=dict(l=40, r=40, t=40, b=40),
        hovermode="x unified",
        showlegend=True,
        legend=dict(
            bgcolor="rgba(15, 23, 42, 0.6)",
            bordercolor="rgba(0, 212, 255, 0.2)",
            borderwidth=1,
            font=dict(size=11)
        ),
        xaxis=dict(
            gridcolor="rgba(0, 212, 255, 0.1)",
            showgrid=True,
            zeroline=False,
            showline=True,
            linecolor="rgba(0, 212, 255, 0.2)"
        ),
        yaxis=dict(
            gridcolor="rgba(0, 212, 255, 0.1)",
            showgrid=True,
            zeroline=False,
            showline=True,
            linecolor="rgba(0, 212, 255, 0.2)"
        )
    )


def line_chart(df: pd.DataFrame, x: str, y: List[str], title: str = ""):
    """
    Premium animated line chart.
    """
    fig = go.Figure()
    
    colors = ["#00d4ff", "#a855f7", "#0ea5e9", "#06b6d4"]
    
    for i, col in enumerate(y):
        fig.add_trace(go.Scatter(
            x=df[x],
            y=df[col],
            name=col,
            mode="lines+markers",
            line=dict(
                color=colors[i % len(colors)],
                width=3,
                shape="spline"
            ),
            marker=dict(
                size=6,
                color=colors[i % len(colors)],
                opacity=0.8,
                line=dict(color="white", width=2)
            ),
            fill="tozeroy" if i == 0 else None,
            fillcolor=f"rgba({int(colors[i % len(colors)].lstrip('#')[:2], 16)}, {int(colors[i % len(colors)].lstrip('#')[2:4], 16)}, {int(colors[i % len(colors)].lstrip('#')[4:], 16)}, 0.1)",
            hovertemplate="<b>%{customdata}</b><br>" +
                         "Date: %{x|%Y-%m-%d}<br>" +
                         "Value: %{y:,.0f}<extra></extra>",
            customdata=[col] * len(df)
        ))
    
    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>",
            font=dict(size=18, color="#ffffff")
        ),
        **create_premium_chart_layout()
    )
    
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def bar_chart(df: pd.DataFrame, x: str, y: str, title: str = "", color: str = "#00d4ff"):
    """
    Premium animated bar chart.
    """
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df[x],
        y=df[y],
        marker=dict(
            color=color,
            opacity=0.8,
            line=dict(color="rgba(0, 212, 255, 0.3)", width=2)
        ),
        hovertemplate="<b>%{x}</b><br>Value: %{y:,.0f}<extra></extra>"
    ))
    
    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>",
            font=dict(size=18, color="#ffffff")
        ),
        **create_premium_chart_layout()
    )
    
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def gauge_chart(value: float, max_value: float = 100, title: str = "", 
                color: str = "#00d4ff"):
    """
    Premium gauge/progress chart.
    """
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        title={"text": title, "font": {"size": 16}},
        delta={"reference": max_value * 0.8},
        gauge=dict(
            axis=dict(range=[0, max_value]),
            bar=dict(color=color),
            steps=[
                {"range": [0, max_value * 0.25], "color": "rgba(0, 212, 255, 0.1)"},
                {"range": [max_value * 0.25, max_value * 0.5], "color": "rgba(0, 212, 255, 0.2)"},
                {"range": [max_value * 0.5, max_value * 0.75], "color": "rgba(0, 212, 255, 0.3)"},
                {"range": [max_value * 0.75, max_value], "color": "rgba(0, 212, 255, 0.4)"}
            ],
            threshold=dict(
                line=dict(color="#a855f7", width=4),
                thickness=0.75,
                value=max_value * 0.9
            )
        ),
        number={"font": {"size": 28, "color": "#00d4ff"}}
    ))
    
    fig.update_layout(
        **create_premium_chart_layout(),
        paper_bgcolor="rgba(15, 23, 42, 0.5)",
        plot_bgcolor="transparent"
    )
    
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def scatter_chart(df: pd.DataFrame, x: str, y: str, size: str = None, 
                  color: str = None, title: str = ""):
    """
    Premium scatter chart.
    """
    fig = px.scatter(
        df,
        x=x,
        y=y,
        size=size,
        color=color,
        title=title,
        color_continuous_scale="Viridis"
    )
    
    fig.update_layout(**create_premium_chart_layout())
    fig.update_traces(marker=dict(size=10, opacity=0.7))
    
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
