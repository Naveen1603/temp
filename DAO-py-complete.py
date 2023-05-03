import pyodbc
import win32com.client
import psycopg2

# Connect to the Access database
access_conn_str = 'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\\path\\to\\access\\db.accdb;'
access_conn = pyodbc.connect(access_conn_str)
dao_engine = win32com.client.Dispatch('DAO.DBEngine.120')

# Connect to the PostgreSQL database
postgres_conn = psycopg2.connect(host='localhost', dbname='postgres', user='postgres', password='password')

# Get a list of tables from the Access database
dao_db = dao_engine.OpenDatabase(access_conn_str)
tables = [table.Name for table in dao_db.TableDefs if table.Attributes == 0]

# Iterate over tables and migrate them
for table in tables:
    # Get table schema and data from Access database
    dao_table = dao_db.TableDefs[table]
    columns = []
    unique_constraints = []
    check_constraints = []
    for field in dao_table.Fields:
        column_name = field.Name
        column_type = 'text'
        if field.Type == 6:
            column_type = 'integer'
        elif field.Type == 7:
            column_type = 'float'
        elif field.Type == 11:
            column_type = 'boolean'
        columns.append(f'{column_name} {column_type}')
        if field.Attributes & 2:
            foreign_name = field.Properties['ForeignName']
            ref_table, ref_column = foreign_name.split('.')
            create_fk_sql = f'ALTER TABLE {table} ADD CONSTRAINT fk_{column_name}_{ref_table}_{ref_column} FOREIGN KEY ({column_name}) REFERENCES {ref_table} ({ref_column})'
            cursor = postgres_conn.cursor()
            cursor.execute(create_fk_sql)
            postgres_conn.commit()
        if field.Attributes & 128:
            unique_constraints.append(f'UNIQUE ({column_name})')
        if field.ValidationRule:
            check_constraints.append(f'CHECK ({field.Name} {field.ValidationRule})')

    # Create table in PostgreSQL database
    create_table_sql = f"CREATE TABLE {table} ({','.join(columns)})"
    if unique_constraints:
        create_table_sql += f', {", ".join(unique_constraints)}'
    cursor = postgres_conn.cursor()
    cursor.execute(create_table_sql)
    postgres_conn.commit()

    # Insert data into PostgreSQL table
    data = dao_table.OpenRecordset().GetRows()
    insert_sql = f"INSERT INTO {table} ({','.join([field.Name for field in dao_table.Fields])}) VALUES ({','.join(['%s' for _ in range(len(dao_table.Fields))])})"
    cursor.executemany(insert_sql, list(zip(*data)))
    postgres_conn.commit()

    # Create check constraints in PostgreSQL database
    for check_constraint in check_constraints:
        create_check_sql = f"ALTER TABLE {table} ADD CONSTRAINT {table}_check CHECK ({check_constraint})"
        cursor.execute(create_check_sql)
        postgres_conn.commit()

    # Get indexes from Access database
    index_fields = [field for field in dao_table.Fields if field.Index != 0]
    indexes = {}
    for field in index_fields:
        index_name = field.Index.Name
        if index_name not in indexes:
            indexes[index_name] = []
        indexes[index_name].append(field.Name)

    # Create indexes in PostgreSQL database
    for index_name, columns in indexes.items():
        create_index_sql = f"CREATE INDEX {table}_{index_name} ON {table} ({','.join(columns)})"
        cursor.execute(create_index_sql)
