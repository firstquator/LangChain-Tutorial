import time, os, json
import streamlit as st
from openai import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import UnstructuredFileLoader
from langchain.retrievers import WikipediaRetriever
from langchain.prompts import PromptTemplate

DIR_NAME = "MyGPT"
BASE_DIR = os.getcwd() if DIR_NAME in os.getcwd() else os.path.join(os.getcwd(), DIR_NAME)
QUIZ_DIR = os.path.join(BASE_DIR, 'uploads/quiz_files')

# -----------------------------------------------------------------------------------------------------------------------------

@st.cache_resource(show_spinner="Loading File...")
def split_file(
        file,
        file_dir=QUIZ_DIR,
):
    file_content = file.read()
    file_path = os.path.join(file_dir, file.name)
    with open(file_path, "wb") as f:
        f.write(file_content)

    splitter = CharacterTextSplitter.from_tiktoken_encoder(
        separator="\n",
        chunk_size=600,
        chunk_overlap=100,
    )

    loader = UnstructuredFileLoader(file_path)
    docs = loader.load_and_split(text_splitter=splitter)

    return docs

@st.cache_resource(show_spinner="Searching Wikipedia . . .")
def wiki_search(term, top_k=5):
    retriever = WikipediaRetriever(top_k_results=top_k, lang='en')
    docs = retriever.get_relevant_documents(term)

    return docs

@st.cache_resource(show_spinner="Making quiz . . .")
def run_quiz_chain(_questions_chain, _docs, topic, nums, num_choices, level, language):
    response = _questions_chain.invoke(_docs)

    return response

class QuizGPT:
    def __init__(
            self,
            type='file',
            file=None,
            topic=None,
            nums=15,
            num_choices=3,
            level=2,
            language='korean',
            model='gpt-4o-mini',
            api_key=None,
        ):
        self.file = file
        self.topic = topic
        if type == 'file':
            self.docs = split_file(file)
        elif type == 'wiki':
            self.docs = wiki_search(topic)

        self.type = type
        self.nums = nums
        self.num_choices = num_choices
        self.level = level
        self.language = language

        self.llm = ChatOpenAI(
            api_key=api_key,
            temperature=0.1,
            model=model,
        ).bind(
            function_call={
                "name": "create_quiz",
            },
            functions=[
                self.__create_function_schema(),
            ]
        )

        self.quiz_prompt = PromptTemplate.from_template(
            """
                You are a helpful assistant that is role playing as a teacher.
                    
                Based ONLY on the following Context make {nums} questions to test the user's knowledge about the text.
                
                Each question should have {num_choices} answers, One of the answers must be correct and the rest must be incorrect.
                    
                Quiz has 1 to 3 levels of difficulty, and the higher the difficulty, the more difficult it is.

                Please set the quiz difficulty level to {level} levels and make a quiz.

                Please translate all the problems into {language}.
                    
                Context: {context}
            """
        )

    def run(self):
        question_chain = self.__create_quiz_chain()
        response = run_quiz_chain(
            question_chain, 
            self.docs, 
            self.topic if self.topic else self.file.name,
            self.nums,
            self.num_choices,
            self.level,
            self.language)
        questions = self.__load_questions(response.additional_kwargs["function_call"]["arguments"])
        self.__make_quiz_form(questions)


    def __make_quiz_form(self, questions):
        with st.form('questions_form'):
            correct = 0
            question_count = len(questions)
            for idx, question in enumerate(questions):
                st.markdown(f"#### 💡 Q{idx+1}. {question['question']}")
                select = st.radio(
                    "정답을 고르세요.", 
                    [answer['answer'] for answer in question['answers']], 
                    index=None,
                    label_visibility="hidden")
                
                if {'answer': select, 'correct': True} in question['answers']:
                    st.success("✅ 정답!")
                    correct += 1
                elif select is not None:
                    st.error("❌ 오답!")

                if correct == question_count:
                    st.balloons()

            submit_btn = st.form_submit_button()

    def __create_quiz_chain(self):
        return {
            'context': self.__format_docs,
            'nums': lambda x: self.nums,
            'num_choices': lambda x: self.num_choices,
            'level': lambda x: self.level,
            'language': lambda x: self.language,
        } | self.quiz_prompt | self.llm

    def __format_docs(self, docs):
        docs = [document.page_content for document in docs]
        return "\n\n".join(docs)

    def __load_questions(self, response):
        return json.loads(response)['questions']

    def __create_function_schema(self):
        function_schema = {
            "name": "create_quiz",
            "description": "function that takes a list of questions and answers and returns a quiz",
            "parameters": {
                "type": "object",
                "properties": {
                    "questions": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "question": {
                                    "type": "string",
                                },
                                "answers": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "answer": {
                                                "type": "string",
                                            },
                                            "correct": {
                                                "type": "boolean",
                                            },
                                        },
                                        "required": ["answer", "correct"],
                                    },
                                },
                            },
                            "required": ["question", "answers"],
                        },
                    },
                },
                "required": ["questions"],
            },
        }

        return function_schema