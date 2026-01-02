"""
Script to view quiz evaluation data from both databases
Run: python view_quiz_data.py
"""

import sqlite3
from pathlib import Path
import sys

# Get database paths
try:
    from src.config import DB_PATH, STUDENT_DB_PATH
except ImportError:
    BASE_DIR = Path(__file__).parent
    DB_PATH = BASE_DIR / "database" / "ai_teacher.db"
    STUDENT_DB_PATH = BASE_DIR / "database" / "students.db"

def view_table(conn, table_name, db_name):
    """View all rows from a table"""
    try:
        cursor = conn.execute(f"SELECT * FROM {table_name} ORDER BY id DESC LIMIT 10")
        rows = cursor.fetchall()
        
        if not rows:
            print(f"\n[{db_name}] {table_name}: (empty - no data)")
            return
        
        print(f"\n{'='*80}")
        print(f"[{db_name}] Table: {table_name} (showing last 10 of {len(rows)} rows)")
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
                elif isinstance(value, str) and len(value) > 30:
                    value = value[:27] + "..."
                values.append(str(value))
            print(" | ".join(values))
    except Exception as e:
        print(f"\n[{db_name}] Error reading {table_name}: {e}")

def main():
    print("="*80)
    print("Quiz Data Viewer - Checking Both Databases")
    print("="*80)
    
    # Check main database (ai_teacher.db)
    print(f"\n[MAIN DATABASE] {DB_PATH}")
    if Path(DB_PATH).exists():
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            
            # Check quiz_evaluations
            view_table(conn, "quiz_evaluations", "MAIN")
            
            # Check student_scores
            view_table(conn, "student_scores", "MAIN")
            
            # Get counts
            cursor = conn.execute("SELECT COUNT(*) FROM quiz_evaluations")
            eval_count = cursor.fetchone()[0]
            cursor = conn.execute("SELECT COUNT(*) FROM student_scores")
            scores_count = cursor.fetchone()[0]
            
            print(f"\n[MAIN DB SUMMARY]")
            print(f"  quiz_evaluations: {eval_count} rows")
            print(f"  student_scores: {scores_count} rows")
            
            conn.close()
        except Exception as e:
            print(f"[MAIN DB ERROR] {e}")
    else:
        print(f"[MAIN DB] File not found: {DB_PATH}")
    
    # Check student database (students.db)
    if STUDENT_DB_PATH and Path(STUDENT_DB_PATH).exists():
        print(f"\n[STUDENT DATABASE] {STUDENT_DB_PATH}")
        try:
            conn = sqlite3.connect(STUDENT_DB_PATH)
            conn.row_factory = sqlite3.Row
            
            # Check quiz_attempts
            view_table(conn, "quiz_attempts", "STUDENT")
            
            # Check question_results
            view_table(conn, "question_results", "STUDENT")
            
            # Check students
            view_table(conn, "students", "STUDENT")
            
            # Check student_progress
            view_table(conn, "student_progress", "STUDENT")
            
            # Get counts
            cursor = conn.execute("SELECT COUNT(*) FROM quiz_attempts")
            attempts_count = cursor.fetchone()[0]
            cursor = conn.execute("SELECT COUNT(*) FROM question_results")
            questions_count = cursor.fetchone()[0]
            cursor = conn.execute("SELECT COUNT(*) FROM students")
            students_count = cursor.fetchone()[0]
            
            print(f"\n[STUDENT DB SUMMARY]")
            print(f"  students: {students_count} rows")
            print(f"  quiz_attempts: {attempts_count} rows")
            print(f"  question_results: {questions_count} rows")
            
            conn.close()
        except Exception as e:
            print(f"[STUDENT DB ERROR] {e}")
    else:
        if STUDENT_DB_PATH:
            print(f"\n[STUDENT DB] File not found: {STUDENT_DB_PATH}")
        else:
            print(f"\n[STUDENT DB] Not configured")

if __name__ == "__main__":
    main()

