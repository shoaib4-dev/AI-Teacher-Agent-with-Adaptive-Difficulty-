"""
Script to update student_progress table - add time (seconds/minutes/hours) and correct/incorrect questions
Run: python update_student_progress_add_time_and_questions.py
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
    """Update student_progress table - add time fields and correct/incorrect questions"""
    print("="*80)
    print("Updating student_progress Table - Add Time Fields and Question Counts")
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
        
        # Backup existing data
        cursor.execute("SELECT COUNT(*) FROM student_progress")
        row_count = cursor.fetchone()[0]
        print(f"\nExisting rows: {row_count}")
        
        old_data = []
        if row_count > 0:
            # Backup data
            cursor.execute("SELECT * FROM student_progress")
            old_data = cursor.fetchall()
            print(f"Backing up {row_count} rows...")
        
        # Drop old table
        print("\nDropping old table...")
        cursor.execute("DROP TABLE IF EXISTS student_progress")
        
        # Create new table with additional fields
        print("Creating new table structure...")
        cursor.execute('''
            CREATE TABLE student_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL UNIQUE,
                score REAL DEFAULT 0.0,
                score_percentage REAL DEFAULT 0.0,
                time_spent_seconds INTEGER DEFAULT 0,
                time_spent_minutes INTEGER DEFAULT 0,
                time_spent_hours INTEGER DEFAULT 0,
                total_questions_generated INTEGER DEFAULT 0,
                correct_questions INTEGER DEFAULT 0,
                incorrect_questions INTEGER DEFAULT 0
            )
        ''')
        
        # Restore data with new fields
        if row_count > 0 and old_data:
            print(f"\nMigrating data...")
            migrated = 0
            
            for row in old_data:
                # Get column names from old structure
                row_dict = {}
                col_names = [desc[0] for desc in cursor.description] if cursor.description else []
                if not col_names:
                    # Try to infer from row length
                    if len(row) >= 6:
                        row_dict = {
                            'id': row[0],
                            'topic': row[1],
                            'score': row[2],
                            'score_percentage': row[3] if len(row) > 3 else row[2],
                            'time_spent_minutes': row[4] if len(row) > 4 else 0,
                            'total_questions_generated': row[5] if len(row) > 5 else 0
                        }
                else:
                    for i, col_name in enumerate(col_names):
                        row_dict[col_name] = row[i]
                
                topic = row_dict.get('topic')
                if not topic:
                    continue
                
                # Calculate time fields from minutes
                time_minutes = row_dict.get('time_spent_minutes', 0) or 0
                time_seconds = time_minutes * 60
                hours = time_seconds // 3600
                minutes = (time_seconds % 3600) // 60
                secs = time_seconds % 60
                
                try:
                    cursor.execute('''
                        INSERT INTO student_progress 
                        (topic, score, score_percentage, 
                         time_spent_seconds, time_spent_minutes, time_spent_hours,
                         total_questions_generated, correct_questions, incorrect_questions)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        topic,
                        row_dict.get('score', 0.0) or 0.0,
                        row_dict.get('score_percentage', row_dict.get('score', 0.0)) or 0.0,
                        time_seconds,
                        minutes,
                        hours,
                        row_dict.get('total_questions_generated', 0) or 0,
                        0,  # correct_questions - will be updated on next quiz
                        0   # incorrect_questions - will be updated on next quiz
                    ))
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
        print("  - time_spent_seconds (total seconds)")
        print("  - time_spent_minutes (calculated)")
        print("  - time_spent_hours (calculated)")
        print("  - total_questions_generated")
        print("  - correct_questions")
        print("  - incorrect_questions")
        print("\nTime is stored in seconds and can be displayed as HH:MM:SS format")
        
        return 0
        
    except Exception as e:
        print(f"\n[ERROR] Error updating table: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(update_student_progress_table())

