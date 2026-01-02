# Quick Guide: Connect Your SQLite Database

## 🎯 Simple 3-Step Process

### Step 1: Place Your Database File

Put your database file (e.g., `myDB.db`) in the `database/` folder:

```
AI_PROJECT/
└── database/
    ├── ai_teacher.db  (default - can ignore)
    └── myDB.db        (your database) ✅
```

**You already have `myDB.db` in the database folder!** ✅

### Step 2: Update Configuration

Open `src/config.py` and change line 10:

**Before:**
```python
DB_FILE = "ai_teacher.db"
```

**After (to use myDB.db):**
```python
DB_FILE = "myDB.db"
```

### Step 3: Test Connection

```powershell
# Start backend
cd src
python app.py
```

You should see:
```
Database initialized at: ...\database\myDB.db
Starting AI Teacher Agent on http://localhost:8000
```

✅ **Done!** Your database is connected.

---

## 📋 Detailed Steps

### Option A: Manual Setup (Recommended)

1. **Open** `src/config.py` in your editor

2. **Find this line:**
   ```python
   DB_FILE = "ai_teacher.db"
   ```

3. **Change it to:**
   ```python
   DB_FILE = "myDB.db"
   ```

4. **Save the file**

5. **Test it:**
   ```powershell
   cd src
   python app.py
   ```

### Option B: Using Different Database Name

If your database has a different name (e.g., `students.db`):

1. Make sure it's in `database/` folder
2. Update `src/config.py`:
   ```python
   DB_FILE = "students.db"
   ```

---

## ✅ Verification

### Check 1: View Database
```powershell
python view_database.py
```

### Check 2: SQLite Command
```powershell
sqlite3 database\myDB.db ".tables"
```

### Check 3: Backend Logs
When you start the backend, you should see:
```
Database initialized at: C:\Users\...\database\myDB.db
```

---

## 🔍 What Happens Automatically

When you connect your database:

✅ **Existing tables are preserved** - Your data is safe!
✅ **Missing tables are created** - Project tables added automatically
✅ **No data loss** - Uses `CREATE TABLE IF NOT EXISTS`

---

## 📝 Example: Current Setup

**Your current files:**
- `database/ai_teacher.db` (default)
- `database/myDB.db` (your database)

**To use myDB.db:**
1. Open `src/config.py`
2. Change: `DB_FILE = "myDB.db"`
3. Save and run backend

---

## 🆘 Troubleshooting

**Problem:** Database not found
- ✅ Check filename matches exactly (case-sensitive)
- ✅ Check file is in `database/` folder
- ✅ Check file extension is `.db`

**Problem:** Tables not created
- ✅ Check backend logs for errors
- ✅ Verify `init_db()` is called
- ✅ Run: `python view_database.py`

**Problem:** Permission denied
- ✅ Close other programs using the database
- ✅ Check file is not read-only

---

## 📚 Files Created

- `CONNECT_DATABASE.md` - Detailed guide
- `QUICK_DATABASE_SETUP.md` - This quick guide
- `setup_database.py` - Helper script (optional)
- `view_database.py` - View database contents

---

## 🎯 Summary

**To connect `myDB.db`:**

1. ✅ Database already in `database/myDB.db`
2. ⚙️ Update `src/config.py`: `DB_FILE = "myDB.db"`
3. 🚀 Run: `cd src && python app.py`
4. ✅ Done!

