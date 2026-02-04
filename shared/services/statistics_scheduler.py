"""Statistics cache refresh scheduler."""
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from shared.services.cached_statistics_service import CachedStatisticsService
from shared.logging_config import get_logger

logger = get_logger(__name__)


class StatisticsScheduler:
    """Scheduler for refreshing statistics cache."""
    
    def __init__(self, refresh_interval_minutes: int = 30):
        """
        Initialize scheduler.
        
        Args:
            refresh_interval_minutes: Interval between cache refreshes in minutes
        """
        self.refresh_interval = timedelta(minutes=refresh_interval_minutes)
        self.is_running = False
        self.task: Optional[asyncio.Task] = None
        self.last_refresh: Optional[datetime] = None
    
    async def start(self) -> None:
        """Start the statistics refresh scheduler."""
        if self.is_running:
            logger.warning("Statistics scheduler is already running")
            return
        
        self.is_running = True
        self.task = asyncio.create_task(self._refresh_loop())
        logger.info(f"Statistics scheduler started with {self.refresh_interval.total_seconds()/60:.0f} minute interval")
    
    async def stop(self) -> None:
        """Stop the statistics refresh scheduler."""
        if not self.is_running:
            return
        
        self.is_running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        
        logger.info("Statistics scheduler stopped")
    
    async def refresh_now(self) -> Dict[str, bool]:
        """
        Manually trigger statistics refresh.
        
        Returns:
            Dictionary with refresh results
        """
        logger.info("Manual statistics refresh triggered")
        results = await CachedStatisticsService.refresh_all_statistics()
        self.last_refresh = datetime.utcnow()
        return results
    
    async def _refresh_loop(self) -> None:
        """Main refresh loop."""
        # Initial refresh
        await self.refresh_now()
        
        while self.is_running:
            try:
                # Wait for the refresh interval
                await asyncio.sleep(self.refresh_interval.total_seconds())
                
                if not self.is_running:
                    break
                
                # Refresh statistics
                results = await CachedStatisticsService.refresh_all_statistics()
                self.last_refresh = datetime.utcnow()
                
                # Log results
                successful = sum(1 for success in results.values() if success)
                total = len(results)
                
                if successful == total:
                    logger.info(f"Statistics refresh completed successfully ({successful}/{total})")
                else:
                    logger.warning(f"Statistics refresh partially failed ({successful}/{total}): {results}")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in statistics refresh loop: {e}", exc_info=True)
                # Continue the loop even if there's an error
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get scheduler status.
        
        Returns:
            Dictionary with scheduler status information
        """
        return {
            "is_running": self.is_running,
            "refresh_interval_minutes": self.refresh_interval.total_seconds() / 60,
            "last_refresh": self.last_refresh.isoformat() if self.last_refresh else None,
            "next_refresh": (
                (self.last_refresh + self.refresh_interval).isoformat() 
                if self.last_refresh else None
            )
        }


# Global scheduler instance
_scheduler: Optional[StatisticsScheduler] = None


async def start_statistics_scheduler(refresh_interval_minutes: int = 30) -> None:
    """
    Start the global statistics scheduler.
    
    Args:
        refresh_interval_minutes: Interval between refreshes in minutes
    """
    global _scheduler
    
    if _scheduler and _scheduler.is_running:
        logger.warning("Statistics scheduler is already running")
        return
    
    _scheduler = StatisticsScheduler(refresh_interval_minutes)
    await _scheduler.start()


async def stop_statistics_scheduler() -> None:
    """Stop the global statistics scheduler."""
    global _scheduler
    
    if _scheduler:
        await _scheduler.stop()
        _scheduler = None


async def refresh_statistics_now() -> Dict[str, bool]:
    """
    Manually trigger statistics refresh.
    
    Returns:
        Dictionary with refresh results
    """
    global _scheduler
    
    if _scheduler:
        return await _scheduler.refresh_now()
    else:
        # If scheduler is not running, create a temporary one for manual refresh
        return await CachedStatisticsService.refresh_all_statistics()


def get_scheduler_status() -> Optional[Dict[str, Any]]:
    """
    Get global scheduler status.
    
    Returns:
        Dictionary with scheduler status or None if not running
    """
    global _scheduler
    
    if _scheduler:
        return _scheduler.get_status()
    return None