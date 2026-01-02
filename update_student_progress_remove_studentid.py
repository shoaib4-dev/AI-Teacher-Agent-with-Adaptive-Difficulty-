"""
Script to update student_progress table - remove student_id and add score_percentage
Run: python update_student_progress_remove_studentid.py
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
    """Update student_progress table - remove student_id, add score_percentage"""
    print("="*80)
    print("Updating student_progress Table - Remove student_id, Add score_percentage")
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
        
        if row_count > 0:
            # Backup data - get unique topics with latest score
            cursor.execute("SELECT topic, score, time_spent_minutes, total_questions_generated FROM student_progress")
            old_data = cursor.fetchall()
            print(f"Backing up {row_count} rows...")
        
        # Drop old table
        print("\nDropping old table...")
        cursor.execute("DROP TABLE IF EXISTS student_progress")
        
        # Create new simplified table (no student_id, with score_percentage)
        print("Creating new table structure...")
        cursor.execute('''
            CREATE TABLE student_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL UNIQUE,
                score REAL DEFAULT 0.0,
                score_percentage REAL DEFAULT 0.0,
                time_spent_minutes INTEGER DEFAULT 0,
                total_questions_generated INTEGER DEFAULT 0
            )
        ''')
        
        # Restore data (keep only unique topics, use latest score)
        if row_count > 0 and old_data:
            print(f"\nMigrating data (keeping unique topics only)...")
            migrated = 0
            topics_seen = {}
            
            for row in old_data:
                topic, score, time_spent, total_questions = row
                
                # Keep only the latest entry for each topic
                if topic not in topics_seen:
                    topics_seen[topic] = {
                        'score': score or 0.0,
                        'time_spent': time_spent or 0,
                        'total_questions': total_questions or 0
                    }
                else:
                    # Update if this has a higher score or more data
                    if score and score > topics_seen[topic]['score']:
                        topics_seen[topic]['score'] = score
                    topics_seen[topic]['time_spent'] = max(topics_seen[topic]['time_spent'], time_spent or 0)
                    topics_seen[topic]['total_questions'] = max(topics_seen[topic]['total_questions'], total_questions or 0)
            
            # Insert unique topics
            for topic, data in topics_seen.items():
                try:
                    cursor.execute('''
                        INSERT INTO student_progress 
                        (topic, score, score_percentage, time_spent_minutes, total_questions_generated)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (topic, data['score'], data['score'], data['time_spent'], data['total_questions']))
                    migrated += 1
                except Exception as e:
                    print(f"  Warning: Could not migrate topic {topic}: {e}")
            
            print(f"Migrated {migrated} unique topics")
        
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
        print("  - time_spent_minutes")
        print("  - total_questions_generated")
        print("\nNote: student_id has been removed - progress is tracked per topic only")
        
        return 0
        
    except Exception as e:
        print(f"\n[ERROR] Error updating table: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(update_student_progress_table())

