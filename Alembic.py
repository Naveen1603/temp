from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import create_engine, MetaData

# Connect to Access database using SQLAlchemy
access_engine = create_engine('access+pyodbc://user:pass@localhost/path/to/access/file.accdb')
access_metadata = MetaData(bind=access_engine)

# Reflect Access database schema
access_metadata.reflect()

# Connect to Postgres database using SQLAlchemy
postgres_engine = create_engine('postgresql://user:pass@localhost/mydatabase')
postgres_metadata = MetaData(bind=postgres_engine)

# Reflect Postgres database schema
postgres_metadata.reflect()

# Generate SQL queries to migrate Access schema to Postgres schema
with MigrationContext.configure(postgres_engine.connect()) as migration_context:
    diffs = compare_metadata(access_metadata, postgres_metadata)

    # Print SQL queries
    for upgrade_ops in diffs:
        for op in upgrade_ops:
            print(migration_context.generate_revision(None, [op]))
