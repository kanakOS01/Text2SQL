import streamlit as st

st.set_page_config(page_title="Home", page_icon="🏠")

st.title("Welcome to SQL Query Assistant")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.warning("Please login or register to use the application")
    st.info("Use the Login/Register page from the sidebar to get started")
else:
    st.success(f"Welcome back, {st.session_state.username}!")
    st.write("""
    This application helps you:
    - Write and execute SQL queries
    - View database schema
    - Explore sample data
    
    Navigate using the sidebar to access different features.
    """)