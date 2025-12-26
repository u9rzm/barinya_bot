"""Error handling utilities for bot handlers."""
import asyncio
import functools
import traceback
from typing import Any, Callable, Optional, Union

from aiogram.types import Message, CallbackQuery, Update
from aiogram.exceptions import TelegramAPIError, TelegramBadRequest, TelegramForbiddenError

from shared.logging_config import get_logger, get_bot_logger, log_admin_action

logger = get_logger(__name__)
bot_logger = get_bot_logger()


def handle_bot_errors(
    send_error_message: bool = True,
    error_message: str = "❌ Произошла ошибка. Попробуйте позже или обратитесь к администратору."
):
    """
    Decorator for handling errors in bot handlers.
    
    Args:
        send_error_message: Whether to send error message to user
        error_message: Custom error message to send to user
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            try:
                return await func(*args, **kwargs)
            except TelegramForbiddenError as e:
                # User blocked the bot - this is expected behavior
                event = args[0] if args else None
                user_id = None
                
                if isinstance(event, (Message, CallbackQuery)):
                    user_id = event.from_user.id if event.from_user else None
                
                bot_logger.warning(f"User {user_id} blocked the bot: {e}")
                # Don't try to send message if user blocked the bot
                return None
                
            except TelegramBadRequest as e:
                # Bad request - log and optionally notify user
                event = args[0] if args else None
                user_id = None
                
                if isinstance(event, (Message, CallbackQuery)):
                    user_id = event.from_user.id if event.from_user else None
                
                logger.error(f"Telegram bad request for user {user_id}: {e}")
                
                if send_error_message and isinstance(event, Message):
                    try:
                        await event.answer("❌ Неверный формат команды или данных.")
                    except Exception:
                        pass  # If we can't send error message, just log it
                elif send_error_message and isinstance(event, CallbackQuery):
                    try:
                        await event.answer("❌ Ошибка обработки запроса.")
                    except Exception:
                        pass
                
                return None
                
            except TelegramAPIError as e:
                # Other Telegram API errors
                event = args[0] if args else None
                user_id = None
                
                if isinstance(event, (Message, CallbackQuery)):
                    user_id = event.from_user.id if event.from_user else None
                
                logger.error(f"Telegram API error for user {user_id}: {e}")
                
                if send_error_message and isinstance(event, Message):
                    try:
                        await event.answer("❌ Временная ошибка сервиса. Попробуйте позже.")
                    except Exception:
                        pass
                elif send_error_message and isinstance(event, CallbackQuery):
                    try:
                        await event.answer("❌ Временная ошибка. Попробуйте позже.")
                    except Exception:
                        pass
                
                return None
                
            except Exception as e:
                # Unexpected errors
                event = args[0] if args else None
                user_id = None
                handler_name = func.__name__
                
                if isinstance(event, (Message, CallbackQuery)):
                    user_id = event.from_user.id if event.from_user else None
                
                logger.error(
                    f"Unexpected error in handler {handler_name} for user {user_id}: {e}",
                    extra={
                        "handler": handler_name,
                        "user_id": user_id,
                        "error_type": type(e).__name__,
                        "traceback": traceback.format_exc()
                    },
                    exc_info=True
                )
                
                if send_error_message and isinstance(event, Message):
                    try:
                        await event.answer(error_message)
                    except Exception as send_error:
                        logger.error(f"Failed to send error message to user {user_id}: {send_error}")
                elif send_error_message and isinstance(event, CallbackQuery):
                    try:
                        await event.answer("❌ Произошла ошибка.")
                        if event.message:
                            await event.message.answer(error_message)
                    except Exception as send_error:
                        logger.error(f"Failed to send error message to user {user_id}: {send_error}")
                
                return None
        
        return wrapper
    return decorator


def handle_admin_errors(
    log_action: bool = True,
    action_name: Optional[str] = None
):
    """
    Decorator for handling errors in admin handlers with additional logging.
    
    Args:
        log_action: Whether to log admin action
        action_name: Name of the admin action for logging
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            event = args[0] if args else None
            admin_id = None
            
            if isinstance(event, (Message, CallbackQuery)):
                admin_id = event.from_user.id if event.from_user else None
            
            try:
                result = await func(*args, **kwargs)
                
                # Log successful admin action
                if log_action and admin_id:
                    action = action_name or func.__name__
                    log_admin_action(
                        admin_id=admin_id,
                        action=action,
                        target_type="system",
                        details="Action completed successfully"
                    )
                
                return result
                
            except Exception as e:
                # Log failed admin action
                if log_action and admin_id:
                    action = action_name or func.__name__
                    log_admin_action(
                        admin_id=admin_id,
                        action=action,
                        target_type="system",
                        details=f"Action failed: {str(e)}"
                    )
                
                # Re-raise to be handled by the main error handler
                raise
        
        return wrapper
    return decorator


