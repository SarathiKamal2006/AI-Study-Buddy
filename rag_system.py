import os
import numpy as np
import streamlit as st
import google.generativeai as genai

API_KEY = os.getenv("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")
EMBEDDING_MODEL = "models/text-embedding-004"


def get_api_key():
    key = os.getenv("AQ.Ab8RN6Kptadz8MH2ZRVL3eKUBvOIMfzVnDMHDDWK14wCNrfhkA")
    if not key and hasattr(st, "secrets"):
        try:
            key = st.secrets.get("AQ.Ab8RN6Kptadz8MH2ZRVL3eKUBvOIMfzVnDMHDDWK14wCNrfhkA")
        except Exception:
            pass
    return key


def configure_genai():
    key = get_api_key()
    if key:
        genai.configure(api_key=key)


def chunk_text(text, chunk_size=800, overlap=100):
    """Splits full text into overlapping text chunks."""
    if not text:
        return []

    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = min(start + chunk_size, text_len)
        chunks.append(text[start:end])
        if end == text_len:
            break
        start += chunk_size - overlap

    return chunks


def get_embedding(text_str):
    """Generates vector embedding for input text using Gemini Embedding API."""
    configure_genai()
    try:
        response = genai.embed_content(
            model=EMBEDDING_MODEL,
            content=text_str,
            task_type="retrieval_document"
        )
        return response["embedding"]
    except Exception:
        # Fallback to general embedding model if specific task model is unavailable
        response = genai.embed_content(
            model="models/embedding-001",
            content=text_str
        )
        return response["embedding"]


def cosine_similarity(vec_a, vec_b):
    """Calculates cosine similarity between two 1D vectors."""
    dot_product = np.dot(vec_a, vec_b)
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(dot_product / (norm_a * norm_b))


class RAGSystem:
    def __init__(self, text):
        self.raw_text = text
        self.chunks = chunk_text(text)
        self.embeddings = []
        self._build_index()

    def _build_index(self):
        """Creates embeddings for all chunks in document."""
        if not self.chunks:
            return

        for chunk in self.chunks:
            emb = get_embedding(chunk)
            self.embeddings.append(emb)

        self.embeddings = np.array(self.embeddings)

    def retrieve(self, query, top_k=3):
        """Retrieves top_k relevant text chunks for a user query."""
        if len(self.chunks) == 0 or len(self.embeddings) == 0:
            return []

        configure_genai()
        try:
            query_emb = genai.embed_content(
                model=EMBEDDING_MODEL,
                content=query,
                task_type="retrieval_query"
            )["embedding"]
        except Exception:
            query_emb = genai.embed_content(
                model="models/embedding-001",
                content=query
            )["embedding"]

        scores = [cosine_similarity(query_emb, doc_emb) for doc_emb in self.embeddings]
        top_indices = np.argsort(scores)[::-1][:top_k]

        return [self.chunks[idx] for idx in top_indices if idx < len(self.chunks)]

    def answer_question(self, query, top_k=3):
        """Answers user question using retrieved chunk context and Gemini."""
        configure_genai()
        model = genai.GenerativeModel("gemini-2.5-flash")
        relevant_chunks = self.retrieve(query, top_k=top_k)
        context = "\n\n---\n\n".join(relevant_chunks)

        prompt = f"""
You are an intelligent study assistant. Answer the user's question using ONLY the provided document context.
If the answer cannot be found in the context, politely state that the document does not contain relevant information.

Context:
{context}

Question:
{query}

Answer:
"""
        response = model.generate_content(prompt)
        return response.text, relevant_chunks

