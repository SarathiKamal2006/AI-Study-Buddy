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
    return key

def generate_quiz(text):
    api_key = get_api_key()
    if api_key:
        genai.configure(api_key=api_key)

    model = genai.GenerativeModel("gemini-2.5-flash")

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
    response = model.generate_content(prompt)

    return response.text