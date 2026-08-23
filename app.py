import os
import re
import json
import numpy as np
import streamlit as st
from PyPDF2 import PdfReader
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page Setup
st.set_page_config(
    page_title="AI Study Buddy - RAG Summarizer & Quiz",
    page_icon="📚",
    layout="wide"
)

# Custom Dark Glassmorphism Styling
st.markdown("""
<style>
    /* Hide Streamlit Top Header, Toolbar, Star, Edit, and GitHub icons */
    #MainMenu {visibility: hidden; display: none !important;}
    header {visibility: hidden; display: none !important;}
    footer {visibility: hidden; display: none !important;}
    div[data-testid="stToolbar"] {visibility: hidden; display: none !important;}
    div[data-testid="stDecoration"] {visibility: hidden; display: none !important;}
    div[data-testid="stStatusWidget"] {visibility: hidden; display: none !important;}
    div[data-testid="stHeader"] {visibility: hidden; display: none !important;}
    .stAppHeader {display: none !important;}
    button[title="View source on GitHub"] {display: none !important;}

    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #6366f1, #a855f7, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        color: #94a3b8;
        font-size: 1.1rem;
        margin-bottom: 1.5rem;
    }
    .score-badge {
        font-size: 1.5rem;
        font-weight: 700;
        color: #10b981;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid rgba(16, 185, 129, 0.3);
        display: inline-block;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)



# Helper: Get Gemini API Key
def get_api_key():
    # 1. Session State user key
    if st.session_state.get("user_gemini_key"):
        k = st.session_state["user_gemini_key"].strip()
        if k and k != "your_gemini_api_key_here" and not k.startswith("your_"):
            return k

    # 2. Environment variable or .env file
    key = os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_KEY")

    # 3. Streamlit Secrets
    if not key and hasattr(st, "secrets"):
        try:
            key = st.secrets.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_KEY")
        except Exception:
            pass

    if key and isinstance(key, str):
        key = key.strip()
        if key and key != "your_gemini_api_key_here" and not key.startswith("your_"):
            return key

    return None


# Helper: Call Gemini API with automatic model fallback on 429 Quota / 404 errors
def call_gemini_with_fallback(prompt, api_key):
    if not api_key or api_key == "your_gemini_api_key_here" or api_key.startswith("your_"):
        return "🔑 **Gemini API Key Missing**: Please paste your Gemini API Key into your `.env` file (`GEMINI_API_KEY=AIzaSy...`). Get a free key at [Google AI Studio](https://aistudio.google.com/)."

    genai.configure(api_key=api_key)

    # Standard free-tier supported models (prioritizing gemini-1.5-flash which has stable quota)
    candidate_models = [
        "models/gemini-1.5-flash",
        "gemini-1.5-flash",
        "models/gemini-2.0-flash",
        "gemini-2.0-flash",
        "models/gemini-1.5-pro",
        "gemini-1.5-pro",
        "models/gemini-pro",
        "gemini-pro"
    ]

    try:
        api_models = [m.name for m in genai.list_models() if 'generateContent' in getattr(m, 'supported_generation_methods', [])]
        for m in api_models:
            # Exclude experimental or 3.1 models that return limit: 0 on free tier
            if "3.1" in m or "exp" in m:
                continue
            if m not in candidate_models:
                candidate_models.append(m)
    except Exception:
        pass

    last_error = None
    for model_name in candidate_models:
        try:
            model = genai.GenerativeModel(model_name)
            res = model.generate_content(prompt)
            if res and hasattr(res, "text") and res.text:
                return res.text
            elif res and hasattr(res, "parts") and res.parts:
                return "".join(p.text for p in res.parts if hasattr(p, "text"))
        except Exception as e:
            last_error = e
            err_msg = str(e).lower()
            # If 429 (Quota Exceeded) or 404 (Not Found), automatically move to the next model!
            if "429" in err_msg or "quota" in err_msg or "404" in err_msg or "not found" in err_msg or "limit: 0" in err_msg or "resource_exhausted" in err_msg:
                continue
            if "403" in err_msg or "denied access" in err_msg or "unauthenticated" in err_msg or "api_key_invalid" in err_msg or "401" in err_msg or "permissiondenied" in err_msg:
                break

    if last_error:
        err_str = str(last_error)
        if "403" in err_str or "denied access" in err_str.lower() or "permissiondenied" in err_str.lower():
            return "🔑 **Gemini API Key Access Denied (HTTP 403)**: The API Key in your `.env` file is invalid, placeholder, or expired. Please generate a free API Key at [Google AI Studio](https://aistudio.google.com/) and paste it into `.env` (`GEMINI_API_KEY=AIzaSy...`)."
        if "429" in err_str or "quota" in err_str.lower() or "resource_exhausted" in err_str.lower():
            return "⚠️ **Rate Limit / Quota Reached**: All free-tier models are currently rate-limited. Please wait 10 seconds and click again."
        return f"⚠️ **Error generating content**: {err_str}"

    return "Could not generate content from Gemini API."



# Helper: Extract text from PDF
def extract_pdf_text(uploaded_file):
    try:
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
        return text.strip()
    except Exception as e:
        st.error(f"Error reading PDF file: {str(e)}")
        return ""


# RAG System: Vector Indexing & Retrieval
class RAGEngine:
    def __init__(self, text, chunk_size=1200, overlap=150):
        self.text = text
        self.chunks = self._create_chunks(text, chunk_size, overlap)
        self.embeddings = []
        self._build_embeddings()

    def _create_chunks(self, text, chunk_size, overlap):
        if not text:
            return []
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunks.append(text[start:end])
            if end == len(text):
                break
            start += chunk_size - overlap
        return chunks

    def _build_embeddings(self):
        api_key = get_api_key()
        if not api_key or not self.chunks:
            return
        genai.configure(api_key=api_key)

        try:
            res = genai.embed_content(
                model="models/text-embedding-004",
                content=self.chunks,
                task_type="retrieval_document"
            )
            self.embeddings = np.array(res["embedding"])
        except Exception:
            # Fallback mini-batch embedding
            embs = []
            for chunk in self.chunks:
                try:
                    e = genai.embed_content(
                        model="models/embedding-001",
                        content=chunk
                    )["embedding"]
                    embs.append(e)
                except Exception:
                    pass
            self.embeddings = np.array(embs) if embs else np.array([])

    def retrieve(self, query, top_k=3):
        if len(self.chunks) == 0 or len(self.embeddings) == 0:
            return self.chunks[:top_k]

        api_key = get_api_key()
        if not api_key:
            return self.chunks[:top_k]

        genai.configure(api_key=api_key)
        try:
            q_emb = genai.embed_content(
                model="models/text-embedding-004",
                content=query,
                task_type="retrieval_query"
            )["embedding"]
        except Exception:
            try:
                q_emb = genai.embed_content(
                    model="models/embedding-001",
                    content=query
                )["embedding"]
            except Exception:
                return self.chunks[:top_k]

        # Cosine Similarity
        scores = []
        for doc_emb in self.embeddings:
            dot = np.dot(q_emb, doc_emb)
            norm_q = np.linalg.norm(q_emb)
            norm_d = np.linalg.norm(doc_emb)
            sim = float(dot / (norm_q * norm_d)) if norm_q > 0 and norm_d > 0 else 0.0
            scores.append(sim)

        top_indices = np.argsort(scores)[::-1][:top_k]
        return [self.chunks[i] for i in top_indices if i < len(self.chunks)]


# Core Feature: Generate Summary
def generate_summary(text, rag_engine):
    api_key = get_api_key()
    if not api_key:
        return "⚠️ **Gemini API Key Missing**: Please set `GEMINI_API_KEY` in environment variables or Streamlit Secrets."

    chunks = rag_engine.chunks[:6] if len(rag_engine.chunks) > 6 else rag_engine.chunks
    context = "\n\n".join(chunks)

    prompt = f"""
    You are an expert AI tutor. Generate a comprehensive, easy-to-understand summary of the following document notes.

    Format the summary with:
    - 📌 **Key Highlights & Overview**
    - 🔑 **Core Concepts & Definitions**
    - 💡 **Main Takeaways / Bullet Points**

    Document Content:
    {context}
    """

    return call_gemini_with_fallback(prompt, api_key)


# Core Feature: Generate 10 MCQ Quiz
def generate_10_mcq_quiz(text, rag_engine):
    api_key = get_api_key()
    if not api_key:
        return None, "⚠️ **Gemini API Key Missing**: Please set `GEMINI_API_KEY` in environment variables or Streamlit Secrets."

    context = "\n\n".join(rag_engine.chunks[:8])

    prompt = f"""
    Create exactly 10 Multiple Choice Questions (MCQs) based on the document text provided below.

    You MUST return ONLY a valid JSON array of 10 objects. Do not include markdown code block formatting like ```json or ```. No prose or introductory text.

    Required JSON format for each item:
    [
      {{
        "id": 1,
        "question": "Clear question text?",
        "options": {{
          "A": "Option A text",
          "B": "Option B text",
          "C": "Option C text",
          "D": "Option D text"
        }},
        "answer": "A",
        "explanation": "Brief explanation of why option A is correct."
      }}
    ]

    Document Content:
    {context}
    """

    try:
        raw = call_gemini_with_fallback(prompt, api_key)
        if raw.startswith("⚠️"):
            return None, raw
            
        raw = raw.strip()
        # Clean JSON fences if model returns markdown
        if raw.startswith("```"):
            raw = re.sub(r'^```(?:json)?', '', raw, flags=re.IGNORECASE)
            raw = re.sub(r'```$', '', raw).strip()

        quiz_json = json.loads(raw)
        if isinstance(quiz_json, list) and len(quiz_json) > 0:
            return quiz_json, None
        return None, "Failed to parse 10 questions from Gemini response."
    except Exception as e:
        return None, f"⚠️ **Error generating quiz**: {str(e)}"


# Core Feature: RAG Q&A
def answer_rag_question(query, rag_engine):
    api_key = get_api_key()
    if not api_key:
        return "⚠️ **Gemini API Key Missing**: Please set `GEMINI_API_KEY` in environment variables or Streamlit Secrets.", []

    retrieved_chunks = rag_engine.retrieve(query, top_k=3)
    context = "\n\n---\n\n".join(retrieved_chunks)

    prompt = f"""
    You are an AI Study Assistant. Answer the question accurately using ONLY the provided document context chunks.
    If the context does not contain enough information, state that clearly.

    Retrieved Document Context:
    {context}

    User Question:
    {query}

    Answer:
    """

    ans = call_gemini_with_fallback(prompt, api_key)
    return ans, retrieved_chunks



# ================= MAIN STREAMLIT APPLICATION =================

st.markdown('<div class="main-title">📚 AI Study Buddy</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Upload any study notes or PDF textbook to generate instant Summaries, a 10-Question Interactive Quiz, and ask RAG Q&A questions!</div>', unsafe_allow_html=True)

# PDF File Upload Section
uploaded_file = st.file_uploader("📂 Upload PDF Document", type=["pdf"])


if uploaded_file:
    # Read text
    text = extract_pdf_text(uploaded_file)

    if not text or not text.strip():
        st.error("⚠️ **No extractable text found in PDF**: The uploaded file may be a scanned image PDF or empty. Please upload a PDF containing selectable text.")
    else:
        st.success(f"✅ PDF Uploaded Successfully! Extracted **{len(text)}** characters across pages.")

        # Cache RAG System in session state to avoid re-embedding on interaction
        doc_id = f"{uploaded_file.name}_{len(text)}"
        if st.session_state.get("current_doc_id") != doc_id:
            with st.spinner("⚡ Building RAG Vector Embeddings Index from document..."):
                st.session_state["rag_engine"] = RAGEngine(text)
                st.session_state["current_doc_id"] = doc_id
                st.session_state["summary"] = None
                st.session_state["quiz_data"] = None
                st.session_state["user_answers"] = {}
                st.session_state["quiz_submitted"] = False

        rag_engine = st.session_state["rag_engine"]

        # Action Buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📝 Generate Document Summary", use_container_width=True, type="primary"):
                with st.spinner("Generating Summary using RAG & Gemini AI..."):
                    st.session_state["summary"] = generate_summary(text, rag_engine)

        with col2:
            if st.button("🎯 Generate 10-Question Practice Quiz", use_container_width=True, type="secondary"):
                with st.spinner("Creating 10 MCQs from document context..."):
                    quiz_data, err = generate_10_mcq_quiz(text, rag_engine)
                    if quiz_data:
                        st.session_state["quiz_data"] = quiz_data
                        st.session_state["user_answers"] = {}
                        st.session_state["quiz_submitted"] = False
                    else:
                        st.error(err)

        # SECTION 1: DOCUMENT SUMMARY
        if st.session_state.get("summary"):
            st.markdown("---")
            st.subheader("📝 Document Summary")
            st.markdown(st.session_state["summary"])

        # SECTION 2: INTERACTIVE 10-QUESTION MCQ QUIZ
        if st.session_state.get("quiz_data"):
            st.markdown("---")
            st.subheader("🎯 Interactive Practice Quiz (10 Questions)")

            quiz_list = st.session_state["quiz_data"]

            # Render questions inside radio controls
            for idx, q in enumerate(quiz_list, 1):
                st.markdown(f"**Question {idx} of 10**: {q['question']}")
                opts = [f"{k}) {v}" for k, v in q["options"].items()]
                
                selected_opt = st.radio(
                    f"Select your answer for Q{idx}:",
                    options=opts,
                    key=f"q_{idx}",
                    index=None,
                    disabled=st.session_state.get("quiz_submitted", False)
                )

                if selected_opt:
                    selected_key = selected_opt[0] # "A", "B", "C", "D"
                    st.session_state["user_answers"][idx] = selected_key

                # Show Feedback after quiz submission
                if st.session_state.get("quiz_submitted"):
                    user_ans = st.session_state["user_answers"].get(idx)
                    correct_ans = q["answer"]
                    
                    if user_ans == correct_ans:
                        st.success(f"✅ Correct! (Answer: {correct_ans}) — {q.get('explanation', '')}")
                    else:
                        st.error(f"❌ Incorrect. Your answer: {user_ans if user_ans else 'None'} | Correct answer: **{correct_ans}**")
                        if q.get("explanation"):
                            st.info(f"💡 Explanation: {q['explanation']}")
                
                st.markdown("<br>", unsafe_allow_html=True)

            # Submit & Score Buttons
            if not st.session_state.get("quiz_submitted"):
                if st.button("🏆 Submit Quiz & Check Score", type="primary"):
                    st.session_state["quiz_submitted"] = True
                    st.rerun()
            else:
                # Calculate score
                score = sum(1 for idx, q in enumerate(quiz_list, 1) if st.session_state["user_answers"].get(idx) == q["answer"])
                st.markdown(f'<div class="score-badge">Your Total Score: {score} / 10</div>', unsafe_allow_html=True)
                
                if st.button("🔄 Retake Quiz", type="secondary"):
                    st.session_state["user_answers"] = {}
                    st.session_state["quiz_submitted"] = False
                    st.rerun()

        # SECTION 3: RAG Q&A
        st.markdown("---")
        st.subheader("🔍 RAG Question Answering")
        st.write("Ask any targeted question about your uploaded document. The RAG engine searches relevant vector chunks and answers with context.")

        query = st.text_input("Enter your question:", placeholder="e.g. What is the main theory described on page 3?")

        if st.button("⚡ Get Answer", type="primary"):
            if query.strip():
                with st.spinner("Searching document vector context & generating answer..."):
                    ans, chunks = answer_rag_question(query, rag_engine)
                    st.markdown("### Answer:")
                    st.markdown(ans)

                    if chunks:
                        with st.expander("📄 View Retrieved Document Context Chunks (RAG Source)"):
                            for i, chunk in enumerate(chunks, 1):
                                st.markdown(f"**Chunk {i}:**")
                                st.info(chunk)
            else:
                st.warning("Please type a question before submitting.")