import os
import streamlit as st
import uuid
import re
import time
from datetime import datetime

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

if "messages" not in st.session_state:
    st.session_state.messages = []

if "theme" not in st.session_state:
    st.session_state.theme = "light"

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

col_space, col_history, col_toggle = st.columns([6, 2, 2])

with col_toggle:
    is_dark = st.toggle("🌙 Dark Mode", value=(st.session_state.theme == "dark"))
    new_theme = "dark" if is_dark else "light"
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

if st.session_state.theme == "dark":
    BG_STYLE = "#090d16"  # 🟢 FIXED: Deep uniform pitch black background layout
    TXT_MAIN = "#f8fafc"
    TXT_MUTED = "#94a3b8"
    TXT_ORANGE = "#ff7a33"
    CARD_1_BG = "#111827"       
    CARD_2_BG = "#1f2937"       
    CARD_3_BG = "#111827"       
    CARD_4_BG = "#1f2937"       
    CARD_BORDER = "#374151"
    FORCE_FONT = "#f8fafc"
    INPUT_BG = "#1f2937"
    INPUT_BORDER = "2px solid #3b82f6"
    INPUT_SHADOW = "0px 0px 20px rgba(59, 130, 246, 0.6)"
else:
    BG_STYLE = "linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)"  # 🟢 HIGHLIGHTED: Elevated premium light color theme gradient
    TXT_MAIN = "#0f172a"
    TXT_MUTED = "#475569"
    TXT_ORANGE = "#0284c7"      
    CARD_1_BG = "#e0f2fe"       
    CARD_2_BG = "#f0f9ff"       
    CARD_3_BG = "#e0f2fe"       
    CARD_4_BG = "#ffffff"       
    CARD_BORDER = "#bae6fd"
    FORCE_FONT = "#0f172a"
    INPUT_BG = "#ffffff"
    INPUT_BORDER = "2px solid #0284c7"
    INPUT_SHADOW = "0px 0px 15px rgba(2, 132, 199, 0.3)"

CSS_SHEET = f"""
<style>
    /* 🟢 FACTORY OVERRIDE FLUSH: Targets structural canvas elements to destroy the pink border bleed */
    html, body, .stApp, div[data-testid="stAppViewContainer"], div[data-testid="stAppViewBlockContainer"], .main, .block-container {{ 
        background: {BG_STYLE} !important; 
        background-color: {BG_STYLE} !important;
        color: {TXT_MAIN} !important; 
    }}
    @keyframes fadeInUp {{
        from {{ opacity: 0; transform: translateY(15px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    .hero-container {{ text-align: center; padding: 1.5rem 0; animation: fadeInUp 0.5s ease-out both; }}
    .hero-title {{ font-size: 3.2rem; font-weight: 800; color: {TXT_ORANGE} !important; margin-bottom: 0.5rem; }}
    .hero-subtitle {{ font-size: 1.25rem; font-weight: 500; color: {TXT_MUTED} !important; margin-bottom: 2rem; }}
    
    /* 🟢 ANIMATIONS: Fluid ease interactions added onto layout elements */
    .ui-card {{ 
        border: 1px solid {CARD_BORDER}; border-radius: 20px; padding: 2rem; min-height: 240px; 
        display: flex; flex-direction: column; justify-content: space-between;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1); animation: fadeInUp 0.7s ease-out both;
    }}
    .ui-card:hover {{
        transform: translateY(-8px) scale(1.02); 
        box-shadow: 0 20px 25px -5px rgba(59, 130, 246, 0.2); 
        border-color: #3b82f6 !important;
    }}
    .card-title {{ font-size: 1.6rem; font-weight: 700; color: {TXT_MAIN} !important; margin-bottom: 0.8rem; }}
    .card-desc {{ font-size: 1rem; color: {TXT_MUTED} !important; line-height: 1.6; }}
    .card-icon {{ font-size: 2.5rem; text-align: right; }}
    
    .stChatMessage, .stChatMessage p, .stChatMessage div, .stChatMessage span,
    div[data-testid="stMarkdownContainer"] p, td, th, table, tr, li, ul, ol {{ 
        color: {FORCE_FONT} !important; 
    }}
    table {{ background-color: {CARD_4_BG} !important; border: 1px solid {CARD_BORDER} !important; width: 100%; border-radius: 12px; overflow: hidden; }}
    th, td {{ border: 1px solid {CARD_BORDER} !important; padding: 12px; }}
    
    /* 🟢 ILLUMINATED GLASSMORPHIC HIGHLIGHT CHAT BAR */
    div[data-testid="stChatInput"] {{
        background-color: {INPUT_BG} !important; 
        border: {INPUT_BORDER} !important;
        border-radius: 32px !important; 
        box-shadow: {INPUT_SHADOW} !important;
        padding: 4px 12px !important;
    }}
    
    /* 🟢 FORK ICON ACCENT CONTRACT PROTECTION */
    svg, .stIconOpen, div[data-testid="stActionButton"] svg, a svg, .stActionButton button svg {{ 
        fill: {TXT_MAIN} !important; 
        color: {TXT_MAIN} !important; 
    }}
</style>
"""
st.markdown(CSS_SHEET, unsafe_allow_html=True)

st.markdown(f"""
<div class="hero-container">
    <div class="hero-title">Begin Your Next Adventure 🎈</div>
    <div class="hero-subtitle">Hi! I'm your AI Travel Partner, here to organize live global metrics seamlessly. Happy Travels! ✈️</div>
</div>
""", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1: st.markdown(f'<div class="ui-card" style="background-color: {CARD_1_BG};"><div><div class="card-title">Build Itinerary</div><div class="card-desc">Tailored day-by-day travel timelines linked straight to target budget matrices.</div></div><div class="card-icon">📍</div></div>', unsafe_allow_html=True)
with c2: st.markdown(f'<div class="ui-card" style="background-color: {CARD_2_BG};"><div><div class="card-title">Find Flights</div><div class="card-desc">Comprehensive comfort metrics, real airline carriers, and explicit clock timings.</div></div><div class="card-icon">📅</div></div>', unsafe_allow_html=True)
with c3: st.markdown(f'<div class="ui-card" style="background-color: {CARD_3_BG};"><div><div class="card-title">Find Hotels</div><div class="card-desc">Top 10 premium listings sorted explicitly by customer review scores.</div></div><div class="card-icon">🏨</div></div>', unsafe_allow_html=True)
with c4: st.markdown(f'<div class="ui-card" style="background-color: {CARD_4_BG};"><div><div class="card-title">Live Weather</div><div class="card-desc">Full 7-day extended forecast lookaheads updated from active data infrastructure.</div></div><div class="card-icon">🔮</div></div>', unsafe_allow_html=True)

st.markdown("<br><hr style='border-top: 1px solid var(--stBorderColor);'><br>", unsafe_allow_html=True)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if user_input := st.chat_input("Ask for trip plans, top-rated hotels, or specific flight timelines here..."):
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
            greeting_reply = "Hello! 👋 I'm your AI Trip Partner. Where are you planning your next adventure? Tell me any destination, and I'll extract top-rated hotels, 7-day weather outlooks, and detailed flight comfort options for you!"
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
