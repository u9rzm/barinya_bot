from shared.redis import get_redis
from shared.config import settings
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pydantic import BaseModel
import json
import secrets


class CacheUser(BaseModel):
    """Redis User Model"""
    id: int
    telegram_id: int
    loyalty_points: float | None = 0
    total_spent: float | None = 0
    loyalty_level_id: int | None = 0
    wallet: str | None = None
    referrer_id: int | None = None
    expires_at: datetime | None = None
class CacheOrder(BaseModel):
    """Redis Order Model"""
    pass


class CacheStatistics(BaseModel):
    """Cached statistics model"""
    data: Dict[str, Any]
    cached_at: datetime
    expires_at: datetime


ttl = settings.session_ttl
session_ttl = settings.session_max_lifetime
SESSION_PREFIX = 'User-session'

"""Write session on first auth"""
async def create_session(data: CacheUser) -> str:
    token: str = secrets.token_urlsafe(32)

    now = datetime.utcnow()
    expires_at = now + timedelta(seconds=session_ttl)


    data.expires_at = expires_at

    await get_redis().set(
        f"{SESSION_PREFIX}:{token}",
        data.model_dump_json(),
        ex=ttl,
    )
    return token

"""Read User Session"""
async def get_session(token: str) -> dict | None:
    redis = get_redis()
    key = f"{SESSION_PREFIX}:{token}"

    raw = await redis.get(key)
    if not raw:
        return None

    session = CacheUser.model_validate_json(raw)

    # max lifetime check
    if session.expires_at < datetime.utcnow():
        await redis.delete(key)
        return None
    # sliding TTL
    await redis.expire(key, ttl)

    return session

async def revoke_session(token: str):
    await get_redis().delete(f"session:{token}")


# Statistics caching
STATISTICS_PREFIX = 'statistics'
STATISTICS_TTL = 30 * 60  # 30 minutes


async def cache_statistics(stats_type: str, data: Dict[str, Any]) -> None:
    """Cache statistics data with TTL."""
    try:
        now = datetime.utcnow()
        expires_at = now + timedelta(seconds=STATISTICS_TTL)
        
        cache_data = CacheStatistics(
            data=data,
            cached_at=now,
            expires_at=expires_at
        )
        
        await get_redis().set(
            f"{STATISTICS_PREFIX}:{stats_type}",
            cache_data.model_dump_json(),
            ex=STATISTICS_TTL,
        )
    except Exception:
        # Silently fail if Redis is not available
        pass


async def get_cached_statistics(stats_type: str) -> Optional[Dict[str, Any]]:
    """Get cached statistics data."""
    try:
        redis = get_redis()
        key = f"{STATISTICS_PREFIX}:{stats_type}"
        
        raw = await redis.get(key)
        if not raw:
            return None
        
        try:
            cached_stats = CacheStatistics.model_validate_json(raw)
            
            # Check if expired
            if cached_stats.expires_at < datetime.utcnow():
                await redis.delete(key)
                return None
            
            return cached_stats.data
        except Exception:
            # If parsing fails, delete the key
            await redis.delete(key)
            return None
    except Exception:
        # Return None if Redis is not available
        return None


async def invalidate_statistics_cache(stats_type: Optional[str] = None) -> None:
    """Invalidate statistics cache."""
    try:
        redis = get_redis()
        
        if stats_type:
            # Invalidate specific type
            await redis.delete(f"{STATISTICS_PREFIX}:{stats_type}")
        else:
            # Invalidate all statistics
            keys = await redis.keys(f"{STATISTICS_PREFIX}:*")
            if keys:
                await redis.delete(*keys)
    except Exception:
        # Silently fail if Redis is not available
        pass


async def get_statistics_cache_info() -> Dict[str, Any]:
    """Get information about cached statistics."""
    try:
        redis = get_redis()
        keys = await redis.keys(f"{STATISTICS_PREFIX}:*")
        
        cache_info = {}
        for key in keys:
            raw = await redis.get(key)
            if raw:
                try:
                    cached_stats = CacheStatistics.model_validate_json(raw)
                    stats_type = key.split(":")[-1]
                    cache_info[stats_type] = {
                        "cached_at": cached_stats.cached_at.isoformat(),
                        "expires_at": cached_stats.expires_at.isoformat(),
                        "ttl": await redis.ttl(key)
                    }
                except Exception:
                    continue
        
        return cache_info
    except Exception:
        # Return empty dict if Redis is not available
        return {}
