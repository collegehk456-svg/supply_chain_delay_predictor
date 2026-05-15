import streamlit as st
from typing import Optional, Any

def metric_card(label: str, value: Any, change: Optional[str] = None, 
                icon: str = "📊", color: str = "primary"):
    """
    Premium metric card with gradient and hover effects.
    """
    color_map = {
        "primary": "linear-gradient(135deg, #00d4ff 0%, #0ea5e9 100%)",
        "secondary": "linear-gradient(135deg, #a855f7 0%, #6366f1 100%)",
        "accent": "linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%)",
    }
    
    gradient = color_map.get(color, color_map["primary"])
    
    st.markdown(f"""
        <style>
        .metric-{id(label)} {{
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid rgba(0, 212, 255, 0.2);
            border-radius: 16px;
            padding: 1.5rem;
            backdrop-filter: blur(10px);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            cursor: pointer;
            position: relative;
            overflow: hidden;
            animation: slideInUp 0.5s ease-out;
        }}
        
        .metric-{id(label)}::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: {gradient};
            opacity: 0;
            z-index: -1;
            transition: opacity 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        
        .metric-{id(label)}:hover {{
            border-color: rgba(0, 212, 255, 0.6);
            box-shadow: 0 20px 50px rgba(0, 212, 255, 0.2);
            transform: translateY(-8px);
        }}
        
        .metric-{id(label)}:hover::before {{
            opacity: 0.05;
        }}
        
        .metric-icon {{
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }}
        
        .metric-value {{
            font-size: 2.5rem;
            font-weight: 800;
            background: {gradient};
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.5rem;
            letter-spacing: -0.01em;
        }}
        
        .metric-label {{
            font-size: 0.875rem;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 600;
            margin-bottom: 0.75rem;
        }}
        
        .metric-change {{
            font-size: 0.85rem;
            padding: 0.5rem 0.75rem;
            background: rgba(0, 212, 255, 0.1);
            color: #00d4ff;
            border-radius: 6px;
            font-weight: 600;
            display: inline-block;
        }}
        </style>
        
        <div class="metric-{id(label)}">
            <div class="metric-icon">{icon}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-label">{label}</div>
            {f'<div class="metric-change">{change}</div>' if change else ''}
        </div>
    """, unsafe_allow_html=True)


def feature_card(title: str, description: str, icon: str, 
                 features: list = None, action_text: str = None):
    """
    Premium feature/info card with icon and features list.
    """
    st.markdown(f"""
        <style>
        .feature-card-{id(title)} {{
            background: linear-gradient(135deg, rgba(0, 212, 255, 0.05) 0%, rgba(168, 85, 247, 0.05) 100%);
            border: 1px solid rgba(0, 212, 255, 0.2);
            border-radius: 16px;
            padding: 2rem;
            backdrop-filter: blur(10px);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            animation: slideInUp 0.5s ease-out;
        }}
        
        .feature-card-{id(title)}:hover {{
            border-color: rgba(0, 212, 255, 0.6);
            box-shadow: 0 30px 60px rgba(0, 212, 255, 0.15);
            transform: translateY(-8px);
        }}
        
        .feature-icon {{
            font-size: 3rem;
            margin-bottom: 1rem;
            display: inline-block;
        }}
        
        .feature-title {{
            font-size: 1.5rem;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 0.75rem;
        }}
        
        .feature-description {{
            color: #cbd5e1;
            font-size: 0.95rem;
            line-height: 1.6;
            margin-bottom: 1.5rem;
        }}
        
        .feature-list {{
            list-style: none;
            margin-bottom: 1.5rem;
        }}
        
        .feature-list li {{
            color: #cbd5e1;
            margin-bottom: 0.75rem;
            padding-left: 1.75rem;
            position: relative;
        }}
        
        .feature-list li::before {{
            content: '✓';
            position: absolute;
            left: 0;
            color: #00d4ff;
            font-weight: bold;
        }}
        </style>
        
        <div class="feature-card-{id(title)}">
            <div class="feature-icon">{icon}</div>
            <div class="feature-title">{title}</div>
            <div class="feature-description">{description}</div>
            {f'<ul class="feature-list">{"\n".join([f"<li>{f}</li>" for f in features])}</ul>' if features else ''}
        </div>
    """, unsafe_allow_html=True)


def info_card(title: str, content: str, color: str = "primary"):
    """
    Minimal info card with customizable color.
    """
    color_borders = {
        "primary": "rgba(0, 212, 255, 0.3)",
        "secondary": "rgba(168, 85, 247, 0.3)",
        "success": "rgba(34, 197, 94, 0.3)",
        "warning": "rgba(251, 146, 60, 0.3)",
        "error": "rgba(239, 68, 68, 0.3)",
    }
    
    border_color = color_borders.get(color, color_borders["primary"])
    
    st.markdown(f"""
        <style>
        .info-card-{id(title)} {{
            background: rgba(15, 23, 42, 0.5);
            border-left: 4px solid {border_color};
            border-radius: 8px;
            padding: 1.5rem;
            backdrop-filter: blur(10px);
            animation: slideInUp 0.5s ease-out;
        }}
        
        .info-title {{
            font-size: 1.1rem;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 0.5rem;
        }}
        
        .info-content {{
            font-size: 0.95rem;
            color: #cbd5e1;
            line-height: 1.6;
        }}
        </style>
        
        <div class="info-card-{id(title)}">
            <div class="info-title">{title}</div>
            <div class="info-content">{content}</div>
        </div>
    """, unsafe_allow_html=True)
