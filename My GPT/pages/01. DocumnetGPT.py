import streamlit as st
from utils.DocumentGPT import DocumentGPT

st.set_page_config(
    page_title="DocumentGPT",
    page_icon="📖",
    layout='wide',
)

st.title("Document GPT")
with st.sidebar:
    model = st.selectbox("GPT 모델", ('gpt-3.5-turbo', 'gpt-4-turbo', 'gpt-4o-mini', 'gpt-4o'))
    file = st.file_uploader("파일 업로드", type=["pdf", "txt", "docx"])

app = DocumentGPT(file, model)
app.run()
