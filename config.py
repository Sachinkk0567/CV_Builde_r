import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

def get_api_key():
    # 1. User manual input in session state
    if "user_api_key" in st.session_state and st.session_state.user_api_key:
        return st.session_state.user_api_key.strip()
    
    # 2. Streamlit Cloud secrets
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"].strip()
        elif "GOOGLE_GEMINI_API_KEY" in st.secrets:
            return st.secrets["GOOGLE_GEMINI_API_KEY"].strip()
    except Exception:
        pass
    
    # 3. Environment variable (.env or system)
    env_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_GEMINI_API_KEY")
    if env_key:
        return env_key.strip()
        
    return None

API_KEY = get_api_key()