async def safe_send_message(
    message_or_callback: Union[Message, CallbackQuery],
    text: str,
    **kwargs
) -> bool:
    """
    Safely send a message with error handling.
    
    Args:
        message_or_callback: Message or CallbackQuery object
        text: Text to send
        **kwargs: Additional arguments for send_message
        
    Returns:
        True if message was sent successfully, False otherwise
    """
    try:
        if isinstance(message_or_callback, Message):
            await message_or_callback.answer(text, **kwargs)
        elif isinstance(message_or_callback, CallbackQuery):
            if message_or_callback.message:
                await message_or_callback.message.answer(text, **kwargs)
            else:
                await message_or_callback.answer(text[:200])  # Callback answers are limited
        
        return True
        
    except TelegramForbiddenError:
        # User blocked the bot
        user_id = message_or_callback.from_user.id if message_or_callback.from_user else None
        bot_logger.warning(f"Cannot send message to user {user_id}: bot blocked")
        return False
        
    except TelegramAPIError as e:
        user_id = message_or_callback.from_user.id if message_or_callback.from_user else None
        logger.error(f"Telegram API error sending message to user {user_id}: {e}")
        return False
        
    except Exception as e:
        user_id = message_or_callback.from_user.id if message_or_callback.from_user else None
        logger.error(f"Unexpected error sending message to user {user_id}: {e}")
        return False


async def safe_answer_callback(
    callback: CallbackQuery,
    text: Optional[str] = None,
    show_alert: bool = False
) -> bool:
    """
    Safely answer a callback query with error handling.
    
    Args:
        callback: CallbackQuery object
        text: Text to show in popup (optional)
        show_alert: Whether to show as alert
        
    Returns:
        True if callback was answered successfully, False otherwise
    """
    try:
        await callback.answer(text, show_alert=show_alert)
        return True
        
    except TelegramAPIError as e:
        user_id = callback.from_user.id if callback.from_user else None
        logger.error(f"Error answering callback for user {user_id}: {e}")
        return False
        
    except Exception as e:
        user_id = callback.from_user.id if callback.from_user else None
        logger.error(f"Unexpected error answering callback for user {user_id}: {e}")
        return False


def log_user_action(
    user_id: int,
    action: str,
    details: Optional[str] = None,
    **kwargs
) -> None:
    """
    Log user action for analytics and debugging.
    
    Args:
        user_id: Telegram user ID
        action: Action performed
        details: Additional details
        **kwargs: Additional metadata
    """
    log_data = {
        "user_id": user_id,
        "action": action,
    }
    
    if details:
        log_data["details"] = details
    
    # Add any additional metadata
    log_data.update(kwargs)
    
    # Create structured log message
    log_message = " | ".join([f"{k}={v}" for k, v in log_data.items()])
    bot_logger.info(f"USER_ACTION: {log_message}")


class ErrorRecovery:
    """Utility class for error recovery operations."""
    
    @staticmethod
    async def retry_with_backoff(
        operation: Callable,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        backoff_factor: float = 2.0
    ) -> Any:
        """
        Retry an operation with exponential backoff.
        
        Args:
            operation: Async function to retry
            max_retries: Maximum number of retries
            initial_delay: Initial delay in seconds
            backoff_factor: Backoff multiplier
            
        Returns:
            Result of the operation
            
        Raises:
            Last exception if all retries fail
        """
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                return await operation()
            except Exception as e:
                last_exception = e
                if attempt < max_retries:
                    delay = initial_delay * (backoff_factor ** attempt)
                    logger.warning(f"Operation failed (attempt {attempt + 1}), retrying in {delay}s: {e}")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"Operation failed after {max_retries + 1} attempts: {e}")
        
        raise last_exception


# Convenience decorators with common configurations
bot_command_handler = handle_bot_errors(
    send_error_message=True,
    error_message="❌ Произошла ошибка при выполнении команды. Попробуйте позже."
)

admin_command_handler = lambda action_name=None: lambda func: handle_admin_errors(
    log_action=True,
    action_name=action_name
)(handle_bot_errors(
    send_error_message=True,
    error_message="❌ Ошибка выполнения административной команды."
)(func))

callback_handler = handle_bot_errors(
    send_error_message=True,
    error_message="❌ Ошибка обработки запроса."
)