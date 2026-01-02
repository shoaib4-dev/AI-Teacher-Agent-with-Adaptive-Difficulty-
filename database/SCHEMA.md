# Database Schema Documentation

## Overview
SQLite database for AI Teacher Agent storing logs, outputs, user queries, agent decisions, and metadata.

## Tables

### 1. `users`
Stores user account information.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key, auto-increment |
| name | TEXT | User's full name |
| email | TEXT | Unique email address |
| password | TEXT | Hashed password |
| created_at | TEXT | Account creation timestamp (ISO format) |

**Indexes:** None

---

### 2. `topic_queries`
Logs all topic explanation requests.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key, auto-increment |
| topic_name | TEXT | Name of the topic requested |
| timestamp | TEXT | Query timestamp (ISO format) |
| student_id | TEXT | User ID (default: 'default') |

**Indexes:**
- `idx_topic_queries_timestamp` on `timestamp DESC`

---

### 3. `quiz_generations`
Logs all quiz generation events.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key, auto-increment |
| topic | TEXT | Quiz topic |
| difficulty | TEXT | Difficulty level (Beginner/Intermediate/Advanced) |
| num_questions | INTEGER | Number of questions generated |
| total_marks | INTEGER | Total marks for the quiz |
| timestamp | TEXT | Generation timestamp (ISO format) |
| student_id | TEXT | User ID (default: 'default') |

**Indexes:** None

---

### 4. `quiz_evaluations`
Stores quiz evaluation results and scores.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key, auto-increment |
| quiz_id | TEXT | Quiz identifier |
| score | REAL | Score percentage (0-100) |
| total_questions | INTEGER | Total number of questions |
| correct_answers | INTEGER | Number of correct answers |
| timestamp | TEXT | Evaluation timestamp (ISO format) |
| student_id | TEXT | User ID (default: 'default') |

**Indexes:** None

---

### 5. `chat_messages`
Stores chat conversation messages.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key, auto-increment |
| user_message | TEXT | User's message |
| ai_response | TEXT | AI agent's response |
| timestamp | TEXT | Message timestamp (ISO format) |
| student_id | TEXT | User ID (default: 'default') |

**Indexes:** None

---

### 6. `feedback`
Stores user feedback submissions.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key, auto-increment |
| name | TEXT | User's name |
| email | TEXT | User's email |
| type | TEXT | Feedback type (bug/feature/improvement/other) |
| subject | TEXT | Feedback subject |
| message | TEXT | Feedback message content |
| rating | INTEGER | Rating (1-5) |
| timestamp | TEXT | Submission timestamp (ISO format) |

**Indexes:** None

---

### 7. `file_uploads`
Tracks uploaded files.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key, auto-increment |
| filename | TEXT | Original filename |
| filepath | TEXT | Storage path |
| file_type | TEXT | File type (pdf/doc/jpg/png) |
| uploaded_at | TEXT | Upload timestamp (ISO format) |
| student_id | TEXT | User ID (default: 'default') |

**Indexes:** None

---

### 8. `agent_decisions`
**Logs all agent decisions and outputs** (Critical for project requirements).

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key, auto-increment |
| decision_type | TEXT | Type of decision (summarization/classification/quiz_generation/topic_explanation/query) |
| context | TEXT | Context or input that led to decision |
| decision | TEXT | Decision/output text |
| confidence | REAL | Confidence score (0-1) |
| timestamp | TEXT | Decision timestamp (ISO format) |

**Indexes:** None

**Usage:** This table stores all agent reasoning outputs including:
- Summarization results
- Classification results
- Quiz generation metadata
- Topic explanation metadata
- Query operation results

---

### 9. `agent_memory`
**Agent Memory - Mandatory Feature** (Conversation/Long-term Memory Integration).

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key, auto-increment |
| user_id | TEXT | User identifier |
| user_message | TEXT | User's message |
| ai_response | TEXT | AI's response |
| context | TEXT | Additional context (optional) |
| timestamp | TEXT | Conversation timestamp (ISO format) |
| session_id | TEXT | Session identifier (optional) |

**Indexes:**
- `idx_user_timestamp` on `(user_id, timestamp DESC)`

**Usage:** Stores conversation history for context-aware responses. This is the mandatory Agent Memory feature.

---

## Data Flow

1. **User Queries** → `topic_queries` table
2. **Agent Decisions** → `agent_decisions` table (all reasoning outputs)
3. **Conversations** → `agent_memory` table (mandatory memory feature)
4. **Quiz Operations** → `quiz_generations` and `quiz_evaluations` tables
5. **Outputs/Reports** → Stored in `agent_decisions` with metadata

## Notes

- All timestamps use ISO 8601 format (e.g., "2025-01-15T10:30:00")
- Default `student_id` is "default" for anonymous users
- `agent_decisions` table is critical for logging all AI reasoning outputs
- `agent_memory` table implements the mandatory Agent Memory feature

