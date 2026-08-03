"""In-memory duplicate-detection cache with a sliding time window."""
import time
import threading


class DuplicateCache:
    def __init__(self, window_seconds: int = 30):
        self.window_seconds = window_seconds
        self._store = {}  # plate -> last_seen_timestamp
        self._lock = threading.Lock()

    def is_duplicate(self, plate: str) -> bool:
        now = time.time()
        with self._lock:
            last_seen = self._store.get(plate)
            if last_seen is not None and (now - last_seen) < self.window_seconds:
                return True
            self._store[plate] = now
            return False

    def size(self) -> int:
        return len(self._store)

    def clear(self):
        with self._lock:
            self._store.clear()

    def purge_expired(self):
        now = time.time()
        with self._lock:
            expired = [p for p, t in self._store.items() if now - t > self.window_seconds]
            for p in expired:
                del self._store[p]


duplicate_cache = DuplicateCache()
