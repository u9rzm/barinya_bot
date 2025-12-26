"""Basic bot commands handlers."""
import logging
from typing import Optional

from aiogram import Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from sqlalchemy.ext.asyncio import AsyncSession

from shared.config import settings
from shared.database import get_async_session
from shared.services import UserService, ReferralService
from shared.logging_config import get_logger, get_bot_logger
from bot.error_handlers import (
    bot_command_handler, 
    callback_handler, 
    safe_send_message, 
    safe_answer_callback,
    log_user_action
)

logger = get_logger(__name__)
bot_logger = get_bot_logger()

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
    # if message.text and len(message.text.split()) > 1:
    #     referral_code = message.text.split('=')[1]
    
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
                    reply_markup=get_main_menu_keyboard()
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
                    username=user.username,
                    first_name=user.first_name,
                    last_name=user.last_name,
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
                    reply_markup=get_main_menu_keyboard()
                )
                
                log_user_action(
                    user.id, 
                    "new_user_registration", 
                    f"username={user.username}, referral_code={referral_code}"
                )
                bot_logger.info(f"New user registered: {user.id} (@{user.username})")


@callback_handler
async def show_menu_callback(callback: CallbackQuery) -> None:
    """
    Handle /menu command - open Mini App with menu.
    
    Args:
        message: Incoming message with /menu command
    """
    if not callback.from_user:
        await callback.answer("❌ Ошибка получения данных пользователя.")
        return
    user = callback.from_user
    
    async with get_async_session() as db:
        user_service = UserService(db)
        existing_user = await user_service.get_user_by_telegram_id(user.id)
        
        if not existing_user:
            await safe_send_message(
                callback,
                "❌ Вы не зарегистрированы в системе. Используйте команду /start для регистрации."
            )
            return
    
    # Create keyboard with Mini App button for menu
    menu_url = 'https://workflow.chickenkiller.com/app'  # Replace with actual Mini App URL
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📱 Открыть меню",
                    web_app=WebAppInfo(url=menu_url)
                )
            ]
        ]
    )
    
    log_user_action(user.id, "menu_command")
    await safe_send_message(
        callback,
        "🍽️ <b>Меню бара</b>\n\n"
        "Нажмите кнопку ниже, чтобы открыть интерактивное меню с актуальными ценами и описаниями блюд:",
        reply_markup=keyboard
    )


@callback_handler  
async def show_profile_callback(callback: CallbackQuery) -> None:
    """
    Handle /profile command - open Mini App with user profile.
    
    Args:
        message: Incoming message with /profile command
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
        profile_url = "https://workflow.chickenkiller.com/profile"  # Replace with actual Mini App URL @hsfgjfsfhdfsqef_bot
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



@callback_handler
async def get_referral_link_callback(callback: CallbackQuery) -> None:
    """
    Handle callback for getting referral link.
    
    Args:
        callback: Callback query from inline button
    """
    if not callback.from_user:
        await callback.answer("❌ Ошибка получения данных пользователя.")
        return
    
    try:
        async with get_async_session() as db:
            user_service = UserService(db)
            existing_user = await user_service.get_user_by_telegram_id(callback.from_user.id)
            
            if not existing_user:
                await callback.answer("❌ Вы не зарегистрированы в системе.")
                return
            
            referral_service = ReferralService(db)
            referral_link = await referral_service.get_referral_link(existing_user.id)
            
            # Get referral stats
            referral_stats = await referral_service.get_referral_stats(existing_user.id)
            
            referral_text = (
                "👥 <b>Ваша реферальная ссылка:</b>\n\n"
                f"<code>{referral_link}</code>\n\n"
                f"📊 Приглашено: {referral_stats.total_referrals} | "
                f"Заработано: {referral_stats.total_earned:.2f} баллов"
            )
            
            # Create keyboard with share button
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="📤 Поделиться",
                            url=f"https://t.me/share/url?url={referral_link}&text=Присоединяйся к нашему бару! 🍻"
                        )
                    ]
                ]
            )
            
            await callback.message.answer(referral_text, reply_markup=keyboard)
            await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in referral callback: {e}", exc_info=True)
        await callback.answer("❌ Произошла ошибка.")


@callback_handler
async def show_help_callback(message: Message) -> None:
    """
    Handle /help command.
    
    Args:
        message: Incoming message with /help command
    """
    help_text = (
        "🤖 <b>Команды бота:</b>\n\n"
        "/start - Начать работу с ботом\n"
        # "/menu - Открыть меню бара\n"
        # "/profile - Открыть профиль\n"
        # "/referral - Получить реферальную ссылку\n"
        # "/help - Показать эту справку\n\n"
        "📱 <b>Основные функции:</b>\n"
        "• Просмотр меню бара\n"
        "• Программа лояльности с баллами\n"
        "• Реферальная система\n"
        "• Уведомления о специальных предложениях\n\n"
        "💡 Используйте кнопки меню для быстрого доступа к функциям!"
    )
    
    await message.answer(help_text, reply_markup=get_main_menu_keyboard())

# @callback_handler
# async def show_menu_callback(callback: CallbackQuery) -> None:
#     # Здесь должна быть логика открытия меню
#     await menu_command(callback.message)  # или своя реализация

# @callback_handler  
# async def show_profile_callback(callback: CallbackQuery) -> None:
#     # Здесь логика открытия профиля
#     await profile_command(callback.message)

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Create main menu inline keyboard.
    
    Returns:
        InlineKeyboardMarkup with main menu buttons
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📱 Меню",
                    callback_data="show_menu"
                )
            ],
            [
                InlineKeyboardButton(
                    text="👤 Профиль",
                    callback_data="show_profile"
                )
            ],
            [
                InlineKeyboardButton(
                    text="👥 Реферальная ссылка",
                    callback_data="get_referral_link"
                )
            ]
        ]
    )
    
    return keyboard


def register_command_handlers(dp: Dispatcher) -> None:
    """Register command handlers."""
    dp.message.register(start_command, CommandStart())
    # dp.message.register(menu_command, Command("menu"))
    # dp.message.register(profile_command, Command("profile"))
    # dp.message.register(referral_command, Command("referral"))
    # dp.message.register(help_command, Command("help"))
    
    # Callback handlers
    dp.callback_query.register(show_menu_callback, F.data == "show_menu")
    dp.callback_query.register(show_profile_callback, F.data == "show_profile")
    dp.callback_query.register(get_referral_link_callback, F.data == "get_referral_link")
    dp.callback_query.register(show_menu_callback, F.data == "show_help")