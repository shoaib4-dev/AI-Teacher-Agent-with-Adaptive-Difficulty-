# Data Sources - What the Agent Retrieves

## Overview
The AI Teacher Agent retrieves data from **multiple sources** to fulfill the project requirement of "at least one source" with support for multiple formats.

## Data Sources Implemented

### 1. ✅ JSON Dataset (Custom-made Dataset)
- **File**: `data/topics_dataset.json`
- **Type**: Custom-made educational topics dataset
- **Content**: 8 educational topics with metadata (category, difficulty, description, key concepts, tags)
- **Usage**: Primary data source for search, filter, and categorize operations
- **Query Types Supported**:
  - **Search**: Search by topic name, description, tags, or key concepts
  - **Filter**: Filter by category, difficulty, or tags
  - **Categorize**: Group topics by categories

### 2. ✅ CSV Dataset (Custom-made Dataset)
- **File**: `data/topics_dataset.csv`
- **Type**: Custom-made dataset in CSV format
- **Content**: Same educational topics data in CSV format
- **Usage**: Alternative data source (auto-detected by DataService)
- **Query Types Supported**: Same as JSON (search, filter, categorize)

### 3. ✅ SQLite Database
- **File**: `database/ai_teacher.db` (or custom database)
- **Type**: Database storage
- **Content**: 
  - User queries (`topic_queries` table)
  - Quiz generations (`quiz_generations` table)
  - Quiz evaluations (`quiz_evaluations` table)
  - Chat messages (`chat_messages` table)
  - Agent decisions (`agent_decisions` table)
  - Agent memory (`agent_memory` table)
- **Usage**: 
  - Stores all logs, outputs, reports, queries, and decisions
  - Can be queried for historical data
  - Supports `database_search` query type

## Query Types (3 Required)

The agent supports **3 types of queries** as required:

### 1. Search Query
- **Purpose**: Find topics matching a search term
- **Data Source**: JSON/CSV dataset
- **Example**: Search for "python" returns topics containing "python" in name, description, tags, or concepts
- **Endpoint**: `POST /api/query` with `query_type: "search"`

### 2. Filter Query
- **Purpose**: Filter topics by specific criteria
- **Data Source**: JSON/CSV dataset
- **Example**: Filter by `{"category": "programming"}` or `{"difficulty": "Beginner"}`
- **Endpoint**: `POST /api/query` with `query_type: "filter"`

### 3. Categorize Query
- **Purpose**: Group topics by categories
- **Data Source**: JSON/CSV dataset
- **Example**: Returns all topics grouped by category (programming, ai, data, etc.)
- **Endpoint**: `POST /api/query` with `query_type: "categorize"`

### Bonus: Database Search
- **Purpose**: Search historical queries from database
- **Data Source**: SQLite database
- **Example**: Search for past topic queries
- **Endpoint**: `POST /api/query` with `query_type: "database_search"`

## Implementation Details

### DataService Class
- **Location**: `src/services/data_service.py`
- **Features**:
  - Auto-detects data source type (JSON or CSV)
  - Loads data from file
  - Provides search, filter, and categorize methods
  - Supports both JSON and CSV formats

### Agent Integration
- **Location**: `src/agent.py`
- **Method**: `query()` method uses DataService
- **Logging**: All queries logged in `agent_decisions` table

## Data Source Priority

1. **JSON Dataset** (Primary) - `data/topics_dataset.json`
2. **CSV Dataset** (Alternative) - `data/topics_dataset.csv`
3. **SQLite Database** (Storage & History) - `database/ai_teacher.db`

## Example Usage

### Search from JSON/CSV Dataset
```python
# Search for "python"
POST /api/query
{
    "query_type": "search",
    "query": "python",
    "limit": 10
}
```

### Filter from JSON/CSV Dataset
```python
# Filter programming topics
POST /api/query
{
    "query_type": "filter",
    "query": '{"category": "programming"}',
    "limit": 10
}
```

### Categorize from JSON/CSV Dataset
```python
# Categorize all topics
POST /api/query
{
    "query_type": "categorize",
    "query": "",
    "limit": 20
}
```

### Search from Database
```python
# Search historical queries
POST /api/query
{
    "query_type": "database_search",
    "query": "machine learning",
    "limit": 10
}
```

## Summary

✅ **Data Sources**: JSON (custom-made), CSV (custom-made), SQLite Database  
✅ **Query Types**: Search, Filter, Categorize (3 required types)  
✅ **Auto-detection**: Automatically detects JSON or CSV format  
✅ **Database Integration**: Can query both dataset and database  
✅ **Comprehensive**: Meets and exceeds project requirements

