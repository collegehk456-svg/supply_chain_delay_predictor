import streamlit as st
from datetime import datetime
import math

def render_navbar():
    """
    Premium navigation bar component with glassmorphism and animations.
    """
    st.markdown("""
        <style>
        .navbar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 1rem 2rem;
            background: linear-gradient(180deg, rgba(15, 23, 42, 0.95) 0%, rgba(10, 14, 39, 0.85) 100%);
            border-bottom: 1px solid rgba(0, 212, 255, 0.2);
            backdrop-filter: blur(10px);
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            animation: slideInDown 0.5s ease-out;
        }
        
        .navbar-brand {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            font-size: 1.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #00d4ff 0%, #a855f7 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-decoration: none;
            letter-spacing: -0.02em;
        }
        
        .navbar-brand:hover {
            filter: brightness(1.2);
        }
        
        .navbar-logo {
            font-size: 2rem;
            animation: float 3s ease-in-out infinite;
        }
        
        .navbar-nav {
            display: flex;
            gap: 2rem;
            align-items: center;
            list-style: none;
            margin: 0;
        }
        
        .nav-item {
            color: #cbd5e1;
            font-size: 0.95rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
        }
        
        .nav-item:hover {
            color: #00d4ff;
        }
        
        .nav-item::after {
            content: '';
            position: absolute;
            bottom: -5px;
            left: 0;
            width: 0;
            height: 2px;
            background: linear-gradient(90deg, #00d4ff, #a855f7);
            transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .nav-item:hover::after {
            width: 100%;
        }
        
        .navbar-status {
            display: flex;
            align-items: center;
            gap: 1rem;
            padding: 0.5rem 1rem;
            background: rgba(0, 212, 255, 0.1);
            border: 1px solid rgba(0, 212, 255, 0.3);
            border-radius: 8px;
            color: #00d4ff;
            font-weight: 600;
            font-size: 0.85rem;
        }
        
        .status-indicator {
            width: 8px;
            height: 8px;
            background: #00d4ff;
            border-radius: 50%;
            animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
        
        @media (max-width: 768px) {
            .navbar {
                padding: 1rem;
            }
            
            .navbar-nav {
                gap: 1rem;
                font-size: 0.85rem;
            }
            
            .navbar-brand {
                font-size: 1.2rem;
            }
            
            .navbar-status {
                font-size: 0.75rem;
            }
        }
        </style>
        
        <div class="navbar">
            <div class="navbar-brand">
                <span class="navbar-logo">🚀</span>
                SmartShip AI
            </div>
            
            <ul class="navbar-nav">
                <li class="nav-item">Dashboard</li>
                <li class="nav-item">Predictions</li>
                <li class="nav-item">Analytics</li>
                <li class="nav-item">Settings</li>
            </ul>
            
            <div class="navbar-status">
                <span class="status-indicator"></span>
                System Operational
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_sidebar_header():
    """
    Premium sidebar header with branding.
    """
    with st.sidebar:
        st.markdown("""
            <style>
            .sidebar-header {
                padding: 2rem 1rem 1rem;
                text-align: center;
                border-bottom: 1px solid rgba(0, 212, 255, 0.2);
                margin-bottom: 2rem;
                animation: slideInLeft 0.5s ease-out;
            }
            
            .sidebar-icon {
                font-size: 3rem;
                margin-bottom: 1rem;
                display: inline-block;
                animation: bounce 2s infinite;
            }
            
            .sidebar-title {
                font-size: 1.5rem;
                font-weight: 800;
                background: linear-gradient(135deg, #00d4ff 0%, #a855f7 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                margin-bottom: 0.5rem;
            }
            
            .sidebar-subtitle {
                font-size: 0.85rem;
                color: #94a3b8;
            }
            
            @keyframes bounce {
                0%, 100% { transform: translateY(0); }
                50% { transform: translateY(-10px); }
            }
            </style>
            
            <div class="sidebar-header">
                <div class="sidebar-icon">🚀</div>
                <div class="sidebar-title">SmartShip</div>
                <div class="sidebar-subtitle">AI Prediction Engine</div>
            </div>
        """, unsafe_allow_html=True)
