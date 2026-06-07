import os
import streamlit as st
import uuid
import re
import time
from datetime import datetime

# --- WORKSPACE KEYS CONFIGURATION HANDSHAKE ---
if "GEMINI_API_KEYS" in st.secrets:
    os.environ["GEMINI_API_KEYS"] = str(st.secrets["GEMINI_API_KEYS"])
if "GROQ_API_KEY" in st.secrets:
    os.environ["GROQ_API_KEY"] = str(st.secrets["GROQ_API_KEY"])
if "SERPAPI_KEY" in st.secrets:
    os.environ["SERPAPI_KEY"] = str(st.secrets["SERPAPI_KEY"])
if "WEATHER_API_KEY" in st.secrets:
    os.environ["WEATHER_API_KEY"] = str(st.secrets["WEATHER_API_KEY"])

from database import save_search, get_search_history
from agent import run_travel_agent, SYSTEM_PROMPT

st.set_page_config(page_title="Free AI Travel Agent", page_icon="✈️", layout="wide")

# --- INITIALIZE CORE PLATFORM SESSION STATES ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "theme" not in st.session_state:
    st.session_state.theme = "dark"

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "active_card" not in st.session_state:
    st.session_state.active_card = "hotels"

if "chat_placeholder" not in st.session_state:
    st.session_state.chat_placeholder = "Ask for trip plans, top-rated hotels, or specific flight timelines here..."

# --- INITIALIZE EXPLICIT STAGE COLUMNS FOR UTILITIES ---
col_space, col_history, col_toggle = st.columns([6, 2, 2])

with col_toggle:
    is_dark_mode = st.toggle("🌙 Dark Mode", value=(st.session_state.theme == "dark"))
    new_theme = "dark" if is_dark_mode else "light"
    if new_theme != st.session_state.theme:
        st.session_state.theme = new_theme
        st.rerun()

with col_history:
    with st.expander("📜 Search History", expanded=False):
        try:
            history_records = get_search_history(st.session_state.session_id, limit=5)
            if history_records:
                for query_text, time_stamp in history_records:
                    st.markdown(f"🔍 `{query_text}`\n<small style='color:gray;'>{time_stamp}</small>", unsafe_allow_html=True)
            else:
                st.markdown("<small>No queries logged yet.</small>", unsafe_allow_html=True)
        except Exception:
            st.markdown("<small>Database logs loading...</small>", unsafe_allow_html=True)

# --- COSMIC ARRAY PRE-COMPILER COMPONENT ---
STAR_CSS_PASS = ""
if is_dark_mode:
    star_blocks = []
    import random
    random.seed(42)  # Maintain rendering layout consistency across app reruns
    for i in range(80):
        sz = random.uniform(1.0, 3.0)
        top_pos = random.uniform(0.0, 100.0)
        left_pos = random.uniform(0.0, 100.0)
        duration = random.uniform(1.0, 4.0)
        delay = random.uniform(0.0, 3.0)
        star_blocks.append(f"""
        .star-{i} {{
            width: {sz:.1f}px; height: {sz:.1f}px; top: {top_pos:.1f}%; left: {left_pos:.1f}%;
            --d: {duration:.1f}s; animation-delay: {delay:.1f}s;
        }}""")
    STAR_CSS_PASS = "\n".join(star_blocks)

