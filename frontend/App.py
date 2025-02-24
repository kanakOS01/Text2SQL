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

