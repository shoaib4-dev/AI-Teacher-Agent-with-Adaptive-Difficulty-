# Timer Troubleshooting Guide

## Issue: Timer Not Showing or Not Recording Time

### Quick Checks:

1. **Open Browser Console (F12)** and check for errors
2. **Verify Timer Element Exists**: 
   - Open browser DevTools
   - Go to Elements tab
   - Search for `quizTimer`
   - Check if element exists and is visible

3. **Check Console Logs**:
   - Should see: `[DEBUG] Timer started` when quiz begins
   - Should see: `[DEBUG] Quiz submission - Time taken: ...` when submitting

### Common Issues:

#### 1. Timer Element Not Found
**Symptom**: Console shows `[ERROR] Timer element not found!`

**Solution**: 
- Make sure you're on the quiz page
- Check that `quizContent` div is visible (not hidden)
- Verify HTML has `<span id="quizTimer">` element

#### 2. Timer Not Starting
**Symptom**: Timer shows `00:00:00` and doesn't update

**Solution**:
- Check browser console for JavaScript errors
- Verify `startQuizTimer()` is being called
- Check if `setInterval` is working (should update every second)

#### 3. Timer Not Visible
**Symptom**: Timer exists but can't see it

**Solution**:
- Check CSS: `.quiz-timer` should have `display: inline-block`
- Check if parent `.quiz-meta` is visible
- Verify timer is not hidden by other elements

#### 4. Time Not Being Recorded
**Symptom**: Timer works but time is 0 in database

**Solution**:
- Check browser console: Should see time logged when submitting
- Check backend logs: Should see `[DEBUG] Saving progress... time_taken_seconds = ...`
- Verify `time_taken_seconds` is being sent in API request
- Check database: Run `python test_time_storage.py`

### Testing Steps:

1. **Generate a Quiz**:
   - Go to Quiz section
   - Enter topic and generate quiz
   - Select questions and create quiz

2. **Check Timer**:
   - Timer should appear in quiz header
   - Should show `00:00:00` initially
   - Should update every second

3. **Wait 10-20 seconds** before submitting

4. **Submit Quiz**:
   - Check browser console for time logged
   - Check backend terminal for time received
   - Check database for time stored

5. **Verify Database**:
   ```bash
   python -c "import sqlite3; conn = sqlite3.connect('database/students.db'); cursor = conn.execute('SELECT topic, time_spent_seconds, time_spent_formatted FROM student_progress ORDER BY id DESC LIMIT 1'); row = cursor.fetchone(); print(f'Last quiz: {row[0]} - {row[1]}s = {row[2]}')"
   ```

### Debug Commands:

**Check if timer element exists:**
```javascript
// In browser console:
document.getElementById('quizTimer')
```

**Check timer state:**
```javascript
// In browser console:
appState.quizElapsedSeconds
appState.quizStartTime
appState.quizTimerInterval
```

**Manually start timer:**
```javascript
// In browser console:
startQuizTimer()
```

**Check database:**
```bash
python test_time_storage.py
```

### Expected Behavior:

- ✅ Timer appears in quiz header when quiz is displayed
- ✅ Timer starts at `00:00:00` and updates every second
- ✅ Timer shows correct time (e.g., `00:01:30` after 90 seconds)
- ✅ When quiz is submitted, time is logged in console
- ✅ Time is sent to backend in API request
- ✅ Time is stored in database as both seconds and formatted string

### Files to Check:

1. **HTML**: `ui/index.html` - Line 268 should have `<span id="quizTimer">`
2. **CSS**: `ui/styles.css` - Should have `.quiz-timer` styles
3. **JavaScript**: `ui/script.js` - Should have `startQuizTimer()`, `updateTimerDisplay()`, `stopQuizTimer()`
4. **Backend**: `src/database/student_db.py` - Should save `time_spent_formatted`

