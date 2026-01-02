"""
Script to remove time columns from student_progress table
Run: python update_student_progress_remove_time_columns.py
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
    """Remove time_spent_seconds and time_spent_formatted columns from student_progress table"""
    print("="*80)
    print("Removing Time Columns from student_progress Table")
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
        
        # Check if time columns exist
        has_time_seconds = 'time_spent_seconds' in existing_columns
        has_time_formatted = 'time_spent_formatted' in existing_columns
        
        if not has_time_seconds and not has_time_formatted:
            print("\n[INFO] Time columns do not exist. No migration needed.")
            conn.close()
            return 0
        
        # Backup existing data
        cursor.execute("SELECT COUNT(*) FROM student_progress")
        row_count = cursor.fetchone()[0]
        print(f"\nExisting rows: {row_count}")
        
        old_data = []
        if row_count > 0:
            # Backup data - get all columns except time columns
            cursor.execute("SELECT id, topic, score, score_percentage, total_questions_generated, correct_questions, incorrect_questions FROM student_progress")
            old_data = cursor.fetchall()
            print(f"Backing up {row_count} rows...")
        
        # Drop old table
        print("\nDropping old table...")
        cursor.execute("DROP TABLE IF EXISTS student_progress")
        
        # Create new table without time columns
        print("Creating new table structure (without time columns)...")
        cursor.execute('''
            CREATE TABLE student_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL UNIQUE,
                score REAL DEFAULT 0.0,
                score_percentage REAL DEFAULT 0.0,
                total_questions_generated INTEGER DEFAULT 0,
                correct_questions INTEGER DEFAULT 0,
                incorrect_questions INTEGER DEFAULT 0
            )
        ''')
        
        # Restore data (without time columns)
        if row_count > 0 and old_data:
            print(f"\nMigrating data (removing time columns)...")
            migrated = 0
            
            for row in old_data:
                row_id, topic, score, score_percentage, total_questions, correct, incorrect = row
                
                if not topic:
                    continue
                
                try:
                    cursor.execute('''
                        INSERT INTO student_progress 
                        (topic, score, score_percentage,
                         total_questions_generated, correct_questions, incorrect_questions)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (topic, score or 0.0, score_percentage or score or 0.0,
                          total_questions or 0, correct or 0, incorrect or 0))
                    migrated += 1
                except Exception as e:
                    print(f"  Warning: Could not migrate topic {topic}: {e}")
            
            print(f"Migrated {migrated} topics")
        
        # Recreate index
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_student_progress 
            ON student_progress(topic)
        ''')
        
        conn.commit()
        conn.close()
        
        print("\n[SUCCESS] student_progress table updated successfully!")
        print("\nNew structure:")
        print("  - id (primary key)")
        print("  - topic (unique)")
        print("  - score")
        print("  - score_percentage")
        print("  - total_questions_generated")
        print("  - correct_questions")
        print("  - incorrect_questions")
        print("\nNote: time_spent_seconds and time_spent_formatted columns have been removed")
        
        return 0
        
    except Exception as e:
        print(f"\n[ERROR] Error updating table: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(update_student_progress_table())
