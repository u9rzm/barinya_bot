"""Telegram bot main entry point."""
import asyncio
import logging
from contextlib import asynccontextmanager
import os

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Update
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp import web
from aiohttp.web_app import Application

from shared.config import settings
from shared.database import get_async_session
from shared.redis import init_redis, close_redis
from shared.logging_config import setup_logging, get_logger
from shared.services.menu_service import MenuServiceGoogleTabs
from shared.services.statistics_scheduler import start_statistics_scheduler, stop_statistics_scheduler
from bot.handlers import register_handlers
from bot.middleware import LoggingMiddleware

# Setup logging system
setup_logging()
logger = get_logger(__name__)

# Global bot and dispatcher instances
bot = Bot(
    token=settings.telegram_bot_token,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())


async def on_startup() -> None:
    """Bot startup handler."""
    logger.info("Bot starting up...")
    
    # Initialize Redis
    try:
        await init_redis()
        logger.info("Redis initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Redis: {e}")
        # Continue without Redis - statistics will work without cache
    
    # Start statistics scheduler
    try:
        await start_statistics_scheduler(refresh_interval_minutes=30)
        logger.info("Statistics scheduler started")
    except Exception as e:
        logger.error(f"Failed to start statistics scheduler: {e}")
        # Continue without scheduler - statistics will work without cache
    
    # Register middleware
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())
    
    # Register handlers
    register_handlers(dp)
    #check menu file
    if os.path.exists(settings.path_menu):
        logger.info("Menu file exists")
    else:
        logger.info("Menu file does not exist")
        MenuServiceGoogleTabs().generate_menu_json()
        logger.info("Menu file created")
    
    # Set webhook if URL is provided
    if settings.telegram_webhook_url:
        await bot.set_webhook(
            url=settings.telegram_webhook_url,
            drop_pending_updates=True
        )
        logger.info(f"Webhook set to: {settings.telegram_webhook_url}")
    else:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("No webhook URL provided, will use polling")


async def on_shutdown() -> None:
    """Bot shutdown handler."""
    logger.info("Bot shutting down...")
    
    # Stop statistics scheduler
    try:
        await stop_statistics_scheduler()
        logger.info("Statistics scheduler stopped")
    except Exception as e:
        logger.error(f"Error stopping statistics scheduler: {e}")
    
    # Close Redis connection
    try:
        await close_redis()
        logger.info("Redis connection closed")
    except Exception as e:
        logger.error(f"Error closing Redis: {e}")
    
    await bot.session.close()


# @asynccontextmanager
# async def lifespan(app: Application):
#     """Application lifespan manager."""
#     await on_startup()
#     yield
#     await on_shutdown()


def create_app() -> Application:
    """Create aiohttp application with webhook handler."""
    app = web.Application()
    app["bot"] = bot
    
    # Setup webhook handler
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    webhook_requests_handler.register(app, path="/webhook")
    setup_application(app, dp, bot=bot)
    
    return app


async def main():
    """Main bot entry point."""
    if settings.telegram_webhook_url:
        # Run with webhook (for production)
        await on_startup()  # Initialize bot before starting server
        
        app = create_app()
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, settings.app_host, settings.app_port)
        await site.start()
        logger.info(f"Webhook server started on {settings.app_host}:{settings.app_port}")
        
        # Keep the server running
        try:
            await asyncio.Future()  # Run forever
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        finally:
            await on_shutdown()
            await runner.cleanup()
    else:
        # Run with polling (for development)
        await on_startup()
        try:
            logger.info("Starting bot with polling...")
            await dp.start_polling(bot)
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        finally:
            await on_shutdown()


if __name__ == "__main__":
    asyncio.run(main())
