import streamlit as st
from setup import init_app
from db import get_user

init_app()

username = st.session_state.get("username")
if username:
    user = get_user(username)
    if user:
        st.switch_page("pages/dashboard.py")

st.title("🔐 Login")

username = st.text_input("Enter your username:")

if st.button("Login"):
    if not username:
        st.warning("Please enter your username.")
    else:
        user = get_user(username)
        if user:
            st.session_state.username = username
            st.switch_page("pages/dashboard.py")

        else:
            st.error("User not found. Please check your username or create an account.")