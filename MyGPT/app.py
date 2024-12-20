import streamlit as st

pages = {
    "GPT MENU": [
        st.Page("./pages/00. home.py", title="🏠 HOME"),
        st.Page('./pages/01. DocumenetGPT.py', title="📖 DocumentGPT"),
        st.Page('./pages/02. TranslateGPT.py', title="🎤 TranslateGPT"),
    ]
}
navigations = st.navigation(pages)

navigations.run()