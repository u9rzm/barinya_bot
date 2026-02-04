"""Commands package."""
from .basic import register_basic_handlers
from .referral import register_referral_handlers
from .review import register_review_handlers
from .admin import register_admin_handlers
from .utils import get_main_menu_keyboard, extract_referral_code

# Import the main registration function
from .registry import register_command_handlers

__all__ = [
    'register_command_handlers',
    'register_basic_handlers',
    'register_referral_handlers', 
    'register_review_handlers',
    'register_admin_handlers',
    'get_main_menu_keyboard',
    'extract_referral_code'
]