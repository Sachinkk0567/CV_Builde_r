import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

API_KEY = None

try:
    if "GEMINI_API_KEY" in st.secrets:
        API_KEY = st.secrets["GEMINI_API_KEY"]
    elif "GOOGLE_GEMINI_API_KEY" in st.secrets:
        API_KEY = st.secrets["GOOGLE_GEMINI_API_KEY"]
except Exception:
    pass

if not API_KEY:
    API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_GEMINI_API_KEY")