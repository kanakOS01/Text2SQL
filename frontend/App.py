# File: app.py
import streamlit as st
from pathlib import Path
import importlib
import sys

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

# Import route handlers
from routes.auth_routes import handle_auth # type: ignore
from routes.query_routes import handle_query
from routes.home_routes import handle_home
from utils.session_manager import check_session, init_session

class Router:
    def __init__(self):
        self.routes = {
            "/": handle_home,
            "/auth": handle_auth,
            "/query": handle_query
        }

    def route(self, path):
        if path in self.routes:
            return self.routes[path]()
        return self.routes["/"](error="Page not found")

# Initialize session state
init_session()

# Create sidebar navigation
def sidebar_nav():
    st.sidebar.title("Navigation")
    
    # Define route mapping for sidebar
    routes = {
        "Home": "/",
        "Login/Register": "/auth",
        "SQL Query": "/query"
    }
    
    # Create navigation
    selection = st.sidebar.radio("Go to", list(routes.keys()))
    return routes[selection]

# Main app
def main():
    st.set_page_config(
        page_title="SQL Query Assistant",
        page_icon="🔍",
        layout="wide"
    )

    # Initialize router
    router = Router()

    # Get current route from sidebar
    current_route = sidebar_nav()

    # Update session state with current route
    st.session_state.current_route = current_route

    # Handle routing
    router.route(current_route)

if __name__ == "__main__":
    main()

# File: routes/auth_routes.py
import streamlit as st
from utils.db_manager import init_db, register_user, login_user
from utils.session_manager import set_user_session, clear_session

def handle_auth():
    st.title("Authentication")
    
    if st.session_state.is_authenticated:
        st.success(f"Logged in as {st.session_state.username}")
        if st.button("Logout"):
            clear_session()
            st.rerun()
        return

    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        login_form()
    
    with tab2:
        register_form()

def login_form():
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if login_user(username, password):
                set_user_session(username)
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid credentials")

def register_form():
    with st.form("register_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submit = st.form_submit_button("Register")
        
        if submit:
            if password != confirm_password:
                st.error("Passwords don't match")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters")
            else:
                if register_user(username, password):
                    st.success("Registration successful! Please login.")
                else:
                    st.error("Username already exists")

# File: routes/query_routes.py
import streamlit as st
from utils.db_manager import execute_query, get_schema
from utils.session_manager import check_session

def handle_query():
    if not check_session():
        st.warning("Please login to access this page")
        return
    
    st.title("SQL Query Interface")
    
    # Schema viewer
    with st.expander("Database Schema"):
        schema = get_schema()
        for table, columns in schema.items():
            st.subheader(f"Table: {table}")
            st.code(columns)
    
    # Query interface
    query = st.text_area("Enter SQL Query", height=150)
    
    if st.button("Execute Query"):
        if query:
            results, error = execute_query(query)
            if error:
                st.error(f"Error: {error}")
            else:
                st.success("Query executed successfully!")
                st.dataframe(results)
        else:
            st.warning("Please enter a query")

# File: routes/home_routes.py
import streamlit as st

def handle_home(error=None):
    st.title("Welcome to SQL Query Assistant")
    
    if error:
        st.error(error)
        return
    
    if st.session_state.is_authenticated:
        st.success(f"Welcome back, {st.session_state.username}!")
    else:
        st.info("Please login to use the SQL Query feature")
    
    st.write("""
    ### Features:
    - Write and execute SQL queries
    - View database schema
    - Explore sample data
    
    Use the sidebar navigation to access different features.
    """)

# File: utils/session_manager.py
import streamlit as st

def init_session():
    if 'is_authenticated' not in st.session_state:
        st.session_state.is_authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'current_route' not in st.session_state:
        st.session_state.current_route = "/"

def check_session():
    return st.session_state.is_authenticated

def set_user_session(username):
    st.session_state.is_authenticated = True
    st.session_state.username = username

def clear_session():
    st.session_state.is_authenticated = False
    st.session_state.username = None

# File: utils/db_manager.py
import sqlite3
import pandas as pd
import hashlib
from datetime import datetime

def init_db():
    conn = sqlite3.connect('app.db')
    c = conn.cursor()
    
    # Create users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY, password TEXT, created_date TEXT)''')
    
    # Create sample tables
    c.execute('''CREATE TABLE IF NOT EXISTS employees
                 (id INTEGER PRIMARY KEY, name TEXT, department TEXT, salary REAL)''')
    
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def register_user(username, password):
    conn = sqlite3.connect('app.db')
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

def login_user(username, password):
    conn = sqlite3.connect('app.db')
    c = conn.cursor()
    c.execute('SELECT password FROM users WHERE username=?', (username,))
    result = c.fetchone()
    conn.close()
    if result:
        return result[0] == hash_password(password)
    return False

def execute_query(query):
    conn = sqlite3.connect('app.db')
    try:
        df = pd.read_sql_query(query, conn)
        return df, None
    except Exception as e:
        return None, str(e)
    finally:
        conn.close()

def get_schema():
    return {
        "employees": """
        CREATE TABLE employees (
            id INTEGER PRIMARY KEY,
            name TEXT,
            department TEXT,
            salary REAL
        )
        """
    }

# Initialize database on import
init_db()