import os
import streamlit as st
import google.generativeai as genai

import json
import re

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

def parse_quiz_text_to_json(raw_text):
    """Parses text quiz output into structured JSON array."""
    questions = []
    blocks = re.split(r'-{3,}', raw_text)
    
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        q_match = re.search(r'Question\s*\d*:\s*(.*?)(?=\n\s*[A-D]\))', block, re.DOTALL | re.IGNORECASE)
        opt_a = re.search(r'A\)\s*(.*?)(?=\n\s*[B-D]\)|$)', block, re.DOTALL | re.IGNORECASE)
        opt_b = re.search(r'B\)\s*(.*?)(?=\n\s*[C-D]\)|$)', block, re.DOTALL | re.IGNORECASE)
        opt_c = re.search(r'C\)\s*(.*?)(?=\n\s*D\)|$)', block, re.DOTALL | re.IGNORECASE)
        opt_d = re.search(r'D\)\s*(.*?)(?=\n\s*Correct Answer:|$)', block, re.DOTALL | re.IGNORECASE)
        ans_match = re.search(r'Correct Answer:\s*([A-D])', block, re.IGNORECASE)

        if q_match and opt_a and opt_b and opt_c and opt_d:
            questions.append({
                "id": len(questions) + 1,
                "question": q_match.group(1).strip(),
                "options": {
                    "A": opt_a.group(1).strip(),
                    "B": opt_b.group(1).strip(),
                    "C": opt_c.group(1).strip(),
                    "D": opt_d.group(1).strip()
                },
                "answer": ans_match.group(1).upper() if ans_match else "A"
            })
    return questions

def generate_quiz_json(text):
    if not text or not str(text).strip():
        return {"error": "Could not extract readable text from this PDF. Please make sure the PDF contains selectable text."}

    api_key = get_api_key()
    if not api_key:
        return {"error": "Gemini API Key Missing. Please set GEMINI_API_KEY in environment variables or Streamlit Cloud Secrets."}

    try:
        genai.configure(api_key=api_key)

        prompt = f"""
Create 5 to 10 Multiple Choice Questions (MCQs) based on the provided notes.
Return ONLY a valid JSON array of objects. Do not include markdown code block backticks, prose, or extra text.

JSON format requirement:
[
  {{
    "id": 1,
    "question": "What is ...?",
    "options": {{
      "A": "Option text 1",
      "B": "Option text 2",
      "C": "Option text 3",
      "D": "Option text 4"
    }},
    "answer": "A"
  }}
]

Notes:
{text}
"""
        # Try dynamic models from API
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
                    raw = (response.text if response and hasattr(response, "text") else "").strip()
                    if not raw and response and hasattr(response, "parts") and response.parts:
                        raw = "".join(part.text for part in response.parts if hasattr(part, "text")).strip()
                    if raw:
                        if raw.startswith("```"):
                            raw = re.sub(r'^```(?:json)?', '', raw, flags=re.IGNORECASE)
                            raw = re.sub(r'```$', '', raw).strip()
                        parsed = json.loads(raw)
                        return parsed
                except Exception:
                    continue
        except Exception:
            pass

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
                raw = (response.text if response and hasattr(response, "text") else "").strip()
                if not raw and response and hasattr(response, "parts") and response.parts:
                    raw = "".join(part.text for part in response.parts if hasattr(part, "text")).strip()
                
                if raw:
                    if raw.startswith("```"):
                        raw = re.sub(r'^```(?:json)?', '', raw, flags=re.IGNORECASE)
                        raw = re.sub(r'```$', '', raw).strip()
                    parsed = json.loads(raw)
                    return parsed
            except Exception as e:
                last_error = e
                err_msg = str(e).lower()
                if "404" in err_msg or "not found" in err_msg or "not available" in err_msg:
                    continue
                try:
                    fallback_text = generate_quiz(text)
                    parsed_fallback = parse_quiz_text_to_json(fallback_text)
                    if parsed_fallback:
                        return parsed_fallback
                except Exception:
                    pass
                if "unauthenticated" in err_msg or "api_key_invalid" in err_msg or "401" in err_msg or "permissiondenied" in err_msg or "quota" in err_msg:
                    break

        return {"error": str(last_error) if last_error else "Failed to generate quiz from API response."}
    except Exception as e:
        return {"error": str(e)}

def generate_quiz(text):
    if not text or not str(text).strip():
        return "⚠️ **Empty Document**: Could not extract readable text from this PDF. Please make sure the PDF contains selectable text (not scanned image pages)."

    api_key = get_api_key()
    if not api_key:
        return "⚠️ **Gemini API Key Missing**: Please set `GEMINI_API_KEY` in your environment variables or Streamlit Cloud Secrets."

    try:
        genai.configure(api_key=api_key)

        prompt = f"""
Create 10 MCQ questions from the uploaded notes.
IMPORTANT:
Follow this EXACT format.
Each question MUST follow this structure:

Question 1:what is......?

A) Option A

B) Option B

C) Option C

D) Option D

Correct Answer: A

------------------------------------

Notes:
{text}
"""
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
            return f"⚠️ **Error generating quiz**: {err_str}"

        return "⚠️ **Error generating quiz**: Unable to get response from Gemini API."
    except Exception as e:
        err_str = str(e)
        if "Unauthenticated" in err_str or "API_KEY_INVALID" in err_str or "401" in err_str or "PermissionDenied" in err_str:
            return "🔑 **Authentication Failed**: The Gemini API Key configured in Streamlit Secrets or environment variables is invalid or expired."
        return f"⚠️ **Error generating quiz**: {err_str}"