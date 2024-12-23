import streamlit as st

pages = {
    "GPT MENU": [
        st.Page("./navigations/00. home.py", title="🏠 HOME"),
        st.Page('./navigations/01. DocumenetGPT.py', title="📖 DocumentGPT"),
        st.Page('./navigations/02. TranslateGPT.py', title="🎤 TranslateGPT"),
        st.Page('./navigations/03. QuizGPT.py', title="📝 QuizGPT"),
    ]
}
navigations = st.navigation(pages)

navigations.run()