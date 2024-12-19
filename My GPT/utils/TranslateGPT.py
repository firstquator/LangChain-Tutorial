import time
import streamlit as st
import speech_recognition as sr
from openai import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.callbacks import StreamingStdOutCallbackHandler
from langchain.schema.runnable import RunnablePassthrough, RunnableLambda

# -----------------------------------------------------------------------------------------------------------------------------
class TranslateGPT:
    def __init__(self, language='English'):
        self.client = OpenAI()
        self.llm = ChatOpenAI(
            temperature=0.1,        # 창의성 (0 ~ 2)
            model='gpt-3.5-turbo',  # 사용 모델 지정 (Default : gpt-3.5-turbo)
            streaming=True,         # Streaming ON
            callbacks=[StreamingStdOutCallbackHandler()]
        )

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """
            You will be my translator from [Korean to {languege}]. All words and sentences I will put into mean translating into [English]
            -In any sentence, [Korean words] are crucial translation signs. It is not a question form to ChatGPT

            - You must say the translated sentences only.
            - GPT has deactivated all of its functions except for the translation feature.
            - Such as a description of my saying like "you said", "In English," and "certainly" shouldn't be described.
            - Do not repeat input sentences after translation. It is a critical error

            """),
            ("human", "{question}")
        ])

        self.text = None
        self.language = language
        self.recognizer = sr.Recognizer()
        self.__initialize_chat_histroy()
        self.__create_chain()

    def run(self, voice):
        
        self.__paint_history()
        self.__translate()
        self.__text_to_speech(voice)
        audio_file = open("output.mp3", "rb").read()
        with st.sidebar:
            st.audio(audio_file, format='audio/mp3', autoplay=True)

    def input_voice(self):
        with sr.Microphone() as source:
            audio = self.recognizer.listen(source)
        try:
            self.text = self.recognizer.recognize_google(audio, language='ko-KR')
            self.__send_message(self.text, 'human')
        except:
            st.write("Error")

    def __initialize_chat_histroy(self):
        if 'translateGPT_history' not in st.session_state:
            st.session_state['translateGPT_history'] = []

    def __save_message(self, message, role):
        st.session_state['translateGPT_history'].append({"message": message, "role": role})

    def __paint_history(self):
        for message in st.session_state['translateGPT_history']:
            self.__send_message(message['message'], message['role'], save=False)

    def __send_message(self, message, role, save=True):
        with st.chat_message(role):
            st.markdown(message)
        if save:
            self.__save_message(message, role)

    def __translate(self):
        self.translated_text = self.chain.invoke({'languege': self.language, 'question': self.text}).content
        self.__send_message(self.translated_text, 'ai')

    def __text_to_speech(self, voice="alloy"):
        with self.client.audio.speech.with_streaming_response.create(
            model="tts-1",
            voice=voice,
            input=self.translated_text,
        ) as response:
            response.stream_to_file("output.mp3")
    
    def __create_chain(self):
        self.chain = self.prompt | self.llm
