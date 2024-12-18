import streamlit as st

st.title("Title")

with st.sidebar:
    st.title("Sidebar Title")
    st.text_input("Input your name : ")

tab_one, tab_two, tab_three = st.tabs(['A', 'B', 'C'])

with tab_one:
    st.write("a")

with tab_two:
    st.write("b")

with tab_three:
    st.write("c")
