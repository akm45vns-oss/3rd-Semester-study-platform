"""
Centralized Groq Key Manager for Multi-Key Distribution, Health Tracking & Rate Limit Failover.

Security Rules:
- NEVER logs or displays raw API keys.
- Each request uses exactly ONE isolated API key.
- Round-robin key distribution with automatic health recovery.
"""
import asyncio
import time
import logging
from enum import Enum
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from app.core.config import settings

logger = logging.getLogger("GroqKeyManager")


class KeyStatus(str, Enum):
    HEALTHY = "HEALTHY"
    RATE_LIMITED = "RATE_LIMITED"
    INVALID = "INVALID"


class AllKeysUnavailableError(Exception):
    """Raised when all configured Groq API keys are currently rate-limited or invalid."""
    pass


@dataclass
class ManagedKey:
    index: int  # 1-indexed (e.g. 1 for KEY 1)
    api_key: str = field(repr=False)  # Never expose in repr
    status: KeyStatus = KeyStatus.HEALTHY
    cooldown_until: float = 0.0
    requests_count: int = 0
    success_count: int = 0
    rate_limit_count: int = 0
    failure_count: int = 0
    latency_ms_total: float = 0.0

    @property
    def label(self) -> str:
        return f"KEY {self.index}"

    @property
    def masked(self) -> str:
        if len(self.api_key) <= 8:
            return "***"
        return f"{self.api_key[:4]}...{self.api_key[-4:]}"

    def is_available(self, now: float) -> bool:
        if self.status == KeyStatus.INVALID:
            return False
        if self.status == KeyStatus.RATE_LIMITED:
            if now >= self.cooldown_until:
                self.status = KeyStatus.HEALTHY
                self.cooldown_until = 0.0
                logger.info(f"[{self.label}] Cooldown expired. Restored to HEALTHY.")
                return True
            return False
        return self.status == KeyStatus.HEALTHY


class GroqKeyManager:
    """
    Thread-safe & async-safe Groq multi-key manager.
    Supports up to 5+ keys with automatic failover, backoff, and health tracking.
    """

    def __init__(self, raw_keys: Optional[List[str]] = None, default_cooldown_seconds: float = 60.0):
        self._lock = asyncio.Lock()
        self._current_index: int = 0
        self._default_cooldown: float = default_cooldown_seconds
        self._keys: List[ManagedKey] = []

        keys_to_load = raw_keys if raw_keys is not None else settings.get_groq_keys()
        if not keys_to_load:
            logger.warning("No Groq API keys found in environment variables (GROQ_API_KEY_1..5, GROQ_API_KEYS, GROQ_API_KEY).")
        
        for idx, k in enumerate(keys_to_load, start=1):
            self._keys.append(ManagedKey(index=idx, api_key=k))

        logger.info(f"Initialized GroqKeyManager with {len(self._keys)} active key slots.")

    @property
    def key_count(self) -> int:
        return len(self._keys)

    @property
    def active_key_count(self) -> int:
        now = time.time()
        return sum(1 for k in self._keys if k.is_available(now))

    async def get_next_key(self) -> ManagedKey:
        """
        Acquire the next available healthy key in round-robin fashion.
        If all keys are currently cooling down, calculates wait time or raises AllKeysUnavailableError.
        """
        async with self._lock:
            if not self._keys:
                raise AllKeysUnavailableError("No Groq API keys configured.")

            now = time.time()
            total_keys = len(self._keys)

            # Check if any key is currently available
            for _ in range(total_keys):
                candidate = self._keys[self._current_index % total_keys]
                self._current_index += 1

                if candidate.is_available(now):
                    candidate.requests_count += 1
                    return candidate

            # If no healthy key, find the earliest recovering key
            cooling_keys = [k for k in self._keys if k.status == KeyStatus.RATE_LIMITED]
            if not cooling_keys:
                raise AllKeysUnavailableError("All configured Groq keys are permanently INVALID.")

            earliest = min(cooling_keys, key=lambda k: k.cooldown_until)
            wait_seconds = max(1.0, earliest.cooldown_until - now)
            logger.warning(
                f"ALL GROQ KEYS TEMPORARILY UNAVAILABLE (Rate-Limited). "
                f"Earliest recovery in {wait_seconds:.1f}s ({earliest.label})."
            )
            raise AllKeysUnavailableError(
                f"All {len(self._keys)} Groq keys rate-limited. Nearest recovery in {wait_seconds:.1f}s."
            )

    async def mark_rate_limited(self, key_index: int, cooldown_seconds: Optional[float] = None) -> None:
        """Mark a specific key as rate-limited with exponential cooldown."""
        async with self._lock:
            for k in self._keys:
                if k.index == key_index:
                    cd = cooldown_seconds if cooldown_seconds is not None else self._default_cooldown
                    # Exponential backoff on repeated 429
                    if k.status == KeyStatus.RATE_LIMITED:
                        cd = min(300.0, cd * 1.5)
                    k.status = KeyStatus.RATE_LIMITED
                    k.cooldown_until = time.time() + cd
                    k.rate_limit_count += 1
                    logger.warning(
                        f"[{k.label}] Rate limit (429) recorded. Cooldown for {cd:.1f}s (Rate limit count: {k.rate_limit_count})."
                    )
                    break

    async def mark_invalid(self, key_index: int, reason: str = "Auth Failure") -> None:
        """Mark a key permanently invalid (e.g. 401 Unauthorized)."""
        async with self._lock:
            for k in self._keys:
                if k.index == key_index:
                    k.status = KeyStatus.INVALID
                    k.failure_count += 1
                    logger.error(f"[{k.label}] Marked permanently INVALID due to: {reason}")
                    break

    async def record_success(self, key_index: int, latency_ms: float) -> None:
        """Record successful generation latency and success metric."""
        async with self._lock:
            for k in self._keys:
                if k.index == key_index:
                    k.success_count += 1
                    k.latency_ms_total += latency_ms
                    break

    async def record_failure(self, key_index: int) -> None:
        """Record non-rate-limit network failure."""
        async with self._lock:
            for k in self._keys:
                if k.index == key_index:
                    k.failure_count += 1
                    break

    def get_stats_summary(self) -> List[Dict[str, Any]]:
        """Get sanitized per-key statistics for the final report."""
        summary = []
        now = time.time()
        for k in self._keys:
            avg_latency = (k.latency_ms_total / k.success_count) if k.success_count > 0 else 0.0
            status_desc = k.status.value
            if k.status == KeyStatus.RATE_LIMITED and k.cooldown_until > now:
                status_desc = f"COOLDOWN ({int(k.cooldown_until - now)}s left)"
            summary.append({
                "label": k.label,
                "status": status_desc,
                "requests": k.requests_count,
                "successes": k.success_count,
                "rate_limits": k.rate_limit_count,
                "failures": k.failure_count,
                "avg_latency_ms": round(avg_latency, 1),
            })
        return summary
