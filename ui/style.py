import streamlit as st

def apply_custom_css():
    st.markdown("""
    <style>
    /* Dark Theme Base */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }
    
    /* Glassmorphic Metrics */
    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(5px);
    }
    
    /* Green highlight for values */
    div[data-testid="stMetricValue"] {
        color: #2ea043;
        font-weight: 800;
    }
    
    /* Chat bubbles overhaul */
    .stChatMessage {
        background-color: #161B22 !important;
        border: 1px solid #30363D !important;
        border-radius: 12px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
    }
    
    /* Primary buttons */
    .stButton>button {
        background-color: #238636;
        color: white;
        border: 1px solid rgba(240, 246, 252, 0.1);
        border-radius: 6px;
        font-weight: 600;
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover {
        background-color: #2ea043;
        transform: translateY(-1px);
        box-shadow: 0 4px 6px rgba(0,255,0,0.1);
    }
    
    /* Subtle headings */
    h1 {
        background: -webkit-linear-gradient(45deg, #58a6ff, #3fb950);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    </style>
    """, unsafe_allow_html=True)
