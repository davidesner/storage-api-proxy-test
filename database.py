import sqlite3
from datetime import datetime
import json

class WorkspaceDatabase:
    def __init__(self):
        self.conn = sqlite3.connect('workspaces.db', check_same_thread=False)
        self.create_tables()
        
    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workspace_credentials (
                workspace_name TEXT PRIMARY KEY,
                workspace_id TEXT NOT NULL,
                credentials TEXT,
                updated_at DATETIME
            )
        ''')
        self.conn.commit()
        
    def get_credentials(self, workspace_name: str) -> dict:
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT workspace_id, credentials FROM workspace_credentials WHERE workspace_name = ?', 
            (workspace_name,)
        )
        result = cursor.fetchone()
        if not result:
            return None
        return {
            "id": result[0],
            "credentials": json.loads(result[1])
        }
        
    def store_credentials(self, workspace_name: str, workspace_id: str, credentials: dict):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO workspace_credentials (workspace_name, workspace_id, credentials, updated_at)
            VALUES (?, ?, ?, ?)
        ''', (workspace_name, workspace_id, json.dumps(credentials), datetime.utcnow()))
        self.conn.commit() 