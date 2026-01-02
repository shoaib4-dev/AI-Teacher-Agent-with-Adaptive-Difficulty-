"""
Test script to verify time is being stored correctly
Run: python test_time_storage.py
"""

import sqlite3
from pathlib import Path

# Get student database path
try:
    from src.config import STUDENT_DB_PATH
except ImportError:
    BASE_DIR = Path(__file__).parent
    STUDENT_DB_PATH = BASE_DIR / "database" / "students.db"

def test_time_storage():
    """Test if time is being stored in student_progress"""
    print("="*80)
    print("Testing Time Storage in student_progress Table")
    print("="*80)
    
    if not Path(STUDENT_DB_PATH).exists():
        print(f"[ERROR] Database file not found at: {STUDENT_DB_PATH}")
        return 1
    
    try:
        conn = sqlite3.connect(STUDENT_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check student_progress table
        cursor.execute('''
            SELECT topic, time_spent_seconds, time_spent_minutes, time_spent_hours,
                   correct_questions, incorrect_questions, total_questions_generated
            FROM student_progress
            ORDER BY topic
        ''')
        
        rows = cursor.fetchall()
        
        print(f"\nFound {len(rows)} topics in student_progress:\n")
        
        for row in rows:
            topic = row['topic']
            time_seconds = row['time_spent_seconds'] or 0
            time_minutes = row['time_spent_minutes'] or 0
            time_hours = row['time_spent_hours'] or 0
            correct = row['correct_questions'] or 0
            incorrect = row['incorrect_questions'] or 0
            total_q = row['total_questions_generated'] or 0
            
            # Format time
            hours = time_seconds // 3600
            minutes = (time_seconds % 3600) // 60
            secs = time_seconds % 60
            time_formatted = f"{hours:02d}:{minutes:02d}:{secs:02d}"
            
            print(f"Topic: {topic}")
            print(f"  Time stored: {time_seconds} seconds ({time_formatted})")
            print(f"  Time components: {time_hours}h {time_minutes}m")
            print(f"  Questions: {total_q} total, {correct} correct, {incorrect} incorrect")
            print()
        
        # Check quiz_attempts table for recent attempts with time
        cursor.execute('''
            SELECT topic, time_taken_seconds, attempt_date, score
            FROM quiz_attempts
            ORDER BY attempt_date DESC
            LIMIT 5
        ''')
        
        attempts = cursor.fetchall()
        
        if attempts:
            print(f"\nRecent quiz attempts (last 5):\n")
            for attempt in attempts:
                topic = attempt['topic']
                time_seconds = attempt['time_taken_seconds']
                date = attempt['attempt_date']
                score = attempt['score']
                
                if time_seconds:
                    hours = time_seconds // 3600
                    minutes = (time_seconds % 3600) // 60
                    secs = time_seconds % 60
                    time_formatted = f"{hours:02d}:{minutes:02d}:{secs:02d}"
                else:
                    time_formatted = "00:00:00 (not recorded)"
                
                print(f"  {date}: {topic} - Score: {score}%, Time: {time_formatted}")
        else:
            print("\nNo quiz attempts found in quiz_attempts table")
        
        conn.close()
        
        print("\n" + "="*80)
        print("Summary:")
        print("  - If time_spent_seconds is 0 for all topics, time is not being saved")
        print("  - If quiz_attempts shows time_taken_seconds but student_progress doesn't,")
        print("    there's an issue with the save_quiz_attempt function")
        print("  - Check backend console logs for [DEBUG] messages when submitting a quiz")
        
        return 0
        
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(test_time_storage())

