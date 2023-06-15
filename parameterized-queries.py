import win32com.client

def read_queries(database_path):
    # Create a DAO DBEngine object
    db_engine = win32com.client.Dispatch("DAO.DBEngine.120")

    # Open the Access database
    db = db_engine.OpenDatabase(database_path)

    # Retrieve all querydefs
    querydefs = db.QueryDefs

    # Iterate over each querydef
    for querydef in querydefs:
        query_name = querydef.Name
        sql = querydef.SQL

        # Check if the querydef has any parameters
        parameters = querydef.Parameters
        if parameters.Count > 0:
            # Query has parameters
            print(f"Query: {query_name} (Requires Parameters)")
            print("Parameters:")
            for param in parameters:
                print(f"  - Name: {param.Name}, Type: {param.Type}")
        else:
            # Query has no parameters
            print(f"Query: {query_name} (No Parameters)")
        print("SQL:")
        print(sql)
        print()

    # Close the database
    db.Close()

# Specify the path to your Access database file
database_path = r"C:\path\to\your\database.accdb"

# Call the function to read queries
read_queries(database_path)
