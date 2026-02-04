"""Commands handlers - main entry point."""
from aiogram import Dispatcher
from shared.logging_config import get_bot_logger

from .basic import register_basic_handlers
from .referral import register_referral_handlers
from .review import register_review_handlers
from .admin import register_admin_handlers

bot_logger = get_bot_logger()

def register_command_handlers(dp: Dispatcher) -> None:
    """Register all command handlers."""
    register_basic_handlers(dp)
    register_referral_handlers(dp)
    register_review_handlers(dp)
    register_admin_handlers(dp)
    
    bot_logger.info("All command handlers registered successfully")