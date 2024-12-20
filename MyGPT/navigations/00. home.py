import os
import streamlit as st
from utils.home import BasicGPT

def move_to_parent_directory():
    # 현재 작업 디렉토리 가져오기
    current_dir = os.getcwd()
    print(f"현재 디렉토리: {current_dir}")
    
    # 상위 디렉토리 경로 계산
    parent_dir = os.path.dirname(current_dir)
    
    # 상위 디렉토리로 이동
    os.chdir(parent_dir)
    
    # 이동 후 현재 작업 디렉토리 확인
    new_dir = os.getcwd()
    st.write(f"상위 디렉토리로 이동 후: {new_dir}")

st.set_page_config(
    page_title="GPT Application Home",
    page_icon="🖥️",
    layout='wide',
)

st.title("⛪ GPT Application Home")
st.markdown('---')
move_to_parent_directory()
col1, col2 = st.columns([1, 1], vertical_alignment='top')

with col1:
    st.markdown("""
        ## 📖 DocumentGPT
        \n

        **법률, 의학 등 어려운 문서를 빠르게 파악하고 싶다면 ?**
        \n
        내용이 길거나, 전문적인 내용들을 AI에게 전달하여, 빠르게 내용을 파악하고 
        \n
        우리가 궁금해하는 내용을 질문하면, AI가 그에 맞는 내용을 빠르게 답변해줍니다.
        \n
        빠르게 문서를 요약하고, 내용을 파악하는 문서 파악 AI를 사용해보세요 !!      
    """)

with col2:
    st.markdown("""
        ## 🎤 TranslateGPT
        \n

        **음성을 원하는 언어로 빠르게 번역하고 싶다면 ?**
        \n
        실시간으로 내가 말한 말을 원하는 언어로 번역하고, 읽어주는 통역사 AI를 사용해 보세요 !!
    """)

st.markdown('---')

def take_open_api_key():
    if "OPENAI_API_KEY" not in st.session_state:
        st.session_state['OPENAI_API_KEY'] = st.session_state.open_ai_key
    else:
        st.info(f"🟢 API 키 입력 완료 !!")

if "OPENAI_API_KEY" in st.session_state:
    with st.sidebar:
        if st.button('🔄 대화 초기화'):
            st.session_state['home_history'] = []
        model = st.selectbox("🧠 GPT 모델", ('gpt-3.5-turbo', 'gpt-4-turbo', 'gpt-4o-mini', 'gpt-4o'))
            
    app = BasicGPT(api_key=st.session_state['OPENAI_API_KEY'], model=model)
    app.run()

else:
    st.markdown("### 🔴 당신의 OPENAI API KEY를 입력해 주세요.")
    with st.form(key="API_KEY"):
        st.text_input("OPENAI API KEY", type='password', key="open_ai_key")
        st.form_submit_button("등록", on_click=take_open_api_key)

