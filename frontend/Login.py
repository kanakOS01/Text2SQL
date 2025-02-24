import streamlit as st
import sqlite3
import hashlib
from datetime import datetime

st.set_page_config(page_title="Login/Register", page_icon="🔐")

# Initialize connection to SQLite database
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY, password TEXT, created_date TEXT)''')
    conn.commit()
    conn.close()

# Hash password
def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# User registration
def register_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        hash_pw = hash_password(password)
        c.execute('INSERT INTO users VALUES (?,?,?)', 
                 (username, hash_pw, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# User login
def login_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT password FROM users WHERE username=?', (username,))
    result = c.fetchone()
    conn.close()
    if result is not None:
        return result[0] == hash_password(password)
    return False

# Initialize the database
init_db()

st.title("Login/Register")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(['Login', 'Register'])
    
    with tab1:
        login_username = st.text_input('Username', key='login_username')
        login_password = st.text_input('Password', type='password', key='login_password')
        
        if st.button('Login'):
            if login_user(login_username, login_password):
                st.session_state.logged_in = True
                st.session_state.username = login_username
                st.success('Logged in successfully!')
                st.rerun()
            else:
                st.error('Invalid username or password')
    
    with tab2:
        reg_username = st.text_input('Username', key='reg_username')
        reg_password = st.text_input('Password', type='password', key='reg_password')
        reg_password_confirm = st.text_input('Confirm Password', type='password')
        
        if st.button('Register'):
            if reg_password != reg_password_confirm:
                st.error('Passwords do not match')
            elif len(reg_password) < 6:
                st.error('Password must be at least 6 characters long')
            else:
                if register_user(reg_username, reg_password):
                    st.success('Registration successful! Please login.')
                else:
                    st.error('Username already exists')
else:
    st.success(f'Currently logged in as {st.session_state.username}')
    if st.button('Logout'):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.rerun()
