import streamlit as st
from utils.DocumentGPT import DocumentGPT

st.set_page_config(
    page_title="DocumentGPT",
    page_icon="📖",
    layout='wide',
)

st.title("Document GPT")

def take_open_api_key():
    if "OPENAI_API_KEY" not in st.session_state:
        st.session_state['OPENAI_API_KEY'] = st.session_state.open_ai_key
    else:
        st.info(f"🟢 API 키 입력 완료 !!")

if "OPENAI_API_KEY" in st.session_state:
    with st.sidebar:
            model = st.selectbox("GPT 모델", ('gpt-3.5-turbo', 'gpt-4-turbo', 'gpt-4o-mini', 'gpt-4o'))
            file = st.file_uploader("파일 업로드", type=["pdf", "txt", "docx"])
            
    app = DocumentGPT(file, model, api_key=st.session_state['OPENAI_API_KEY'])
    app.run()

else:
    with st.form(key="API_KEY"):
        st.text_input("OPENAI API KEY", type='password', key="open_ai_key")
        st.form_submit_button("등록", on_click=take_open_api_key)

    st.markdown("### 🔴 당신의 OPENAI API KEY를 설정해 주세요.")