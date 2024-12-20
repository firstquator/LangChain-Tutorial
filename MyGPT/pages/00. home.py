import streamlit as st

st.set_page_config(
    page_title="GPT Application",
    page_icon="🎈"
)

st.title("GPT Application")

if "api_key" not in st.session_state:
    st.session_state.api_key = set()

def take_open_api_key():
    if "OPENAI_API_KEY" not in st.secrets:
        st.secrets['OPENAI_API_KEY'] = st.session_state.open_ai_key
    else:
        st.info(f"🟢 API 키 입력 완료 !!")

with st.form(key="OPENAI_API_KEY"):
    st.text_input("OPENAI API KEY", type='password', key="open_ai_key")
    st.form_submit_button("등록", on_click=take_open_api_key)

st.markdown('---')

st.secrets['OPENAI_API_KEY']