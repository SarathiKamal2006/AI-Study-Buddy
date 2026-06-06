import google.generativeai as genai

API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")

def generate_summary(text):

    prompt = f"""
    Summarize the following notes in simple language:

    {text}
    """

    response = model.generate_content(prompt)

    return response.text