# How to View Database Contents

## Method 1: Using Python Script (Easiest)

I've created a script to view all database contents:

```powershell
python view_database.py
```

This will show:
- All tables in the database
- All rows from each table
- Summary statistics

## Method 2: Using SQLite Command Line

### Step 1: Open SQLite
```powershell
sqlite3 database\ai_teacher.db
```

### Step 2: View Tables
```sql
.tables
```

### Step 3: View Table Contents

**View all topic queries:**
```sql
SELECT * FROM topic_queries;
```

**View all quiz generations:**
```sql
SELECT * FROM quiz_generations;
```

**View all quiz evaluations:**
```sql
SELECT * FROM quiz_evaluations;
```

**View all chat messages:**
```sql
SELECT * FROM chat_messages;
```

**View agent memory (conversations):**
```sql
SELECT * FROM agent_memory;
```

**View agent decisions:**
```sql
SELECT * FROM agent_decisions;
```

**View feedback:**
```sql
SELECT * FROM feedback;
```

**View users:**
```sql
SELECT * FROM users;
```

### Step 4: Exit SQLite
```sql
.quit
```

## Method 3: Using Python Interactive

```powershell
python
```

```python
import sqlite3
from pathlib import Path

# Connect to database
db_path = Path("database/ai_teacher.db")
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# List tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables:", [t[0] for t in tables])

# View a specific table
cursor.execute("SELECT * FROM agent_memory LIMIT 10")
rows = cursor.fetchall()
for row in rows:
    print(dict(row))

conn.close()
```

## Method 4: Using Database Browser (GUI Tool)

1. Download **DB Browser for SQLite**: https://sqlitebrowser.org/
2. Open the tool
3. Click "Open Database"
4. Navigate to: `database/ai_teacher.db`
5. Browse tables and data visually

## Quick Commands

### View Recent Queries
```sql
SELECT * FROM topic_queries ORDER BY timestamp DESC LIMIT 10;
```

### View Recent Quiz Generations
```sql
SELECT * FROM quiz_generations ORDER BY timestamp DESC LIMIT 10;
```

### View Recent Conversations
```sql
SELECT * FROM agent_memory ORDER BY timestamp DESC LIMIT 10;
```

### View Agent Decisions
```sql
SELECT decision_type, decision, confidence, timestamp 
FROM agent_decisions 
ORDER BY timestamp DESC 
LIMIT 20;
```

### Count Records per Table
```sql
SELECT 
    'topic_queries' as table_name, COUNT(*) as count FROM topic_queries
UNION ALL
SELECT 'quiz_generations', COUNT(*) FROM quiz_generations
UNION ALL
SELECT 'quiz_evaluations', COUNT(*) FROM quiz_evaluations
UNION ALL
SELECT 'chat_messages', COUNT(*) FROM chat_messages
UNION ALL
SELECT 'agent_memory', COUNT(*) FROM agent_memory
UNION ALL
SELECT 'agent_decisions', COUNT(*) FROM agent_decisions
UNION ALL
SELECT 'feedback', COUNT(*) FROM feedback;
```

## Method 5: Using VS Code Extension

1. Install "SQLite Viewer" extension in VS Code
2. Right-click on `database/ai_teacher.db`
3. Select "Open Database"
4. Browse tables in the sidebar

## Important Tables

- **`agent_memory`** - Conversation history (mandatory feature)
- **`agent_decisions`** - All AI reasoning outputs/logs
- **`topic_queries`** - All topic explanation requests
- **`quiz_generations`** - All quiz generation events
- **`quiz_evaluations`** - All quiz evaluation results
- **`chat_messages`** - Chat conversation history
- **`feedback`** - User feedback submissions

## Example Output

When you run `python view_database.py`, you'll see:

```
================================================================================
AI Teacher Agent - Database Viewer
================================================================================
Database: C:\Users\...\database\ai_teacher.db

Found 9 tables: agent_decisions, agent_memory, chat_messages, feedback, ...

================================================================================
Table: agent_memory (5 rows)
================================================================================
id | user_id | user_message | ai_response | context | timestamp
--------------------------------------------------------------------------------
1  | default | What is AI?  | AI is...     | NULL    | 2025-01-15T10:30:00
...
```

