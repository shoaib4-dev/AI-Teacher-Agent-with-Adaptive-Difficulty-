"""
Script to add time_spent_formatted column to student_progress table
Run: python update_student_progress_add_formatted_time.py
"""

import sqlite3
from pathlib import Path
import sys

# Get student database path
try:
    from src.config import STUDENT_DB_PATH
except ImportError:
    BASE_DIR = Path(__file__).parent
    STUDENT_DB_PATH = BASE_DIR / "database" / "students.db"

def update_student_progress_table():
    """Add time_spent_formatted column to student_progress table"""
    print("="*80)
    print("Adding time_spent_formatted Column to student_progress Table")
    print("="*80)
    print(f"Database: {STUDENT_DB_PATH}")
    
    if not Path(STUDENT_DB_PATH).exists():
        print(f"\n[ERROR] Database file not found at: {STUDENT_DB_PATH}")
        return 1
    
    try:
        conn = sqlite3.connect(STUDENT_DB_PATH)
        cursor = conn.cursor()
        
        # Check current structure
        cursor.execute("PRAGMA table_info(student_progress)")
        existing_columns = {row[1]: row[2] for row in cursor.fetchall()}
        print(f"\nCurrent columns: {list(existing_columns.keys())}")
        
        # Check if column already exists
        if 'time_spent_formatted' in existing_columns:
            print("\n[INFO] time_spent_formatted column already exists. Skipping migration.")
            conn.close()
            return 0
        
        # Add the new column
        print("\nAdding time_spent_formatted column...")
        cursor.execute('''
            ALTER TABLE student_progress 
            ADD COLUMN time_spent_formatted TEXT DEFAULT '00:00:00'
        ''')
        
        # Update existing rows with formatted time
        cursor.execute("SELECT id, time_spent_seconds FROM student_progress")
        rows = cursor.fetchall()
        
        print(f"\nUpdating {len(rows)} existing rows with formatted time...")
        for row_id, time_seconds in rows:
            if time_seconds:
                hours = time_seconds // 3600
                minutes = (time_seconds % 3600) // 60
                secs = time_seconds % 60
                time_formatted = f"{hours:02d}:{minutes:02d}:{secs:02d}"
            else:
                time_formatted = "00:00:00"
            
            cursor.execute('''
                UPDATE student_progress
                SET time_spent_formatted = ?
                WHERE id = ?
            ''', (time_formatted, row_id))
        
        conn.commit()
        conn.close()
        
        print("\n[SUCCESS] time_spent_formatted column added successfully!")
        print("\nNew structure includes:")
        print("  - time_spent_seconds (INTEGER) - for calculations")
        print("  - time_spent_formatted (TEXT) - stores time as HH:MM:SS format")
        
        return 0
        
    except Exception as e:
        print(f"\n[ERROR] Error updating table: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(update_student_progress_table())

