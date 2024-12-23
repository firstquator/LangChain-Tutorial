import time, os, json
import streamlit as st
from utils.QuizGPT import QuizGPT
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import UnstructuredFileLoader
from langchain.retrievers import WikipediaRetriever
from langchain.schema import BaseOutputParser

st.set_page_config(
    page_title="QuizGPT",
    page_icon="📝",
    layout='wide',
)

st.title("Quiz GPT")

# -----------------------------------------------------------------------------------------------------------------------------

def take_open_api_key():
    if "OPENAI_API_KEY" not in st.session_state:
        st.session_state['OPENAI_API_KEY'] = st.session_state.open_ai_key
    else:
        st.info(f"🟢 API 키 입력 완료 !!")

quizGPT = None
if "OPENAI_API_KEY" in st.session_state:
    with st.sidebar:
        with st.popover("⚙️ 설정"):
            st.markdown('#### 퀴즈 생성 설정')
            nums = st.number_input(
                "문제 개수",
                value=10, 
                min_value=1, 
                max_value=20,
                step=1
            )

            num_choices = st.number_input(
                "객관식 보기 개수",
                value=3, 
                min_value=1, 
                max_value=5,
                step=1
            )
            
            option_map = {1: 'Easy', 2: 'Hard', 3: 'Very Hard'}
            level = st.segmented_control(
                "난이도",
                options=option_map.keys(),
                format_func=lambda option: option_map[option],
                selection_mode='single',
            )

            language = st.selectbox("언어 선택", ['한국어', 'English'])
        choice = st.selectbox("사용방식을 설정하세요.", ("File", "Wikipedia Article"))

        if choice == 'File':
            file = st.file_uploader("💾 파일 업로드", type=['pdf', 'txt', 'docx'])
            if file:
                quizGPT = QuizGPT(type='file', file=file, nums=nums, num_choices=num_choices, level=level, language=language)
        elif choice == "Wikipedia Article":
            topic = st.text_input("Search Wikipedia . . .")
            if topic:
                quizGPT = QuizGPT(type='wiki', topic=topic, nums=nums, num_choices=num_choices, level=level, language=language)
        

    if not quizGPT:
        st.markdown("""
            환영합니다!
                    
            당신이 업로드한 위키백과 기사나 파일에서 퀴즈를 만들어 지식을 테스트하고 공부하는 데 도움을 드리겠습니다.

            사이드바에서 파일을 업로드하거나 위키백과에서 검색하는 것으로 시작하세요.

        """)

    else:
        response = quizGPT.run()
else:
    st.markdown("### 🔴 당신의 OPENAI API KEY를 입력해 주세요.")
    with st.form(key="API_KEY"):
        st.text_input("OPENAI API KEY", type='password', key="open_ai_key")
        st.form_submit_button("등록", on_click=take_open_api_key)

    # with st.form('questions_form'):
    #     for question in response['questions']:
    #         value = st.radio("Select an option", [answer['answer'] for answer in question['answer']], index=None)

    #         if {"answer":value, "correct": True} in question['question']:
    #             st.success("Correct !!")
    #         elif value is not None:
    #             st.error("Wrong !!")
    #     button = st.form_submit_button()