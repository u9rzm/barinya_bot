"""Event handlers for bot status changes."""
import logging

from aiogram import Dispatcher
from aiogram.types import ChatMemberUpdated
from aiogram.filters import ChatMemberUpdatedFilter, KICKED, LEFT, MEMBER

from shared.database import get_async_session
from shared.services import UserService
from shared.logging_config import get_logger, get_bot_logger
from bot.error_handlers import handle_bot_errors

logger = get_logger(__name__)
bot_logger = get_bot_logger()


@handle_bot_errors(send_error_message=False)
async def bot_blocked_handler(event: ChatMemberUpdated) -> None:
    """
    Handle bot being blocked by user.
    
    Args:
        event: ChatMemberUpdated event when user blocks/unblocks bot
    """
    user_id = event.from_user.id
    
    # Check if bot was blocked (kicked or left)
    if event.new_chat_member.status in [KICKED, LEFT]:
        # User blocked the bot
        async with get_async_session() as db:
            user_service = UserService(db)
            existing_user = await user_service.get_user_by_telegram_id(user_id)
            
            if existing_user:
                await user_service.update_user_status(existing_user.id, False)
                await db.commit()
                bot_logger.info(f"User {user_id} blocked bot, marked as inactive")
            
    elif event.new_chat_member.status == MEMBER:
        # User unblocked the bot
        async with get_async_session() as db:
            user_service = UserService(db)
            existing_user = await user_service.get_user_by_telegram_id(user_id)
            
            if existing_user:
                await user_service.update_user_status(existing_user.id, True)
                await db.commit()
                bot_logger.info(f"User {user_id} unblocked bot, marked as active")


def register_event_handlers(dp: Dispatcher) -> None:
    """Register event handlers."""
    # Handle bot being blocked/unblocked
    dp.my_chat_member.register(
        bot_blocked_handler,
        ChatMemberUpdatedFilter(member_status_changed=True)
    )