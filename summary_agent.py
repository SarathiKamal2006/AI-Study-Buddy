import os
import streamlit as st
import google.generativeai as genai

def get_api_key():
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        pass
    key = os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_KEY")
    if not key and hasattr(st, "secrets"):
        try:
            key = st.secrets.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_KEY")
        except Exception:
            pass
    if key and isinstance(key, str):
        key = key.strip()
    return key if key else None

def generate_summary(text):
    api_key = get_api_key()
    if not api_key:
        return "⚠️ **Gemini API Key Missing**: Please set `GEMINI_API_KEY` in your environment variables or Streamlit Cloud Secrets."
    
    try:
        genai.configure(api_key=api_key)
        
        prompt = f"""
        Summarize the following notes in simple language:

        {text}
        """

        for model_name in ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-2.5-flash"]:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                return response.text
            except Exception as e:
                if "404" in str(e) or "not found" in str(e).lower() or "not available" in str(e).lower():
                    continue
                raise e
    except Exception as e:
        err_str = str(e)
        if "Unauthenticated" in err_str or "API_KEY_INVALID" in err_str or "401" in err_str or "PermissionDenied" in err_str:
            return "🔑 **Authentication Failed**: The Gemini API Key configured in Streamlit Secrets or environment variables is invalid or expired."
        return f"⚠️ **Error generating summary**: {err_str}"