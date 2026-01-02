# Student Progress Table - Simplified Structure

## Table Structure

The `student_progress` table in `students.db` now has a simplified structure with only the required fields:

### Columns:
1. **id** - Primary key (auto-increment)
2. **topic** - The topic selected/studied (UNIQUE)
3. **score** - Latest quiz score for this topic (0-100)
4. **score_percentage** - Percentage score (0-100) - same as score
5. **time_spent_seconds** - Total time spent in seconds (accumulated)
6. **time_spent_minutes** - Minutes component (calculated from seconds)
7. **time_spent_hours** - Hours component (calculated from seconds)
8. **total_questions_generated** - Total questions generated for this topic (accumulated)
9. **correct_questions** - Total correct answers (accumulated)
10. **incorrect_questions** - Total incorrect answers (accumulated)

### Unique Constraint:
- `topic` - One progress record per topic (no student_id - progress is tracked globally per topic)

## How Data is Saved

When a quiz is evaluated:

1. **Topic**: Saved from the quiz topic
2. **Score**: Latest score from the quiz (replaces previous score)
3. **Time Spent**: Accumulated from all quiz attempts (in minutes)
4. **Total Questions Generated**: Accumulated count of all questions generated for this topic

## Example Data

```
topic              | score | %    | time (HH:MM:SS) | total_q | correct | incorrect
-------------------|-------|------|-----------------|---------|---------|----------
Machine Learning   | 75.5  | 75.5 | 00:15:30        | 20      | 15      | 5
Python Basics      | 90.0  | 90.0 | 00:30:45        | 15      | 14      | 1
```

**Time Format**: Time is stored in `time_spent_seconds` and can be displayed as `HH:MM:SS` format:
- `time_spent_seconds = 930` → `00:15:30` (15 minutes 30 seconds)
- `time_spent_seconds = 1845` → `00:30:45` (30 minutes 45 seconds)
- `time_spent_seconds = 3661` → `01:01:01` (1 hour 1 minute 1 second)

## Viewing the Data

### Using SQLite Browser:
1. Open `database/students.db`
2. Go to "Browse Data" tab
3. Select `student_progress` table

### Using SQL:
```sql
SELECT * FROM student_progress;
-- Or for a specific topic:
SELECT * FROM student_progress WHERE topic = 'Machine Learning';
```

### Using Python Script:
```bash
# View formatted progress with time in HH:MM:SS
python view_student_progress.py

# View all quiz data
python view_quiz_data.py
```

## Notes

- **No student_id**: Progress is tracked per topic only, not per student. All students' progress on a topic is aggregated.
- **Score**: This is the **latest** score, not an average. Each new quiz updates the score.
- **Score Percentage**: Same as score (0-100), stored explicitly for clarity.
- **Time Spent**: 
  - Stored in `time_spent_seconds` (total seconds, accumulated)
  - `time_spent_minutes` and `time_spent_hours` are calculated components
  - Can be displayed as `HH:MM:SS` format (e.g., `01:15:30` = 1 hour 15 minutes 30 seconds)
  - Time is **accumulated** - adds up time from all quiz attempts
- **Total Questions**: This is **accumulated** - adds up all questions generated for this topic.
- **Correct/Incorrect Questions**: These are **accumulated** - adds up correct and incorrect answers across all quiz attempts.
- If multiple quizzes are taken on the same topic, the score is updated to the latest, but time, questions, and answer counts are accumulated.

## Migration

The table has been automatically migrated from the old structure. Old data has been preserved where possible:
- Score migrated from `best_score` or `average_score`
- Time migrated from `time_spent_minutes` (if existed)
- Questions estimated from `quizzes_completed` if needed

