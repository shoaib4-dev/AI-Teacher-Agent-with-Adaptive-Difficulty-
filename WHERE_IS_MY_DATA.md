# Where is My Quiz Data Stored?

## Quick Answer

Your quiz data is stored in **TWO databases**:

### 1. Main Database: `ai_teacher.db`
**Location:** `database/ai_teacher.db`

**Tables:**
- ✅ `quiz_evaluations` - Quiz results (FIXED - now has all columns)
- ✅ `student_scores` - Detailed student scores

### 2. Student Database: `students.db`  
**Location:** `database/students.db`

**Tables:**
- ✅ `quiz_attempts` - Complete quiz attempts with all details
- ✅ `question_results` - Individual question results
- ✅ `students` - Student information
- ✅ `student_progress` - Learning progress by topic

## How to View Data

### Method 1: Use the Python Script (Easiest)
```bash
python view_quiz_data.py
```
This shows data from BOTH databases.

### Method 2: SQLite Browser

1. **Open DB Browser for SQLite**
2. **For Main Database:**
   - Open: `database/ai_teacher.db`
   - Tables: `quiz_evaluations`, `student_scores`

3. **For Student Database:**
   - Open: `database/students.db`
   - Tables: `quiz_attempts`, `question_results`, `students`, `student_progress`

### Method 3: Command Line

```bash
# Main database
sqlite3 database/ai_teacher.db
SELECT * FROM quiz_evaluations;
SELECT * FROM student_scores;

# Student database  
sqlite3 database/students.db
SELECT * FROM quiz_attempts;
SELECT * FROM question_results;
SELECT * FROM students;
SELECT * FROM student_progress;
```

## What Was Fixed

✅ **Database schema updated** - Added missing columns to `quiz_evaluations` table:
- `topic`
- `difficulty` 
- `total_marks`
- `obtained_marks`

✅ **Better error logging** - Now you'll see messages if data saving fails

✅ **Data is being saved** - Check `students.db` - it has all your quiz data!

## Important Notes

1. **Data is saved to BOTH databases automatically:**
   - Main DB: System tracking
   - Student DB: Detailed analytics

2. **If you don't see data in SQLite Browser:**
   - **Refresh the view** (F5 or right-click → Refresh)
   - Make sure you're looking at the correct database
   - Run `python view_quiz_data.py` to verify data exists

3. **Most complete data is in `students.db`:**
   - `quiz_attempts` - Full quiz details
   - `question_results` - Every question's result
   - `student_progress` - Progress tracking

## Next Steps

1. **Submit a new quiz** - Data will now be saved with all columns
2. **View in SQLite Browser** - Refresh to see new data
3. **Use the Python script** - `python view_quiz_data.py` for quick overview

