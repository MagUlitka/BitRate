import streamlit as st
from db import init_db

def init_app():
    st.set_page_config(page_title="BitRate Exchange", layout="centered", initial_sidebar_state="collapsed")
    init_db()