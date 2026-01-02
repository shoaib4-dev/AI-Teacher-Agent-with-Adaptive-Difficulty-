"""
Database initialization and connection management
"""

import sqlite3
from pathlib import Path

def get_db_connection(db_path):
    """Get database connection"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path):
    """Initialize database with all required tables"""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    
    # Topic queries table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS topic_queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic_name TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            student_id TEXT DEFAULT 'default'
        )
    ''')
    
    # Quiz generations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quiz_generations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            num_questions INTEGER NOT NULL,
            total_marks INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            student_id TEXT DEFAULT 'default'
        )
    ''')
    
    # Quiz evaluations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quiz_evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_id TEXT NOT NULL,
            topic TEXT,
            difficulty TEXT,
            score REAL NOT NULL,
            total_questions INTEGER NOT NULL,
            correct_answers INTEGER NOT NULL,
            total_marks REAL NOT NULL,
            obtained_marks REAL NOT NULL,
            timestamp TEXT NOT NULL,
            student_id TEXT DEFAULT 'default'
        )
    ''')
    
    # Student scores table (detailed score tracking)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS student_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            quiz_id TEXT NOT NULL,
            topic TEXT,
            difficulty TEXT,
            score REAL NOT NULL,
            total_marks REAL NOT NULL,
            obtained_marks REAL NOT NULL,
            correct_answers INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')
    
    # Chat messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT NOT NULL,
            ai_response TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            student_id TEXT DEFAULT 'default'
        )
    ''')
    
    # Feedback table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            type TEXT NOT NULL,
            subject TEXT NOT NULL,
            message TEXT NOT NULL,
            rating INTEGER NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')
    
    # File uploads table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS file_uploads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            file_type TEXT NOT NULL,
            uploaded_at TEXT NOT NULL,
            student_id TEXT DEFAULT 'default'
        )
    ''')
    
    # Agent decisions table (for logging)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS agent_decisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            decision_type TEXT NOT NULL,
            context TEXT,
            decision TEXT NOT NULL,
            confidence REAL,
            timestamp TEXT NOT NULL
        )
    ''')
    
    # Agent memory table (for conversation memory - mandatory feature)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS agent_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            user_message TEXT NOT NULL,
            ai_response TEXT NOT NULL,
            context TEXT,
            timestamp TEXT NOT NULL,
            session_id TEXT
        )
    ''')
    
    # Create indexes for better performance
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_user_timestamp 
        ON agent_memory(user_id, timestamp DESC)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_topic_queries_timestamp 
        ON topic_queries(timestamp DESC)
    ''')
    
    conn.commit()
    conn.close()
    print(f"Database initialized at: {db_path}")

