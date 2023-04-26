import pyodbc
import psycopg2

# Connect to MS Access database
conn_str_access = (
    r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
    r"DBQ=path\to\your\database.accdb;"
)
conn_access = pyodbc.connect(conn_str_access)

# Connect to PostgreSQL database
conn_str_postgres = "dbname=your_database user=your_username password=your_password host=your_host port=your_port"
conn_postgres = psycopg2.connect(conn_str_postgres)

# Get a cursor for MS Access
cursor_access = conn_access.cursor()

# Get table schema from MS Access
table_name = 'your_table_name'
schema = []
pk_columns = []
for row in cursor_access.columns(table=table_name):
    column_name = row.column_name
    data_type = row.type_name.lower()
    is_nullable = row.is_nullable == 'YES'
    schema.append((column_name, data_type, is_nullable))
    if row.primary_key:
        pk_columns.append(column_name)

# Create equivalent schema in PostgreSQL
cursor_postgres = conn_postgres.cursor()
table_name_postgres = 'your_table_name_postgres'

query = f"CREATE TABLE {table_name_postgres} ("
for column_name, data_type, is_nullable in schema:
    query += f"{column_name} {data_type}"
    if not is_nullable:
        query += " NOT NULL"
    query += ", "
query += f"PRIMARY KEY ({', '.join(pk_columns)})" if pk_columns else ""
query += ");"

cursor_postgres.execute(query)
conn_postgres.commit()

# Add table and column constraints
for row in cursor_access.foreignKeys(table=table_name):
    constraint_name = row.fk_name
    column_name = row.fk_column_name
    referenced_table_name = row.pk_table_name
    referenced_column_name = row.pk_column_name
    query = f"ALTER TABLE {table_name_postgres} ADD CONSTRAINT {constraint_name} FOREIGN KEY ({column_name}) REFERENCES {referenced_table_name} ({referenced_column_name});"
    cursor_postgres.execute(query)
    conn_postgres.commit()

for row in cursor_access.statistics(table=table_name):
    if row.index_name is not None and row.index_name.startswith("IX"):
        index_name = row.index_name
        column_name = row.column_name
        unique = row.unique
        query = f"CREATE {'UNIQUE' if unique else ''} INDEX {index_name} ON {table_name_postgres} ({column_name});"
        cursor_postgres.execute(query)
        conn_postgres.commit()

# Add sequences
for column_name, data_type, is_nullable in schema:
    if "serial" in data_type:
        sequence_name = f"{table_name_postgres}_{column_name}_seq"
        query = f"CREATE SEQUENCE {sequence_name};"
        cursor_postgres.execute(query)
        conn_postgres.commit()
        query = f"SELECT setval('{sequence_name}', COALESCE((SELECT MAX({column_name})+1 FROM {table_name_postgres}), 1), false);"
        cursor_postgres.execute(query)
        conn_postgres.commit()
        query = f"ALTER TABLE {table_name_postgres} ALTER COLUMN {column_name} SET DEFAULT nextval('{sequence_name}');"
        cursor_postgres.execute(query)
        conn_postgres.commit()

print("Table created successfully in PostgreSQL.")
