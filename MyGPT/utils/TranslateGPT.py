import time, os
import streamlit as st
import speech_recognition as sr
from openai import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.callbacks import StreamingStdOutCallbackHandler

DIR_NAME = "MyGPT"
BASE_DIR = os.getcwd() if DIR_NAME in os.getcwd() else os.path.join(os.getcwd(), DIR_NAME)
AUDIO_DIR = os.path.join(BASE_DIR, 'uploads/audios')

# -----------------------------------------------------------------------------------------------------------------------------
class TranslateGPT:
    def __init__(self, 
            model='gpt-4o-mini',
            api_key=None,
            audio_path=AUDIO_DIR,
        ):
        self.audio_path = audio_path
        self.client = OpenAI(
            api_key=api_key
        )
        self.llm = ChatOpenAI(
            api_key=api_key,
            temperature=0.1,        # 창의성 (0 ~ 2)
            model=model,            # 사용 모델 지정 (Default : gpt-3.5-turbo)
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

        self.audio = None
        self.text = None
        self.__initialize_chat_histroy()
        self.__create_chain()

    def run(self, voice, language):
        self.__send_message(self.text, 'human')
        self.__translate(language, voice)

    def input_voice(self):
        self.audio = st.audio_input("🎤 : 녹음 시작 / 🗑 : 음성 초기화")
        if self.audio:
            with st.spinner("번역 중 . . ."):
                self.text = self.__speech_to_text(self.audio)

    def paint_history(self):
        for message in st.session_state['translateGPT_history']:
            self.__send_message(
                message['message'], 
                message['role'], 
                audio_file=message['audio_file'], 
                save=False, 
                stream=False)

    def __initialize_chat_histroy(self):
        if 'translateGPT_history' not in st.session_state:
            st.session_state['translateGPT_history'] = []

    def __save_message(self, message, role, audio_file=None):
        st.session_state['translateGPT_history'].append({
                "message": message, 
                "role": role, 
                "audio_file": audio_file,
            }
        )

    def __send_message(self, message, role, audio_file=None, save=True, stream=True, autoplay=False):
        if role == 'human':
            self.__paint_human_message(message, stream=stream)
        elif role == 'ai':
            self.__paint_ai_message(message, audio_file=audio_file, autoplay=autoplay, stream=stream)

        if save:
            self.__save_message(message, role, audio_file=audio_file)

    def __paint_human_message(self, message, stream=True):
        with st.chat_message('human'):
            if stream:
                st.write_stream(self.__stream_data(message))
            else:
                st.markdown(message)
    
    def __paint_ai_message(self, message, audio_file=None, stream=True, autoplay=False):
        col1, col2 = st.columns([2, 1])
        with col1:
            with st.chat_message('ai'):
                if stream:
                    st.write_stream(self.__stream_data(message))
                else:
                    st.markdown(message)
        with col2:
            if audio_file:
                st.audio(audio_file, format='audio/mp3', autoplay=autoplay)

    def __stream_data(self, message):
        for word in message.split(" "):
            yield word + " "
            time.sleep(0.07)

    def __translate(self, language, voice):
        self.translated_text = self.chain.invoke({'languege': language, 'question': self.text}).content
        self.__text_to_speech(voice)

        # with open(os.path.join(self.audio_path, 'output.mp3'), 'rb') as audio_file:
        audio_file = audio_file.read()
        self.__send_message(self.translated_text, 'ai', audio_file=audio_file, autoplay=True)
        

    def __text_to_speech(self, voice="alloy"):
        with self.client.audio.speech.with_streaming_response.create(
            model="tts-1",
            voice=voice,
            input=self.translated_text,
        ) as response:
            response.stream_to_file(os.path.join(self.audio_path, "output.mp3"))

    def __speech_to_text(self, audio):
        transcription = self.client.audio.transcriptions.create(
            model='whisper-1',
            file=audio,
            language='ko'
        )

        return transcription.text
    
    def __create_chain(self):
        self.chain = self.prompt | self.llm
