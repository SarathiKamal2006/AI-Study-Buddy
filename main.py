import uuid
from typing import Optional
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from pdf_reader import extract_text
from summary_agent import generate_summary
from quiz_agent import generate_quiz_json, generate_quiz
from rag_system import RAGSystem
import database

# Initialize SQLite table on startup
database.create_table()

app = FastAPI(
    title="AI Study Buddy API",
    description="FastAPI Backend for AI Study Buddy - PDF Summaries, Quizzes, and RAG Q&A",
    version="2.0.0"
)

# Enable CORS for React frontend (local dev and deployed environments)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session store for uploaded documents and RAG vector indexes
documents_store = {}


class SummaryRequest(BaseModel):
    doc_id: str


class QuizRequest(BaseModel):
    doc_id: str


class QARequest(BaseModel):
    doc_id: str
    query: str


class SaveScoreRequest(BaseModel):
    topic: str
    score: int


@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "AI Study Buddy Backend API",
        "version": "2.0.0"
    }


@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    try:
        raw_text = extract_text(file.file)
        if not raw_text or not raw_text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from the uploaded PDF.")

        doc_id = str(uuid.uuid4())
        rag_sys = RAGSystem(raw_text)

        documents_store[doc_id] = {
            "filename": file.filename,
            "text": raw_text,
            "rag_system": rag_sys
        }

        return {
            "doc_id": doc_id,
            "filename": file.filename,
            "char_count": len(raw_text),
            "text_sample": raw_text[:300] + "..."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")


@app.post("/api/summary")
def get_summary(req: SummaryRequest):
    if req.doc_id not in documents_store:
        raise HTTPException(status_code=404, detail="Document not found. Please upload a PDF first.")

    doc = documents_store[req.doc_id]
    summary = generate_summary(doc["text"])
    return {"summary": summary}


@app.post("/api/quiz")
def get_quiz(req: QuizRequest):
    if req.doc_id not in documents_store:
        raise HTTPException(status_code=404, detail="Document not found. Please upload a PDF first.")

    doc = documents_store[req.doc_id]
    quiz_data = generate_quiz_json(doc["text"])
    
    # If JSON parsing failed, fallback to text format
    if isinstance(quiz_data, dict) and "error" in quiz_data:
        raw_text = generate_quiz(doc["text"])
        return {"quiz_text": raw_text}

    return {"quiz": quiz_data}


@app.post("/api/qa")
def ask_question(req: QARequest):
    if req.doc_id not in documents_store:
        raise HTTPException(status_code=404, detail="Document not found. Please upload a PDF first.")

    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query string cannot be empty.")

    doc = documents_store[req.doc_id]
    rag_sys: RAGSystem = doc["rag_system"]
    answer, chunks = rag_sys.answer_question(req.query)

    return {
        "answer": answer,
        "chunks": chunks
    }


@app.post("/api/score")
def save_score(req: SaveScoreRequest):
    try:
        database.save_score(req.topic, req.score)
        return {"status": "success", "message": "Score saved to database."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
