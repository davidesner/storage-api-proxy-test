import aiosqlite
from datetime import datetime
import json
import os
import asyncio
from typing import Optional

class WorkspaceDatabase:
    def __init__(self):
        self.db_path = 'data/workspaces.db'
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._connection: Optional[aiosqlite.Connection] = None
        self._lock = asyncio.Lock()
        
    async def _get_connection(self) -> aiosqlite.Connection:
        async with self._lock:
            if self._connection is None:
                self._connection = await aiosqlite.connect(self.db_path)
            return self._connection
        
    async def initialize(self):
        """Initialize the database with required tables"""
        conn = await self._get_connection()
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS workspace_credentials (
                workspace_name TEXT PRIMARY KEY,
                workspace_id TEXT NOT NULL,
                credentials TEXT,
                updated_at DATETIME
            )
        ''')
        await conn.commit()
        
    async def get_credentials(self, workspace_name: str) -> dict:
        conn = await self._get_connection()
        async with conn.execute(
            'SELECT workspace_id, credentials FROM workspace_credentials WHERE workspace_name = ?', 
            (workspace_name,)
        ) as cursor:
            result = await cursor.fetchone()
            if not result:
                return None
            return {
                "id": result[0],
                "credentials": json.loads(result[1])
            }
        
    async def store_credentials(self, workspace_name: str, workspace_id: str, credentials: dict):
        conn = await self._get_connection()
        await conn.execute('''
            INSERT OR REPLACE INTO workspace_credentials (workspace_name, workspace_id, credentials, updated_at)
            VALUES (?, ?, ?, ?)
        ''', (workspace_name, workspace_id, json.dumps(credentials), datetime.utcnow()))
        await conn.commit()
        
    async def close(self):
        """Close the database connection"""
        if self._connection is not None:
            await self._connection.close()
            self._connection = None 