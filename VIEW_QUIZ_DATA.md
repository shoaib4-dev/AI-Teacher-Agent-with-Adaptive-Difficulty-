# How to View Quiz Data in SQLite

## Databases

Your AI Teacher Assistant uses **two databases**:

### 1. Main Database: `ai_teacher.db`
**Location:** `database/ai_teacher.db`

**Tables with quiz data:**
- `quiz_evaluations` - Quiz evaluation results
- `student_scores` - Detailed student score tracking

### 2. Student Database: `students.db`
**Location:** `database/students.db`

**Tables with quiz data:**
- `quiz_attempts` - Complete quiz attempts
- `question_results` - Individual question results
- `students` - Student information
- `student_progress` - Learning progress by topic

## Viewing Data in SQLite Browser

### Option 1: Using DB Browser for SQLite

1. **Open DB Browser for SQLite**
2. **Open Database:**
   - Click "Open Database"
   - Navigate to: `C:\Users\Shoaib Ahmad\OneDrive\Desktop\AI_PROJECT\database\`
   - Select `ai_teacher.db` or `students.db`

3. **View Tables:**
   - Click on "Browse Data" tab
   - Select table from dropdown (e.g., `quiz_evaluations`, `student_scores`, `quiz_attempts`)

### Option 2: Using Command Line

```bash
# Open main database
sqlite3 database/ai_teacher.db

# View quiz_evaluations
SELECT * FROM quiz_evaluations;

# View student_scores
SELECT * FROM student_scores;

# Open student database
sqlite3 database/students.db

# View quiz_attempts
SELECT * FROM quiz_attempts;

# View question_results
SELECT * FROM question_results;

# View students
SELECT * FROM students;

# View student_progress
SELECT * FROM student_progress;
```

### Option 3: Using Python Script

Run the provided script:
```bash
python view_quiz_data.py
```

This will show data from both databases.

## Important Notes

1. **Data is saved to BOTH databases:**
   - Main database (`ai_teacher.db`) - for system tracking
   - Student database (`students.db`) - for detailed student analytics

2. **If you don't see data:**
   - Make sure you're looking at the correct database
   - Refresh the view in SQLite Browser (F5)
   - Check if quiz was actually submitted (check browser console)
   - Run `python view_quiz_data.py` to verify data exists

3. **Tables to check:**
   - **Main DB:** `quiz_evaluations`, `student_scores`
   - **Student DB:** `quiz_attempts`, `question_results`, `students`, `student_progress`

## Quick Check Commands

```sql
-- In ai_teacher.db
SELECT COUNT(*) FROM quiz_evaluations;
SELECT COUNT(*) FROM student_scores;

-- In students.db
SELECT COUNT(*) FROM quiz_attempts;
SELECT COUNT(*) FROM question_results;
SELECT COUNT(*) FROM students;
```

## Troubleshooting

If data is not showing:
1. Check backend console for error messages
2. Verify database file paths in `src/config.py`
3. Ensure database files exist in `database/` folder
4. Try refreshing the SQLite Browser view
5. Check if commits are happening (look for "Quiz evaluation data saved" message in backend)

