import time, os
import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder 
from langchain.schema.runnable import RunnablePassthrough, RunnableLambda

class BasicGPT:
    def __init__(
            self,
            model='gpt-4o',
            memory=ConversationBufferMemory(
                max_token_limit=120,
                return_messages=True,
            ),
            api_key=None):
        
        self.llm = ChatOpenAI(
            api_key=api_key,
            model=model,
            temperature=0.1,
        )

        self.memory = memory if 'memory' not in st.session_state else  st.session_state['memory']
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """
            질문하는 내용을 잘 답해줘. 이 때, 이전 대화기록이 있으면 참고해줘.
            """),
            MessagesPlaceholder(variable_name='history'),
            ("human", "{question}")
        ])

        self.__initialize_session()

    def run(self):
        if st.session_state['home_history']:
            self.__paint_history()

        message = st.chat_input("AI에게 질문해 보세요 :)")

        if message:
            self.__send_message(message, "human")

            chain = self.__create_chain()
            response = chain.invoke(message)

            self.__send_message(response.content, 'ai', stream=True)

            self.memory.save_context({"input": message}, {"output": response.content})

    def __initialize_session(self):
        if 'home_history' not in st.session_state:
            st.session_state['home_history'] = []

        if 'memory' not in st.session_state:
            st.session_state['memory'] = self.memory
    
    def __save_message(self, message, role):
        st.session_state['home_history'].append({"message": message, "role": role})

    def __send_message(self, message, role, save=True, stream=True):
        with st.chat_message(role):
            if stream:
                st.write_stream(self.__stream_data(message))
            else:
                st.markdown(message)

        if save:
            self.__save_message(message, role)

    def __paint_history(self):
        for message in st.session_state['home_history']:
            self.__send_message(message['message'], message['role'], save=False, stream=False)

    def __stream_data(self, message):
        for word in message.split(" "):
            yield word + " "
            time.sleep(0.07)

    def __load_memory(self, _):
        return self.memory.load_memory_variables({})['history']
    
    def __create_chain(self):
        chain = {
            'question': RunnablePassthrough(),
            'history': self.__load_memory,
        } | self.prompt | self.llm

        return chain