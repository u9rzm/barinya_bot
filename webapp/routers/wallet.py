from fastapi import APIRouter, HTTPException, Depends, Query
from shared.redis import get_redis
from shared.services.cache_service import CacheUser
from webapp.dependencies.auth import get_current_user
from shared.logging_config import get_logger
from datetime import datetime
import json

logger = get_logger(__name__)
router = APIRouter(tags=["wallet"])

WALLET_CACHE_PREFIX = "wallet_connection"
WALLET_CACHE_TTL = 3600  # 1 час


@router.get("/api/wallet/connect")
async def connect_wallet(
    address: str = Query(..., description="Wallet address to connect"),
    session: CacheUser = Depends(get_current_user)
):
    """
    Подключение кошелька к пользователю
    Сохраняет данные в кеш для дальнейшей обработки
    """
    if not address:
        raise HTTPException(400, "Wallet address is required")
    
    # Валидация адреса кошелька (базовая проверка)
    if len(address) < 10:
        raise HTTPException(400, "Invalid wallet address format")
    
    try:
        redis = get_redis()
        
        # Создаем ключ для кеша
        cache_key = f"{WALLET_CACHE_PREFIX}:{session.telegram_id}"
        
        # Данные для сохранения в кеш
        wallet_data = {
            "user_id": session.id,
            "telegram_id": session.telegram_id,
            "wallet_address": address,
            "status": "pending",
            "connected_at": None
        }
        
        # Сохраняем в кеш
        await redis.set(
            cache_key,
            json.dumps(wallet_data),
            ex=WALLET_CACHE_TTL
        )
        
        logger.info(f"Wallet connection request cached for user {session.telegram_id}, address: {address}")
        
        return {
            "success": True,
            "message": "Wallet connection request saved",
            "wallet_address": address,
            "status": "pending",
            "loyalty_points": session.loyalty_points,
            "loyalty_level_id": session.loyalty_level_id
        }
        
    except Exception as e:
        logger.error(f"Error connecting wallet for user {session.telegram_id}: {str(e)}")
        raise HTTPException(500, "Failed to process wallet connection")


@router.get("/api/wallet/disconnect")
async def disconnect_wallet(
    session: CacheUser = Depends(get_current_user)
):
    """
    Отключение кошелька от пользователя
    Удаляет данные из кеша
    """
    try:
        redis = get_redis()
        cache_key = f"{WALLET_CACHE_PREFIX}:{session.telegram_id}"
        
        # Проверяем, есть ли данные в кеше
        cached_data = await redis.get(cache_key)
        
        if cached_data:
            # Удаляем данные из кеша
            await redis.delete(cache_key)
            logger.info(f"Wallet disconnected for user {session.telegram_id}")
            
            return {
                "success": True,
                "message": "Wallet disconnected successfully",
                "loyalty_points": session.loyalty_points,
                "loyalty_level_id": session.loyalty_level_id
            }
        else:
            # Если данных нет в кеше, все равно возвращаем успех
            logger.info(f"No wallet connection found for user {session.telegram_id}")
            
            return {
                "success": True,
                "message": "No wallet connection found",
                "loyalty_points": session.loyalty_points,
                "loyalty_level_id": session.loyalty_level_id
            }
        
    except Exception as e:
        logger.error(f"Error disconnecting wallet for user {session.telegram_id}: {str(e)}")
        raise HTTPException(500, "Failed to disconnect wallet")