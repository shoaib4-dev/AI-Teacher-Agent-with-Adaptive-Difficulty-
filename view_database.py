"""
Script to view database contents
Run: python view_database.py
"""

import sqlite3
from pathlib import Path
import sys

# Get database path
try:
    from src.config import DB_PATH
except ImportError:
    # Default path
    BASE_DIR = Path(__file__).parent
    DB_PATH = BASE_DIR / "database" / "ai_teacher.db"

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def print_table(conn, table_name):
    """Print all rows from a table"""
    cursor = conn.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    
    if not rows:
        print(f"\n{table_name}: (empty)")
        return
    
    print(f"\n{'='*80}")
    print(f"Table: {table_name} ({len(rows)} rows)")
    print('='*80)
    
    # Get column names
    columns = [description[0] for description in cursor.description]
    print(" | ".join(columns))
    print("-" * 80)
    
    # Print rows
    for row in rows:
        values = []
        for col in columns:
            value = row[col]
            if value is None:
                value = "NULL"
            elif isinstance(value, str) and len(value) > 50:
                value = value[:47] + "..."
            values.append(str(value))
        print(" | ".join(values))

def list_tables(conn):
    """List all tables in database"""
    cursor = conn.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """)
    return [row[0] for row in cursor.fetchall()]

def main():
    print("="*80)
    print("AI Teacher Agent - Database Viewer")
    print("="*80)
    print(f"Database: {DB_PATH}")
    
    if not Path(DB_PATH).exists():
        print(f"\n[ERROR] Database file not found at: {DB_PATH}")
        print("Make sure the database file exists.")
        return
    
    try:
        conn = get_db_connection()
        
        # List all tables
        tables = list_tables(conn)
        print(f"\nFound {len(tables)} tables: {', '.join(tables)}")
        
        # Print each table
        for table in tables:
            print_table(conn, table)
        
        # Summary statistics
        print("\n" + "="*80)
        print("SUMMARY STATISTICS")
        print("="*80)
        
        for table in tables:
            cursor = conn.execute(f"SELECT COUNT(*) as count FROM {table}")
            count = cursor.fetchone()[0]
            print(f"{table}: {count} rows")
        
        conn.close()
        print("\n[SUCCESS] Database viewing complete!")
        
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

