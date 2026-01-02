"""
Configuration - Database Settings
Change DB_FILE to your database filename
"""

from pathlib import Path

# Database Configuration
BASE_DIR = Path(__file__).parent.parent
DB_FILE = "ai_teacher.db"  # Main database for system data
DB_PATH = str(BASE_DIR / "database" / DB_FILE)

# Student Database Configuration - Separate database for student data
STUDENT_DB_FILE = "students.db"  # CHANGE THIS to your student database filename (e.g., "my_students.db")
STUDENT_DB_PATH = str(BASE_DIR / "database" / STUDENT_DB_FILE)

