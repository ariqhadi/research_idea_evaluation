import streamlit as st

age = st.slider("How old are you?", 0, 5)
st.write("I'm ", age, "years old")