import os
import streamlit as st
import google.generativeai as genai

# Default key fallback if environment/secrets are not configured
FALLBACK_API_KEY = "AQ.Ab8RN6Kptadz8MH2ZRVL3eKUBvOIMfzVnDMHDDWK14wCNrfhkA"

def get_api_key():
    key = os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_KEY")
    if not key and hasattr(st, "secrets"):
        try:
            key = st.secrets.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_KEY")
        except Exception:
            pass
    if not key:
        key = FALLBACK_API_KEY
    return key

def generate_summary(text):
    api_key = get_api_key()
    if api_key:
        genai.configure(api_key=api_key)

    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = f"""
    Summarize the following notes in simple language:

    {text}
    """

    response = model.generate_content(prompt)
    return response.text