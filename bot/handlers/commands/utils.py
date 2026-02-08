"""Utility functions for commands."""
from typing import Optional
from urllib.parse import parse_qs
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from shared.config import settings

admin_ids = [int(id.strip()) for id in settings.admin_telegram_ids.split(",") if id.strip()]

def extract_referral_code(text: str) -> Optional[str]:
    """
    Extract referral code from /start command text.
    Supports formats:
    - /start F8O4QQXP
    - /start start=F8O4QQXP
    - https://t.me/bot?start=F8O4QQXP
    """
    if not text:
        return None
    
    # Убираем команду /start
    if text.startswith('/start'):
        text = text[7:]  # Убираем "/start "
    
    # Если есть параметры ссылки
    if 'start=' in text:
        # Разбираем query параметры
        if '?' in text:
            query_string = text.split('?')[1]
            params = parse_qs(query_string)
            return params.get('start', [None])[0]
        else:
            # Просто start=CODE
            return text.split('start=')[1]
    
    # Просто код после /start
    return text.strip() if text.strip() else None

def get_main_menu_keyboard(user_id: int = None) -> InlineKeyboardMarkup:
    """
    Create main menu inline keyboard.    
    Returns:
        InlineKeyboardMarkup with main menu buttons
    """
    menu_url = settings.webapp_url
    main_buttons = [ 
        [
            InlineKeyboardButton(
                text="📱 Открыть меню",
                web_app=WebAppInfo(url=menu_url)
            )
        ],
        [
            InlineKeyboardButton(
                text="👥 Реферальная ссылка",
                callback_data="get_referral_link"
            )
        ],              
        [
            InlineKeyboardButton(
                text="✍️ Оставить отзыв",
                callback_data="start_review"
            )
        ]
    ]
    
    if user_id and user_id in admin_ids:
        main_buttons.append([
            InlineKeyboardButton(
                text="👤 Настройки",
                callback_data="settings"
            )]
        )
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=main_buttons
    )
    
    return keyboard