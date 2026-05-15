import streamlit as st
import time

def skeleton_loader(count: int = 3, height: int = 200):
    """
    Animated skeleton loading component.
    """
    st.markdown("""
        <style>
        @keyframes shimmer {
            0% { background-position: -1000px 0; }
            100% { background-position: 1000px 0; }
        }
        
        .skeleton {
            background: linear-gradient(
                90deg,
                rgba(255, 255, 255, 0.05) 0%,
                rgba(255, 255, 255, 0.1) 50%,
                rgba(255, 255, 255, 0.05) 100%
            );
            background-size: 1000px 100%;
            animation: shimmer 2s infinite;
            border-radius: 12px;
            margin-bottom: 1rem;
        }
        </style>
    """, unsafe_allow_html=True)
    
    for i in range(count):
        st.markdown(f'<div class="skeleton" style="height: {height}px;"></div>', 
                   unsafe_allow_html=True)


def pulse_loader(text: str = "Loading..."):
    """
    Animated pulse loader.
    """
    st.markdown(f"""
        <style>
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
        }}
        
        .pulse-loader {{
            text-align: center;
            padding: 2rem;
            animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
            font-size: 1.1rem;
            color: #00d4ff;
            font-weight: 600;
        }}
        </style>
        
        <div class="pulse-loader">⚡ {text}</div>
    """, unsafe_allow_html=True)


def spinner_loader():
    """
    Animated spinner loader.
    """
    st.markdown("""
        <style>
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .spinner {
            display: inline-block;
            width: 40px;
            height: 40px;
            border: 4px solid rgba(0, 212, 255, 0.2);
            border-top-color: #00d4ff;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 2rem auto;
            display: block;
        }
        </style>
        
        <div class="spinner"></div>
    """, unsafe_allow_html=True)


def progress_bar(value: float, total: float = 100, label: str = ""):
    """
    Premium animated progress bar.
    """
    percentage = (value / total) * 100
    
    st.markdown(f"""
        <style>
        .progress-container {{
            margin: 1.5rem 0;
        }}
        
        .progress-label {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 0.5rem;
            font-size: 0.9rem;
            color: #cbd5e1;
        }}
        
        .progress-bar {{
            width: 100%;
            height: 8px;
            background: rgba(0, 212, 255, 0.1);
            border-radius: 4px;
            overflow: hidden;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #00d4ff, #a855f7);
            width: {percentage}%;
            transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
            border-radius: 4px;
            box-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
        }}
        </style>
        
        <div class="progress-container">
            {f'<div class="progress-label"><span>{label}</span><span>{percentage:.1f}%</span></div>' if label else ''}
            <div class="progress-bar">
                <div class="progress-fill"></div>
            </div>
        </div>
    """, unsafe_allow_html=True)
