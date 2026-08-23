import streamlit as st

from pdf_reader import extract_text
from summary_agent import generate_summary
from quiz_agent import generate_quiz
from rag_system import RAGSystem

st.set_page_config(page_title="AI Study Buddy", layout="wide", page_icon="📚")

st.title("📚 AI Study Buddy")
st.write("Upload your study notes or PDF documents to summarize, generate quizzes, or ask specific questions using RAG!")

uploaded_file = st.file_uploader(
    "Upload PDF Document",
    type=["pdf"]
)

if uploaded_file:
    # Extract raw text from PDF
    text = extract_text(uploaded_file)

    if not text or not text.strip():
        st.error("⚠️ **No readable text found in PDF**: The uploaded file (e.g. scanned image PDF or slide conversion without text) does not contain selectable text. Please upload a PDF file containing text.")
    else:
        st.success(f"PDF Uploaded and Extracted Successfully! ({len(text)} characters extracted)")

        # Cache RAG System in Session State to prevent re-indexing on every re-render
        file_id = uploaded_file.name + "_" + str(len(text))
        if "rag_system" not in st.session_state or st.session_state.get("file_id") != file_id:
            with st.spinner("Building RAG Vector Index from document..."):
                st.session_state["rag_system"] = RAGSystem(text)
                st.session_state["file_id"] = file_id
                st.session_state["summary"] = None
                st.session_state["quiz"] = None

        rag_sys = st.session_state["rag_system"]

        col1, col2 = st.columns(2)

        with col1:
            if st.button("📝 Generate Summary", use_container_width=True):
                with st.spinner("Generating Summary..."):
                    st.session_state["summary"] = generate_summary(text)

        with col2:
            if st.button("❓ Generate Quiz", use_container_width=True):
                with st.spinner("Generating Quiz..."):
                    st.session_state["quiz"] = generate_quiz(text)

        # Display Summary if generated
        if st.session_state.get("summary"):
            st.markdown("---")
            st.subheader("📝 Document Summary")
            summary_content = st.session_state["summary"]
            if summary_content and isinstance(summary_content, str):
                st.markdown(summary_content)
            else:
                st.error("Could not generate summary for this document.")

        # Display Quiz if generated
        if st.session_state.get("quiz"):
            st.markdown("---")
            st.subheader("❓ Practice Quiz")
            quiz_content = st.session_state["quiz"]
            if quiz_content and isinstance(quiz_content, str):
                st.markdown(quiz_content)
            else:
                st.error("Could not generate quiz for this document.")

        st.divider()
        st.subheader("🔍 Ask Questions (RAG Q&A)")
        st.write("Ask targeted questions about your uploaded document. The RAG system will retrieve relevant chunks and answer based on document context.")

        user_query = st.text_input("Enter your question:", placeholder="e.g. What are the key concepts explained in this document?")

        if st.button("Get Answer", type="primary"):
            if user_query.strip():
                with st.spinner("Searching document context & generating answer..."):
                    answer, chunks = rag_sys.answer_question(user_query)

                    st.subheader("Answer:")
                    if answer and isinstance(answer, str):
                        st.markdown(answer)
                    else:
                        st.error("Could not generate an answer.")

                    if chunks:
                        with st.expander("📄 View Retrieved Document Chunks (RAG Context)"):
                            for i, chunk in enumerate(chunks, 1):
                                st.markdown(f"**Chunk {i}:**")
                                st.info(chunk)
            else:
                st.warning("Please enter a question before submitting.")
