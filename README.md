# 📚 AI Study Buddy (Streamlit + Gemini RAG)

An AI-powered interactive study assistant built with **Streamlit**, **Google Gemini API**, **RAG (Retrieval-Augmented Generation)**, **NumPy**, and **PyPDF2**.

---

## ✨ Features

- 📄 **PDF Text Extraction**: Upload lecture notes, articles, or textbooks.
- ⚡ **RAG Vector Search Engine**: Automatically chunks documents, computes embeddings using `models/text-embedding-004`, and performs vector similarity retrieval with NumPy cosine distance.
- 📝 **AI Document Summarizer**: Generates clear, structured study summaries (Key Highlights, Core Concepts, Takeaways).
- 🎯 **Interactive 10 MCQ Practice Quiz**: Generates 10 custom practice multiple-choice questions with options (A, B, C, D), interactive radio selection, score calculation (e.g., 8/10), and detailed explanations.
- 🔍 **RAG Q&A Assistant**: Ask specific questions and view exact document context source chunks used to generate answers.

---

## 🚀 How to Run Locally

### 1. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 2. Set Your Gemini API Key
Option A — In your PowerShell terminal:
```powershell
$env:GEMINI_API_KEY="your_actual_gemini_api_key_here"
```

Option B — Enter your key directly in the app's sidebar UI!

### 3. Run the Streamlit App
```powershell
python -m streamlit run app.py
```

---

## 🌐 Deploy Free to Streamlit Cloud

1. Push your code to GitHub repository `SarathiKamal2006/AI-Study-Buddy`.
2. Go to **[share.streamlit.io](https://share.streamlit.io/)** and sign in.
3. Click **New App** and select:
   - **Repository:** `SarathiKamal2006/AI-Study-Buddy`
   - **Main file path:** `app.py`
4. Under **Secrets**, add:
   ```toml
   GEMINI_API_KEY = "your_api_key_here"
   ```
5. Click **Deploy**!
