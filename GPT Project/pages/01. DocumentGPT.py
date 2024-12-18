import time
import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import UnstructuredFileLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import CacheBackedEmbeddings
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.storage import LocalFileStore
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough

st.set_page_config(
    page_title="DocumentGPT",
    page_icon="📖"
)

@st.cache_data(show_spinner="Embedding File...")
def embed_file(file):
    file_content = file.read()
    file_path = f"./.cache/files/{file.name}"
    with open(file_path, "wb") as f:
        f.write(file_content)

    cache_dir = LocalFileStore(f'../.cache/embeddings/{file.name}')
    # Token 방식으로 텍스트를 인식
    splitter = CharacterTextSplitter.from_tiktoken_encoder(
        separator="\n",                 # 특정 기준으로 분할
        chunk_size=600,
        chunk_overlap=100,
    )

    # UnstruturedFileLoader : 많은 파일들을 불러올 수 있음. docx, xlsx, pdf, ppt, txt 등 많은 파일들을 불러올 수 있는 Loader
    loader= UnstructuredFileLoader("./files/대입합불정리_세특포함_디랩.pdf")
    docs = loader.load_and_split(text_splitter=splitter)                                                                                                                                           
    embeddings = OpenAIEmbeddings()
    cacehd_embeddings = CacheBackedEmbeddings.from_bytes_store(
        embeddings, cache_dir
    )
    # 캐시를 적용하여 임베딩
    # vectorstore = Chroma.from_documents(docs, cacehd_embeddings)
    vectorstore = FAISS.from_documents(docs, cacehd_embeddings)
    retriver = vectorstore.as_retriever()

    return retriver

def send_message(message, role, save=True):
    with st.chat_message(role):
        st.markdown(message)
    
    if save:
        st.session_state['messages'].append({"message": message, "role": role})

def paint_history():
    for message in st.session_message['message']:
        send_message(message['message'], message['role'], save=False)

st.title("Document GPT")

# 파일 Upload
st.markdown("""
여러분이 질문하고 싶은 파일을 Chatbot에게 연결해 주세요!
""")

with st.sidebar:
    file = st.file_uploader("Upload a.txt .pdf or .docx file", type=["pdf", "txt", "docx"])

if file:
    retriever = embed_file(file)
    send_message("저는 준비됐습니다. 언제든 질문해주세요 : )", "ai")
    paint_history()
    message = st.chat_input("업로드한 파일에 대해서 질문해 보세요 :)")
    if message:
        send_message(message, "human")

else:
    st.session_state['message'] = []