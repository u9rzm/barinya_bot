"""Background task scheduler service."""
import asyncio
from datetime import datetime
from typing import Optional

from shared.services.wallet_sync_service import WalletSyncService
from shared.logging_config import get_logger

logger = get_logger(__name__)


class SchedulerService:
    """Service for managing background scheduled tasks."""
    
    def __init__(self):
        """Initialize scheduler service."""
        self.wallet_sync_service = WalletSyncService()
        self._running = False
        self._task: Optional[asyncio.Task] = None
    
    async def start(self) -> None:
        """Start the scheduler."""
        if self._running:
            logger.warning("Scheduler is already running")
            return
        
        self._running = True
        self._task = asyncio.create_task(self._run_scheduler())
        logger.info("Background scheduler started")
    
    async def stop(self) -> None:
        """Stop the scheduler."""
        if not self._running:
            return
        
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        
        logger.info("Background scheduler stopped")
    
    async def _run_scheduler(self) -> None:
        """Main scheduler loop."""
        logger.info("Starting scheduler loop")
        
        while self._running:
            try:
                # Запускаем синхронизацию кошельков
                await self._run_wallet_sync()
                
                # Ждем 1 час (3600 секунд)
                await asyncio.sleep(3600)
                
            except asyncio.CancelledError:
                logger.info("Scheduler cancelled")
                break
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                # В случае ошибки ждем 5 минут перед повтором
                await asyncio.sleep(300)
    
    async def _run_wallet_sync(self) -> None:
        """Run wallet synchronization task."""
        try:
            logger.info("Starting wallet synchronization task")
            start_time = datetime.utcnow()
            
            # Запускаем синхронизацию
            result = await self.wallet_sync_service.process_cached_wallets()
            
            # Очищаем старые маркеры
            cleaned = await self.wallet_sync_service.cleanup_old_processed_markers()
            
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            logger.info(
                f"Wallet sync completed in {duration:.2f}s: "
                f"{result.get('processed', 0)} processed, "
                f"{result.get('errors', 0)} errors, "
                f"{cleaned} markers cleaned"
            )
            
        except Exception as e:
            logger.error(f"Error in wallet sync task: {e}")
    
    async def run_wallet_sync_now(self) -> dict:
        """
        Run wallet synchronization immediately (for manual trigger).
        
        Returns:
            Synchronization result
        """
        logger.info("Manual wallet sync triggered")
        result = await self.wallet_sync_service.process_cached_wallets()
        cleaned = await self.wallet_sync_service.cleanup_old_processed_markers()
        result["cleaned_markers"] = cleaned
        return result


# Глобальный экземпляр планировщика
scheduler = SchedulerService()