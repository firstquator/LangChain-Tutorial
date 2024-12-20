import streamlit as st

pages = {
    "GPT MENU": [
        st.Page("./navigations/00. home.py", title="🏠 HOME"),
        st.Page('./navigations/01. DocumenetGPT.py', title="📖 DocumentGPT"),
        st.Page('./navigations/02. TranslateGPT.py', title="🎤 TranslateGPT"),
    ]
}
navigations = st.navigation(pages)

navigations.run()