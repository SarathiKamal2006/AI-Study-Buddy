# 📚 AI Study Buddy

An AI-powered interactive study assistant built with Streamlit, Google Gemini API, PyPDF2, and RAG (Retrieval-Augmented Generation).

## ✨ Features

- 📄 **PDF Text Extraction**: Upload study material or lecture notes in PDF format.
- 📝 **AI Summarization**: Generate concise, easy-to-understand summaries powered by Google Gemini.
- ❓ **MCQ Quiz Generator**: Create custom multiple-choice quizzes automatically from your uploaded notes.
- 🔍 **RAG System (Q&A)**: Perform fast vector search and accurate question answering directly from document context using Gemini `text-embedding-004` and `gemini-2.5-flash`.

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.9+ installed
- Google Gemini API Key (Get one from [Google AI Studio](https://aistudio.google.com/))

### 2. Installation

Clone the repository and install the dependencies:

```bash
git clone https://github.com/SarathiKamal2006/AI-Study-Buddy.git
cd AI-Study-Buddy

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration

Set your Gemini API Key in your environment:

**On Linux/macOS:**
```bash
export GEMINI_API_KEY="your_api_key_here"
```

**On Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY="your_api_key_here"
```

*Alternatively, you can enter your API Key directly in the app's sidebar UI or configure `.streamlit/secrets.toml`.*

### 4. Run the Application

```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`.

---

## 🌐 Deploying on Streamlit Cloud

1. Push code to your GitHub repository: [`https://github.com/SarathiKamal2006/AI-Study-Buddy`](https://github.com/SarathiKamal2006/AI-Study-Buddy)
2. Go to [share.streamlit.io](https://share.streamlit.io/) and log in with GitHub.
3. Click **"New App"** and select:
   - **Repository**: `SarathiKamal2006/AI-Study-Buddy`
   - **Branch**: `main`
   - **Main file path**: `app.py`
4. Under **Advanced Settings** -> **Secrets**, add:
   ```toml
   GEMINI_API_KEY = "your_gemini_api_key"
   ```
5. Click **Deploy!**

---

## 🛠️ Tech Stack

- **Frontend/App Framework**: Streamlit
- **LLM & Embeddings**: Google Gemini API (`gemini-2.5-flash`, `text-embedding-004`)
- **PDF Processing**: PyPDF2
- **Vector Operations**: NumPy
- **Database**: SQLite3
