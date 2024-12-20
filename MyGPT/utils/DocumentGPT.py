import time, os
import streamlit as st
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.storage import LocalFileStore
from langchain.memory import ConversationBufferMemory
from langchain.embeddings import CacheBackedEmbeddings
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import UnstructuredFileLoader
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder 
from langchain.schema.runnable import RunnablePassthrough, RunnableLambda

@st.cache_resource(show_spinner="Embedding File...")
def embed_file(
    file, 
    file_dir='../uploads/files', 
    embedding_dir='../uploads/embeddings'):
    file_content = file.read()
    file_path = os.path.join(file_dir, file.name)
    with open(file_path, "wb") as f:
        f.write(file_content)

    cache_dir = LocalFileStore(os.path.join(embedding_dir, file.name))
    splitter = CharacterTextSplitter.from_tiktoken_encoder(
        separator="\n",
        chunk_size=600,
        chunk_overlap=200,
    )

    loader = UnstructuredFileLoader(file_path)
    docs = loader.load_and_split(text_splitter=splitter)
    embeddings = OpenAIEmbeddings()
    cached_embeddings = CacheBackedEmbeddings.from_bytes_store(embeddings, cache_dir)

    vectorstore = FAISS.from_documents(docs, cached_embeddings)
    return vectorstore.as_retriever()

class DocumentGPT:
    def __init__(self,
                 file,
                 model='GPT-3.5-turbo',
                 api_key=None, 
                 memory=ConversationBufferMemory(
                    max_token_limit=120,
                    return_messages=True,           # 문자열 기반이 아닌, ChatPromptTemplate 에서 사용할 수 있는 형태로 반환
                )
        ):
        st.write(os.getcwd())
        self.file = file
        self.llm = ChatOpenAI(
            api_key=api_key,
            model=model,
            temperature=0.1,
        )
        self.memory = memory if 'memory' not in st.session_state else  st.session_state['memory']
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """
            너는 질문에 대해서 오직 주어진 Context을 사용해서 답변 해야 해. 만약, 너가 답을 모르겠다면 꼭 모른다고 말해.
            절대 지어내면 안돼.

            Context: {context}
            """),
            MessagesPlaceholder(variable_name='history'),
            ("human", "{question}")
        ])
        self.retriever = None
        self.__initialize_session()

    def run(self):
        if self.file:
            self.retriever = embed_file(self.file)
            self.__send_message("저는 준비됐습니다. 언제든 질문해주세요 : )", "ai", save=False, stream=False)
            if st.session_state['documentGPT_history']:
                self.__paint_history()
            message = st.chat_input("업로드한 파일에 대해서 질문해 보세요 :)")

            if message:
                self.__send_message(message, "human")

                chain = self.__create_chain()
                response = chain.invoke(message)
                self.__send_message(response.content, 'ai', self.docs, stream=True)

                self.memory.save_context({"input": message}, {"output": response.content})
        else:
            st.markdown("여러분이 질문하고 싶은 파일을 Chatbot에게 연결해 주세요!")
            st.session_state['documentGPT_history'] = []

    def __initialize_session(self):
        if 'documentGPT_history' not in st.session_state:
            st.session_state['documentGPT_history'] = []

        if 'memory' not in st.session_state:
            st.session_state['memory'] = self.memory

    def __save_message(self, message, role, docs):
        st.session_state['documentGPT_history'].append({"message": message, "role": role, 'docs': docs})

    def __send_message(self, message, role, docs=None, save=True, stream=True):
        with st.chat_message(role):
            if stream:
                st.write_stream(self.__stream_data(message))
            else:
                st.markdown(message)

            if docs:
                with st.popover("📋 사용 정보"):
                    for doc in docs:
                        st.markdown("🟢 " + doc)
        if save:
            self.__save_message(message, role, docs)

    def __paint_history(self):
        for message in st.session_state['documentGPT_history']:
            self.__send_message(message['message'], message['role'], message['docs'], save=False, stream=False)

    def __format_docs(self, docs):
        self.docs = [document.page_content for document in docs]
        return "\n\n".join(self.docs)
    
    def __stream_data(self, message):
        for word in message.split(" "):
            yield word + " "
            time.sleep(0.07)
    
    def __load_memory(self, _):
        return self.memory.load_memory_variables({})['history']

    def __create_chain(self):
        chain = {
            'context': self.retriever | RunnableLambda(self.__format_docs),
            'question': RunnablePassthrough(),
            'history': self.__load_memory,
        } | self.prompt | self.llm

        return chain