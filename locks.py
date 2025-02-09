import threading
from typing import Dict

class WorkspaceLocks:
    def __init__(self):
        self._locks: Dict[str, threading.Lock] = {}
        self._locks_lock = threading.Lock()
        
    def get_lock(self, workspace_name: str) -> threading.Lock:
        with self._locks_lock:
            if workspace_name not in self._locks:
                self._locks[workspace_name] = threading.Lock()
            return self._locks[workspace_name]
            
    def acquire_lock(self, workspace_name: str, timeout: float = 10.0) -> bool:
        lock = self.get_lock(workspace_name)
        return lock.acquire(timeout=timeout)
        
    def release_lock(self, workspace_name: str):
        lock = self.get_lock(workspace_name)
        try:
            lock.release()
        except RuntimeError:
            # Lock was already released
            pass 