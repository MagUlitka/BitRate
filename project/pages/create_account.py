import streamlit as st
from setup import init_app
from db import get_user, create_user

init_app()

username = st.session_state.get("username")
if username:
    user = get_user(username)
    if user:
        st.switch_page("pages/dashboard.py")

st.header("🔐 Create Account")
with st.form("account_creation_form"):
    username = st.text_input("Enter your desired username:")
    submitted = st.form_submit_button("Create Account")

    if submitted:
        if not username:
            st.warning("Please enter a username.")
        else:
            if get_user(username):
                st.error("Username already taken. Try another one.")
            else:
                create_user(username)
                st.success(f"Account '{username}' created!")
                st.session_state.username = username
                st.switch_page("pages/dashboard.py")

    st.markdown("---")
if st.button("I already have an account"):
    st.switch_page("pages/login.py")
        
