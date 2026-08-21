"""
FPL Mini-League Ultra-Elegant Analytics Dashboard
Streamlit Web Application featuring a modern Premier League glassmorphism aesthetic,
custom vector SVG icons, interactive Plotly visualizations, squad pitch view, and local snapshot persistence.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import html
import json
import os
import re
import sqlite3

from fpl_api import FPLApiClient
from fpl_analytics import FPLMiniLeagueAnalyzer
from exporter import FPLExporter

# Page Configuration
st.set_page_config(
    page_title="FPL Masterclass | Premier League Intelligence",
    page_icon="🦁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- LUXURY VECTOR SVG ICONS -----------------
SVG_ICONS = {
    # Premium Glowing Lion Crest Emblem
    "fpl_crest": """<svg width="44" height="44" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="crestGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#37003c"/>
                <stop offset="50%" stop-color="#1f0024"/>
                <stop offset="100%" stop-color="#0a000d"/>
            </linearGradient>
            <linearGradient id="neonGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#00FF87"/>
                <stop offset="100%" stop-color="#02EFFF"/>
            </linearGradient>
            <linearGradient id="goldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#FFE27A"/>
                <stop offset="100%" stop-color="#D4A017"/>
            </linearGradient>
            <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                <feDropShadow dx="0" dy="0" stdDeviation="3" flood-color="#00FF87" flood-opacity="0.4"/>
            </filter>
        </defs>
        <path d="M24 2 L42 10 V23 C42 34.5 34.5 42 24 46 C13.5 42 6 34.5 6 23 V10 Z" fill="url(#crestGrad)" stroke="url(#neonGrad)" stroke-width="2" filter="url(#glow)"/>
        <!-- Crown Top -->
        <path d="M16 16 L19 22 L24 14 L29 22 L32 16 L31 25 H17 Z" fill="url(#goldGrad)"/>
        <!-- Lion Head Stylized Silhouette -->
        <circle cx="24" cy="27" r="4.5" fill="#FFFFFF"/>
        <path d="M20 30 C20 27.5 28 27.5 28 30 C28 34 20 34 20 30 Z" fill="url(#neonGrad)"/>
        <circle cx="22.5" cy="26.5" r="0.8" fill="#140020"/>
        <circle cx="25.5" cy="26.5" r="0.8" fill="#140020"/>
        <path d="M23 28.5 L24 29.5 L25 28.5" stroke="#140020" stroke-width="0.8" stroke-linecap="round"/>
    </svg>""",

    "trophy": """<svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M6 9H4.5C3.12 9 2 7.88 2 6.5C2 5.12 3.12 4 4.5 4H6" stroke="#FFE27A" stroke-width="2" stroke-linecap="round"/>
        <path d="M18 9H19.5C20.88 9 22 7.88 22 6.5C22 5.12 20.88 4 19.5 4H18" stroke="#FFE27A" stroke-width="2" stroke-linecap="round"/>
        <path d="M4 22H20" stroke="#FFE27A" stroke-width="2" stroke-linecap="round"/>
        <path d="M10 14.66V17C10 17.55 9.55 18 9 18H7.5" stroke="#FFE27A" stroke-width="2" stroke-linecap="round"/>
        <path d="M14 14.66V17C14 17.55 14.45 18 15 18H16.5" stroke="#FFE27A" stroke-width="2" stroke-linecap="round"/>
        <path d="M18 2H6V9C6 12.31 8.69 15 12 15C15.31 15 18 12.31 18 9V2Z" fill="rgba(255,226,122,0.15)" stroke="#FFE27A" stroke-width="2" stroke-linejoin="round"/>
        <polygon points="12,5 13,7.5 15.5,7.5 13.5,9 14.2,11.5 12,10 9.8,11.5 10.5,9 8.5,7.5 11,7.5" fill="#FFE27A"/>
    </svg>""",

    "calendar": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="3" y="4" width="18" height="18" rx="3" fill="rgba(2,239,255,0.08)" stroke="#02EFFF" stroke-width="2"/>
        <path d="M16 2V6" stroke="#00FF87" stroke-width="2" stroke-linecap="round"/>
        <path d="M8 2V6" stroke="#00FF87" stroke-width="2" stroke-linecap="round"/>
        <path d="M3 10H21" stroke="#02EFFF" stroke-width="1.8"/>
        <circle cx="8" cy="14" r="1.2" fill="#00FF87"/>
        <circle cx="12" cy="14" r="1.2" fill="#00FF87"/>
        <circle cx="16" cy="14" r="1.2" fill="#00FF87"/>
        <circle cx="8" cy="18" r="1.2" fill="#02EFFF"/>
        <circle cx="12" cy="18" r="1.2" fill="#02EFFF"/>
        <circle cx="16" cy="18" r="1.2" fill="#02EFFF"/>
    </svg>""",

    "users": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M16 21V19C16 16.79 14.21 15 12 15H6C3.79 15 2 16.79 2 19V21" stroke="#00FF87" stroke-width="2" stroke-linecap="round"/>
        <circle cx="9" cy="7" r="4" fill="rgba(0,255,135,0.15)" stroke="#00FF87" stroke-width="2"/>
        <path d="M22 21V19C21.99 17.18 20.73 15.61 19 15.13" stroke="#02EFFF" stroke-width="2" stroke-linecap="round"/>
        <path d="M16 3.13C17.74 3.61 19 5.18 19 7C19 8.82 17.74 10.39 16 10.87" stroke="#02EFFF" stroke-width="2" stroke-linecap="round"/>
    </svg>""",

    "lightning": """<svg width="18" height="18" viewBox="0 0 24 24" fill="#00FF87" xmlns="http://www.w3.org/2000/svg">
        <path d="M13 2L3 14H12L11 22L21 10H12L13 2Z" stroke="#00FF87" stroke-width="2" stroke-linejoin="round"/>
    </svg>""",

    "flame": """<svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M8.5 14.5A2.5 2.5 0 0 0 11 12C11 10.62 10.5 10 10 9C8.93 6.86 9.78 4.95 12 3C12.5 5.5 14 7.9 16 9.5C18 11.1 19 13 19 15A7 7 0 1 1 5 15C5 13.85 5.43 12.71 6 12A2.5 2.5 0 0 0 8.5 14.5Z" fill="rgba(0,255,135,0.18)" stroke="#00FF87" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>""",

    "chart": """<svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <line x1="18" y1="20" x2="18" y2="10" stroke="#02EFFF" stroke-width="2.5" stroke-linecap="round"/>
        <line x1="12" y1="20" x2="12" y2="4" stroke="#00FF87" stroke-width="2.5" stroke-linecap="round"/>
        <line x1="6" y1="20" x2="6" y2="14" stroke="#FFE27A" stroke-width="2.5" stroke-linecap="round"/>
        <path d="M2 20H22" stroke="rgba(255,255,255,0.3)" stroke-width="2" stroke-linecap="round"/>
        <path d="M4 11L10 6L14 9L20 3" stroke="#02EFFF" stroke-width="1.8" stroke-dasharray="2 2"/>
    </svg>""",

    "crown": """<svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M2 4L5 16H19L22 4L16 11L12 4L8 11L2 4Z" fill="rgba(233,0,82,0.2)" stroke="#E90052" stroke-width="2" stroke-linejoin="round"/>
        <rect x="4" y="18" width="16" height="3" rx="1.5" fill="#E90052"/>
        <circle cx="12" cy="3" r="1.5" fill="#FFE27A"/>
        <circle cx="2" cy="3" r="1.5" fill="#FFE27A"/>
        <circle cx="22" cy="3" r="1.5" fill="#FFE27A"/>
    </svg>""",

    "shield": """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 22C12 22 20 18 20 12V5L12 2L4 5V12C4 18 12 22 12 22Z" fill="rgba(0,255,135,0.1)" stroke="#00FF87" stroke-width="2" stroke-linejoin="round"/>
    </svg>""",

    "search": """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="11" cy="11" r="7" stroke="#00FF87" stroke-width="2"/>
        <path d="M20 20L16 16" stroke="#00FF87" stroke-width="2.5" stroke-linecap="round"/>
    </svg>""",

    "info": """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="12" cy="12" r="10" stroke="#02EFFF" stroke-width="2"/>
        <path d="M12 16V12" stroke="#02EFFF" stroke-width="2" stroke-linecap="round"/>
        <circle cx="12" cy="8" r="1" fill="#02EFFF"/>
    </svg>""",

    "jersey_gk": """<svg width="24" height="24" viewBox="0 0 24 24" fill="#ECC94B"><path d="M6 2L2 8L6 10V22H18V10L22 8L18 2H14C14 3.1 13.1 4 12 4C10.9 4 10 3.1 10 2H6Z"/></svg>""",
    "jersey_def": """<svg width="24" height="24" viewBox="0 0 24 24" fill="#4299E1"><path d="M6 2L2 8L6 10V22H18V10L22 8L18 2H14C14 3.1 13.1 4 12 4C10.9 4 10 3.1 10 2H6Z"/></svg>""",
    "jersey_mid": """<svg width="24" height="24" viewBox="0 0 24 24" fill="#48BB78"><path d="M6 2L2 8L6 10V22H18V10L22 8L18 2H14C14 3.1 13.1 4 12 4C10.9 4 10 3.1 10 2H6Z"/></svg>""",
    "jersey_fwd": """<svg width="24" height="24" viewBox="0 0 24 24" fill="#F56565"><path d="M6 2L2 8L6 10V22H18V10L22 8L18 2H14C14 3.1 13.1 4 12 4C10.9 4 10 3.1 10 2H6Z"/></svg>"""
}

