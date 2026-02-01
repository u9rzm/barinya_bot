"""Wallet synchronization service for processing cached wallet connections."""
import json
import asyncio
from typing import List, Dict, Any
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from shared.database import get_db
from shared.redis import get_redis
from shared.services.wallet_service import WalletService
from shared.services.user_service import UserService
from shared.logging_config import get_logger

logger = get_logger(__name__)

WALLET_CACHE_PREFIX = "wallet_connection"
WALLET_PROCESSED_PREFIX = "wallet_processed"


class WalletSyncService:
    """Service for synchronizing cached wallet connections with database."""
    
    def __init__(self):
        """Initialize wallet sync service."""
        pass
    
    async def process_cached_wallets(self) -> Dict[str, Any]:
        """
        Process all cached wallet connections and sync with database.
        
        Returns:
            Dictionary with processing results
        """
        redis = get_redis()
        processed_count = 0
        error_count = 0
        results = []
        
        try:
            # Получаем все ключи кеша кошельков
            pattern = f"{WALLET_CACHE_PREFIX}:*"
            keys = await redis.keys(pattern)
            
            logger.info(f"Found {len(keys)} wallet cache entries to process")
            
            for key in keys:
                try:
                    # Получаем данные из кеша
                    cached_data = await redis.get(key)
                    if not cached_data:
                        continue
                    
                    wallet_data = json.loads(cached_data)
                    telegram_id = wallet_data.get("telegram_id")
                    wallet_address = wallet_data.get("wallet_address")
                    user_id = wallet_data.get("user_id")
                    status = wallet_data.get("status", "pending")
                    
                    # Проверяем, что это новое подключение (статус pending)
                    if status != "pending":
                        continue
                    
                    # Проверяем, не обрабатывали ли мы уже этот кошелек
                    processed_key = f"{WALLET_PROCESSED_PREFIX}:{telegram_id}:{wallet_address}"
                    if await redis.exists(processed_key):
                        continue
                    
                    # Обрабатываем подключение кошелька
                    result = await self._process_single_wallet(
                        user_id=user_id,
                        telegram_id=telegram_id,
                        wallet_address=wallet_address,
                        cache_key=key
                    )
                    
                    if result["success"]:
                        processed_count += 1
                        # Отмечаем как обработанный (TTL 24 часа)
                        await redis.set(processed_key, "processed", ex=86400)
                    else:
                        error_count += 1
                    
                    results.append(result)
                    
                except Exception as e:
                    logger.error(f"Error processing wallet cache key {key}: {e}")
                    error_count += 1
                    results.append({
                        "success": False,
                        "key": key,
                        "error": str(e)
                    })
            
            summary = {
                "total_keys": len(keys),
                "processed": processed_count,
                "errors": error_count,
                "timestamp": datetime.utcnow().isoformat(),
                "results": results
            }
            
            logger.info(f"Wallet sync completed: {processed_count} processed, {error_count} errors")
            return summary
            
        except Exception as e:
            logger.error(f"Error in wallet sync process: {e}")
            return {
                "total_keys": 0,
                "processed": processed_count,
                "errors": error_count + 1,
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
    
    async def _process_single_wallet(
        self,
        user_id: int,
        telegram_id: int,
        wallet_address: str,
        cache_key: str
    ) -> Dict[str, Any]:
        """
        Process a single wallet connection.
        
        Args:
            user_id: User ID
            telegram_id: Telegram ID
            wallet_address: Wallet address
            cache_key: Redis cache key
            
        Returns:
            Processing result dictionary
        """
        try:
            # Получаем сессию базы данных
            async for db in get_db():
                try:
                    wallet_service = WalletService(db)
                    user_service = UserService(db)
                    
                    # Проверяем, что пользователь существует
                    user = await user_service.get_user_by_id(user_id)
                    if not user:
                        logger.warning(f"User {user_id} not found for wallet {wallet_address}")
                        return {
                            "success": False,
                            "user_id": user_id,
                            "telegram_id": telegram_id,
                            "wallet_address": wallet_address,
                            "error": "User not found"
                        }
                    
                    # Проверяем, что telegram_id совпадает
                    if user.telegram_id != telegram_id:
                        logger.warning(f"Telegram ID mismatch for user {user_id}: expected {user.telegram_id}, got {telegram_id}")
                        return {
                            "success": False,
                            "user_id": user_id,
                            "telegram_id": telegram_id,
                            "wallet_address": wallet_address,
                            "error": "Telegram ID mismatch"
                        }
                    
                    # Проверяем, изменился ли кошелек
                    if user.wallet == wallet_address:
                        logger.info(f"Wallet {wallet_address} already set for user {user_id}")
                        await self._update_cache_status(cache_key, "connected")
                        return {
                            "success": True,
                            "user_id": user_id,
                            "telegram_id": telegram_id,
                            "wallet_address": wallet_address,
                            "action": "already_connected"
                        }
                    
                    # Добавляем/обновляем кошелек
                    updated_user = await wallet_service.add_wallet_to_user(user_id, wallet_address)
                    
                    # Коммитим изменения
                    await db.commit()
                    
                    # Обновляем статус в кеше
                    await self._update_cache_status(cache_key, "connected")
                    
                    logger.info(f"Successfully connected wallet {wallet_address} to user {user_id}")
                    
                    return {
                        "success": True,
                        "user_id": user_id,
                        "telegram_id": telegram_id,
                        "wallet_address": wallet_address,
                        "action": "connected",
                        "old_wallet": user.wallet
                    }
                    
                except Exception as e:
                    await db.rollback()
                    raise e
                finally:
                    await db.close()
                    
        except Exception as e:
            logger.error(f"Error processing wallet {wallet_address} for user {user_id}: {e}")
            return {
                "success": False,
                "user_id": user_id,
                "telegram_id": telegram_id,
                "wallet_address": wallet_address,
                "error": str(e)
            }
    
    async def _update_cache_status(self, cache_key: str, status: str) -> None:
        """
        Update wallet connection status in cache.
        
        Args:
            cache_key: Redis cache key
            status: New status
        """
        try:
            redis = get_redis()
            cached_data = await redis.get(cache_key)
            
            if cached_data:
                wallet_data = json.loads(cached_data)
                wallet_data["status"] = status
                wallet_data["connected_at"] = datetime.utcnow().isoformat()
                
                # Обновляем кеш с тем же TTL
                ttl = await redis.ttl(cache_key)
                if ttl > 0:
                    await redis.set(cache_key, json.dumps(wallet_data), ex=ttl)
                else:
                    await redis.set(cache_key, json.dumps(wallet_data), ex=3600)
                    
        except Exception as e:
            logger.error(f"Error updating cache status for {cache_key}: {e}")
    
    async def cleanup_old_processed_markers(self) -> int:
        """
        Clean up old processed markers (older than 24 hours).
        
        Returns:
            Number of cleaned up markers
        """
        try:
            redis = get_redis()
            pattern = f"{WALLET_PROCESSED_PREFIX}:*"
            keys = await redis.keys(pattern)
            
            cleaned = 0
            for key in keys:
                ttl = await redis.ttl(key)
                if ttl <= 0:  # Expired or no TTL
                    await redis.delete(key)
                    cleaned += 1
            
            if cleaned > 0:
                logger.info(f"Cleaned up {cleaned} old processed wallet markers")
            
            return cleaned
            
        except Exception as e:
            logger.error(f"Error cleaning up processed markers: {e}")
            return 0