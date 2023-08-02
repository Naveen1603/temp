import streamlit as st
import psycopg2

# Connect to PostgreSQL database
connection = psycopg2.connect(
    database="your_db_name",
    user="your_username",
    password="your_password",
    host="localhost",
    port="5432"
)
cursor = connection.cursor()

# Fetch query names and query strings from the database
cursor.execute("SELECT query_name, query_string FROM queries")
query_data = cursor.fetchall()

# Close the database connection
cursor.close()
connection.close()

# Streamlit web app
st.title("Interactive Query Viewer")

# Display a list of buttons representing query names
selected_query_name = st.selectbox("Select a query:", [row[0] for row in query_data])

# Get the corresponding query string based on the selected query name
selected_query_string = next(row[1] for row in query_data if row[0] == selected_query_name)

# Execute the query and display the results
if st.button("Run Query"):
    connection = psycopg2.connect(
        database="your_db_name",
        user="your_username",
        password="your_password",
        host="localhost",
        port="5432"
    )
    cursor = connection.cursor()
    cursor.execute(selected_query_string)
    results = cursor.fetchall()
    st.write("Query Results:")
    st.write(results)
    cursor.close()
    connection.close()
