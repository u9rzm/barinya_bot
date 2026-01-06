from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shared.config import settings
from shared.database import get_db
from shared.services.jwt import create_access_token
from webapp.middleware.telegram import TelegramWebAppAuth
from shared.services.user_service import UserService
from shared.logging_config import get_logger
import logging


logger = get_logger(__name__)
router = APIRouter(tags=["auth"])


@router.post("/api/auth")
async def auth(data: dict, db: AsyncSession = Depends(get_db)):
    lo
    
    init_data = data.get("initData")
    if not init_data:
        raise HTTPException(400, "initData missing")

    telegram_user = TelegramWebAppAuth(
        settings.telegram_bot_token
    ).validate_init_data(init_data)

    if not telegram_user:
        raise HTTPException(401, "Invalid Telegram initData")

    # # Получаем пользователя
    # await UserService(db).get_user_by_telegram_id(
    #     telegram_user["telegram_id"]
    # ) 
    # записываем количество боллов
    token = create_access_token({
        "telegram_id": telegram_user["telegram_id"]
    })

    return {"access_token": token}
