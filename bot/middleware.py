"""Bot middleware for logging and other cross-cutting concerns."""
import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update, Message, CallbackQuery

from shared.logging_config import get_bot_logger, get_logger

logger = get_logger(__name__)
bot_logger = get_bot_logger()


class LoggingMiddleware(BaseMiddleware):
    """Middleware for logging incoming updates."""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Process the update with logging."""
        
        # Log incoming update
        if isinstance(event, Message):
            user_id = event.from_user.id if event.from_user else "Unknown"
            username = event.from_user.username if event.from_user else "Unknown"
            text = event.text or event.caption or "[Non-text message]"
            bot_logger.info(f"Message from {user_id} (@{username}): {text}")
            
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id if event.from_user else "Unknown"
            username = event.from_user.username if event.from_user else "Unknown"
            callback_data = event.data or "[No data]"
            bot_logger.info(f"Callback from {user_id} (@{username}): {callback_data}")
        
        try:
            # Call the handler
            result = await handler(event, data)
            
            # Log successful processing
            if isinstance(event, Message):
                bot_logger.debug(f"Successfully processed message from {user_id}")
            elif isinstance(event, CallbackQuery):
                bot_logger.debug(f"Successfully processed callback from {user_id}")
            
            return result
        except Exception as e:
            # Log error with context
            if isinstance(event, Message):
                logger.error(f"Error processing message from {user_id} (@{username}): {e}", exc_info=True)
            elif isinstance(event, CallbackQuery):
                logger.error(f"Error processing callback from {user_id} (@{username}): {e}", exc_info=True)
            else:
                logger.error(f"Error processing update: {e}", exc_info=True)
            raise