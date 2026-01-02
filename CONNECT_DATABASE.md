# Step-by-Step Guide: Connect Your SQLite Database

## Overview
This guide will help you connect your own SQLite database (`myDB.db` or any other database) to the AI Teacher Agent project.

## Step 1: Place Your Database File

1. **Locate your database file** (e.g., `myDB.db`)
2. **Copy it to the `database/` folder** in your project:
   ```
   AI_PROJECT/
   └── database/
       ├── ai_teacher.db  (default)
       └── myDB.db        (your database) ← Place it here
   ```

## Step 2: Update Configuration File

1. **Open** `src/config.py`
2. **Change** the `DB_FILE` variable to your database filename:

```python
# Before
DB_FILE = "ai_teacher.db"

# After (if your database is named myDB.db)
DB_FILE = "myDB.db"
```

**Example:**
```python
"""
Configuration - Database Settings
Change DB_FILE to your database filename
"""

from pathlib import Path

# Database Configuration
BASE_DIR = Path(__file__).parent.parent
DB_FILE = "myDB.db"  # Your database filename
DB_PATH = str(BASE_DIR / "database" / DB_FILE)
```

## Step 3: Verify Database Path

The database will be located at:
```
AI_PROJECT/database/your_database_name.db
```

Make sure this path is correct in `src/config.py`.

## Step 4: Check Your Database Tables

Your database will automatically create required tables if they don't exist. The project uses `CREATE TABLE IF NOT EXISTS`, so:

✅ **Existing tables are preserved**
✅ **Missing tables are created automatically**
✅ **Your existing data is safe**

### Required Tables (Created Automatically)

The project will create these tables if they don't exist:
- `users`
- `topic_queries`
- `quiz_generations`
- `quiz_evaluations`
- `chat_messages`
- `feedback`
- `file_uploads`
- `agent_decisions`
- `agent_memory`

## Step 5: Test the Connection

### Method 1: Run the Backend

```powershell
cd src
python app.py
```

If you see:
```
Database initialized at: C:\Users\...\database\myDB.db
Starting AI Teacher Agent on http://localhost:8000
```

✅ **Success!** Your database is connected.

### Method 2: View Database Contents

```powershell
python view_database.py
```

This will show all tables and data from your database.

### Method 3: Check Database File

```powershell
# List database files
dir database\*.db

# Check if your database exists
Test-Path database\myDB.db
```

## Step 6: Verify Tables Are Created

After running the backend, check your database:

```powershell
sqlite3 database\myDB.db ".tables"
```

You should see all the required tables listed.

## Step 7: Test with Real Operations

1. **Start the backend:**
   ```powershell
   cd src
   python app.py
   ```

2. **Use the frontend** to:
   - Explain a topic → Data saved to `topic_queries`
   - Generate a quiz → Data saved to `quiz_generations`
   - Chat with agent → Data saved to `agent_memory`
   - Submit feedback → Data saved to `feedback`

3. **Check the database:**
   ```powershell
   python view_database.py
   ```

## Troubleshooting

### Issue 1: Database Not Found

**Error:** `Database file not found`

**Solution:**
- Check that your database file is in `database/` folder
- Verify the filename in `src/config.py` matches exactly (case-sensitive)
- Check file extension: `.db` not `.sqlite` or `.sqlite3`

### Issue 2: Permission Denied

**Error:** `Permission denied` or `database is locked`

**Solution:**
- Close any other programs using the database
- Make sure the database file is not read-only
- Check file permissions

### Issue 3: Tables Not Created

**Error:** Tables missing after running backend

**Solution:**
- Check backend logs for errors
- Verify `init_db()` is being called in `src/app.py`
- Manually check: `sqlite3 database\myDB.db ".tables"`

### Issue 4: Existing Data Conflicts

**Solution:**
- The project uses `CREATE TABLE IF NOT EXISTS` - your data is safe
- If you have tables with different schemas, they won't be modified
- Only missing tables will be created

## Example: Connecting myDB.db

### Step 1: Database is already in `database/myDB.db` ✅

### Step 2: Update `src/config.py`:
```python
DB_FILE = "myDB.db"
```

### Step 3: Run backend:
```powershell
cd src
python app.py
```

### Step 4: Verify:
```powershell
python view_database.py
```

## Advanced: Using Database from Different Location

If your database is in a different location:

### Option 1: Update DB_PATH directly

In `src/config.py`:
```python
# Absolute path
DB_PATH = r"C:\Users\YourName\Documents\my_database.db"

# Or relative path
DB_PATH = str(BASE_DIR / ".." / "my_custom_folder" / "myDB.db")
```

### Option 2: Use Environment Variable

1. Create `.env` file:
   ```
   DB_PATH=C:\Users\YourName\Documents\my_database.db
   ```

2. Update `src/config.py`:
   ```python
   import os
   from dotenv import load_dotenv
   load_dotenv()
   
   DB_PATH = os.getenv("DB_PATH", str(BASE_DIR / "database" / "ai_teacher.db"))
   ```

## Summary Checklist

- [ ] Database file placed in `database/` folder
- [ ] Updated `DB_FILE` in `src/config.py`
- [ ] Verified database path is correct
- [ ] Started backend successfully
- [ ] Checked tables are created
- [ ] Tested with real operations
- [ ] Verified data is being saved

## Quick Reference

**Config File:** `src/config.py`
```python
DB_FILE = "your_database_name.db"  # Change this
```

**Database Location:** `database/your_database_name.db`

**View Database:** `python view_database.py`

**Test Connection:** Start backend and check logs

