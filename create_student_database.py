"""
Script to create and initialize the student database
Run this script to create your student database
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.database.student_db import init_student_db
from src.config import STUDENT_DB_PATH

def main():
    """Create and initialize the student database"""
    print("=" * 60)
    print("Creating Student Database")
    print("=" * 60)
    
    # Ensure database directory exists
    db_dir = Path(STUDENT_DB_PATH).parent
    db_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize the database
    try:
        init_student_db(STUDENT_DB_PATH)
        print(f"\n[SUCCESS] Student database created successfully!")
        print(f"[INFO] Database location: {STUDENT_DB_PATH}")
        print("\nDatabase tables created:")
        print("  - students (student information)")
        print("  - quiz_attempts (quiz results)")
        print("  - question_results (individual question details)")
        print("  - student_progress (learning progress tracking)")
        print("  - learning_sessions (study session tracking)")
        print("  - topic_views (topic viewing history)")
        print("\nYou can now connect your AI teacher assistant to this database!")
    except Exception as e:
        print(f"\n[ERROR] Error creating database: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())

