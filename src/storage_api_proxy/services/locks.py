import asyncio
from datetime import datetime, timedelta
from typing import Dict

class WorkspaceLocks:
    def __init__(self, timeout_seconds: int = 30):
        self.locks: Dict[str, asyncio.Lock] = {}
        self.lock_times: Dict[str, datetime] = {}
        self.timeout = timeout_seconds
        self._cleanup_lock = asyncio.Lock()

    async def acquire_lock(self, workspace_name: str) -> bool:
        """Try to acquire a lock for a workspace"""
        async with self._cleanup_lock:
            await self._cleanup_expired_locks()
            
            if workspace_name not in self.locks:
                self.locks[workspace_name] = asyncio.Lock()
            
            try:
                # Try to acquire the lock with timeout
                lock = self.locks[workspace_name]
                await asyncio.wait_for(lock.acquire(), timeout=self.timeout)
                self.lock_times[workspace_name] = datetime.utcnow()
                return True
            except asyncio.TimeoutError:
                return False

    async def release_lock(self, workspace_name: str) -> None:
        """Release a workspace lock"""
        if workspace_name in self.locks and self.locks[workspace_name].locked():
            self.locks[workspace_name].release()
            self.lock_times.pop(workspace_name, None)

    async def _cleanup_expired_locks(self) -> None:
        """Remove expired locks"""
        now = datetime.utcnow()
        expired = [
            name for name, time in self.lock_times.items()
            if now - time > timedelta(seconds=self.timeout)
        ]
        for name in expired:
            await self.release_lock(name) 