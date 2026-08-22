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
        for model_name in ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-2.5-flash"]:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                raw = response.text.strip()
                # Clean JSON markdown fences if present
                if raw.startswith("```"):
                    raw = re.sub(r'^```(?:json)?', '', raw, flags=re.IGNORECASE)
                    raw = re.sub(r'```$', '', raw).strip()
                parsed = json.loads(raw)
                return parsed
            except Exception as e:
                if "404" in str(e) or "not found" in str(e).lower():
                    continue
                # Try fallback text parser if JSON parse fails
                try:
                    fallback_text = generate_quiz(text)
                    return parse_quiz_text_to_json(fallback_text)
                except Exception:
                    pass
                raise e
    except Exception as e:
        return {"error": str(e)}

def generate_quiz(text):
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
        return f"⚠️ **Error generating quiz**: {err_str}"