# --- THEME STYLING ROUTER MATRIX ---
if is_dark_mode:
    TXT_MAIN = "#F8FAFC"
    TXT_MUTED = "rgba(255, 255, 255, 0.4)"
    CARD_BG = "rgba(255, 255, 255, 0.04)"
    CARD_BORDER = "rgba(255, 255, 255, 0.1)"
    TABLE_BG = "#060912"
    FORCE_FONT = "#F8FAFC"
    
    ACTIVE_BORDER_STYLE = "2px solid #00B4D8 !important"
    ACTIVE_SHADOW_STYLE = "0 0 15px rgba(0, 180, 216, 0.4) !important"
    CARD_HOVER_SHADOW = "0 20px 40px rgba(0, 180, 216, 0.15) !important"
    CARD_HOVER_BORDER = "#00B4D8 !important"
    
    BTN_BG_OVERRIDE = "rgba(255, 255, 255, 0.07) !important"
    BTN_TXT_OVERRIDE = "rgba(255, 255, 255, 0.7) !important"
    BTN_BORDER_OVERRIDE = "0.5px solid rgba(255, 255, 255, 0.12) !important"

    CSS_SHEET = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Syne:wght@700;800&display=swap');

        @keyframes twinkle {{ 0% {{ opacity: .1; transform: scale(0.8); }} 100% {{ opacity: .9; transform: scale(1.2); }} }}
        @keyframes drift {{ 0% {{ transform: translate(0,0); }} 100% {{ transform: translate(20px,20px); }} }}
        @keyframes gradshift {{ 0% {{ background-position:0% 50% }} 50% {{ background-position:100% 50% }} 100% {{ background-position:0% 50% }} }}
        @keyframes spin {{ 0% {{ transform: rotate(0deg) scale(1) }} 50% {{ transform: rotate(180deg) scale(1.2) }} 100% {{ transform: rotate(360deg) scale(1) }} }}
        @keyframes cardIn {{ from {{ opacity:0; transform: translateY(24px) }} to {{ opacity:1; transform: translateY(0) }} }}
        @keyframes rotatering {{ from {{ transform: translate(-50%,-50%) rotate(0deg) }} to {{ transform: translate(-50%,-50%) rotate(360deg) }} }}

        html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stBottom"] {{
            background-color: #060912 !important;
            background: #060912 !important;
            background-image: none !important;
            color: {TXT_MAIN} !important;
            font-family: 'Space Grotesk', sans-serif !important;
        }}

        [data-testid="stAppViewBlockContainer"], .main, .block-container {{
            background-color: #060912 !important;
            background: #060912 !important;
            color: {TXT_MAIN} !important;
        }}

        /* 🔴 COMPONENT PURGE BOUNDARIES: Absolute protection layer against light background leaks */
        div[data-testid="stBottom"],
        div[data-testid="stBottomBlockContainer"],
        .stChatInputContainer,
        .stChatInput,
        div[data-parent-container="true"],
        div[class*="stChatInputContainer"],
        .stForm,
        div[data-testid="stForm"],
        .stApp [data-testid="stBottom"] {{
            background-color: #060912 !important;
            background: #060912 !important;
            background-image: none !important;
            border: none !important;
            box-shadow: none !important;
            border-top: none !important;
            padding: 0 !important;
        }}

        [data-testid="stBottomBlockContainer"] > div {{
            background-color: transparent !important;
            background-image: none !important;
            background: transparent !important;
        }}
        
        header[data-testid="stHeader"] {{ background: transparent !important; }}
        
        /* Cosmic Aesthetic Vectors */
        .stars {{ position: absolute; inset: 0; pointer-events: none; z-index: 0; }}
        .star {{ position: absolute; border-radius: 50%; background: #fff; animation: twinkle var(--d, 2s) ease-in-out infinite alternate; }}
        {STAR_CSS_PASS}
        
        .nebula {{ position: absolute; border-radius: 50%; filter: blur(60px); pointer-events: none; z-index: 0; }}
        .n1 {{ width: 300px; height: 300px; background: rgba(99,60,255,0.18); top: -80px; right: -60px; animation: drift 8s ease-in-out infinite alternate; }}
        .n2 {{ width: 250px; height: 250px; background: rgba(0,210,180,0.12); bottom: -40px; left: -40px; animation: drift 10s ease-in-out infinite alternate-reverse; }}
        .n3 {{ width: 180px; height: 180px; background: rgba(255,80,160,0.10); top: 50%; left: 40%; animation: drift 12s ease-in-out infinite alternate; }}
        
        .orbit {{ position: absolute; width: 500px; height: 500px; border: 0.5px solid rgba(99,60,255,0.06); border-radius: 50%; top: 50%; left: 50%; transform: translate(-50%,-50%); pointer-events: none; z-index: 0; animation: rotatering 30s linear infinite; }}
        .orbit2 {{ width: 700px; height: 700px; border-color: rgba(0,210,180,0.04); animation-duration: 50s; animation-direction: reverse; }}

        .hero {{ text-align: center; margin-bottom: 2.5rem; position: relative; z-index: 1; }}
        
        /* Reengineered Title Grid to align precisely with your typography asset */
        h1, [data-testid="stMarkdownContainer"] h1 {{
            font-family: 'Syne', sans-serif !important;
            text-transform: none !important;
            letter-spacing: normal !important;
            font-stretch: normal !important;
            font-weight: 800 !important;
            font-size: 3.2rem !important;
            background: linear-gradient(135deg,#a78bfa,#38bdf8,#34d399,#fb7185) !important;
            background-size: 300% 300% !important;
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
            background-clip: text !important;
            animation: gradshift 5s ease infinite !important;
            display: inline-block !important;
            margin: 0 !important;
        }}
        
        .hero-sparkle {{
            display: inline-block !important;
            animation: spin 4s linear infinite !important;
            font-size: 2.8rem !important;
            margin-left: 10px !important;
            vertical-align: middle !important;
            -webkit-text-fill-color: initial !important;
        }}
        
        .hero-subtitle {{ font-family: 'Space Grotesk', sans-serif !important; font-size: 14px; color: rgba(255,255,255,0.5) !important; margin-top: 10px; letter-spacing: 0.02em; }}

        .card-node {{
            position: relative; border: 1px solid {CARD_BORDER}; background: {CARD_BG};
            border-radius: 16px; padding: 1.25rem; height: 270px; display: flex; flex-direction: column; justify-content: space-between;
            box-shadow: none; transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
            animation: cardIn 0.6s ease both; backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
        }}
        
        .card-node:hover {{ border-color: rgba(255,255,255,0.25); transform: translateY(-4px); }}
        .card-active {{ border: {ACTIVE_BORDER_STYLE}; background: rgba(255, 255, 255, 0.08) !important; box-shadow: {ACTIVE_SHADOW_STYLE}; transform: translateY(-4px); }}

        /* 🟢 CLEAR INTEGRATION HIGHLIGHT: High-contrast heavy headers for enhanced user scanning */
        .card-title-style {{ 
            font-family: 'Syne', sans-serif !important; 
            font-size: 17px !important; 
            font-weight: 900 !important; 
            color: #FFFFFF !important;
            margin-top: 4px;
        }}
        .card-title-style span {{ display: block; font-size: 12px; font-weight: 400; color: rgba(255,255,255,0.45); margin-top: 2px; font-family: 'Space Grotesk', sans-serif !important; }}
        .card-desc-style {{ font-size: 12px; color: rgba(255,255,255,0.4); line-height: 1.6; margin-top: 6px; }}
        .card-icon-style {{ font-size: 32px; margin-bottom: 4px; }}

        .stButton > button {{
            background: {BTN_BG_OVERRIDE}; color: {BTN_TXT_OVERRIDE}; border: {BTN_BORDER_OVERRIDE};
            padding: 9px !important; border-radius: 10px !important; font-size: 12px !important; font-weight: 500 !important;
            font-family: 'Space Grotesk', sans-serif !important; width: 100% !important; transition: all 0.2s !important;
        }}
        .c1-btn > div > button:hover {{ background: rgba(167,139,250,0.25) !important; border-color: rgba(167,139,250,0.5) !important; color: #c4b5fd !important; }}
        .c2-btn > div > button:hover {{ background: rgba(56,189,248,0.25) !important; border-color: rgba(56,189,248,0.5) !important; color: #7dd3fc !important; }}
        .c3-btn > div > button:hover {{ background: rgba(52,211,153,0.25) !important; border-color: rgba(52,211,153,0.5) !important; color: #6ee7b7 !important; }}
        .c4-btn > div > button:hover {{ background: rgba(251,113,133,0.25) !important; border-color: rgba(251,113,133,0.5) !important; color: #fda4af !important; }}

        div[data-testid="stExpander"] {{ background: {CARD_BG} !important; border: 1px solid {CARD_BORDER} !important; border-radius: 14px !important; }}
        .stChatMessage, .stChatMessage p, .stChatMessage div, .stChatMessage span, div[data-testid="stMarkdownContainer"] p, td, th, table, tr, li, ul, ol {{ color: {FORCE_FONT} !important; }}
        table {{ background-color: {TABLE_BG} !important; border: 1px solid {CARD_BORDER} !important; width: 100%; border-radius: 12px; }}

        /* Opaque text box wrapper overrides with fixed structural boundaries */
        div[data-testid="stChatInput"], 
        div[data-testid="stChatInput"] *,
        .stChatInput,
        .stChatInput * {{
            background-color: rgba(16, 24, 48, 0.9) !important; 
            background: rgba(16, 24, 48, 0.9) !important;
        }}

        div[data-testid="stChatInput"] {{
            border: 0.5px solid rgba(255, 255, 255, 0.12) !important;
            border-radius: 50px !important; 
            padding: 4px 8px 4px 12px !important;
            margin-bottom: 12px !important;
            box-shadow: none !important;
        }}
        div[data-testid="stChatInput"]:focus-within {{ border-color: rgba(167,139,250,0.5) !important; }}
        
        div[data-testid="stChatInput"] textarea {{ color: #FFFFFF !important; -webkit-text-fill-color: #FFFFFF !important; font-size: 13px !important; caret-color: #FFFFFF !important; }}
        div[data-testid="stChatInput"] textarea::placeholder {{ color: rgba(255, 255, 255, 0.3) !important; -webkit-text-fill-color: rgba(255, 255, 255, 0.3) !important; }}
        
        div[data-testid="stChatInput"] button {{
            width: 38px !important; height: 38px !important; border-radius: 50% !important;
            background: linear-gradient(135deg,#7c3aed,#0ea5e9) !important; border: none !important;
            display: flex !important; align-items: center !important; justify-content: center !important;
            box-shadow: 0 0 12px rgba(124,58,237,0.3) !important;
        }}
        div[data-testid="stChatInput"] button:hover {{ transform: scale(1.1) !important; box-shadow: 0 0 16px rgba(124,58,237,0.5) !important; }}
        div[data-testid="stChatInput"] button svg {{ fill: #FFFFFF !important; color: #FFFFFF !important; width: 18px !important; height: 18px !important; }}
        svg, .stIconOpen, div[data-testid="stActionButton"] svg, a svg {{ fill: {TXT_MAIN} !important; color: {TXT_MAIN} !important; }}
    </style>
    """
else:
    # 🌟 PRESERVED UNTOUCHED LIGHT MODE INTERFACE SCHEME
    TXT_MAIN = "#1E293B"
    TXT_MUTED = "#64748B"
    CARD_BG = "rgba(255, 255, 255, 0.85)"
    TABLE_BG = "#FFFFFF"
    FORCE_FONT = "#1E293B"  
    
    ACTIVE_BORDER_STYLE = "2px solid #D84315 !important"
    ACTIVE_SHADOW_STYLE = "0px 10px 30px rgba(216, 67, 21, 0.2) !important"
    CARD_HOVER_SHADOW = "0px 15px 35px rgba(30, 41, 59, 0.12) !important"
    CARD_HOVER_BORDER = "#D84315 !important"
    
    BTN_BG_OVERRIDE = "#FFFFFF !important"
    BTN_TXT_OVERRIDE = "#D84315 !important"
    BTN_BORDER_OVERRIDE = "1px solid rgba(216, 67, 21, 0.2) !important"

    CSS_SHEET = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        @keyframes lightModeBreathing {{
            0% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
            100% {{ background-position: 0% 50%; }}
        }}

        @keyframes fadeInUp {{
            from {{ opacity: 0; transform: translateY(24px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        .stApp, [data-testid="stAppViewContainer"], [data-testid="stBottom"] {{
            background: linear-gradient(135deg, #F0FDF4 0%, #E0F2FE 50%, #FAEAEF 100%) !important;
            background-size: 300% 300% !important;
            animation: lightModeBreathing 14s ease infinite !important;
            color: {TXT_MAIN} !important;
            font-family: 'Inter', sans-serif !important;
        }}

        [data-testid="stAppViewBlockContainer"], .main, .block-container {{ background: transparent !important; color: {TXT_MAIN} !important; }}
        [data-testid="stBottomBlockContainer"] {{ background: transparent !important; border: none !important; }}
        header[data-testid="stHeader"] {{ background: transparent !important; }}
        
        .hero {{ text-align: center; padding: 1.5rem 0 1rem 0; }}
        .hero-title {{ font-size: 2.8rem; font-weight: 800; color: #D84315 !important; margin-bottom: 0.5rem; }}
        .hero-sub {{ font-size: 1.2rem; font-weight: 500; color: {TXT_MUTED} !important; margin-bottom: 0.5rem; }}
        .hero-small {{ font-size: 0.95rem; color: {TXT_MUTED} !important; margin-bottom: 2rem; }}

        .card-node {{
            position: relative; border: 1px solid #CBD5E1; background: {CARD_BG};
            border-radius: 16px; padding: 1.8rem; height: 250px; display: flex; flex-direction: column; justify-content: space-between;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); animation: fadeInUp 0.7s ease both;
        }}
        
        .c-delay-1 {{ background-color: #BAE6FD !important; }} 
        .c-delay-2 {{ background-color: #DBEAFE !important; }} 
        .c-delay-3 {{ background-color: #BFDBFE !important; }} 
        .c-delay-4 {{ background-color: #FFFFFF !important; }} 
        
        .card-node:hover {{ border-color: {CARD_HOVER_BORDER}; transform: translateY(-6px); box-shadow: {CARD_HOVER_SHADOW}; }}
        .card-active {{ border: {ACTIVE_BORDER_STYLE}; box-shadow: {ACTIVE_SHADOW_STYLE}; transform: translateY(-6px); }}

        .card-title-style {{ font-size: 1.5rem; font-weight: 700; color: {TXT_MAIN}; margin-bottom: 0.8rem; }}
        .card-desc-style {{ font-size: 0.95rem; color: {TXT_MUTED}; line-height: 1.5; }}
        .card-icon-style {{ font-size: 2.2rem; text-align: right; margin-top: auto; }}

        .stButton > button {{
            background: {BTN_BG_OVERRIDE}; color: {BTN_TXT_OVERRIDE}; border: {BTN_BORDER_OVERRIDE};
            padding: 9px !important; border-radius: 10px !important; font-size: 12px !important; font-weight: 500 !important;
            width: 100% !important; transition: all 0.2s !important;
        }}
        .stButton > button:hover {{ background: #D84315 !important; color: #FFFFFF !important; transform: translateY(-2px) !important; }}
        
        .stChatInputContainer, div[data-testid="stChatInputContainer"], div[data-parent-container="true"] {{
            background-color: #FAEAEF !important;
            background: #FAEAEF !important;
            border-top: 1px solid #CBD5E1 !important;
        }}

        div[data-testid="stChatInput"] {{
            background-color: #FFFFFF !important; border: 2px solid #CBD5E1 !important;
            border-radius: 28px !important; box-shadow: none !important;
            padding: 6px 16px !important;
        }}
        div[data-testid="stChatInput"] textarea {{ color: #1E293B !important; -webkit-text-fill-color: #1E293B !important; }}
        div[data-testid="stChatInput"] textarea::placeholder {{ color: #64748B !important; -webkit-text-fill-color: #64748B !important; }}
        div[data-testid="stChatInput"] button svg {{ fill: #D84315 !important; color: #D84315 !important; }}
        svg, .stIconOpen, div[data-testid="stActionButton"] svg, a svg {{ fill: {TXT_MAIN} !important; color: {TXT_MAIN} !important; }}
    </style>
    """

st.markdown(CSS_SHEET, unsafe_allow_html=True)

# --- INJECT GRAPHIC CANVAS VIEWPORTS ---
if is_dark_mode:
    star_items = "\n".join([f'<div class="star star-{i}"></div>' for i in range(80)])
    st.markdown(f"""
    <div class="stars">{star_items}</div>
    <div class="nebula n1"></div>
    <div class="nebula n2"></div>
    <div class="nebula n3"></div>
    <div class="orbit"></div>
    <div class="orbit orbit2"></div>
    """, unsafe_allow_html=True)

# --- HERO REPLICA RENDER HEADER ---
if is_dark_mode:
    st.markdown("""
    <div class="hero">
        <h1>Begin Your Next Adventure</h1><span class="hero-sparkle">✦</span>
        <div class="hero-subtitle">Your AI Travel Partner — live global metrics, seamlessly organized ✈</div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="hero">
        <div class="hero-title">Begin Your Next Adventure 🎈</div>
        <div class="hero-sub">Hi! I'm your AI Trip Partner, here to make trip planning easy. Share your travel details, and I'll make your ideal plan! Happy Travels! ✈️</div>
        <div class="hero-small">Start by describing your destination parameters or pricing limits freely below!</div>
    </div>
    """, unsafe_allow_html=True)

# --- INTERACTIVE 4-COLUMN GRID LAYOUT CONTAINER ---
c1, c2, c3, c4 = st.columns(4)

with c1:
    is_active = "card-active" if st.session_state.active_card == "itinerary" else ""
    if is_dark_mode:
        st.markdown(f"""
        <div class="card-node c-delay-1 {is_active}">
            <span class="card-badge b-purple">AI OPT</span>
            <div class="card-icon-style">🗺️</div>
            <div class="card-title-style">Build <span>Itinerary</span></div>
            <div class="card-desc-style">Tailored day-by-day timelines linked to your budget targets.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="card-node c-delay-1 {is_active}">
            <div class="card-title-style">Build Itinerary</div>
            <div class="card-desc-style">Tailored completely for your preferences and calendar layout windows.</div>
            <div class="card-icon-style">📍</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('<div class="c1-btn">', unsafe_allow_html=True)
    if st.button("Select Itinerary Builder", key="act_itinerary", use_container_width=True):
        st.session_state.active_card = "itinerary"
        st.session_state.chat_placeholder = "Plan a comprehensive 3-day itinerary trip to [Destination]..."
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    is_active = "card-active" if st.session_state.active_card == "flights" else ""
    if is_dark_mode:
        st.markdown(f"""
        <div class="card-node c-delay-2 {is_active}">
            <span class="card-badge b-blue">● LIVE</span>
            <div class="card-icon-style">✈️</div>
            <div class="card-title-style">Find <span>Flights</span></div>
            <div class="card-desc-style">Real airline carriers with comfort metrics and clock timelines.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="card-node c-delay-2 {is_active}">
            <div class="card-title-style">Find Flights</div>
            <div class="card-desc-style">Comprehensive comfort metrics, real timings, and open seat routes verified.</div>
            <div class="card-icon-style">📅</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('<div class="c2-btn">', unsafe_allow_html=True)
    if st.button("Select Flight Lookup", key="act_flights", use_container_width=True):
        st.session_state.active_card = "flights"
        st.session_state.chat_placeholder = "Search live flight choices from HYD to [Destination]..."
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with c3:
    is_active = "card-active" if st.session_state.active_card == "hotels" else ""
    if is_dark_mode:
        st.markdown(f"""
        <div class="card-node c-delay-3 {is_active}">
            <span class="card-badge b-green">● TOP 10</span>
            <div class="card-icon-style">🏨</div>
            <div class="card-title-style">Find <span>Hotels</span></div>
            <div class="card-desc-style">Premium listings sorted by customer review scores first.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="card-node c-delay-3 {is_active}">
            <div class="card-title-style">Find Hotels</div>
            <div class="card-desc-style">Top 10 premium listings sorted cleanly by user review scores first.</div>
            <div class="card-icon-style">🏨</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('<div class="c3-btn">', unsafe_allow_html=True)
    if st.button("Select Hotel Lookup", key="act_hotels", use_container_width=True):
        st.session_state.active_card = "hotels"
        st.session_state.chat_placeholder = "Find 10 top-rated premium hotels inside [Destination]..."
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with c4:
    is_active = "card-active" if st.session_state.active_card == "weather" else ""
    if is_dark_mode:
        st.markdown(f"""
        <div class="card-node c-delay-4 {is_active}">
            <span class="card-badge b-red">● FEED</span>
            <div class="card-icon-style">🌤️</div>
            <div class="card-title-style">Live <span>Weather</span></div>
            <div class="card-desc-style">7-day extended forecasts from active data infrastructure feeds.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="card-node c-delay-4 {is_active}">
            <div class="card-title-style">Not sure?</div>
            <div class="card-desc-style">Let our fluid conversational AI suggest global options step-by-step.</div>
            <div class="card-icon-style">🔮</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('<div class="c4-btn">', unsafe_allow_html=True)
    if st.button("Select Weather Feed" if is_dark_mode else "Consult Assistant", key="act_weather", use_container_width=True):
        st.session_state.active_card = "weather"
        st.session_state.chat_placeholder = "What is the 7-day weather extended forecast lookahead for [City]..." if is_dark_mode else "Suggest some global holiday spots..."
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br><hr style='border-top: 1px solid var(--stBorderColor);'><br>", unsafe_allow_html=True)

# --- CHAT THREAD VIEW DISPLAY LAYER ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- PERSISTENT CONVERSATIONAL INTERACTION CHANNEL ---
if user_input := st.chat_input(st.session_state.chat_placeholder):
    try:
        save_search(st.session_state.session_id, user_input)
    except Exception:
        pass

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
        
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        response_placeholder.markdown("🔍 *Consulting live global travel networks and verifying comfort matrices...*")
        
        clean_input = user_input.strip().lower()
        if clean_input in ["hi", "hii", "hello", "hey", "greetings"]:
            greeting_reply = "Hello! 👋 I'm your AI Travel Partner. Tell me any destination, and I'll extract itineraries, weather outlooks, and flight options for you!"
            response_placeholder.markdown(greeting_reply)
            st.session_state.messages.append({"role": "assistant", "content": greeting_reply})
        else:
            clean_reply, error_msg = run_travel_agent(user_input, force_groq=False)
            used_groq_backup = False
            
            if clean_reply is None:
                response_placeholder.markdown("🔄 *Primary network channels responding with latency anomalies. Routing via fallback engine (Groq Llama)...*")
                clean_reply, fallback_error = run_travel_agent(user_input, force_groq=True)
                used_groq_backup = True
                if clean_reply is None:
                    execution_error = f"Gemini exhausted. Groq Backup Error: {fallback_error}"
            
            if clean_reply is not None:
                if used_groq_backup:
                    clean_reply = "⚡ *System automatically routed via high-speed backup network layer (Groq).* \n\n" + clean_reply
                    
                response_placeholder.markdown(clean_reply)
                st.session_state.messages.append({"role": "assistant", "content": clean_reply})
            else:
                response_placeholder.markdown(f"❌ Connection Error Across Core Infrastructure: {execution_error}")
