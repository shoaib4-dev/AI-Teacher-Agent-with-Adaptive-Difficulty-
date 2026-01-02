# Testing & Verifying Backend

## What is the Backend?

The backend is a **FastAPI web server** that provides:
- **API endpoints** for the frontend to communicate with
- **AI agent logic** for reasoning, memory, and data processing
- **Database operations** for storing and retrieving data
- **Validation** using Pydantic models

**Location**: `src/app.py` - This is the main backend file

## How to Start the Backend

### Step 1: Navigate to src folder
```powershell
cd src
```

### Step 2: Start the server
```powershell
python app.py
```

You should see:
```
Starting AI Teacher Agent on http://localhost:8000
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 3: Keep the terminal open
The server runs in the foreground. Keep this terminal window open.

## How to Check if Backend is Working

### Method 1: Check Health Endpoint (Easiest)

Open your browser and visit:
```
http://localhost:8000/api/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-15T10:30:00.123456"
}
```

✅ **If you see this**: Backend is working!

### Method 2: Check Root Endpoint

Visit:
```
http://localhost:8000/
```

**Expected Response:**
```json
{
  "service": "AI Teacher Agent",
  "status": "running"
}
```

✅ **If you see this**: Backend is working!

### Method 3: Use API Documentation (Best Method)

FastAPI automatically generates interactive API documentation!

Visit:
```
http://localhost:8000/docs
```

**What you'll see:**
- List of all available endpoints
- Try it out feature - test endpoints directly
- Request/response schemas
- Example requests

**How to test:**
1. Click on any endpoint (e.g., `/api/health`)
2. Click "Try it out"
3. Click "Execute"
4. See the response

✅ **If you can see the docs and test endpoints**: Backend is working perfectly!

### Method 4: Test with PowerShell/Command Line

Open a **new terminal** (keep backend running in first terminal):

```powershell
# Test health endpoint
curl http://localhost:8000/api/health

# Test root endpoint
curl http://localhost:8000/

# Test data sources
curl http://localhost:8000/api/data-sources
```

**Expected**: JSON responses

### Method 5: Test with Frontend

1. Start backend: `cd src && python app.py`
2. Start frontend: `cd ui && python -m http.server 8080`
3. Open browser: `http://localhost:8080`
4. Try features:
   - Explain a topic
   - Generate a quiz
   - Chat with agent

✅ **If frontend works**: Backend is working!

## Testing All Endpoints

### 1. Health Check
```
GET http://localhost:8000/api/health
```

### 2. Root
```
GET http://localhost:8000/
```

### 3. Data Sources Info
```
GET http://localhost:8000/api/data-sources
```

### 4. Dataset Statistics
```
GET http://localhost:8000/api/dataset/stats
```

### 5. Explain Topic
```
POST http://localhost:8000/api/topics/explain
Content-Type: application/json

{
  "topic_name": "Python Basics"
}
```

### 6. Generate Quiz
```
POST http://localhost:8000/api/quiz/generate
Content-Type: application/json

{
  "topic": "Python",
  "difficulty": "Beginner",
  "num_questions": 5,
  "total_marks": 50,
  "marks_per_question": 10
}
```

### 7. Query Dataset
```
POST http://localhost:8000/api/query
Content-Type: application/json

{
  "query_type": "search",
  "query": "python",
  "limit": 10
}
```

### 8. Chat with Agent
```
POST http://localhost:8000/api/chat/message
Content-Type: application/json

{
  "message": "What is Python?",
  "user_id": "test_user"
}
```

### 9. Get Memory
```
GET http://localhost:8000/api/memory?user_id=test_user&limit=10
```

### 10. Summarize
```
POST http://localhost:8000/api/reasoning/summarize
Content-Type: application/json

{
  "content": "Python is a programming language..."
}
```

### 11. Classify
```
POST http://localhost:8000/api/reasoning/classify
Content-Type: application/json

{
  "content": "How do I learn Python programming?",
  "categories": ["academic", "technical", "general"]
}
```

## Common Issues & Solutions

### Issue 1: "Port 8000 already in use"
**Solution**: 
- Stop the previous server (Ctrl+C in terminal)
- Or change port in `src/app.py` (line 162): `uvicorn.run(app, host="0.0.0.0", port=8001)`

### Issue 2: "ModuleNotFoundError"
**Solution**:
```powershell
# Install dependencies
pip install -r requirements.txt
```

### Issue 3: "Database error"
**Solution**:
- Check `src/config.py` - database path is correct
- Database file will be created automatically

### Issue 4: "Cannot connect to backend"
**Solution**:
- Make sure backend is running (check terminal)
- Check firewall settings
- Verify port 8000 is not blocked

## Quick Verification Checklist

- [ ] Backend starts without errors
- [ ] `http://localhost:8000/api/health` returns JSON
- [ ] `http://localhost:8000/docs` shows API documentation
- [ ] Can test endpoints in `/docs` interface
- [ ] Frontend can communicate with backend
- [ ] Database operations work (check database file exists)

## Using Postman (Optional)

If you have Postman installed:

1. Import collection or create new request
2. Set method (GET/POST)
3. Enter URL: `http://localhost:8000/api/health`
4. Click Send
5. See response

## Using Python Script to Test

Create `test_backend.py`:

```python
import requests

# Test health
response = requests.get("http://localhost:8000/api/health")
print("Health:", response.json())

# Test explain topic
response = requests.post(
    "http://localhost:8000/api/topics/explain",
    json={"topic_name": "Python"}
)
print("Topic Explanation:", response.json())

# Test query
response = requests.post(
    "http://localhost:8000/api/query",
    json={"query_type": "search", "query": "python", "limit": 5}
)
print("Query Results:", response.json())
```

Run:
```powershell
pip install requests
python test_backend.py
```

## Summary

**Best way to check backend:**
1. Start backend: `cd src && python app.py`
2. Visit: `http://localhost:8000/docs`
3. Test endpoints using the interactive interface

**Quick check:**
- Visit: `http://localhost:8000/api/health`
- Should return: `{"status": "healthy", ...}`

✅ **If health endpoint works, backend is working correctly!**

