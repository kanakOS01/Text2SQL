import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="SQL Query", page_icon="📊")

# Initialize sample database
def init_sample_db():
    conn = sqlite3.connect('sample.db')
    c = conn.cursor()
    
    # Create sample tables
    c.execute('''CREATE TABLE IF NOT EXISTS employees
                 (id INTEGER PRIMARY KEY, name TEXT, department TEXT, salary REAL)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS departments
                 (id INTEGER PRIMARY KEY, name TEXT, location TEXT)''')
    
    # Add sample data if tables are empty
    c.execute('SELECT COUNT(*) FROM employees')
    if c.fetchone()[0] == 0:
        employees_data = [
            (1, 'John Doe', 'IT', 75000),
            (2, 'Jane Smith', 'HR', 65000),
            (3, 'Bob Johnson', 'Sales', 80000),
            (4, 'Alice Brown', 'IT', 72000),
            (5, 'Charlie Wilson', 'Sales', 85000)
        ]
        c.executemany('INSERT INTO employees VALUES (?,?,?,?)', employees_data)
        
    c.execute('SELECT COUNT(*) FROM departments')
    if c.fetchone()[0] == 0:
        departments_data = [
            (1, 'IT', 'New York'),
            (2, 'HR', 'Chicago'),
            (3, 'Sales', 'Los Angeles')
        ]
        c.executemany('INSERT INTO departments VALUES (?,?,?)', departments_data)
    
    conn.commit()
    conn.close()

# Execute SQL query
def execute_query(query):
    conn = sqlite3.connect('sample.db')
    try:
        df = pd.read_sql_query(query, conn)
        return df, None
    except Exception as e:
        return None, str(e)
    finally:
        conn.close()

# Initialize the sample database
init_sample_db()

st.title("SQL Query Interface")

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please login to use this feature")
    st.stop()

# Display database schema
with st.expander("Database Schema"):
    st.write("**Employees Table**")
    st.code("""
    CREATE TABLE employees (
        id INTEGER PRIMARY KEY,
        name TEXT,
        department TEXT,
        salary REAL
    )
    """)
    
    st.write("**Departments Table**")
    st.code("""
    CREATE TABLE departments (
        id INTEGER PRIMARY KEY,
        name TEXT,
        location TEXT
    )
    """)

# Sample queries
with st.expander("Sample Queries"):
    st.code("SELECT * FROM employees WHERE department = 'IT'")
    st.code("""
    SELECT e.name, e.department, d.location
    FROM employees e
    JOIN departments d ON e.department = d.name
    WHERE e.salary > 70000
    """)

# Query input
query = st.text_area(
    'Enter your SQL query:',
    placeholder="Example: SELECT * FROM employees WHERE department = 'IT'"
)

col1, col2 = st.columns([1, 4])
with col1:
    execute = st.button('Execute Query')
    
if execute and query:
    result, error = execute_query(query)
    if error:
        st.error(f'Error executing query: {error}')
    else:
        st.success('Query executed successfully!')
        st.dataframe(result)
elif execute:
    st.warning('Please enter a query')

# File: .streamlit/config.toml
