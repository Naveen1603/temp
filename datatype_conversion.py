access_to_postgres_types = {
    'BIT': 'BOOLEAN',
    'BYTE': 'SMALLINT',
    'INTEGER': 'INTEGER',
    'LONGINTEGER': 'BIGINT',
    'CURRENCY': 'NUMERIC(19,4)',
    'DECIMAL': 'NUMERIC({precision},{scale})',
    'SINGLE': 'REAL',
    'DOUBLE': 'DOUBLE PRECISION',
    'DATETIME': 'TIMESTAMP',
    'TEXT': 'VARCHAR',
    'MEMO': 'TEXT',
    'OLEOBJECT': 'BYTEA',
    'BINARY': 'BYTEA',
    'VARBINARY': 'BYTEA',
    'LONGVARBINARY': 'BYTEA',
    'IMAGE': 'BYTEA',
    'YESNO': 'BOOLEAN'
}


