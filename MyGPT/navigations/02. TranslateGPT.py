import streamlit as st
from utils.TranslateGPT import TranslateGPT

st.set_page_config(
    page_title="TranslateGPT",
    page_icon="🎤",
    layout='wide',
)

st.title("Translate GPT")

# -----------------------------------------------------------------------------------------------------------------------------

def take_open_api_key():
    if "OPENAI_API_KEY" not in st.session_state:
        st.session_state['OPENAI_API_KEY'] = st.session_state.open_ai_key
    else:
        st.info(f"🟢 API 키 입력 완료 !!")

if "OPENAI_API_KEY" in st.session_state:
    with st.sidebar:
        translateGPT = TranslateGPT(api_key=st.session_state['OPENAI_API_KEY'])

        if st.button('🔄 대화 초기화'):
            st.session_state['translateGPT_history'] = []
            translateGPT.paint_history()

        translateGPT.input_voice()

        voice = st.selectbox("🔊 보이스 선택", ('alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer'))
        language = st.selectbox("🗣️ 번역 언어", ("English", "Korean", " Japenese", "Chinese", "German", "Spanish"))

    if st.session_state['translateGPT_history']:
        translateGPT.paint_history()

    if translateGPT.text:
        translateGPT.run(voice, language)

else:
    st.markdown("### 🔴 당신의 OPENAI API KEY를 입력해 주세요.")
    with st.form(key="API_KEY"):
        st.text_input("OPENAI API KEY", type='password', key="open_ai_key")
        st.form_submit_button("등록", on_click=take_open_api_key)