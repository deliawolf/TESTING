import streamlit as st

def load_css():
    st.markdown("""
        <style>
        /* Import Google Fonts - Inter & JetBrains Mono */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

        :root {
            --primary-color: #3b82f6;
            --primary-hover: #2563eb;
            --bg-color: #f8fafc;
            --card-bg: rgba(255, 255, 255, 0.8);
            --text-color: #1e293b;
            --border-color: #e2e8f0;
            --sidebar-bg: #ffffff;
        }

        @media (prefers-color-scheme: dark) {
            :root {
                --primary-color: #60a5fa;
                --primary-hover: #3b82f6;
                --bg-color: #0f172a;
                --card-bg: rgba(30, 41, 59, 0.7);
                --text-color: #f1f5f9;
                --border-color: #334155;
                --sidebar-bg: #1e293b;
            }
        }

        /* Global Reset & Typography */
        html, body {
            font-family: 'Inter', sans-serif;
            color: var(--text-color);
            background-color: var(--bg-color);
            font-size: 16px !important; /* Increase base font size */
        }

        /* Streamlit Main Container */
        .stApp {
            background-color: var(--bg-color);
        }

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: var(--sidebar-bg) !important;
            border-right: 1px solid var(--border-color);
            box-shadow: 4px 0 24px rgba(0,0,0,0.02);
        }

        /* Custom Navigation Menu Styling (Radio Buttons) */
        div[data-testid="stSidebar"] .stRadio > label {
            display: none; /* Hide label */
        }
        div[data-testid="stSidebar"] .stRadio > div {
            gap: 0.5rem;
        }
        div[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label {
            background: transparent;
            border: 1px solid transparent;
            border-radius: 8px;
            padding: 0.75rem 1rem;
            margin-bottom: 0.25rem;
            transition: all 0.2s ease;
            color: var(--text-color);
            font-weight: 500;
            cursor: pointer;
            display: flex;
            align-items: center;
        }
        div[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label:hover {
            background: rgba(59, 130, 246, 0.1);
            color: var(--primary-color);
        }
        div[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label[data-checked="true"] {
            background: rgba(59, 130, 246, 0.15);
            color: var(--primary-color);
            border-color: rgba(59, 130, 246, 0.2);
            font-weight: 600;
        }
        /* Hide the default radio circle */
        div[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label > div:first-child {
            display: none;
        }

        /* Glassmorphism Cards */
        .stCard {
            background: var(--card-bg) !important;
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid var(--border-color) !important;
            border-radius: 16px !important;
            padding: 1.5rem !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03) !important;
            margin-bottom: 1.5rem !important;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .stCard:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -2px rgba(0, 0, 0, 0.04) !important;
            border-color: var(--primary-color) !important;
        }

        /* Terminal Window */
        .terminal-window {
            background-color: #1a1b26 !important;
            color: #a9b1d6 !important;
            font-family: 'JetBrains Mono', monospace !important;
            padding: 1.25rem !important;
            border-radius: 12px !important;
            height: 450px !important;
            overflow-y: auto !important;
            border: 1px solid #2f334d !important;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2) !important;
            font-size: 0.95rem !important; /* Increased terminal font size */
            line-height: 1.5 !important;
        }
        .terminal-window::-webkit-scrollbar { width: 8px; }
        .terminal-window::-webkit-scrollbar-track { background: transparent; }
        .terminal-window::-webkit-scrollbar-thumb { background: #414868; border-radius: 4px; }

        /* Buttons */
        .stButton button {
            border-radius: 10px !important;
            font-weight: 600 !important;
            padding: 0.6rem 1.2rem !important;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
            border: none !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
            font-size: 1rem !important; /* Explicit button font size */
        }
        .stButton button:hover {
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important;
        }
        /* Primary Button */
        .stButton button[kind="primary"] {
            background: linear-gradient(135deg, var(--primary-color), var(--primary-hover)) !important;
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3) !important;
        }
        .stButton button[kind="primary"]:hover {
            box-shadow: 0 6px 16px rgba(59, 130, 246, 0.4) !important;
        }

        /* Inputs & Selectboxes - Simplified to fix bugs */
        .stTextInput input {
            border-radius: 8px !important;
            border: 1px solid var(--border-color) !important;
            padding: 0.5rem !important;
        }
        .stTextInput input:focus {
            border-color: var(--primary-color) !important;
            box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
        }
        /* Removed aggressive overrides for stSelectbox to let Streamlit handle the dropdown rendering correctly */

        /* Headers */
        h1, h2, h3 {
            font-weight: 800 !important;
            letter-spacing: -0.025em !important;
            color: var(--text-color);
        }
        h1 { font-size: 2.5rem !important; background: linear-gradient(to right, var(--primary-color), #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }

        /* Custom Classes */
        .device-card-header {
            font-size: 1.25rem !important;
            font-weight: 700 !important;
            margin-bottom: 0.5rem !important;
            display: flex;
            align-items: center;
            gap: 0.75rem;
            color: var(--text-color);
        }
        .device-card-detail {
            font-size: 0.9rem !important;
            color: #64748b;
            margin-bottom: 0.25rem !important;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        @media (prefers-color-scheme: dark) {
            .device-card-detail { color: #94a3b8; }
        }
        </style>
    """, unsafe_allow_html=True)

def card_container(key=None):
    """Helper to create a styled container that looks like a card."""
    container = st.container()
    container.markdown('<div class="stCard">', unsafe_allow_html=True)
    return container

def close_card():
    """Closes the card div."""
    st.markdown('</div>', unsafe_allow_html=True)
