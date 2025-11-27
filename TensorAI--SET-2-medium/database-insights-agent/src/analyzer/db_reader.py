import sqlite3
import pandas as pd

def connect_to_database(db_path):
    """Connect to the SQLite database."""
    conn = sqlite3.connect(db_path)
    return conn

def discover_schema(conn):
    """Discover the schema of the database."""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    schema = {}
    
    for table in tables:
        table_name = table[0]
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        schema[table_name] = [column[1] for column in columns]
    
    return schema

def read_table_data(conn, table_name):
    """Read data from a specified table into a pandas DataFrame."""
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    return df

def close_connection(conn):
    """Close the database connection."""
    conn.close()

def read_data(conn):
    """Read all tables from the database and return as DataFrames dictionary."""
    dataframes = {}
    
    # Get list of tables (excluding SQLite system tables)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"Found {len(tables)} tables: {tables}")
    
    # Read each table into a DataFrame
    for table in tables:
        try:
            df = pd.read_sql_query(f"SELECT * FROM '{table}'", conn)
            dataframes[table] = df
            print(f"✅ Read table '{table}': {len(df)} rows, {len(df.columns)} columns")
        except Exception as e:
            print(f"❌ Error reading table '{table}': {e}")
    
    return dataframes

def get_table_info(conn, table_name):
    """Get detailed information about a specific table."""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    
    cursor.execute(f"SELECT COUNT(*) FROM '{table_name}'")
    row_count = cursor.fetchone()[0]
    
    return {
        'columns': columns,
        'row_count': row_count,
        'column_names': [col[1] for col in columns],
        'column_types': [col[2] for col in columns]
    }

def get_database_summary(conn):
    """Get a complete summary of the database structure."""
    summary = {
        'tables': {},
        'total_tables': 0,
        'total_records': 0
    }
    
    # Get all table names
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [row[0] for row in cursor.fetchall()]
    
    summary['total_tables'] = len(tables)
    
    # Get info for each table
    for table in tables:
        table_info = get_table_info(conn, table)
        summary['tables'][table] = table_info
        summary['total_records'] += table_info['row_count']
    
    return summary