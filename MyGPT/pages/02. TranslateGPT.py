import streamlit as st
from utils.TranslateGPT import TranslateGPT

st.set_page_config(
    page_title="TranslateGPT",
    page_icon="🎤",
    layout='wide',
)

st.title("Translate GPT")

# -----------------------------------------------------------------------------------------------------------------------------


if "OPENAI_API_KEY" not in st.secrets:
    with st.sidebar:
            translateGPT = TranslateGPT(api_key=st.secrets['OPENAI_API_KEY'])
            col1, col2 = st.columns(2)
            with col1:
                translateBtn = st.button('번역하기')
            if translateBtn:
                with st.status("🟢 마이크 ON") as status:
                    translateGPT.input_voice()

                    status.update(label="🔴 마이크 OFF", expanded=False)
            with col2:
                if st.button('초기화'):
                    st.session_state['translateGPT_history'] = []

            voice = st.selectbox("보이스 선택", ('alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer'))
            language = st.selectbox("번역 언어", ("English", "Japenese", "Chinese", "German", "Spanish"))

    if translateGPT.text:
        translateGPT.run(voice, language)

else:
    st.markdown("### 🔴 당신의 OPENAI API KEY를 설정해 주세요.")