import os
import streamlit as st
import google.generativeai as genai

def get_api_key():
    key = os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_KEY")
    if not key and hasattr(st, "secrets"):
        try:
            key = st.secrets.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_KEY")
        except Exception:
            pass
    if not key and "gemini_api_key" in st.session_state:
        key = st.session_state.get("gemini_api_key")
    return key

def generate_summary(text):
    api_key = get_api_key()
    if not api_key:
        return "⚠️ Error: Gemini API Key is missing. Please set GEMINI_API_KEY in your environment, Streamlit secrets, or sidebar."
    
    genai.configure(api_key=api_key)

    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = f"""
    Summarize the following notes in simple language:

    {text}
    """

    response = model.generate_content(prompt)
    return response.text