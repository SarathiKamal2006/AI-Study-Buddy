# 📚 AI Study Buddy (React + FastAPI)

An AI-powered interactive study assistant built with a **React 18** single page application frontend, **FastAPI** REST backend, Google Gemini API, PyPDF2, and RAG (Retrieval-Augmented Generation).

## ✨ Features

- 📄 **PDF Extraction**: Upload lecture notes or textbooks in PDF format.
- 📝 **AI Summarization**: Generate clear, formatted document summaries using Gemini API.
- 🎯 **Interactive MCQ Quiz Engine**: Take custom interactive multiple-choice practice quizzes with instant score tracking.
- 🔍 **RAG Vector Search Q&A**: Perform fast vector similarity retrieval and question answering with expandable document chunk context using `text-embedding-004` and `gemini-1.5-flash`.

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.9+
- Node.js 18+ and npm
- Google Gemini API Key (Get one free from [Google AI Studio](https://aistudio.google.com/))

### 2. Environment Setup

Set your Gemini API Key in your terminal:

**On Linux / macOS:**
```bash
export GEMINI_API_KEY="your_api_key_here"
```

**On Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY="your_api_key_here"
```

---

### 3. Running the FastAPI Backend

```bash
# Install Python dependencies
pip install -r requirements.txt

# Start FastAPI server
uvicorn main:app --reload --port 8000
```

FastAPI server runs at `http://localhost:8000` (API documentation at `http://localhost:8000/docs`).

---

### 4. Running the React Frontend

Open a new terminal window:

```bash
cd frontend

# Install Node dependencies
npm install

# Start Vite dev server
npm run dev
```

Open your browser at `http://localhost:3000`.

---

## 🛠️ Tech Stack

- **Frontend**: React 18, Vite, Lucide React, Glassmorphic Vanilla CSS Design System
- **Backend API**: FastAPI, Uvicorn, Pydantic, Python 3.11
- **LLM & Embeddings**: Google Gemini API (`gemini-1.5-flash`, `text-embedding-004`)
- **PDF Processing**: PyPDF2
- **Vector Operations**: NumPy
- **Database**: SQLite3
