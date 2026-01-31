from shared.redis import get_redis
from shared.config import settings
from datetime import datetime, timedelta
from typing import Optional
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
    referrer_id: int | None = None
    expires_at: datetime | None = None
class CacheOrder(BaseModel):
    """Redis Order Model"""
    pass


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
