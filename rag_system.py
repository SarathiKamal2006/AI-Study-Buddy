import os
import numpy as np
import streamlit as st
import google.generativeai as genai

EMBEDDING_MODEL = "models/text-embedding-004"


def get_api_key():
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        pass
    # 1. Environment Variable
    key = os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_KEY")

    # 2. Streamlit Secrets
    if not key and hasattr(st, "secrets"):
        try:
            key = st.secrets.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_KEY")
        except Exception:
            pass

    if key and isinstance(key, str):
        key = key.strip()

    return key if key else None


def configure_genai():
    key = get_api_key()
    if key:
        genai.configure(api_key=key)
        return True
    return False


def chunk_text(text, chunk_size=1500, overlap=150):
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
        self.embeddings = np.array([])
        self._build_index()

    def _build_index(self):
        """Creates vector embeddings for all document chunks in batch."""
        if not self.chunks:
            return

        configure_genai()

        # Batch embed all chunks in a single API call for maximum speed
        try:
            res = genai.embed_content(
                model=EMBEDDING_MODEL,
                content=self.chunks,
                task_type="retrieval_document"
            )
            self.embeddings = np.array(res["embedding"])
        except Exception:
            # Fallback to batch embedding with default model
            try:
                res = genai.embed_content(
                    model="models/embedding-001",
                    content=self.chunks
                )
                self.embeddings = np.array(res["embedding"])
            except Exception:
                # If large batch fails, process in mini-batches of 10
                embs = []
                batch_size = 10
                for i in range(0, len(self.chunks), batch_size):
                    batch = self.chunks[i:i + batch_size]
                    try:
                        b_res = genai.embed_content(
                            model="models/embedding-001",
                            content=batch
                        )
                        embs.extend(b_res["embedding"])
                    except Exception:
                        pass
                self.embeddings = np.array(embs)

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
        if not configure_genai():
            return "⚠️ **Gemini API Key Missing**: Please set `GEMINI_API_KEY` in your environment variables or Streamlit Cloud Secrets.", []

        try:
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
            for model_name in ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-2.5-flash"]:
                try:
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(prompt)
                    return response.text, relevant_chunks
                except Exception as e:
                    if "404" in str(e) or "not found" in str(e).lower() or "not available" in str(e).lower():
                        continue
                    raise e
        except Exception as e:
            err_str = str(e)
            if "Unauthenticated" in err_str or "API_KEY_INVALID" in err_str or "401" in err_str or "PermissionDenied" in err_str:
                return "🔑 **Authentication Failed**: The Gemini API Key configured in Streamlit Secrets or environment variables is invalid or expired.", []
            return f"⚠️ **Error generating answer**: {err_str}", []
