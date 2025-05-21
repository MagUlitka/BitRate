import streamlit as st
from setup import init_app
from db import get_user

init_app()

username = st.session_state.get("username")
if username:
    user = get_user(username)
    if user:
        st.switch_page("pages/dashboard.py")


with st.container():
    st.markdown(
            """
            <div style="text-align: center; padding-top: 20vh;">
                <h1>💱 BitRate Exchange Simulator</h1>
                <p>Simulate buying and selling Bitcoin with virtual PLN.<br>Learn how crypto exchanges work without risking real money.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    left, middle1, middle2, right = st.columns([2, 3,3, 2])
    with middle1:
        if st.button("Get Started"):
            st.switch_page("pages/create_account.py")
    with middle2:
        if st.button("Already have an account?"):
            st.switch_page("pages/login.py")