"""
View student_progress table with formatted time display
Run: python view_student_progress.py
"""

import sqlite3
from pathlib import Path
import sys

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Get student database path
try:
    from src.config import STUDENT_DB_PATH
except ImportError:
    BASE_DIR = Path(__file__).parent
    STUDENT_DB_PATH = BASE_DIR / "database" / "students.db"

def format_time(seconds):
    """Format seconds as HH:MM:SS"""
    if not seconds:
        return "00:00:00"
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def view_student_progress():
    """View student progress with formatted time"""
    print("="*100)
    print("Student Progress Table")
    print("="*100)
    print(f"Database: {STUDENT_DB_PATH}\n")
    
    if not Path(STUDENT_DB_PATH).exists():
        print(f"[ERROR] Database file not found at: {STUDENT_DB_PATH}")
        return 1
    
    try:
        conn = sqlite3.connect(STUDENT_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT topic, score, score_percentage, 
                   time_spent_seconds, time_spent_minutes, time_spent_hours,
                   total_questions_generated, correct_questions, incorrect_questions
            FROM student_progress
            ORDER BY topic
        ''')
        
        rows = cursor.fetchall()
        
        if not rows:
            print("No progress data found.")
            conn.close()
            return 0
        
        # Print header
        print(f"{'Topic':<40} {'Score':<8} {'%':<6} {'Time (HH:MM:SS)':<12} {'Total Q':<8} {'Correct':<8} {'Incorrect':<8}")
        print("-" * 100)
        
        # Print rows
        for row in rows:
            topic = row['topic'] or 'N/A'
            score = row['score'] or 0.0
            percentage = row['score_percentage'] or 0.0
            time_seconds = row['time_spent_seconds'] or 0
            time_formatted = format_time(time_seconds)
            total_questions = row['total_questions_generated'] or 0
            correct = row['correct_questions'] or 0
            incorrect = row['incorrect_questions'] or 0
            
            print(f"{topic:<40} {score:<8.1f} {percentage:<6.1f} {time_formatted:<12} {total_questions:<8} {correct:<8} {incorrect:<8}")
        
        print("-" * 100)
        print(f"\nTotal topics: {len(rows)}")
        
        # Summary statistics
        total_time = sum(row['time_spent_seconds'] or 0 for row in rows)
        total_questions = sum(row['total_questions_generated'] or 0 for row in rows)
        total_correct = sum(row['correct_questions'] or 0 for row in rows)
        total_incorrect = sum(row['incorrect_questions'] or 0 for row in rows)
        
        print(f"\nSummary:")
        print(f"  Total time spent: {format_time(total_time)}")
        print(f"  Total questions: {total_questions}")
        print(f"  Total correct: {total_correct}")
        print(f"  Total incorrect: {total_incorrect}")
        if total_questions > 0:
            accuracy = (total_correct / total_questions) * 100
            print(f"  Overall accuracy: {accuracy:.1f}%")
        
        conn.close()
        return 0
        
    except Exception as e:
        print(f"\n[ERROR] Error viewing progress: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(view_student_progress())

