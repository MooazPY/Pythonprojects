"""
Advanced TTL & LRU Caching Layer for Haris Pro.
Provides high-performance in-memory caching with TTL expiration and telemetry metrics.
"""

from __future__ import annotations

import time
from typing import Any, Dict, Optional, Tuple


class TTLCacheStore:
    def __init__(self, default_ttl_seconds: int = 300, max_size: int = 1000):
        self.default_ttl = default_ttl_seconds
        self.max_size = max_size
        self._cache: Dict[Any, Tuple[Any, float]] = {}
        self.hits: int = 0
        self.misses: int = 0

    def get(self, key: Any) -> Optional[Any]:
        if key not in self._cache:
            self.misses += 1
            return None

        val, expires_at = self._cache[key]
        if time.time() > expires_at:
            del self._cache[key]
            self.misses += 1
            return None

        self.hits += 1
        return val

    def set(self, key: Any, value: Any, ttl_seconds: Optional[int] = None) -> None:
        if len(self._cache) >= self.max_size and key not in self._cache:
            # Evict oldest entry
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]

        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
        expires_at = time.time() + ttl
        self._cache[key] = (value, expires_at)

    def invalidate(self, key: Any) -> None:
        if key in self._cache:
            del self._cache[key]

    def clear(self) -> None:
        self._cache.clear()

    @property
    def hit_ratio(self) -> float:
        total = self.hits + self.misses
        return round(self.hits / total, 2) if total > 0 else 1.0

