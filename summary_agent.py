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
    if not text or not str(text).strip():
        return "⚠️ **Empty Document**: Could not extract readable text from this PDF. Please make sure the PDF contains selectable text (not scanned image pages)."

    api_key = get_api_key()
    if not api_key:
        return "⚠️ **Gemini API Key Missing**: Please set `GEMINI_API_KEY` in your environment variables or Streamlit Cloud Secrets."
    
    try:
        genai.configure(api_key=api_key)
        
        prompt = f"""
        Summarize the following notes in simple language with clear bullet points and main key concepts:

        {text}
        """

        # 1. Dynamically fetch models available for this API key
        try:
            available_models = [m.name for m in genai.list_models() if 'generateContent' in getattr(m, 'supported_generation_methods', [])]
            priority_keywords = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro", "gemini-pro", "flash"]
            sorted_models = []
            for kw in priority_keywords:
                for m in available_models:
                    if kw in m and m not in sorted_models:
                        sorted_models.append(m)
            for m in available_models:
                if m not in sorted_models:
                    sorted_models.append(m)
                    
            for model_name in sorted_models:
                try:
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(prompt)
                    if response and hasattr(response, "text") and response.text:
                        return response.text
                    elif response and hasattr(response, "parts") and response.parts:
                        return "".join(part.text for part in response.parts if hasattr(part, "text"))
                except Exception:
                    continue
        except Exception:
            pass

        # 2. Hardcoded fallback list (with both 'models/' prefix and without)
        candidate_models = [
            "models/gemini-1.5-flash",
            "gemini-1.5-flash",
            "models/gemini-1.5-pro",
            "gemini-1.5-pro",
            "models/gemini-pro",
            "gemini-pro",
            "models/gemini-2.0-flash",
            "gemini-2.0-flash"
        ]
        last_error = None

        for model_name in candidate_models:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                if response and hasattr(response, "text") and response.text:
                    return response.text
                elif response and hasattr(response, "parts") and response.parts:
                    return "".join(part.text for part in response.parts if hasattr(part, "text"))
            except Exception as e:
                last_error = e
                err_msg = str(e).lower()
                if "404" in err_msg or "not found" in err_msg or "not available" in err_msg:
                    continue
                if "unauthenticated" in err_msg or "api_key_invalid" in err_msg or "401" in err_msg or "permissiondenied" in err_msg or "quota" in err_msg:
                    break

        if last_error:
            err_str = str(last_error)
            if "Unauthenticated" in err_str or "API_KEY_INVALID" in err_str or "401" in err_str or "PermissionDenied" in err_str:
                return "🔑 **Authentication Failed**: The Gemini API Key configured in Streamlit Secrets or environment variables is invalid or expired."
            if "RESOURCE_EXHAUSTED" in err_str or "quota" in err_str.lower() or "429" in err_str:
                return "⚠️ **API Quota Exceeded**: Your Gemini API Key has reached its rate/quota limit. Please check your Google AI Studio quota."
            return f"⚠️ **Error generating summary**: {err_str}"

        return "⚠️ **Error generating summary**: Unable to get response from Gemini API. Please check your API key and connection."
    except Exception as e:
        err_str = str(e)
        if "Unauthenticated" in err_str or "API_KEY_INVALID" in err_str or "401" in err_str or "PermissionDenied" in err_str:
            return "🔑 **Authentication Failed**: The Gemini API Key configured in Streamlit Secrets or environment variables is invalid or expired."
        return f"⚠️ **Error generating summary**: {err_str}"