import streamlit as st
from utils.TranslateGPT import TranslateGPT

st.set_page_config(
    page_title="TranslateGPT",
    page_icon="🎤",
    layout='wide',
)

st.title("Translate GPT")

# -----------------------------------------------------------------------------------------------------------------------------


with st.sidebar:
    translateGPT = TranslateGPT()
    if st.button("번역하기"):
        with st.status("🟢 마이크 ON") as status:
            translateGPT.input_voice()

            status.update(label="🔴 마이크 OFF", expanded=False)

    voice = st.selectbox("보이스 선택", ('alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer'))

if translateGPT.text:
    translateGPT.run(voice)