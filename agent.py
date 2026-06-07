import os
import re
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from tools import search_flights, search_hotels, get_weather

SYSTEM_PROMPT = """You are an elite, highly conversational AI Travel Concierge. Today's date is 2026-06-06.
You operate as a completely open, fully flexible assistant. Accept instructions exactly as phrased by the user.
Your core task is to parse queries efficiently and execute underlying tooling parameters dynamically:
- When planning stays or hotels, always deliver up to 10 comprehensive listings explicitly prioritizing the highest customer rating matrices.
- When generating weather, ensure you provide the multi-day weekly lookahead layout details.
- When formatting data tables, build beautiful, readable expense matrices. Do not output raw JSON segments or internal tool metadata fields."""

def clean_key_string(raw_key: str) -> str:
    if not raw_key:
        return ""
    return re.sub(r"[\[\]'\"\s]", "", str(raw_key)).strip()

def get_keys_pool():
    if "GEMINI_API_KEYS" not in st.secrets:
        return []
    raw_keys = st.secrets["GEMINI_API_KEYS"]
    if isinstance(raw_keys, str):
        return [k.strip() for k in raw_keys.split(",") if k.strip()]
    if isinstance(raw_keys, list):
        return [str(k).strip() for k in raw_keys if str(k).strip()]
    return []

def run_travel_agent(user_prompt: str, force_groq=False):
    """Direct orchestration wrapper loop layer execution."""
    tools_map = {"search_flights": search_flights, "search_hotels": search_hotels, "get_weather": get_weather}
    llm = None
    
    if force_groq and "GROQ_API_KEY" in st.secrets:
        try:
            clean_groq_key = clean_key_string(st.secrets["GROQ_API_KEY"])
            llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=clean_groq_key, temperature=0.0)
        except Exception:
            pass
            
    if llm is None:
        keys_pool = get_keys_pool()
        for active_key in keys_pool:
            try:
                clean_key = clean_key_string(active_key)
                llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", api_key=clean_key, temperature=0.0)
                break
            except Exception:
                continue

    if llm is None and "GROQ_API_KEY" in st.secrets:
        try:
            clean_groq_key = clean_key_string(st.secrets["GROQ_API_KEY"])
            llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=clean_groq_key, temperature=0.0)
        except Exception:
            return None, "Infrastructure configuration error."

    if llm is None:
        return None, "Authentication signature keys rejected."

    # 🟢 DIRECT MULTI-TOOL COLLAPSING AGGREGATOR ENGINE LOGIC LOOP
    # If the user asks for a complete itinerary or full trip plan, we programmatically chain the real tools together.
    lower_prompt = user_prompt.lower()
    if "plan" in lower_prompt or "itinerary" in lower_prompt or "trip" in lower_prompt:
        try:
            # Step 1: Intelligently extract target location keywords out of the text string
            words = [w.title() for w in re.findall(r'\b\w+\b', user_prompt) if w.lower() not in [
                "plan", "a", "trip", "to", "for", "days", "day", "in", "the", "and", "me", "show", "hotels", "weather", "near"
            ]]
            target_city = words[0] if words else "Goa"
            
            # Step 2: Query real live API data pipelines sequentially
            weather_data = get_weather.invoke({"target_city": target_city})
            hotels_data = search_hotels.invoke({"destination_city": target_city, "check_in_date": "", "check_out_date": ""})
            flights_data = search_flights.invoke({"departure_airport": "HYD", "arrival_airport": "BLR", "outbound_date": "", "return_date": ""})
            
            # Step 3: Synthesis matrix compilation pass
            synthesis_prompt = f"""The user wants an itinerary trip plan based on this query: '{user_prompt}'.
            Here is the real, verified live metric data fetched from infrastructure pipelines:
            
            [LIVE WEATHER FORECAST DATA]
            {weather_data}
            
            [LIVE HOTELS SORTED LISTINGS DATA]
            {hotels_data}
            
            [LIVE FLIGHT CONNECTIONS TIMINGS]
            {flights_data}
            
            Please build a highly comprehensive, beautiful day-by-day travel itinerary. 
            Calculate an explicit, itemized pricing budget sheet matrix (including total flight fares and accommodation nightly totals accumulated over the trip duration). 
            Do not make up fake data—rely completely on the provided values."""
            
            final_messages = [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=synthesis_prompt)]
            response = llm.invoke(final_messages)
            return str(response.content), None
        except Exception as e:
            return None, str(e)

    # Standard tool calling router path for single targeted queries
    tools_list = [search_flights, search_hotels, get_weather]
    llm_with_tools = llm.bind_tools(tools_list)
    
    try:
        messages = [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=user_prompt)]
        response = llm_with_tools.invoke(messages)
        
        if hasattr(response, 'tool_calls') and response.tool_calls:
            tool_call = response.tool_calls[0]
            tool_name = tool_call['name']
            tool_args = tool_call['args']
            
            if tool_name in tools_map:
                tool_result = tools_map[tool_name].invoke(tool_args)
                
                final_messages = [
                    SystemMessage(content=SYSTEM_PROMPT),
                    HumanMessage(content=user_prompt),
                    response,
                    HumanMessage(content=f"Tool output received: {tool_result}\n\nPlease format this text beautifully according to the concierge guidelines.")
                ]
                final_response = llm.invoke(final_messages)
                return str(final_response.content), None
                
        return str(response.content), None
    except Exception as err:
        return None, str(err)
