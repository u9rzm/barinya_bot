from fastapi import APIRouter, HTTPException, Depends, Query, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession

from shared.config import settings
from shared.database import get_db
from shared.redis import get_redis

from shared.services.cache_service import create_session, CacheUser
from webapp.dependencies.auth import get_current_user
from fastapi.responses import JSONResponse
from webapp.middleware.telegram import TelegramWebAppAuth
from shared.services.user_service import UserService
from shared.logging_config import get_logger
import logging
from urllib.parse import unquote


logger = get_logger(__name__)
router = APIRouter(tags=["auth"])

# 
@router.get("/api/auth/user")
async def auth_user(
    authorization: str | None = Header(None),
    db: AsyncSession = Depends(get_db),
    ):
    if not authorization:
        return JSONResponse(
            status_code=401,
            content={"error": "unauthorized", "message": "Authorization header missing"},
        )

    try:
        scheme, token = authorization.split(" ", 1)
    except ValueError:
        return JSONResponse(
            status_code=401,
            content={"error": "unauthorized", "message": "Invalid authorization header format"},
        )

    if scheme.lower() != "tma":
        return JSONResponse(
            status_code=401,
            content={"error": "unauthorized", "message": f"Unsupported auth scheme: {scheme}"},
        )

    decoded_init_data = unquote(token)

    telegram_user = TelegramWebAppAuth(
        settings.telegram_bot_token
    ).validate_init_data(decoded_init_data)

    if not telegram_user:
        return JSONResponse(
            status_code=401,
            content={"error": "unauthorized", "message": "Invalid Telegram initData"},
        )

    # Получаем или создаём пользователя в БД
    data_from_db = await UserService(db).get_user_by_telegram_id(
        telegram_user["telegram_id"]
    )

    if not data_from_db:
        await UserService(db).create_user(
                    telegram_id=telegram_user["telegram_id"]
                    )
        await db.commit()

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

    return JSONResponse(
        status_code=200,
        content={
        "user":{
            "access_token": token,
            "loyalty_points": session.loyalty_points,
            "loyalty_level_id": session.loyalty_level_id,
    },
    "message": "Authentication successful",})

@router.get("/api/auth/user/check")
async def auth_check_user(session: CacheUser = Depends(get_current_user)):
    logger.info(f"Getting cach from session : {session} ")
    return JSONResponse(
        status_code=200,
        content={
        "user":{
            "loyalty_points": session.loyalty_points,
            "loyalty_level_id": session.loyalty_level_id,
    },
    "message": "Authentication successful",})

@router.get("/api/auth/iikofront")
async def auth_iikofront(
    authorization: str | None = Header(None),
    db: AsyncSession = Depends(get_db),
    ):
    if not authorization:
        return JSONResponse(
            status_code=401,
            content={"error": "unauthorized", "message": "Authorization header missing"},
        )
    try:
        scheme, token = authorization.split(" ", 1)
    except ValueError:
        return JSONResponse(
            status_code=401,
            content={"error": "unauthorized", "message": "Invalid authorization header format"},
        )

    if scheme.lower() != "iikofront":
        return JSONResponse(
            status_code=401,
            content={"error": "unauthorized", "message": f"Unsupported auth scheme: {scheme}"},
        )

    session = CacheIikoFront(
        id=data_from_db.id,
        telegram_id=data_from_db.telegram_id,
        loyalty_points=data_from_db.loyalty_points,
        wallet=data_from_db.wallet,
        total_spent=data_from_db.total_spent,
        loyalty_level_id=data_from_db.loyalty_level_id,
        referrer_id=data_from_db.referrer_id,
    )

    token = await create_session(session)

    logger.info(f"Auth success iikoFront")

    return JSONResponse(
        status_code=200,
        content={
            "message": "Authentication iikoFront successful",})