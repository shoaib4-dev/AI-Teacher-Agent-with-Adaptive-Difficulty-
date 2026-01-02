# Student Database Setup Guide

This guide explains how to set up and use the separate student database for storing student data, quiz marks, scores, and progress.

## Overview

The AI Teacher Assistant uses **two separate databases**:

1. **Main Database** (`ai_teacher.db`) - Stores system data, agent decisions, chat messages, etc.
2. **Student Database** (`students.db`) - Stores student-specific data including:
   - Student information
   - Quiz attempts and results
   - Individual question results
   - Learning progress by topic
   - Study sessions
   - Topic viewing history

## Step 1: Create the Student Database

Run the database creation script:

```bash
python create_student_database.py
```

This will create the `students.db` file in the `database/` directory with all required tables.

## Step 2: Configure the Database Path

The student database path is configured in `src/config.py`:

```python
STUDENT_DB_FILE = "students.db"  # Change this to your preferred filename
STUDENT_DB_PATH = str(BASE_DIR / "database" / STUDENT_DB_FILE)
```

## Step 3: Database Schema

The student database includes the following tables:

### 1. `students`
Stores basic student information:
- `student_id` (unique identifier)
- `name`
- `email`
- `created_at`, `last_active`
- Statistics: `total_quizzes_taken`, `total_topics_studied`, `average_score`

### 2. `quiz_attempts`
Stores complete quiz results:
- Quiz details: `quiz_id`, `topic`, `difficulty`
- Scores: `score`, `total_marks`, `obtained_marks`
- Statistics: `total_questions`, `correct_answers`, `incorrect_answers`, `unanswered_questions`
- `time_taken_seconds`, `attempt_date`

### 3. `question_results`
Stores individual question results:
- Links to `quiz_attempt_id`
- Question details: `question_id`, `question_text`
- Answers: `student_answer`, `correct_answer`
- Results: `is_correct`, `marks_awarded`, `max_marks`, `feedback`

### 4. `student_progress`
Tracks learning progress by topic:
- `student_id`, `topic`, `difficulty_level`
- `status` (not_started, in_progress, completed)
- `progress_percentage`
- Statistics: `quizzes_completed`, `best_score`, `average_score`
- `last_studied`, `time_spent_minutes`

### 5. `learning_sessions`
Tracks study sessions:
- `student_id`, `topic`
- `session_type` (quiz, explanation, practice, etc.)
- `start_time`, `end_time`, `duration_minutes`
- `activities_completed`

### 6. `topic_views`
Tracks topic viewing history:
- `student_id`, `topic`
- `view_count`
- `first_viewed`, `last_viewed`
- `total_time_spent_minutes`

## Step 4: Automatic Data Storage

When a student completes a quiz, the system automatically:

1. **Creates/Updates Student Record** - If the student doesn't exist, a new record is created
2. **Saves Quiz Attempt** - Complete quiz results are saved to `quiz_attempts`
3. **Saves Question Details** - Each question's result is saved to `question_results`
4. **Updates Progress** - Student progress for that topic is updated in `student_progress`
5. **Updates Statistics** - Student's overall statistics are recalculated

## Step 5: API Endpoints

The following API endpoints are available for accessing student data:

### Get All Students
```
GET /api/students
```
Returns a list of all students with their statistics.

### Get Student Statistics
```
GET /api/students/{student_id}/stats
```
Returns comprehensive statistics for a specific student including:
- Student information
- Quiz statistics (total quizzes, average score, best score, etc.)
- Progress by topic
- Recent quiz attempts

### Create/Update Student
```
POST /api/students?name={name}&student_id={id}&email={email}
```
Creates a new student or updates existing student information.

## Step 6: Viewing the Database

You can view the student database using:

1. **SQLite Browser** - Use a tool like DB Browser for SQLite
2. **Python Script** - Use the `view_database.py` script (modify it to point to `students.db`)
3. **API Endpoints** - Use the REST API endpoints above

## Example: View Student Progress

```python
import requests

# Get student statistics
response = requests.get('http://localhost:8000/api/students/student123/stats')
stats = response.json()

print(f"Student: {stats['student']['name']}")
print(f"Total Quizzes: {stats['quiz_stats']['total_quizzes']}")
print(f"Average Score: {stats['quiz_stats']['avg_score']:.2f}%")
print(f"Best Score: {stats['quiz_stats']['best_score']:.2f}%")

# View progress by topic
for progress in stats['progress']:
    print(f"\nTopic: {progress['topic']}")
    print(f"  Difficulty: {progress['difficulty_level']}")
    print(f"  Progress: {progress['progress_percentage']:.1f}%")
    print(f"  Quizzes Completed: {progress['quizzes_completed']}")
    print(f"  Best Score: {progress['best_score']:.2f}%")
```

## Troubleshooting

### Database Not Found
If you get an error about the database not being found:
1. Run `python create_student_database.py` to create it
2. Check that `STUDENT_DB_PATH` in `src/config.py` is correct

### Data Not Saving
If quiz data isn't being saved to the student database:
1. Check that `STUDENT_DB_PATH` is set in `src/config.py`
2. Check the backend logs for any error messages
3. Ensure the database file has write permissions

### Viewing Data
To view the database contents:
```bash
# Using SQLite command line
sqlite3 database/students.db
.tables
SELECT * FROM students;
SELECT * FROM quiz_attempts;
```

## Next Steps

- Customize the database schema if needed
- Add additional tracking fields
- Create custom reports using the API endpoints
- Integrate with your frontend to display student progress

