"""Basic bot commands handlers."""
import logging
from typing import Optional
from aiogram import Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from shared.config import settings
from shared.database import get_async_session
from shared.services import UserService, ReferralService
from shared.logging_config import get_logger, get_bot_logger, log_user_action
from bot.error_handlers import (
    bot_command_handler, 
    callback_handler, 
    safe_send_message
)
from .utils import get_main_menu_keyboard, extract_referral_code

logger = get_logger(__name__)
bot_logger = get_bot_logger()

@bot_command_handler
async def start_command(message: Message) -> None:
    """
    Handle /start command with optional referral code.
    
    Args:
        message: Incoming message with /start command
    """
    # Parse referral code from command arguments
    
    referral_code: Optional[str] = None
    if message.text:
        referral_code = extract_referral_code(message.text)
    
    user = message.from_user
    if not user:
        await safe_send_message(message, "❌ Не удалось получить информацию о пользователе.")
        return
    
    print(f"Received /start command from user {user.id} with referral code {referral_code} mmessage:{message.text}")

    async with get_async_session() as db:
            user_service = UserService(db)            
            # Check if user already exists
            existing_user = await user_service.get_user_by_telegram_id(user.id)
            
            if existing_user:
                # User already registered
                log_user_action(user.id, "start_command_existing_user")
                await safe_send_message(
                    message,
                    f"👋 С возвращением, {user.first_name or user.username or 'друг'}!\n\n"
                    "Используйте меню ниже для навигации:",
                    reply_markup=get_main_menu_keyboard(user.id)
                )
            else:
                # Register new user
                referrer_id = None
                
                
                # Process referral code if provided
                if referral_code:
                    # print(f"Referral code {referral_code}")
                    referral_service = ReferralService(db)                    
                    try:
                        referrer_user = await user_service.get_user_by_referral_code(referral_code)    
                        if referrer_user:
                            referrer_id = referrer_user.id
                            bot_logger.info(f"Referral code {referral_code} found for user {user.id}")
                        else:
                            bot_logger.warning(f"Referral code {referral_code} not found for user {user.id}")
                        # await referral_service.register_referral(user.id, referral_code)  
                        # bot_logger.info(f"Referral code {referral_code} registered for user {user.id}")
                        # # Get referrer info for welcome message
                                                                    
                        
                    except Exception as e:
                        bot_logger.warning(f"Failed to process referral code {referral_code} for user {user.id}: {e}")
                
                # Create new user
                new_user = await user_service.create_user(
                    telegram_id=user.id,
                    referrer_id=referrer_id
                )
                
                await db.commit()
                
                # Send welcome message
                welcome_text = (
                    f"🎉 Добро пожаловать в бар, {user.first_name or user.username or 'друг'}!\n\n"
                    "Теперь вы можете:\n"
                    "• 📱 Просматривать меню в нашем приложении\n"
                    "• 🎯 Накапливать баллы лояльности\n"
                    "• 👥 Приглашать друзей и получать бонусы\n"
                    "• 🔔 Получать уведомления о специальных предложениях\n\n"
                )
                
                if referral_code and referrer_id:
                    welcome_text += "✨ Вы зарегистрировались по реферальной ссылке! Ваш друг получит бонусы с ваших заказов.\n\n"
                
                welcome_text += "Используйте меню ниже для начала работы:"
                
                await safe_send_message(
                    message,
                    welcome_text,
                    reply_markup=get_main_menu_keyboard(user.id)
                )
                
                log_user_action(
                    user.id, 
                    "new_user_registration", 
                    f"username={user.username}, referral_code={referral_code}"
                )
                bot_logger.info(f"New user registered: {user.id} (@{user.username})")

@callback_handler  
async def show_profile_callback(callback: CallbackQuery) -> None:
    """
    Handle /profile command - open Mini App with user profile.
    
    Args:
        callback: Callback query from inline button
    """
    if not callback.from_user:
        await callback.answer("❌ Ошибка получения данных пользователя.")
        return
    user = callback.from_user
    
    try:
        async with get_async_session() as db:
            user_service = UserService(db)
            existing_user = await user_service.get_user_by_telegram_id(user.id)
            logger.debug(f"User {user.id} found in database: {existing_user}")
            
            if not existing_user:
                await callback.answer(
                    "❌ Вы не зарегистрированы в системе. Используйте команду /start для регистрации."
                )
                return
        
        # Create keyboard with Mini App button for profile
        profile_url = settings.webapp_url
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="👤 Открыть профиль",
                        web_app=WebAppInfo(url=profile_url)
                    )
                ]
            ]
        )
        
        await callback.answer(
            "👤 <b>Ваш профиль</b>\n\n"
            "Нажмите кнопку ниже, чтобы открыть профиль с информацией о баллах лояльности, "
            "истории заказов и реферальной статистике:",
            reply_markup=keyboard
        )
        
    except Exception as e:
        logger.error(f"Error in profile command: {e}", exc_info=True)
        await callback.answer("❌ Произошла ошибка. Попробуйте позже.")

def register_basic_handlers(dp: Dispatcher) -> None:
    """Register basic command handlers."""
    dp.message.register(start_command, CommandStart())
    # Profile callback can be registered here if needed