import streamlit as st

from pdf_reader import extract_text
from summary_agent import generate_summary
from quiz_agent import generate_quiz

st.title("AI Study Buddy")

uploaded_file = st.file_uploader(
    "Upload PDF",
    type=["pdf"]
)

if uploaded_file:

    text = extract_text(uploaded_file)

    st.success("PDF Uploaded Successfully")

    if st.button("Generate Summary"):

        summary = generate_summary(text)

        st.subheader("Summary")
        st.write(summary)

    if st.button("Generate Quiz"):

        quiz = generate_quiz(text)

        st.subheader("Quiz")
        st.write(quiz)