# ----------------- LUXURY STYLING & CSS -----------------
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@600;700;800&display=swap" rel="stylesheet">

<style>
    :root {
        --pl-purple: #37003c;
        --pl-purple-dark: #120017;
        --pl-green: #00ff87;
        --pl-cyan: #02efff;
        --pl-pink: #e90052;
        --gold: #ffd700;
        --bg-dark: #07090e;
        --card-bg: rgba(255, 255, 255, 0.032);
        --card-border: rgba(255, 255, 255, 0.08);
        --text-muted: #8c9ba5;
    }

    html, body, [class*="css"], .stMarkdown, .stText {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Overall Dark Stadium Atmosphere */
    [data-testid="stAppViewContainer"] > .main {
        background:
            radial-gradient(ellipse 800px 450px at 10% -5%, rgba(0, 255, 135, 0.09) 0%, transparent 60%),
            radial-gradient(ellipse 800px 450px at 90% -5%, rgba(2, 239, 255, 0.07) 0%, transparent 60%),
            radial-gradient(circle at 50% 100%, #0d121c 0%, var(--bg-dark) 60%);
    }

    /* Ultra-Refined Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1118 0%, #080a0f 100%);
        border-right: 1px solid var(--card-border);
    }
    section[data-testid="stSidebar"] .stMarkdown, section[data-testid="stSidebar"] label {
        color: #d1d8e0 !important;
        font-weight: 600;
    }

    /* Sidebar Brand Card - Sharp Angular Cut */
    .sidebar-brand-card {
        background: linear-gradient(135deg, rgba(55, 0, 60, 0.7) 0%, rgba(20, 0, 25, 0.85) 100%);
        border: 1px solid rgba(0, 255, 135, 0.35);
        clip-path: polygon(0 0, 100% 0, 100% calc(100% - 16px), calc(100% - 16px) 100%, 0 100%);
        padding: 18px;
        margin-bottom: 20px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
        display: flex;
        align-items: center;
        gap: 14px;
        position: relative;
    }
    .brand-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.3rem;
        font-weight: 800;
        letter-spacing: -0.3px;
        background: linear-gradient(90deg, #FFFFFF 0%, #00FF87 70%, #02EFFF 100%);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.2;
    }
    .brand-sub {
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        color: rgba(255, 255, 255, 0.65);
        margin-top: 2px;
        font-weight: 600;
    }

    /* Custom Input Section Card */
    .sidebar-section-header {
        display: flex;
        align-items: center;
        gap: 8px;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 0.88rem;
        font-weight: 700;
        color: #F0F4F8;
        margin-bottom: 6px;
        margin-top: 14px;
    }

    /* Action Button - Sharp Angular Chamfered Cut */
    div.stButton > button[kind="primary"], div.stDownloadButton > button {
        background: linear-gradient(135deg, #00FF87 0%, #02EFFF 100%) !important;
        color: #0b0f17 !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 800 !important;
        font-size: 0.94rem !important;
        letter-spacing: 0.5px !important;
        border: none !important;
        border-radius: 0px !important;
        clip-path: polygon(10px 0, 100% 0, calc(100% - 10px) 100%, 0 100%) !important;
        padding: 12px 24px !important;
        box-shadow: 0 4px 20px rgba(0, 255, 135, 0.35) !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
    }
    div.stButton > button[kind="primary"]:hover, div.stDownloadButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 28px rgba(0, 255, 135, 0.55) !important;
        background: linear-gradient(135deg, #02EFFF 0%, #00FF87 100%) !important;
    }

    /* Top-Right 3-Dots Kebab Popover Button */
    div[data-testid="stPopover"] > button {
        background: rgba(255, 255, 255, 0.04) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(0, 255, 135, 0.35) !important;
        border-radius: 14px !important;
        color: #00FF87 !important;
        font-size: 1.6rem !important;
        font-weight: 900 !important;
        padding: 14px 18px !important;
        line-height: 1 !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 18px rgba(0, 0, 0, 0.3) !important;
    }
    div[data-testid="stPopover"] > button:hover {
        background: rgba(55, 0, 60, 0.6) !important;
        border-color: #00FF87 !important;
        box-shadow: 0 0 20px rgba(0, 255, 135, 0.4) !important;
        transform: scale(1.05) !important;
    }
    div[data-testid="stPopoverBody"] {
        background: #0f141d !important;
        border: 1px solid rgba(0, 255, 135, 0.25) !important;
        border-radius: 16px !important;
        box-shadow: 0 16px 40px rgba(0, 0, 0, 0.6) !important;
        padding: 18px !important;
    }

    /* Top Hero Banner - Sharp Faceted Cut Corners */
    .hero-banner {
        background: linear-gradient(135deg, #160022 0%, #2e0034 45%, #12001a 100%);
        border: 1px solid rgba(0, 255, 135, 0.35);
        border-bottom: 3px solid rgba(255, 215, 0, 0.7);
        border-radius: 0px;
        clip-path: polygon(0 0, calc(100% - 22px) 0, 100% 22px, 100% 100%, 22px 100%, 0 calc(100% - 22px));
        padding: 26px 32px;
        margin-bottom: 25px;
        box-shadow: 0 14px 40px rgba(0, 0, 0, 0.45);
        position: relative;
        overflow: hidden;
    }
    .hero-banner::before {
        content: "";
        position: absolute;
        top: -60%;
        right: -10%;
        width: 420px;
        height: 420px;
        background: radial-gradient(circle, rgba(0, 255, 135, 0.16) 0%, rgba(2, 239, 255, 0.06) 50%, transparent 75%);
        border-radius: 50%;
        pointer-events: none;
    }
    .hero-header-row {
        display: flex;
        align-items: center;
        gap: 18px;
        position: relative;
        z-index: 1;
    }
    .hero-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.35rem;
        font-weight: 800;
        background: linear-gradient(90deg, #FFFFFF 0%, #00FF87 60%, #02EFFF 100%);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        letter-spacing: -0.5px;
        line-height: 1.15;
    }
    .hero-subtitle {
        color: rgba(255, 255, 255, 0.85);
        font-size: 1.02rem;
        margin-top: 5px;
        font-weight: 500;
    }
    .hero-badge-container {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 16px;
        position: relative;
        z-index: 1;
    }
    .hero-badge {
        background: rgba(255, 255, 255, 0.06);
        -webkit-backdrop-filter: blur(12px);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.16);
        clip-path: polygon(8px 0, 100% 0, calc(100% - 8px) 100%, 0 100%);
        color: #FFFFFF;
        padding: 6px 16px;
        font-size: 0.84rem;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 7px;
    }
    .hero-badge-accent {
        background: linear-gradient(90deg, #00FF87 0%, #02EFFF 100%);
        color: #0b0f17 !important;
        font-weight: 800;
        border: none;
    }

    /* KPI Stat Cards - Sharp Chamfered Corners */
    .kpi-card {
        background: var(--card-bg);
        -webkit-backdrop-filter: blur(14px);
        backdrop-filter: blur(14px);
        clip-path: polygon(0 0, calc(100% - 14px) 0, 100% 14px, 100% 100%, 0 100%);
        padding: 20px 22px;
        border: 1px solid var(--card-border);
        box-shadow: 0 6px 24px rgba(0, 0, 0, 0.25);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        position: relative;
    }
    .kpi-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 32px rgba(0, 0, 0, 0.4);
        border-color: rgba(0, 255, 135, 0.4);
    }
    .kpi-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 8px;
    }
    .kpi-label {
        font-size: 0.76rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: var(--text-muted);
        font-weight: 700;
    }
    .kpi-value {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.65rem;
        font-weight: 800;
        color: #FFFFFF;
        margin: 0;
        line-height: 1.2;
    }
    .kpi-subtext {
        font-size: 0.82rem;
        color: #A0AEC0;
        margin-top: 6px;
        font-weight: 500;
    }
    .kpi-accent-purple { border-left: 4px solid #00FF87; }
    .kpi-accent-green  { border-left: 4px solid #02EFFF; }
    .kpi-accent-pink   { border-left: 4px solid #E90052; }
    .kpi-accent-cyan   { border-left: 4px solid #FFE27A; }

    /* Modern Sharp Segmented Tabs Bar */
    div[data-baseweb="tab-highlight"], div[data-baseweb="tab-border"] {
        display: none !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px !important;
        background: rgba(15, 20, 30, 0.85) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        backdrop-filter: blur(16px) !important;
        padding: 6px !important;
        border-radius: 0px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        clip-path: polygon(0 0, 100% 0, 100% calc(100% - 10px), calc(100% - 10px) 100%, 0 100%);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3) !important;
        margin-bottom: 24px !important;
        display: flex !important;
        flex-wrap: wrap !important;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 9px 20px !important;
        border-radius: 0px !important;
        clip-path: polygon(8px 0, 100% 0, calc(100% - 8px) 100%, 0 100%) !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.88rem !important;
        color: #8C9BA5 !important;
        border: none !important;
        background: transparent !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #FFFFFF !important;
        background: rgba(255, 255, 255, 0.08) !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #37003c 0%, #1f0024 100%) !important;
        color: #00FF87 !important;
        border: 1px solid rgba(0, 255, 135, 0.45) !important;
        box-shadow: 0 4px 16px rgba(0, 255, 135, 0.22) !important;
    }

    /* Pitch Card Visualizer - Sharp Tactical Hexagonal Style */
    .pitch-container {
        background: linear-gradient(180deg, #14441e 0%, #0d2e14 100%);
        border: 2px solid #236932;
        border-radius: 0px;
        clip-path: polygon(0 0, calc(100% - 16px) 0, 100% 16px, 100% 100%, 16px 100%, 0 calc(100% - 16px));
        padding: 22px;
        box-shadow: inset 0 0 50px rgba(0,0,0,0.45);
        margin: 15px 0;
        color: white;
    }
    .pitch-row {
        display: flex;
        justify-content: space-around;
        align-items: center;
        margin-bottom: 18px;
    }
    .player-card {
        background: rgba(20, 26, 36, 0.96);
        color: #FFFFFF;
        border-radius: 0px;
        clip-path: polygon(0 0, calc(100% - 8px) 0, 100% 8px, 100% 100%, 0 100%);
        padding: 8px 12px;
        text-align: center;
        box-shadow: 0 4px 14px rgba(0,0,0,0.35);
        border: 1px solid rgba(255,255,255,0.12);
        min-width: 96px;
        font-size: 0.82rem;
        position: relative;
        transition: transform 0.15s ease;
    }
    .player-card:hover {
        transform: scale(1.05);
        border-color: #00FF87;
    }
    .player-card-cap {
        border: 1.5px solid #FFD700;
        background: rgba(36, 30, 10, 0.96);
        box-shadow: 0 0 16px rgba(255, 215, 0, 0.5);
    }
    .player-name {
        font-weight: 700;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .player-team {
        color: #98A2B3;
        font-size: 0.73rem;
        font-weight: 600;
        margin-top: 2px;
    }
    .badge-c {
        position: absolute;
        top: -8px;
        right: -8px;
        background: #FFD700;
        color: #000;
        font-weight: 800;
        clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
        width: 22px;
        height: 22px;
        font-size: 0.72rem;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 2px 6px rgba(0,0,0,0.4);
    }
    .badge-vc {
        position: absolute;
        top: -8px;
        right: -8px;
        background: #E2E8F0;
        color: #1A202C;
        font-weight: 800;
        clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
        width: 22px;
        height: 22px;
        font-size: 0.68rem;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 2px 6px rgba(0,0,0,0.4);
    }

    /* Rank Badges - Sharp Hexagon Shield */
    .rank-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 28px;
        height: 28px;
        clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 800;
        font-size: 0.82rem;
        background: rgba(255, 255, 255, 0.08);
        color: #eef2f6;
    }
    .rank-badge.gold {
        background: linear-gradient(135deg, #ffe27a, #d4a017);
        color: #241a00;
        border: none;
        box-shadow: 0 0 12px rgba(255, 215, 0, 0.5);
    }
    .rank-badge.silver {
        background: linear-gradient(135deg, #f1f1f4, #a7abb3);
        color: #1a1a1a;
        border: none;
        box-shadow: 0 0 10px rgba(200, 200, 210, 0.4);
    }
    .rank-badge.bronze {
        background: linear-gradient(135deg, #e0a469, #9c5a26);
        color: #2a1200;
        border: none;
        box-shadow: 0 0 10px rgba(205, 127, 50, 0.4);
    }

    .move-chip {
        display: inline-flex;
        align-items: center;
        gap: 3px;
        font-size: 0.74rem;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 999px;
    }
    .move-chip.up { color: #00FF87; background: rgba(0, 255, 135, 0.12); }
    .move-chip.down { color: #ff6b85; background: rgba(255, 107, 133, 0.12); }
    .move-chip.flat { color: var(--text-muted); background: rgba(255, 255, 255, 0.05); }

    .std-team { font-weight: 700; color: #F5F7FA; }
    .std-manager { font-size: 0.75rem; color: var(--text-muted); margin-top: 1px; }
    .std-points { font-family: 'Space Grotesk', sans-serif; font-weight: 700; color: #00FF87; }
    .std-total { font-family: 'Space Grotesk', sans-serif; font-weight: 700; color: #F5F7FA; }
    .std-chip-tag {
        font-size: 0.68rem;
        font-weight: 700;
        padding: 2px 9px;
        border-radius: 999px;
        background: rgba(2, 239, 255, 0.12);
        color: #02EFFF;
        border: 1px solid rgba(2, 239, 255, 0.3);
    }
    .std-muted { color: var(--text-muted); }
    .std-hit { color: #ff8a8a; font-weight: 600; }
    .std-col-head {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.7px;
        color: var(--text-muted);
        font-weight: 700;
    }

    div[class*="st-key-mgrrow_"] {
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        transition: background 0.12s ease;
    }
    div[class*="st-key-mgrrow_"]:hover { background: rgba(255, 255, 255, 0.035); }
    div[class*="st-key-mgrrow_"] .stButton > button {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: #F5F7FA !important;
        text-align: left !important;
        justify-content: flex-start !important;
        padding: 6px 4px !important;
        font-weight: 700 !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    div[class*="st-key-mgrrow_"] .stButton > button:hover {
        color: #00FF87 !important;
        text-decoration: underline;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- LOCAL SNAPSHOT STORAGE (SQLITE) -----------------
DB_PATH = "fpl_data.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS league_snapshots (
            league_id INTEGER,
            gameweek INTEGER,
            league_name TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            data_json TEXT,
            PRIMARY KEY (league_id, gameweek)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS paid_league_settings (
            league_id INTEGER PRIMARY KEY,
            fee_per_person INTEGER,
            paid_entry_ids TEXT,
            prize_p1 INTEGER,
            prize_p2 INTEGER,
            prize_p3 INTEGER
        )
    """)
    conn.commit()
    conn.close()

def get_paid_league_settings(league_id: int):
    try:
        init_db()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT fee_per_person, paid_entry_ids, prize_p1, prize_p2, prize_p3 FROM paid_league_settings WHERE league_id = ?", (league_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            fee, ids_json, p1, p2, p3 = row
            return {
                "fee": fee if fee is not None else 50000,
                "paid_entry_ids": json.loads(ids_json) if ids_json else [],
                "p1": p1 or 50,
                "p2": p2 or 30,
                "p3": p3 or 20
            }
    except Exception:
        pass
    return {"fee": 50000, "paid_entry_ids": [], "p1": 50, "p2": 30, "p3": 20}

def save_paid_league_settings(league_id: int, fee: int, paid_entry_ids: list, p1: int = 50, p2: int = 30, p3: int = 20):
    try:
        init_db()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO paid_league_settings (league_id, fee_per_person, paid_entry_ids, prize_p1, prize_p2, prize_p3)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (league_id, fee, json.dumps(paid_entry_ids), p1, p2, p3))
        conn.commit()
        conn.close()
    except Exception:
        pass

def save_snapshot_to_db(league_id: int, gameweek: int, league_name: str, data: dict):
    try:
        init_db()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        clean_data = {
            "league_info": data.get("league_info"),
            "gameweek": data.get("gameweek"),
            "total_managers": data.get("total_managers"),
            "raw_standings": data.get("raw_standings", [])
        }
        json_str = json.dumps(clean_data, default=str)
        cursor.execute("""
            INSERT OR REPLACE INTO league_snapshots (league_id, gameweek, league_name, data_json)
            VALUES (?, ?, ?, ?)
        """, (league_id, gameweek, league_name, json_str))
        conn.commit()
        conn.close()
    except Exception:
        pass

init_db()

@st.cache_resource
def get_api_client():
    return FPLApiClient()

@st.cache_data(ttl=300, show_spinner=False)
def load_league_data(league_id: int, gameweek: int, max_entries: int):
    api = FPLApiClient()
    analyzer = FPLMiniLeagueAnalyzer(api)
    data = analyzer.fetch_full_league_data(league_id=league_id, gameweek=gameweek, max_entries=max_entries)
    save_snapshot_to_db(league_id, gameweek, data.get("league_info", {}).get("name", ""), data)
    return data

# ----------------- SHARED SQUAD PITCH RENDERER -----------------
def render_pitch_html(squad_items):
    starters = [p for p in squad_items if p.get("is_starting")]
    bench = [p for p in squad_items if not p.get("is_starting")]

    gks = [p for p in starters if p["position"] == "GKP"]
    defs = [p for p in starters if p["position"] == "DEF"]
    mids = [p for p in starters if p["position"] == "MID"]
    fwds = [p for p in starters if p["position"] == "FWD"]

    def make_card(p, bench_card=False):
        cap_html = ''
        cap_class = ''
        if p.get("is_captain"):
            cap_html = '<div class="badge-c">C</div>'
            cap_class = ' player-card-cap'
        elif p.get("is_vice_captain"):
            cap_html = '<div class="badge-vc">V</div>'
        pos = p.get("position")
        jersey_svg = SVG_ICONS.get(f"jersey_{pos.lower()}", "") if pos else ""
        opacity_style = ' style="opacity: 0.88;"' if bench_card else ''
        team_suffix = " (B)" if bench_card else f" • £{p.get('now_cost', 0):.1f}m"
        card = f'<div class="player-card{cap_class}"{opacity_style}>'
        card += cap_html
        card += f'<div style="display: flex; justify-content: center; margin-bottom: 2px;">{jersey_svg}</div>'
        card += f'<div class="player-name">{p["web_name"]}</div>'
        card += f'<div class="player-team">{p["team_short"]}{team_suffix}</div>'
        card += '</div>'
        return card

    out = '<div class="pitch-container">'
    out += '<div class="pitch-row">' + "".join(make_card(p) for p in gks) + '</div>'
    out += '<div class="pitch-row">' + "".join(make_card(p) for p in defs) + '</div>'
    out += '<div class="pitch-row">' + "".join(make_card(p) for p in mids) + '</div>'
    out += '<div class="pitch-row">' + "".join(make_card(p) for p in fwds) + '</div>'
    out += '</div>'

    out += '<div style="background: rgba(0,0,0,0.28); border: 1px dashed rgba(255,255,255,0.15); border-radius: 10px; padding: 10px; display: flex; justify-content: space-around; position: relative; z-index: 1;">'
    out += "".join(make_card(p, bench_card=True) for p in bench)
    out += '</div>'
    return out

_MD_SPECIAL = re.compile(r'([!"#$%&\'()*+,\-./:;<=>?@\[\\\]^_`{|}~])')
def _md_escape(text):
    return _MD_SPECIAL.sub(r'\\\1', str(text))

# ----------------- MANAGER DETAIL CARD (DIALOG) -----------------
@st.dialog("📋 Detail Manajer", width="large")
def show_manager_dialog(row, chips_df):
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 14px; margin-bottom: 6px;">
        <span class="rank-badge {({1: "gold", 2: "silver", 3: "bronze"}.get(int(row["Rank"]), ""))}" style="width: 40px; height: 40px; font-size: 1.1rem;">{int(row["Rank"])}</span>
        <div>
            <div style="font-family: 'Space Grotesk', sans-serif; font-weight: 800; font-size: 1.3rem; color: #F5F7FA;">{html.escape(str(row["Team Name"]))}</div>
            <div style="color: var(--text-muted); font-size: 0.9rem;">{html.escape(str(row["Manager"]))}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Poin GW", f'{row.get("GW Points", 0)}')
    c2.metric("Total Poin", f'{row.get("Total Points", 0)}')
    overall_rank = row.get("Overall Rank", "-")
    c3.metric("Rank Dunia", f"{overall_rank:,}" if isinstance(overall_rank, (int, float)) else str(overall_rank))
    c4.metric("Nilai Tim", f'£{row.get("Team Value (£m)", 0):.1f}m')

    c5, c6, c7 = st.columns(3)
    c5.metric("Bench Poin", f'{row.get("Bench Points", 0)}')
    c6.metric("Transfer", f'{row.get("Transfers", 0)}')
    hits = row.get("Transfer Cost", 0) or 0
    c7.metric("Hits", f'-{hits} pts' if hits else "0 pts")

    st.markdown(f"👑 **Kapten:** {html.escape(str(row.get('Captain', '-')))} &nbsp;|&nbsp; 🅥 **Wakil Kapten:** {html.escape(str(row.get('Vice Captain', '-')))}", unsafe_allow_html=True)

    active_chip = row.get("Active Chip", "-")
    if active_chip and active_chip != "-":
        st.markdown(f'<span class="std-chip-tag">🃏 Chip aktif GW ini: {html.escape(str(active_chip))}</span>', unsafe_allow_html=True)

    st.markdown("---")
    squad = row.get("squad", [])
    if squad:
        st.markdown("##### 🧑‍🤝‍🧑 Susunan Pemain")
        st.markdown(render_pitch_html(squad), unsafe_allow_html=True)
    else:
        st.info("Susunan pemain belum tersedia untuk gameweek ini.")

# ----------------- SIDEBAR CONTROLS -----------------
st.sidebar.markdown(f"""
<div class="sidebar-brand-card">
    {SVG_ICONS['fpl_crest']}
    <div>
        <div class="brand-title">FPL MASTERCLASS</div>
        <div class="brand-sub">PREMIER LEAGUE INTELLIGENCE</div>
    </div>
</div>
""", unsafe_allow_html=True)

api = get_api_client()
current_gw = api.get_current_gameweek()

# Custom Vector Section: League ID
st.sidebar.markdown(f"""
<div class="sidebar-section-header">
    {SVG_ICONS['trophy']}
    <span>League ID FPL</span>
</div>
""", unsafe_allow_html=True)

league_id_input = st.sidebar.number_input(
    "League ID FPL",
    min_value=1,
    value=1004418,
    step=1,
    label_visibility="collapsed",
    help="ID angka yang ada di URL klasemen Mini-League Anda (contoh: fantasy.premierleague.com/leagues/1004418/standings/c)"
)

# Custom Vector Section: Gameweek
st.sidebar.markdown(f"""
<div class="sidebar-section-header">
    {SVG_ICONS['calendar']}
    <span>Pilih Gameweek (GW)</span>
</div>
""", unsafe_allow_html=True)

selected_gw = st.sidebar.slider(
    "Pilih Gameweek (GW)",
    min_value=1,
    max_value=38,
    value=current_gw,
    label_visibility="collapsed",
    help="Gameweek yang ingin dianalisis."
)

# Custom Vector Section: Max Managers
st.sidebar.markdown(f"""
<div class="sidebar-section-header">
    {SVG_ICONS['users']}
    <span>Maksimal Manajer</span>
</div>
""", unsafe_allow_html=True)

max_managers = st.sidebar.selectbox(
    "Maksimal Manajer",
    options=[25, 50, 100, 250, 500],
    index=1,
    label_visibility="collapsed",
    help="Batasi untuk mempercepat loading jika liga beranggotakan banyak manajer."
)

st.sidebar.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)
fetch_btn = st.sidebar.button("⚡ TARIK & ANALISIS DATA", type="primary", use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.markdown(f"""
<div style="display: flex; align-items: center; gap: 8px; margin: 4px 0 6px;">
    {SVG_ICONS['info']}
    <span style="font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 0.95rem; color: #F5F7FA;">Cara Mencari League ID</span>
</div>
""", unsafe_allow_html=True)
st.sidebar.caption(
    "1. Buka [fantasy.premierleague.com](https://fantasy.premierleague.com)\n"
    "2. Masuk ke menu **Leagues & Cups** -> Pilih Liga Anda\n"
    "3. Angka di URL address bar browser adalah League ID:\n"
    "`/leagues/{LEAGUE_ID}/standings/c`"
)

# ----------------- MAIN APP EXECUTION -----------------
if fetch_btn:
    load_league_data.clear()

with st.spinner(f"✨ Menghubungi FPL API untuk League #{league_id_input} (GW{selected_gw})..."):
    try:
        data = load_league_data(league_id=league_id_input, gameweek=selected_gw, max_entries=max_managers)
    except Exception as e:
        st.error(f"⚠️ Gagal mengambil data liga: {e}. Pastikan League ID benar dan koneksi internet aktif.")
        st.stop()

if fetch_btn:
    st.toast("✅ Data berhasil ditarik ulang dari FPL API.", icon="⚡")

league_info = data.get("league_info", {})
league_name = league_info.get("name", f"League #{league_id_input}")
total_managers = data.get("total_managers", 0)

# ----------------- PREPARE EXPORT BUFFERS -----------------
standings_df = data.get("standings_df", pd.DataFrame())
ownership_df = data.get("ownership_df", pd.DataFrame())
captaincy_df = data.get("captaincy_df", pd.DataFrame())
chips_df = data.get("chips_df", pd.DataFrame())
history_df = data.get("history_df", pd.DataFrame())

excel_buffer = BytesIO()
with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
    standings_clean = standings_df.drop(columns=[c for c in ["entry_id", "squad"] if c in standings_df.columns])
    standings_clean.to_excel(writer, sheet_name="Standings", index=False)
    if not ownership_df.empty:
        ownership_df.to_excel(writer, sheet_name="Ownership_EO", index=False)
    if not captaincy_df.empty:
        captaincy_df.to_excel(writer, sheet_name="Captains", index=False)
    if not chips_df.empty:
        chips_df.to_excel(writer, sheet_name="Chips", index=False)
    if not history_df.empty:
        history_df.to_excel(writer, sheet_name="GW_History", index=False)

excel_data_bytes = excel_buffer.getvalue()
csv_data_bytes = standings_df.drop(columns=[c for c in ["entry_id", "squad"] if c in standings_df.columns]).to_csv(index=False).encode('utf-8')

# ----------------- SIDEBAR EXPORT SECTION -----------------
st.sidebar.markdown("---")
st.sidebar.markdown(f"""
<div class="sidebar-section-header">
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M21 15V19C21 20.1 20.1 21 19 21H5C3.9 21 3 20.1 3 19V15" stroke="#00FF87" stroke-width="2" stroke-linecap="round"/>
        <path d="M7 10L12 15L17 10" stroke="#00FF87" stroke-width="2" stroke-linecap="round"/>
        <path d="M12 15V3" stroke="#00FF87" stroke-width="2" stroke-linecap="round"/>
    </svg>
    <span>Ekspor Laporan</span>
</div>
""", unsafe_allow_html=True)

st.sidebar.download_button(
    label="📊 Download Excel (.xlsx)",
    data=excel_data_bytes,
    file_name=f"FPL_Report_{league_id_input}_GW{selected_gw}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True
)

st.sidebar.download_button(
    label="📄 Download CSV",
    data=csv_data_bytes,
    file_name=f"FPL_Standings_{league_id_input}_GW{selected_gw}.csv",
    mime="text/csv",
    use_container_width=True
)

# ----------------- SIDEBAR PENGATURAN LIGA IURAN -----------------
paid_settings = get_paid_league_settings(league_id_input)
all_mgr_dict = {int(row["entry_id"]): f"{row['Team Name']} ({row['Manager']})" for _, row in standings_df.iterrows()} if not standings_df.empty else {}

st.sidebar.markdown("---")
with st.sidebar.expander("💰 Pengaturan Liga Iuran", expanded=False):
    st.caption("Pilih manajer yang ikut iuran & atur nominal:")
    
    saved_ids = [int(eid) for eid in paid_settings.get("paid_entry_ids", []) if int(eid) in all_mgr_dict]
    
    selected_paid_ids = st.multiselect(
        "Peserta yang Ikut Iuran:",
        options=list(all_mgr_dict.keys()),
        default=saved_ids,
        format_func=lambda eid: all_mgr_dict.get(eid, f"ID {eid}"),
        key=f"paid_mgr_select_{league_id_input}",
        help="Pilih manajer yang sudah membayar iuran"
    )
    
    fee_val = st.number_input(
        "Biaya Iuran per Orang (Rp):",
        min_value=0,
        value=int(paid_settings.get("fee", 50000)),
        step=10000,
        key=f"fee_val_{league_id_input}"
    )
    
    if st.button("💾 SIMPAN PESERTA IURAN", use_container_width=True, type="secondary"):
        save_paid_league_settings(league_id_input, fee_val, selected_paid_ids, paid_settings.get("p1", 50), paid_settings.get("p2", 30), paid_settings.get("p3", 20))
        st.toast(f"✅ Tersimpan! {len(selected_paid_ids)} peserta terdaftar di Liga Iuran.", icon="💰")
        st.rerun()

# ----------------- HERO BANNER -----------------
st.markdown(f"""
<div class="hero-banner">
    <div class="hero-header-row">
        {SVG_ICONS['fpl_crest']}
        <div>
            <h1 class="hero-title">{league_name}</h1>
            <div class="hero-subtitle">Premier League Intelligence & Live Analytics Suite</div>
        </div>
    </div>
    <div class="hero-badge-container">
        <span class="hero-badge hero-badge-accent">{SVG_ICONS['shield']} League #{league_id_input}</span>
        <span class="hero-badge">{SVG_ICONS['users']} {total_managers} Manajer</span>
        <span class="hero-badge">{SVG_ICONS['calendar']} Gameweek {selected_gw}</span>
        <span class="hero-badge" style="border-color: rgba(0,255,135,0.4); color: #00FF87;">● Live API Sync</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ----------------- TOP METRIC CARDS -----------------
standings_df = data.get("standings_df", pd.DataFrame())
if not standings_df.empty:
    leader = standings_df.iloc[0]
    top_gw_scorer = standings_df.sort_values(by="GW Points", ascending=False).iloc[0]
    avg_gw_pts = standings_df["GW Points"].mean()
    cap_top = data["captaincy_df"].iloc[0]["Captain"] if not data["captaincy_df"].empty else "-"
    cap_pct = data["captaincy_df"].iloc[0]["% of League"] if not data["captaincy_df"].empty else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="kpi-card kpi-accent-purple">
            <div class="kpi-header">
                <span class="kpi-label">Leaderboard #1</span>
                {SVG_ICONS['trophy']}
            </div>
            <div class="kpi-value">{leader['Team Name']}</div>
            <div class="kpi-subtext"><b>{leader['Total Points']}</b> pts • {leader['Manager']}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="kpi-card kpi-accent-green">
            <div class="kpi-header">
                <span class="kpi-label">Top Scorer GW{selected_gw}</span>
                {SVG_ICONS['flame']}
            </div>
            <div class="kpi-value">{top_gw_scorer['Team Name']}</div>
            <div class="kpi-subtext"><b>{top_gw_scorer['GW Points']}</b> poin di GW ini</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="kpi-card kpi-accent-pink">
            <div class="kpi-header">
                <span class="kpi-label">Rata-Rata Liga</span>
                {SVG_ICONS['chart']}
            </div>
            <div class="kpi-value">{avg_gw_pts:.1f} <span style="font-size: 1rem; color: #8c9ba5;">pts</span></div>
            <div class="kpi-subtext">Rata-rata seluruh {total_managers} manajer</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="kpi-card kpi-accent-cyan">
            <div class="kpi-header">
                <span class="kpi-label">Top Captaincy</span>
                {SVG_ICONS['crown']}
            </div>
            <div class="kpi-value" style="font-size: 1.35rem;">{cap_top}</div>
            <div class="kpi-subtext">Dipilih oleh <b>{cap_pct}%</b> manajer</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 22px;'></div>", unsafe_allow_html=True)

# ----------------- ELEGANT TABS -----------------
tab1, tab_paid, tab2, tab3, tab4, tab5 = st.tabs([
    "Klasemen Liga", 
    "Klasemen Iuran", 
    "Tren & Performa", 
    "Kapten & EO", 
    "Pelacak Chip", 
    "Head-to-Head"
])

# ================= TAB 1: STANDINGS =================
with tab1:
    st.markdown("### 🏆 Klasemen Mini-League (Semua Peserta)")
    
    col_search, col_spacer = st.columns([2, 1])
    with col_search:
        search_query = st.text_input("🔍 Cari Manajer atau Nama Tim:", "", placeholder="Ketik nama tim / manajer...")
    
    display_df = standings_df.copy()
    if search_query:
        display_df = display_df[
            display_df["Team Name"].str.contains(search_query, case=False, na=False) |
            display_df["Manager"].str.contains(search_query, case=False, na=False)
        ]

    if not display_df.empty:
        # Table Header
        h_rank, h_move, h_team, h_mgr, h_gw, h_tot, h_or, h_cap, h_chip, h_hits, h_val = st.columns(
            [0.6, 0.7, 1.5, 1.3, 0.8, 0.9, 1.1, 1.6, 0.9, 0.7, 1.0]
        )
        h_rank.markdown('<div class="std-col-head">Rank</div>', unsafe_allow_html=True)
        h_move.markdown('<div class="std-col-head">Move</div>', unsafe_allow_html=True)
        h_team.markdown('<div class="std-col-head">Tim (Klik detail)</div>', unsafe_allow_html=True)
        h_mgr.markdown('<div class="std-col-head">Manajer</div>', unsafe_allow_html=True)
        h_gw.markdown('<div class="std-col-head">GW Pts</div>', unsafe_allow_html=True)
        h_tot.markdown('<div class="std-col-head">Total</div>', unsafe_allow_html=True)
        h_or.markdown('<div class="std-col-head">Overall</div>', unsafe_allow_html=True)
        h_cap.markdown('<div class="std-col-head">Kapten</div>', unsafe_allow_html=True)
        h_chip.markdown('<div class="std-col-head">Chip</div>', unsafe_allow_html=True)
        h_hits.markdown('<div class="std-col-head">Hits</div>', unsafe_allow_html=True)
        h_val.markdown('<div class="std-col-head">Nilai</div>', unsafe_allow_html=True)

        chips_data = data.get("chips_df")

        for _, row in display_df.iterrows():
            r_val = int(row["Rank"])
            med_cls = {1: "gold", 2: "silver", 3: "bronze"}.get(r_val, "")
            
            mv_str = str(row["Move"])
            if "▲" in mv_str or "+" in mv_str:
                mv_html = f'<span class="move-chip up">{html.escape(mv_str)}</span>'
            elif "▼" in mv_str or "-" in mv_str:
                mv_html = f'<span class="move-chip down">{html.escape(mv_str)}</span>'
            else:
                mv_html = f'<span class="move-chip flat">{html.escape(mv_str)}</span>'

            c_rank, c_move, c_team, c_mgr, c_gw, c_tot, c_or, c_cap, c_chip, c_hits, c_val = st.columns(
                [0.6, 0.7, 1.5, 1.3, 0.8, 0.9, 1.1, 1.6, 0.9, 0.7, 1.0]
            )

            c_rank.markdown(f'<div style="padding: 6px 0;"><span class="rank-badge {med_cls}">{r_val}</span></div>', unsafe_allow_html=True)
            c_move.markdown(f'<div style="padding: 6px 0;">{mv_html}</div>', unsafe_allow_html=True)

            btn_label = f"**{_md_escape(row['Team Name'])}**"
            if c_team.button(btn_label, key=f"mgrrow_{row['entry_id']}", help="Klik untuk membuka susunan squad & detail"):
                show_manager_dialog(row, chips_data)
            c_mgr.markdown(f'<div class="std-muted" style="padding: 10px 0; font-style: italic;">{html.escape(str(row["Manager"]))}</div>', unsafe_allow_html=True)

            c_gw.markdown(f'<div class="std-points" style="padding: 6px 0;">{row["GW Points"]}</div>', unsafe_allow_html=True)
            c_tot.markdown(f'<div class="std-total" style="padding: 6px 0;">{row["Total Points"]}</div>', unsafe_allow_html=True)
            
            or_val = row.get("Overall Rank", "-")
            or_fmt = f"{or_val:,}" if isinstance(or_val, (int, float)) else str(or_val)
            c_or.markdown(f'<div class="std-muted" style="padding: 6px 0; font-size: 0.8rem;">{or_fmt}</div>', unsafe_allow_html=True)

            c_cap.markdown(f'<div style="padding: 6px 0; font-size: 0.82rem; color: #E2E8F0;">{html.escape(str(row["Captain"]))}</div>', unsafe_allow_html=True)

            chip_val = str(row["Active Chip"])
            if chip_val and chip_val != "-":
                c_chip.markdown(f'<div style="padding: 6px 0;"><span class="std-chip-tag">{html.escape(chip_val)}</span></div>', unsafe_allow_html=True)
            else:
                c_chip.markdown('<div class="std-muted" style="padding: 6px 0;">-</div>', unsafe_allow_html=True)

            hits_val = row.get("Transfer Cost", 0) or 0
            if hits_val:
                c_hits.markdown(f'<div class="std-hit" style="padding: 6px 0;">-{hits_val}</div>', unsafe_allow_html=True)
            else:
                c_hits.markdown('<div class="std-muted" style="padding: 6px 0;">0</div>', unsafe_allow_html=True)

            c_val.markdown(f'<div class="std-muted" style="padding: 6px 0; font-size: 0.82rem;">£{row.get("Team Value (£m)", 0):.1f}m</div>', unsafe_allow_html=True)
    else:
        st.info("Belum ada data klasemen untuk ditampilkan.")

# ================= TAB PAID: KLASEMEN IURAN =================
with tab_paid:
    st.markdown("### 💰 Klasemen Khusus Liga Iuran")
    
    paid_ids_set = set(paid_settings.get("paid_entry_ids", []))
    paid_df = standings_df[standings_df["entry_id"].isin(paid_ids_set)].copy() if not standings_df.empty else pd.DataFrame()
    
    if paid_df.empty:
        st.info("💡 **Belum ada peserta yang dipilih untuk Liga Iuran.**\n\nSilakan buka menu **'💰 Pengaturan Liga Iuran'** di sidebar sebelah kiri untuk mencentang manajer yang sudah membayar iuran.")
    else:
        # Calculate Paid Rank
        paid_df = paid_df.sort_values(by=["Total Points", "GW Points"], ascending=[False, False]).reset_index(drop=True)
        paid_df["Paid_Rank"] = range(1, len(paid_df) + 1)
        
        # Prize Pool Stats
        fee_amount = int(paid_settings.get("fee", 50000))
        total_pool = len(paid_df) * fee_amount
        p1_cut = int(total_pool * paid_settings.get("p1", 50) / 100)
        p2_cut = int(total_pool * paid_settings.get("p2", 30) / 100)
        p3_cut = int(total_pool * paid_settings.get("p3", 20) / 100)
        
        pk1, pk2, pk3, pk4 = st.columns(4)
        with pk1:
            st.markdown(f"""
            <div class="kpi-card kpi-accent-purple">
                <div class="kpi-header">
                    <span class="kpi-label">Total Prize Pool</span>
                    {SVG_ICONS['trophy']}
                </div>
                <div class="kpi-value" style="font-size: 1.45rem;">Rp {total_pool:,.0f}</div>
                <div class="kpi-subtext">{len(paid_df)} Peserta • Rp {fee_amount:,.0f}/org</div>
            </div>
            """, unsafe_allow_html=True)
        with pk2:
            st.markdown(f"""
            <div class="kpi-card kpi-accent-green">
                <div class="kpi-header">
                    <span class="kpi-label">Juara 1 ({paid_settings.get('p1', 50)}%)</span>
                    <span class="rank-badge gold" style="width: 22px; height: 22px; font-size: 0.75rem;">1</span>
                </div>
                <div class="kpi-value" style="font-size: 1.45rem; color: #00FF87;">Rp {p1_cut:,.0f}</div>
                <div class="kpi-subtext">Estimasi Hadiah Peringkat 1</div>
            </div>
            """, unsafe_allow_html=True)
        with pk3:
            st.markdown(f"""
            <div class="kpi-card kpi-accent-cyan">
                <div class="kpi-header">
                    <span class="kpi-label">Juara 2 ({paid_settings.get('p2', 30)}%)</span>
                    <span class="rank-badge silver" style="width: 22px; height: 22px; font-size: 0.75rem;">2</span>
                </div>
                <div class="kpi-value" style="font-size: 1.45rem; color: #02EFFF;">Rp {p2_cut:,.0f}</div>
                <div class="kpi-subtext">Estimasi Hadiah Peringkat 2</div>
            </div>
            """, unsafe_allow_html=True)
        with pk4:
            st.markdown(f"""
            <div class="kpi-card kpi-accent-pink">
                <div class="kpi-header">
                    <span class="kpi-label">Juara 3 ({paid_settings.get('p3', 20)}%)</span>
                    <span class="rank-badge bronze" style="width: 22px; height: 22px; font-size: 0.75rem;">3</span>
                </div>
                <div class="kpi-value" style="font-size: 1.45rem; color: #E90052;">Rp {p3_cut:,.0f}</div>
                <div class="kpi-subtext">Estimasi Hadiah Peringkat 3</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<div style='margin-bottom: 18px;'></div>", unsafe_allow_html=True)
        
        # Search Filter for Paid Standings
        col_ps, col_pdl = st.columns([2, 1])
        with col_ps:
            paid_search = st.text_input("🔍 Cari Peserta Iuran:", "", placeholder="Ketik nama tim / manajer...", key="paid_search_input")
        
        display_paid_df = paid_df.copy()
        if paid_search:
            display_paid_df = display_paid_df[
                display_paid_df["Team Name"].str.contains(paid_search, case=False, na=False) |
                display_paid_df["Manager"].str.contains(paid_search, case=False, na=False)
            ]
        
        with col_pdl:
            paid_excel_buf = BytesIO()
            with pd.ExcelWriter(paid_excel_buf, engine="openpyxl") as writer:
                clean_paid = paid_df.drop(columns=[c for c in ["squad"] if c in paid_df.columns])
                clean_paid.to_excel(writer, sheet_name="Paid_Standings", index=False)
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            st.download_button(
                label="📊 Export Excel Iuran",
                data=paid_excel_buf.getvalue(),
                file_name=f"FPL_Paid_League_{league_id_input}_GW{selected_gw}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="dl_paid_excel",
                use_container_width=True
            )
        
        # Table Header
        h_prank, h_porg, h_pteam, h_pmgr, h_pgw, h_ptot, h_por, h_pcap, h_pchip, h_phits, h_pval = st.columns(
            [0.7, 0.6, 1.5, 1.3, 0.8, 0.9, 1.1, 1.6, 0.9, 0.7, 1.0]
        )
        h_prank.markdown('<div class="std-col-head">Rank Iuran</div>', unsafe_allow_html=True)
        h_porg.markdown('<div class="std-col-head">Rank Asli</div>', unsafe_allow_html=True)
        h_pteam.markdown('<div class="std-col-head">Tim (Klik detail)</div>', unsafe_allow_html=True)
        h_pmgr.markdown('<div class="std-col-head">Manajer</div>', unsafe_allow_html=True)
        h_pgw.markdown('<div class="std-col-head">GW Pts</div>', unsafe_allow_html=True)
        h_ptot.markdown('<div class="std-col-head">Total</div>', unsafe_allow_html=True)
        h_por.markdown('<div class="std-col-head">Overall</div>', unsafe_allow_html=True)
        h_pcap.markdown('<div class="std-col-head">Kapten</div>', unsafe_allow_html=True)
        h_pchip.markdown('<div class="std-col-head">Chip</div>', unsafe_allow_html=True)
        h_phits.markdown('<div class="std-col-head">Hits</div>', unsafe_allow_html=True)
        h_pval.markdown('<div class="std-col-head">Nilai</div>', unsafe_allow_html=True)
        
        chips_data = data.get("chips_df")
        
        for _, row in display_paid_df.iterrows():
            pr_val = int(row["Paid_Rank"])
            med_cls = {1: "gold", 2: "silver", 3: "bronze"}.get(pr_val, "")
            
            c_prank, c_porg, c_pteam, c_pmgr, c_pgw, c_ptot, c_por, c_pcap, c_pchip, c_phits, c_pval = st.columns(
                [0.7, 0.6, 1.5, 1.3, 0.8, 0.9, 1.1, 1.6, 0.9, 0.7, 1.0]
            )

            c_prank.markdown(f'<div style="padding: 6px 0;"><span class="rank-badge {med_cls}">{pr_val}</span></div>', unsafe_allow_html=True)
            c_porg.markdown(f'<div class="std-muted" style="padding: 6px 0; font-size: 0.82rem;">#{row["Rank"]}</div>', unsafe_allow_html=True)

            btn_label = f"**{_md_escape(row['Team Name'])}**"
            if c_pteam.button(btn_label, key=f"paidmgr_{row['entry_id']}", help="Klik untuk membuka susunan squad & detail"):
                show_manager_dialog(row, chips_data)
            c_pmgr.markdown(f'<div class="std-muted" style="padding: 10px 0; font-style: italic;">{html.escape(str(row["Manager"]))}</div>', unsafe_allow_html=True)

            c_pgw.markdown(f'<div class="std-points" style="padding: 6px 0;">{row["GW Points"]}</div>', unsafe_allow_html=True)
            c_ptot.markdown(f'<div class="std-total" style="padding: 6px 0;">{row["Total Points"]}</div>', unsafe_allow_html=True)
            
            or_val = row.get("Overall Rank", "-")
            or_fmt = f"{or_val:,}" if isinstance(or_val, (int, float)) else str(or_val)
            c_por.markdown(f'<div class="std-muted" style="padding: 6px 0; font-size: 0.8rem;">{or_fmt}</div>', unsafe_allow_html=True)
            
            c_pcap.markdown(f'<div style="padding: 6px 0; font-size: 0.82rem; color: #E2E8F0;">{html.escape(str(row["Captain"]))}</div>', unsafe_allow_html=True)
            
            chip_val = str(row["Active Chip"])
            if chip_val and chip_val != "-":
                c_pchip.markdown(f'<div style="padding: 6px 0;"><span class="std-chip-tag">{html.escape(chip_val)}</span></div>', unsafe_allow_html=True)
            else:
                c_pchip.markdown('<div class="std-muted" style="padding: 6px 0;">-</div>', unsafe_allow_html=True)
                
            hits_val = row.get("Transfer Cost", 0) or 0
            if hits_val:
                c_phits.markdown(f'<div class="std-hit" style="padding: 6px 0;">-{hits_val}</div>', unsafe_allow_html=True)
            else:
                c_phits.markdown('<div class="std-muted" style="padding: 6px 0;">0</div>', unsafe_allow_html=True)
                
            c_pval.markdown(f'<div class="std-muted" style="padding: 6px 0; font-size: 0.82rem;">£{row.get("Team Value (£m)", 0):.1f}m</div>', unsafe_allow_html=True)

# ================= TAB 2: TRENDS & CHARTS =================
with tab2:
    st.markdown("### 📈 Grafik Perjalanan & Performa Musim")
    history_df = data.get("history_df", pd.DataFrame())

    if history_df.empty:
        st.info("Data riwayat gameweek akan muncul setelah gameweek berjalan dan ada pertandingan yang selesai.")
    else:
        col_ctrl1, col_ctrl2 = st.columns([1, 1])
        with col_ctrl1:
            chart_type = st.selectbox(
                "Pilih Tampilan Grafik:", 
                ["Akumulasi Total Poin", "Poin Per Gameweek", "Pergerakan Overall Rank FPL"]
            )
        with col_ctrl2:
            top_mgrs_count = st.slider(
                "Jumlah Manajer Teratas yang Ditampilkan:", 
                3, min(25, total_managers), min(8, total_managers)
            )

        top_entry_ids = standings_df.head(top_mgrs_count)["entry_id"].tolist()
        filtered_hist = history_df[history_df["entry_id"].isin(top_entry_ids)]

        plotly_layout = dict(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            hovermode="x unified",
            legend=dict(orientation="h", y=-0.25, x=0.5, xanchor="center"),
            margin=dict(l=20, r=20, t=40, b=40),
            font=dict(family="Plus Jakarta Sans", color="#D1D8E0")
        )

        if chart_type == "Akumulasi Total Poin":
            fig = px.line(
                filtered_hist, 
                x="gameweek", 
                y="total_points", 
                color="team_name",
                markers=True,
                line_shape="spline",
                title="📈 Pertumbuhan Total Poin Manajer (GW1 s/d GW Saat Ini)",
                labels={"gameweek": "Gameweek", "total_points": "Total Poin", "team_name": "Tim"},
                color_discrete_sequence=["#00FF87", "#02EFFF", "#FFE27A", "#E90052", "#9F7AEA", "#F6AD55"]
            )
            fig.update_layout(**plotly_layout)
            st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "Poin Per Gameweek":
            fig = px.line(
                filtered_hist, 
                x="gameweek", 
                y="gw_points", 
                color="team_name",
                markers=True,
                line_shape="spline",
                title=f"⚡ Skor Poin per Gameweek",
                labels={"gameweek": "Gameweek", "gw_points": "Poin GW", "team_name": "Tim"},
                color_discrete_sequence=["#00FF87", "#02EFFF", "#FFE27A", "#E90052", "#9F7AEA", "#F6AD55"]
            )
            fig.update_layout(**plotly_layout)
            st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "Pergerakan Overall Rank FPL":
            fig = px.line(
                filtered_hist, 
                x="gameweek", 
                y="overall_rank", 
                color="team_name",
                markers=True,
                line_shape="spline",
                title="🌍 Pergerakan Overall Rank Dunia (Makin ke atas = makin tinggi)",
                labels={"gameweek": "Gameweek", "overall_rank": "Overall Rank", "team_name": "Tim"},
                color_discrete_sequence=["#00FF87", "#02EFFF", "#FFE27A", "#E90052", "#9F7AEA", "#F6AD55"]
            )
            fig.update_yaxes(autorange="reversed")
            fig.update_layout(**plotly_layout)
            st.plotly_chart(fig, use_container_width=True)

# ================= TAB 3: CAPTAIN & EO =================
with tab3:
    st.markdown(f"### 👑 Captaincy & Effective Ownership (EO) — GW{selected_gw}")

    col_cap, col_pie = st.columns([1, 1])
    captaincy_df = data.get("captaincy_df", pd.DataFrame())
    
    with col_cap:
        st.markdown("#### 🎯 Distribusi Pilihan Kapten")
        if not captaincy_df.empty:
            st.dataframe(
                captaincy_df, 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "Count": st.column_config.NumberColumn("Jumlah Manajer", format="%d"),
                    "% of League": st.column_config.NumberColumn("% di Liga", format="%.1f%%")
                }
            )
    with col_pie:
        if not captaincy_df.empty:
            fig_cap = px.pie(
                captaincy_df, 
                names="Captain", 
                values="Count", 
                hole=0.45,
                color_discrete_sequence=["#00FF87", "#02EFFF", "#FFE27A", "#E90052", "#9F7AEA"]
            )
            fig_cap.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=10, r=10, t=30, b=10),
                legend=dict(orientation="h", y=-0.15),
                font=dict(family="Plus Jakarta Sans", color="#D1D8E0")
            )
            st.plotly_chart(fig_cap, use_container_width=True)

    st.markdown("---")
    st.markdown("### 📊 Kepemilikan Pemain (League Ownership & Effective Ownership)")
    st.caption("💡 **Effective Ownership (EO)** = % Manajer yang memainkan pemain sebagai Starter + Kapten (+2x) + Triple Captain (+3x).")

    ownership_df = data.get("ownership_df", pd.DataFrame())
    if not ownership_df.empty:
        col_pos, col_min_own = st.columns([1, 1])
        with col_pos:
            pos_filter = st.multiselect("Filter Posisi Pemain:", ["GKP", "DEF", "MID", "FWD"], default=["GKP", "DEF", "MID", "FWD"])
        with col_min_own:
            min_eo = st.slider("Minimal Effective Ownership (EO %):", 0, 100, 0)

        filtered_own = ownership_df[
            (ownership_df["Pos"].isin(pos_filter)) &
            (ownership_df["Effective Own % (EO)"] >= min_eo)
        ]

        top_eo = filtered_own.head(15)
        if not top_eo.empty:
            fig_eo = px.bar(
                top_eo, 
                x="Player", 
                y="Effective Own % (EO)", 
                color="Pos",
                color_discrete_map={"GKP": "#ECC94B", "DEF": "#4299E1", "MID": "#48BB78", "FWD": "#F56565"},
                text="Effective Own % (EO)",
                title="Top 15 Pemain dengan Effective Ownership (EO) Tertinggi di Liga",
                labels={"Effective Own % (EO)": "EO %", "Player": "Pemain"}
            )
            fig_eo.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig_eo.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=20, r=20, t=40, b=40),
                font=dict(family="Plus Jakarta Sans", color="#D1D8E0")
            )
            st.plotly_chart(fig_eo, use_container_width=True)

        st.dataframe(
            filtered_own,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Cost (£m)": st.column_config.NumberColumn("Harga", format="£%.1fm"),
                "League Own %": st.column_config.NumberColumn("League Own %", format="%.1f%%"),
                "Effective Own % (EO)": st.column_config.NumberColumn("EO %", format="%.1f%%"),
                "FPL Overall Own %": st.column_config.NumberColumn("FPL Global Own %", format="%.1f%%")
            }
        )

# ================= TAB 4: CHIPS TRACKER =================
with tab4:
    st.markdown("### 🃏 Pelacak Chip Mini-League")
    st.caption("Pantau penggunaan chip strategis (Wildcard, Free Hit, Triple Captain, Bench Boost) oleh seluruh manajer liga.")

    chips_df = data.get("chips_df", pd.DataFrame())
    if not chips_df.empty:
        col_c1, col_c2, col_c3, col_c4 = st.columns(4)
        with col_c1:
            used_wc = (chips_df["Wildcard 1"] != "-").sum() + (chips_df["Wildcard 2"] != "-").sum()
            st.metric("Wildcard Terpakai", f"{used_wc}x", f"{used_wc/total_managers*100:.0f}% liga")
        with col_c2:
            used_fh = (chips_df["Free Hit"] != "-").sum()
            st.metric("Free Hit Terpakai", f"{used_fh}x", f"{used_fh/total_managers*100:.0f}% liga")
        with col_c3:
            used_tc = (chips_df["Triple Captain"] != "-").sum()
            st.metric("Triple Captain Terpakai", f"{used_tc}x", f"{used_tc/total_managers*100:.0f}% liga")
        with col_c4:
            used_bb = (chips_df["Bench Boost"] != "-").sum()
            st.metric("Bench Boost Terpakai", f"{used_bb}x", f"{used_bb/total_managers*100:.0f}% liga")

        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        st.dataframe(chips_df, use_container_width=True, hide_index=True)

# ================= TAB 5: VISUAL HEAD-TO-HEAD & SQUAD PITCH =================
with tab5:
    st.markdown(f"### ⚔️ Visual Head-to-Head & Squad Comparison — GW{selected_gw}")
    
    if len(standings_df) < 2:
        st.info("Dibutuhkan minimal 2 manajer di dalam liga untuk perbandingan tim.")
    else:
        manager_names = [f"{row['Team Name']} ({row['Manager']})" for _, row in standings_df.iterrows()]
        manager_entries = standings_df["entry_id"].tolist()
        name_to_entry = dict(zip(manager_names, manager_entries))

        col_m1, col_m2 = st.columns(2)
        with col_m1:
            sel_m1 = st.selectbox("Pilih Tim 1:", manager_names, index=0)
        with col_m2:
            sel_m2 = st.selectbox("Pilih Tim 2:", manager_names, index=min(1, len(manager_names)-1))

        entry_1 = name_to_entry[sel_m1]
        entry_2 = name_to_entry[sel_m2]

        row_1 = standings_df[standings_df["entry_id"] == entry_1].iloc[0]
        row_2 = standings_df[standings_df["entry_id"] == entry_2].iloc[0]

        squad_1_list = row_1.get("squad", [])
        squad_2_list = row_2.get("squad", [])

        if not squad_1_list or not squad_2_list:
            st.info("⚠️ Data susunan pemain (squad) belum tersedia untuk GW ini (misal: sebelum batas waktu transfer GW dimulai).")
        else:
            squad_1 = {p["id"]: p for p in squad_1_list}
            squad_2 = {p["id"]: p for p in squad_2_list}

            common_ids = set(squad_1.keys()).intersection(set(squad_2.keys()))
            diff_1_ids = set(squad_1.keys()) - set(squad_2.keys())
            diff_2_ids = set(squad_2.keys()) - set(squad_1.keys())

            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.03); border: 1px solid var(--card-border); border-radius: 12px; padding: 14px 18px; margin-bottom: 20px;">
                <b style="color: #00FF87;">🤝 Pemain Bersama ({len(common_ids)} / 15 Pemain):</b><br>
                <span style="color: #D1D8E0; font-size: 0.9rem;">
                    {" • ".join([f"<b>{squad_1[pid]['web_name']}</b> ({squad_1[pid]['team_short']})" for pid in common_ids]) if common_ids else "<i>Tidak ada pemain yang sama</i>"}
                </span>
            </div>
            """, unsafe_allow_html=True)

            col_s1, col_s2 = st.columns(2)

            with col_s1:
                st.markdown(f"#### 🛡️ {row_1['Team Name']}")
                st.caption(f"👑 **Kapten:** {row_1['Captain']} &nbsp;|&nbsp; 🔁 **Hits:** -{row_1['Transfer Cost']} pts")
                st.markdown(render_pitch_html(squad_1_list), unsafe_allow_html=True)
                
                st.markdown("##### ⚡ Pemain Diferensial (Hanya di Tim 1):")
                if diff_1_ids:
                    for pid in diff_1_ids:
                        p = squad_1[pid]
                        role_tag = " 👑 [C]" if p.get("is_captain") else (" [VC]" if p.get("is_vice_captain") else "")
                        bench_tag = " (Bench)" if not p.get("is_starting") else ""
                        st.markdown(f"- **{p['web_name']}** ({p['team_short']} - {p['position']}) £{p['now_cost']:.1f}m{role_tag}{bench_tag}")
                else:
                    st.write("_Tidak ada pemain pembeda._")

            with col_s2:
                st.markdown(f"#### 🛡️ {row_2['Team Name']}")
                st.caption(f"👑 **Kapten:** {row_2['Captain']} &nbsp;|&nbsp; 🔁 **Hits:** -{row_2['Transfer Cost']} pts")
                st.markdown(render_pitch_html(squad_2_list), unsafe_allow_html=True)
                
                st.markdown("##### ⚡ Pemain Diferensial (Hanya di Tim 2):")
                if diff_2_ids:
                    for pid in diff_2_ids:
                        p = squad_2[pid]
                        role_tag = " 👑 [C]" if p.get("is_captain") else (" [VC]" if p.get("is_vice_captain") else "")
                        bench_tag = " (Bench)" if not p.get("is_starting") else ""
                        st.markdown(f"- **{p['web_name']}** ({p['team_short']} - {p['position']}) £{p['now_cost']:.1f}m{role_tag}{bench_tag}")
                else:
                    st.write("_Tidak ada pemain pembeda._")


