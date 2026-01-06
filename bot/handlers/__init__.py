"""Bot handlers package."""
from aiogram import Dispatcher

from bot.handlers.commands import register_command_handlers
# from bot.handlers.admin import register_admin_handlers
from bot.handlers.events import register_event_handlers


def register_handlers(dp: Dispatcher) -> None:
    """Register all bot handlers."""
    register_command_handlers(dp)
    # register_admin_handlers(dp)
    register_event_handlers(dp)