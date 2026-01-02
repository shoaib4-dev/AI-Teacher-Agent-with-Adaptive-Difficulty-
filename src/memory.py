"""
Agent Memory - Mandatory Feature
Simple conversation memory
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.database.db import get_db_connection
from datetime import datetime
from typing import List, Dict

class AgentMemory:
    """Simple agent memory"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_table()
    
    def _init_table(self):
        """Initialize memory table"""
        conn = get_db_connection(self.db_path)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS agent_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                user_message TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                context TEXT,
                timestamp TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()
    
    def store_conversation(self, user_id: str, user_message: str, ai_response: str, context: str = None):
        """Store conversation"""
        conn = get_db_connection(self.db_path)
        conn.execute(
            "INSERT INTO agent_memory (user_id, user_message, ai_response, context, timestamp) VALUES (?, ?, ?, ?, ?)",
            (user_id, user_message, ai_response, context, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
    
    def get_memory(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get memory"""
        conn = get_db_connection(self.db_path)
        cursor = conn.execute(
            "SELECT user_message, ai_response, context, timestamp FROM agent_memory WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
            (user_id, limit)
        )
        rows = cursor.fetchall()
        conn.close()
        return [
            {"user_message": r[0], "ai_response": r[1], "context": r[2], "timestamp": r[3]}
            for r in rows
        ]
    
    def get_context(self, user_id: str, limit: int = 5) -> str:
        """Get context string"""
        memory = self.get_memory(user_id, limit)
        parts = []
        for m in reversed(memory):
            parts.append(f"User: {m['user_message']}")
            parts.append(f"Assistant: {m['ai_response']}")
        return "\n".join(parts)

