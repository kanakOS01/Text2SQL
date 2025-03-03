import streamlit as st
import requests
import pandas as pd

API_BASE_URL = "http://localhost:8000"

st.set_page_config(page_title="Text2SQL App", layout="centered")
st.title("📝 Text2SQL Query Generator")

st.sidebar.header("Select or Add Database")


def main():
        
    # headers = {
    #     'accept': 'application/json',
    #     'content-type': 'application/x-www-form-urlencoded',
    # }

    # params = {
    #     'db_name': 'employees',
    #     'db_uri': 'mysql://root@localhost:3306/employees',
    # }

    # response = requests.post('http://localhost:8000/databases/', params=params, headers=headers)
    
    def fetch_databases():
        try:
            response = requests.get(f"{API_BASE_URL}/databases")                
            if response.status_code == 200:
                return response.json()  # Directly return the list of DB objects
        except Exception as e:
            raise e


    db_list = fetch_databases()
    

    # Add Database
    if st.sidebar.button(label="Add Database", icon=":material/add:"):
        with st.sidebar.form("add_database_form"):
            st.subheader("Add a New Database")
            new_db_name = st.text_input("Database Name")
            new_db_uri = st.text_input("Database URI")
            submit_db = st.form_submit_button("Add Database")

            if submit_db and new_db_name and new_db_uri:
                payload = {"db_name": new_db_name, "db_uri": new_db_uri}
                headers = {"Content-Type": "application/json"}
                add_response = requests.post(f"{API_BASE_URL}/databases/", params=payload, headers=headers)

                st.write(add_response)
                if add_response.status_code == 200:
                    st.sidebar.success(f"Database '{new_db_name}' added!", icon=":material/check:")
                    st.rerun()  # Refresh the page to update DB list
                else:
                    st.sidebar.error("Error adding database.", icon=":material/close:")
            

    # Database Selection
    db_list = fetch_databases()

    if db_list:
        # print(db_list)
        db_options = {db['db_name']: db['id'] for db in db_list}  # Map name to ID
        selected_db_name = st.sidebar.selectbox("Choose a database:", list(db_options.keys()), key="db_select")
        selected_db_id = db_options[selected_db_name]  # Get the corresponding ID
    else:
        st.sidebar.warning("No databases found. Add one first.")
        st.stop()


    # Fetch schema when database is selected
    if selected_db_name:
        with st.spinner("Fetching database schema..."):
            schema_response = requests.get(f"{API_BASE_URL}/databases/{selected_db_id}/schema")
            if schema_response.status_code == 200:
                schema = schema_response.json().get("schema", [])
            else:
                schema = []
        st.success("Schema Fetched!", icon=":material/check:")
        st.write(f"\n**Schema:**")
        st.write(schema)

    # Input Query
    query_text = st.text_area("Enter your natural language query", "")

    if st.button("Generate SQL Query"):
        if not query_text:
            st.error("Please enter a query.")
            st.stop()

        # Step 2: Convert to SQL
        # with st.spinner("Converting query to SQL..."):
        sql_response = requests.post(f"{API_BASE_URL}/query/{selected_db_id}/generate_sql", params={"text_query": query_text})
        if sql_response.status_code == 200:
            sql_query = sql_response.json().get("sql_query", "")
        else:
            st.error("Error in SQL generation", icon=":material/close:")
            st.stop()

        st.success("SQL Query Generated!", icon=":material/check:")
        st.code(sql_query, language="sql")

        # Step 3: Execute SQL Query
        # with st.spinner("Executing SQL Query..."):
        query_result_response = requests.post(f"{API_BASE_URL}/query/{selected_db_id}/execute_sql", params={"sql_query": sql_query})
        
        if query_result_response.status_code == 200:
            query_result = query_result_response.json().get("data", [])
        else:
            st.error("Error executing query", icon=":material/close:")
            st.stop()

        st.success("Query Executed!", icon=":material/check:")

        # Display results
        if not query_result:
            st.warning("No data returned.")
        else:
            df = pd.DataFrame(query_result)
            st.dataframe(df)


if __name__ == "__main__":
    main()