"""
Script to fix database schema - adds missing columns to existing tables
Run: python fix_database_schema.py
"""

import sqlite3
from pathlib import Path
import sys

# Get database path
try:
    from src.config import DB_PATH
except ImportError:
    BASE_DIR = Path(__file__).parent
    DB_PATH = BASE_DIR / "database" / "ai_teacher.db"

def fix_database_schema():
    """Add missing columns to quiz_evaluations table"""
    print("="*80)
    print("Fixing Database Schema")
    print("="*80)
    print(f"Database: {DB_PATH}")
    
    if not Path(DB_PATH).exists():
        print(f"\n[ERROR] Database file not found at: {DB_PATH}")
        return 1
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check current columns
        cursor.execute("PRAGMA table_info(quiz_evaluations)")
        existing_columns = [row[1] for row in cursor.fetchall()]
        print(f"\nCurrent columns in quiz_evaluations: {existing_columns}")
        
        # Add missing columns
        missing_columns = []
        
        if 'topic' not in existing_columns:
            print("Adding 'topic' column...")
            cursor.execute("ALTER TABLE quiz_evaluations ADD COLUMN topic TEXT")
            missing_columns.append('topic')
        
        if 'difficulty' not in existing_columns:
            print("Adding 'difficulty' column...")
            cursor.execute("ALTER TABLE quiz_evaluations ADD COLUMN difficulty TEXT")
            missing_columns.append('difficulty')
        
        if 'total_marks' not in existing_columns:
            print("Adding 'total_marks' column...")
            cursor.execute("ALTER TABLE quiz_evaluations ADD COLUMN total_marks REAL")
            missing_columns.append('total_marks')
        
        if 'obtained_marks' not in existing_columns:
            print("Adding 'obtained_marks' column...")
            cursor.execute("ALTER TABLE quiz_evaluations ADD COLUMN obtained_marks REAL")
            missing_columns.append('obtained_marks')
        
        if missing_columns:
            conn.commit()
            print(f"\n[SUCCESS] Added {len(missing_columns)} missing columns: {', '.join(missing_columns)}")
        else:
            print("\n[INFO] All columns already exist - no changes needed")
        
        # Verify final structure
        cursor.execute("PRAGMA table_info(quiz_evaluations)")
        final_columns = [row[1] for row in cursor.fetchall()]
        print(f"\nFinal columns: {final_columns}")
        
        conn.close()
        print("\n[SUCCESS] Database schema fixed!")
        return 0
        
    except Exception as e:
        print(f"\n[ERROR] Error fixing schema: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(fix_database_schema())

