import streamlit as st

from pdf_reader import extract_text
from summary_agent import generate_summary
from quiz_agent import generate_quiz
from rag_system import RAGSystem

st.set_page_config(page_title="AI Study Buddy", layout="wide")

st.title("📚 AI Study Buddy")
st.write("Upload your study notes or PDF documents to summarize, generate quizzes, or ask specific questions using RAG!")

uploaded_file = st.file_uploader(
    "Upload PDF Document",
    type=["pdf"]
)

if uploaded_file:
    # Extract raw text from PDF
    text = extract_text(uploaded_file)

    st.success("PDF Uploaded and Extracted Successfully!")

    # Cache RAG System in Session State to prevent re-indexing on every re-render
    file_id = uploaded_file.name + "_" + str(len(text))
    if "rag_system" not in st.session_state or st.session_state.get("file_id") != file_id:
        with st.spinner("Building RAG Vector Index from document..."):
            st.session_state["rag_system"] = RAGSystem(text)
            st.session_state["file_id"] = file_id

    rag_sys = st.session_state["rag_system"]

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📝 Generate Summary", use_container_width=True):
            with st.spinner("Generating Summary..."):
                summary = generate_summary(text)
                st.subheader("Document Summary")
                st.write(summary)

    with col2:
        if st.button("❓ Generate Quiz", use_container_width=True):
            with st.spinner("Generating Quiz..."):
                quiz = generate_quiz(text)
                st.subheader("Practice Quiz")
                st.write(quiz)

    st.divider()
    st.subheader("🔍 Ask Questions (RAG Q&A)")
    st.write("Ask targeted questions about your uploaded document. The RAG system will retrieve relevant chunks and answer based on document context.")

    user_query = st.text_input("Enter your question:", placeholder="e.g. What are the key concepts explained in chapter 2?")

    if st.button("Get Answer", type="primary"):
        if user_query.strip():
            with st.spinner("Searching document context & generating answer..."):
                answer, chunks = rag_sys.answer_question(user_query)

                st.subheader("Answer:")
                st.write(answer)

                with st.expander("📄 View Retrieved Document Chunks (RAG Context)"):
                    for i, chunk in enumerate(chunks, 1):
                        st.markdown(f"**Chunk {i}:**")
                        st.info(chunk)
        else:
            st.warning("Please enter a question before submitting.")