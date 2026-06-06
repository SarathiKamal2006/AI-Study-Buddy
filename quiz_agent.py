import google.generativeai as genai
import os
API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")

def generate_quiz(text):

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