from fastapi import APIRouter, HTTPException, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from shared.config import settings
from shared.database import get_db
from shared.redis import get_redis

from shared.services.cache_service import create_session, CacheUser
from webapp.dependencies.auth import get_current_user

from webapp.middleware.telegram import TelegramWebAppAuth
from shared.services.user_service import UserService
from shared.logging_config import get_logger
import logging
from urllib.parse import unquote


logger = get_logger(__name__)
router = APIRouter(tags=["auth"])

# 
@router.get("/api/auth")
async def auth(
    initData: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    if not initData:
        raise HTTPException(400, "initData missing")

    decoded_init_data = unquote(initData)

    telegram_user = TelegramWebAppAuth(
        settings.telegram_bot_token
    ).validate_init_data(decoded_init_data)

    if not telegram_user:
        raise HTTPException(401, "Invalid Telegram initData")

    data_from_db = await UserService(db).get_user_by_telegram_id(
        telegram_user["telegram_id"]
    )

    if not data_from_db:
        raise HTTPException(404, "User not found")



    session = CacheUser(
        id=data_from_db.id,
        telegram_id=data_from_db.telegram_id,
        loyalty_points=data_from_db.loyalty_points,
        wallet=data_from_db.wallet,
        total_spent=data_from_db.total_spent,
        loyalty_level_id=data_from_db.loyalty_level_id,
        referrer_id=data_from_db.referrer_id,
    )

    token = await create_session(session)

    logger.info(f"Auth success telegram_id={session.telegram_id}")

    return {
        "access_token": token,
        "loyalty_points": session.loyalty_points,
        "loyalty_level_id": session.loyalty_level_id,
    }


@router.get("/api/auth/check")
async def auth_check(session: CacheUser = Depends(get_current_user)):
    logger.info(f"Getting cach from session : {session} ")
    return {
        'loyalty_points': session.loyalty_points,
        'loyalty_level_id': session.loyalty_level_id,
    }