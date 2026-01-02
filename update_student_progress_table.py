"""
Script to update student_progress table to new simplified schema
Run: python update_student_progress_table.py
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
    """Update student_progress table to simplified schema"""
    print("="*80)
    print("Updating student_progress Table Schema")
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
        
        # Check if table needs to be recreated
        required_columns = {'id', 'student_id', 'topic', 'score', 'time_spent_minutes', 'total_questions_generated'}
        current_columns = set(existing_columns.keys())
        
        if current_columns == required_columns:
            print("\n[INFO] Table already has correct structure - no changes needed")
            conn.close()
            return 0
        
        # Backup existing data if any
        cursor.execute("SELECT COUNT(*) FROM student_progress")
        row_count = cursor.fetchone()[0]
        print(f"\nExisting rows: {row_count}")
        
        if row_count > 0:
            # Backup data
            cursor.execute("SELECT * FROM student_progress")
            old_data = cursor.fetchall()
            old_columns = [desc[0] for desc in cursor.description]
            print(f"Backing up {row_count} rows...")
        
        # Drop old table
        print("\nDropping old table...")
        cursor.execute("DROP TABLE IF EXISTS student_progress")
        
        # Create new simplified table
        print("Creating new simplified table...")
        cursor.execute('''
            CREATE TABLE student_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                topic TEXT NOT NULL,
                score REAL DEFAULT 0.0,
                time_spent_minutes INTEGER DEFAULT 0,
                total_questions_generated INTEGER DEFAULT 0,
                FOREIGN KEY (student_id) REFERENCES students(student_id),
                UNIQUE(student_id, topic)
            )
        ''')
        
        # Restore data if possible (migrate what we can)
        if row_count > 0 and old_data:
            print(f"\nMigrating data...")
            migrated = 0
            for row in old_data:
                row_dict = dict(zip(old_columns, row))
                student_id = row_dict.get('student_id', '')
                topic = row_dict.get('topic', '')
                score = row_dict.get('score', 0.0) or row_dict.get('best_score', 0.0) or row_dict.get('average_score', 0.0)
                time_spent = row_dict.get('time_spent_minutes', 0) or 0
                total_questions = row_dict.get('total_questions_generated', 0) or row_dict.get('quizzes_completed', 0) * 10  # Estimate
                
                try:
                    cursor.execute('''
                        INSERT INTO student_progress 
                        (student_id, topic, score, time_spent_minutes, total_questions_generated)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (student_id, topic, score, time_spent, total_questions))
                    migrated += 1
                except Exception as e:
                    print(f"  Warning: Could not migrate row for {student_id}/{topic}: {e}")
            
            print(f"Migrated {migrated} of {row_count} rows")
        
        # Recreate index
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_student_progress 
            ON student_progress(student_id, topic)
        ''')
        
        conn.commit()
        conn.close()
        
        print("\n[SUCCESS] student_progress table updated successfully!")
        print("\nNew structure:")
        print("  - student_id")
        print("  - topic")
        print("  - score")
        print("  - time_spent_minutes")
        print("  - total_questions_generated")
        
        return 0
        
    except Exception as e:
        print(f"\n[ERROR] Error updating table: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(update_student_progress_table())

