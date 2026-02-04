#!/usr/bin/env python3
"""
Script to initialize and start the statistics scheduler.
This should be called when the bot starts.
"""
import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.redis import init_redis, close_redis
from shared.services.statistics_scheduler import start_statistics_scheduler, stop_statistics_scheduler
from shared.logging_config import get_logger

logger = get_logger(__name__)


async def main():
    """Initialize and start the statistics scheduler."""
    try:
        # Initialize Redis
        await init_redis()
        logger.info("Redis initialized")
        
        # Start statistics scheduler (refresh every 30 minutes)
        await start_statistics_scheduler(refresh_interval_minutes=30)
        logger.info("Statistics scheduler started")
        
        # Keep the script running
        print("Statistics scheduler is running. Press Ctrl+C to stop.")
        try:
            while True:
                await asyncio.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            print("\nShutting down...")
        
    except Exception as e:
        logger.error(f"Error in statistics scheduler: {e}", exc_info=True)
    finally:
        # Cleanup
        await stop_statistics_scheduler()
        await close_redis()
        logger.info("Statistics scheduler stopped")


if __name__ == "__main__":
    asyncio.run(main())