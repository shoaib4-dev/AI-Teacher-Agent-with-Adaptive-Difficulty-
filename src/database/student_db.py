"""
Student Database - Separate database for student data, quiz marks, scores, and progress
"""

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

def get_student_db_connection(db_path: str):
    """Get connection to student database"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_student_db(db_path: str):
    """Initialize student database with all required tables"""
    conn = get_student_db_connection(db_path)
    cursor = conn.cursor()
    
    # Students table - Basic student information
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            created_at TEXT NOT NULL,
            last_active TEXT,
            total_quizzes_taken INTEGER DEFAULT 0,
            total_topics_studied INTEGER DEFAULT 0,
            average_score REAL DEFAULT 0.0
        )
    ''')
    
    # Quiz attempts table - Detailed quiz results
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quiz_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            quiz_id TEXT NOT NULL,
            topic TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            score REAL NOT NULL,
            total_marks REAL NOT NULL,
            obtained_marks REAL NOT NULL,
            total_questions INTEGER NOT NULL,
            correct_answers INTEGER NOT NULL,
            incorrect_answers INTEGER NOT NULL,
            unanswered_questions INTEGER NOT NULL,
            time_taken_seconds INTEGER,
            attempt_date TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
    ''')
    
    # Question details table - Individual question results
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS question_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_attempt_id INTEGER NOT NULL,
            question_id INTEGER NOT NULL,
            question_text TEXT NOT NULL,
            student_answer TEXT,
            correct_answer TEXT,
            is_correct INTEGER NOT NULL DEFAULT 0,
            marks_awarded REAL NOT NULL,
            max_marks REAL NOT NULL,
            feedback TEXT,
            FOREIGN KEY (quiz_attempt_id) REFERENCES quiz_attempts(id)
        )
    ''')
    
    # Student progress table - Simplified: topic, score, percentage, total questions, correct/incorrect
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS student_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL UNIQUE,
            score REAL DEFAULT 0.0,
            score_percentage REAL DEFAULT 0.0,
            total_questions_generated INTEGER DEFAULT 0,
            correct_questions INTEGER DEFAULT 0,
            incorrect_questions INTEGER DEFAULT 0
        )
    ''')
    
    # Learning sessions table - Track study sessions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS learning_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            topic TEXT,
            session_type TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT,
            duration_minutes INTEGER,
            activities_completed INTEGER DEFAULT 0,
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
    ''')
    
    # Topic explanations viewed - Track what topics students have viewed
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS topic_views (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            topic TEXT NOT NULL,
            view_count INTEGER DEFAULT 1,
            first_viewed TEXT NOT NULL,
            last_viewed TEXT NOT NULL,
            total_time_spent_minutes INTEGER DEFAULT 0,
            FOREIGN KEY (student_id) REFERENCES students(student_id),
            UNIQUE(student_id, topic)
        )
    ''')
    
    # Create indexes for better performance
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_student_quiz_attempts 
        ON quiz_attempts(student_id, attempt_date DESC)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_student_progress 
        ON student_progress(topic)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_question_results_attempt 
        ON question_results(quiz_attempt_id)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_student_sessions 
        ON learning_sessions(student_id, start_time DESC)
    ''')
    
    conn.commit()
    conn.close()
    print(f"Student database initialized at: {db_path}")

def create_or_update_student(db_path: str, student_id: str, name: str, email: Optional[str] = None):
    """Create a new student or update existing student information"""
    conn = get_student_db_connection(db_path)
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
    
    # Check if student exists
    cursor.execute('SELECT id FROM students WHERE student_id = ?', (student_id,))
    exists = cursor.fetchone()
    
    if exists:
        # Update existing student
        if email:
            cursor.execute('''
                UPDATE students 
                SET name = ?, email = ?, last_active = ?
                WHERE student_id = ?
            ''', (name, email, now, student_id))
        else:
            cursor.execute('''
                UPDATE students 
                SET name = ?, last_active = ?
                WHERE student_id = ?
            ''', (name, now, student_id))
    else:
        # Create new student
        cursor.execute('''
            INSERT INTO students (student_id, name, email, created_at, last_active)
            VALUES (?, ?, ?, ?, ?)
        ''', (student_id, name, email, now, now))
    
    conn.commit()
    conn.close()

def save_quiz_attempt(db_path: str, student_id: str, quiz_data: Dict, question_details: List[Dict]):
    """Save a complete quiz attempt with all question details"""
    conn = get_student_db_connection(db_path)
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
    
    # Insert quiz attempt
    cursor.execute('''
        INSERT INTO quiz_attempts (
            student_id, quiz_id, topic, difficulty, score, total_marks, obtained_marks,
            total_questions, correct_answers, incorrect_answers, unanswered_questions,
            time_taken_seconds, attempt_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        student_id,
        quiz_data.get('quiz_id'),
        quiz_data.get('topic', ''),
        quiz_data.get('difficulty', ''),
        quiz_data.get('score', 0.0),
        quiz_data.get('total_marks', 0.0),
        quiz_data.get('obtained_marks', 0.0),
        quiz_data.get('total_questions', 0),
        quiz_data.get('correct_answers', 0),
        quiz_data.get('incorrect_answers', 0),
        quiz_data.get('unanswered_questions', 0),
        quiz_data.get('time_taken_seconds'),
        now
    ))
    
    quiz_attempt_id = cursor.lastrowid
    
    # Insert question details
    for q_detail in question_details:
        cursor.execute('''
            INSERT INTO question_results (
                quiz_attempt_id, question_id, question_text, student_answer,
                correct_answer, is_correct, marks_awarded, max_marks, feedback
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            quiz_attempt_id,
            q_detail.get('question_id'),
            q_detail.get('question_text', ''),
            q_detail.get('student_answer', ''),
            q_detail.get('correct_answer', ''),
            1 if q_detail.get('is_correct', False) else 0,
            q_detail.get('marks_awarded', 0.0),
            q_detail.get('max_marks', 0.0),
            q_detail.get('feedback', '')
        ))
    
    # Update student statistics
    cursor.execute('''
        UPDATE students 
        SET total_quizzes_taken = total_quizzes_taken + 1,
            last_active = ?
        WHERE student_id = ?
    ''', (now, student_id))
    
    # Update or create student progress for this topic
    # Includes: topic, score, score_percentage, time (seconds/minutes/hours), total_questions, correct/incorrect
    topic = quiz_data.get('topic', '')
    if not topic:
        return quiz_attempt_id  # Skip if no topic
    
    score = quiz_data.get('score', 0.0)
    score_percentage = score  # Score is already a percentage (0-100)
    total_questions = quiz_data.get('total_questions', 0)
    correct_questions = quiz_data.get('correct_answers', 0)
    incorrect_questions = quiz_data.get('incorrect_answers', 0)
    
    # Check if progress exists for this topic
    cursor.execute('''
        SELECT * FROM student_progress 
        WHERE topic = ?
    ''', (topic,))
    
    existing = cursor.fetchone()
    
    if existing:
        # Update existing progress - accumulate questions, update score
        existing_dict = dict(existing)
        current_questions = existing_dict.get('total_questions_generated', 0) + total_questions
        current_correct = existing_dict.get('correct_questions', 0) + correct_questions
        current_incorrect = existing_dict.get('incorrect_questions', 0) + incorrect_questions
        
        cursor.execute('''
            UPDATE student_progress
            SET score = ?,
                score_percentage = ?,
                total_questions_generated = ?,
                correct_questions = ?,
                incorrect_questions = ?
            WHERE topic = ?
        ''', (score, score_percentage,
              current_questions, current_correct, current_incorrect, topic))
    else:
        # Create new progress entry
        cursor.execute('''
            INSERT INTO student_progress (
                topic, score, score_percentage,
                total_questions_generated, correct_questions, incorrect_questions
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (topic, score, score_percentage,
              total_questions, correct_questions, incorrect_questions))
    
    # Update student average score
    cursor.execute('''
        UPDATE students
        SET average_score = (
            SELECT AVG(score) FROM quiz_attempts WHERE student_id = ?
        )
        WHERE student_id = ?
    ''', (student_id, student_id))
    
    conn.commit()
    conn.close()
    return quiz_attempt_id

def get_student_stats(db_path: str, student_id: str) -> Dict:
    """Get comprehensive statistics for a student"""
    conn = get_student_db_connection(db_path)
    cursor = conn.cursor()
    
    # Get student info
    cursor.execute('SELECT * FROM students WHERE student_id = ?', (student_id,))
    student = cursor.fetchone()
    
    if not student:
        conn.close()
        return None
    
    # Get quiz statistics
    cursor.execute('''
        SELECT 
            COUNT(*) as total_quizzes,
            AVG(score) as avg_score,
            MAX(score) as best_score,
            MIN(score) as worst_score,
            SUM(total_questions) as total_questions_attempted,
            SUM(correct_answers) as total_correct
        FROM quiz_attempts
        WHERE student_id = ?
    ''', (student_id,))
    quiz_stats = cursor.fetchone()
    
    # Get progress by topic (simplified structure - no student_id)
    cursor.execute('''
        SELECT topic, score, score_percentage, 
               total_questions_generated, correct_questions, incorrect_questions
        FROM student_progress
        ORDER BY topic
    ''')
    progress = []
    for row in cursor.fetchall():
        row_dict = dict(row)
        progress.append(row_dict)
    
    # Get recent quiz attempts
    cursor.execute('''
        SELECT * FROM quiz_attempts
        WHERE student_id = ?
        ORDER BY attempt_date DESC
        LIMIT 10
    ''', (student_id,))
    recent_attempts = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return {
        'student': dict(student),
        'quiz_stats': dict(quiz_stats) if quiz_stats else {},
        'progress': progress,
        'recent_attempts': recent_attempts
    }

def get_all_students(db_path: str) -> List[Dict]:
    """Get list of all students"""
    conn = get_student_db_connection(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT s.*, 
               COUNT(DISTINCT qa.id) as total_quizzes,
               AVG(qa.score) as avg_score
        FROM students s
        LEFT JOIN quiz_attempts qa ON s.student_id = qa.student_id
        GROUP BY s.id
        ORDER BY s.created_at DESC
    ''')
    
    students = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return students

