"""Basic bot commands handlers."""
import logging
from typing import Optional
from urllib.parse import parse_qs

from aiogram import Dispatcher, F, Bot
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from shared.config import settings
from shared.database import get_async_session
from shared.services import UserService, ReferralService
from shared.services.menu_service import MenuServiceGoogleTabs
from shared.logging_config import get_logger, get_bot_logger, log_user_action, log_review_debug
from bot.error_handlers import (
    bot_command_handler, 
    callback_handler, 
    safe_send_message, 
    safe_answer_callback,
    log_user_action
)
from bot.states import ReviewStates

logger = get_logger(__name__)
bot_logger = get_bot_logger()

admin_ids = [int(id.strip()) for id in settings.admin_telegram_ids.split(",") if id.strip()]
bot_logger.info(f"Admin IDs: {admin_ids}")  

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
                            url=f"https://t.me/share/url?url={referral_link}&text=Присоединяйся_к_{settings.bot_name.replace(' ', '_')}! 🍻"
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
async def start_review_callback(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Handle callback for starting review process.
    
    Args:
        callback: Callback query from inline button
        state: FSM context for managing user state
    """
    if not callback.from_user:
        await callback.answer("❌ Ошибка получения данных пользователя.")
        return
    
    try:
        # Set state to waiting for review
        await state.set_state(ReviewStates.waiting_for_review)
        
        # Create cancel button
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="❌ Отменить",
                        callback_data="cancel_review"
                    )
                ]
            ]
        )
        
        await callback.message.answer(
            "✍️ <b>Оставить отзыв</b>\n\n"
            "Напишите ваш отзыв о нашем баре. Мы ценим ваше мнение и обязательно учтем все пожелания!\n\n"
            "Просто отправьте сообщение с вашим отзывом:",
            reply_markup=keyboard
        )
        await callback.answer()
        
        log_user_action(callback.from_user.id, "review_started")
        
    except Exception as e:
        logger.error(f"Error in start review callback: {e}", exc_info=True)
        await callback.answer("❌ Произошла ошибка.")


@callback_handler
async def cancel_review_callback(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Handle callback for canceling review process.
    
    Args:
        callback: Callback query from inline button
        state: FSM context for managing user state
    """
    try:
        await state.clear()
        await callback.message.answer(
            "❌ Отзыв отменен.\n\n"
            "Используйте меню ниже для навигации:",
            reply_markup=get_main_menu_keyboard()
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in cancel review callback: {e}", exc_info=True)
        await callback.answer("❌ Произошла ошибка.")


@bot_command_handler
async def handle_review_message(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Handle review message from user.
    
    Args:
        message: User's review message
        state: FSM context
        bot: Bot instance for sending to group
    """
    if not message.from_user or not message.text:
        await safe_send_message(message, "❌ Не удалось получить текст отзыва.")
        return
    
    try:
        user = message.from_user
        review_text = message.text
        
        # Log review processing start
        log_review_debug(user.id, "review_processing_start", f"text_length={len(review_text)}")
        
        # Clear state
        await state.clear()
        log_review_debug(user.id, "state_cleared")
        
        # Send review to admin channel if configured
        if settings.reviews_channel_id:
            try:
                # Convert to int if it's a string
                channel_id = int(settings.reviews_channel_id) if isinstance(settings.reviews_channel_id, str) else settings.reviews_channel_id
            except (ValueError, TypeError) as conv_e:
                bot_logger.error(f"Failed to convert channel ID to int: {conv_e}")
                return
                
            try:
                admin_message = (
                    "📝 <b>Новый отзыв</b>\n\n"
                    f"👤 <b>От:</b> {user.first_name or 'Неизвестно'}"
                )
                
                if user.username:
                    admin_message += f" (@{user.username})"
                
                admin_message += f"\n🆔 <b>ID:</b> {user.id}\n\n"
                admin_message += f"💬 <b>Отзыв:</b>\n{review_text}"
                
                result = await bot.send_message(
                    chat_id=channel_id,
                    text=admin_message,
                )
                
                bot_logger.info(f"Review sent to admin channel from user {user.id}")
                
            except Exception as e:
                bot_logger.error(f"Failed to send review to admin channel: {e}")
                import traceback
                bot_logger.error(f"Full traceback: {traceback.format_exc()}")
                # Don't show error to user, just log it
        else:
            bot_logger.warning("Reviews channel ID not configured")
        
        # Confirm to user
        await safe_send_message(
            message,
            "✅ <b>Спасибо за отзыв!</b>\n\n"
            "Ваш отзыв получен и будет рассмотрен администрацией. "
            "Мы ценим ваше мнение и стремимся стать лучше!\n\n"
            "Используйте меню ниже для навигации:",
            reply_markup=get_main_menu_keyboard()
        )
        
        log_user_action(user.id, "review_submitted", f"review_length={len(review_text)}")
        log_review_debug(user.id, "review_processing_complete", "success")
        
    except Exception as e:
        logger.error(f"Error handling review message: {e}", exc_info=True)
        await safe_send_message(message, "❌ Произошла ошибка при отправке отзыва.")
        await state.clear()

@bot_command_handler
async def upload_menu_google_sheets_callback(callback: CallbackQuery) -> None:
    """
    Handle /upload_menu_google_sheets command - upload menu from Google Sheets.
    
    Args:
        message: Incoming message with /upload_menu_google_sheets command
    """
    user = callback.from_user
    if not user or user.id not in admin_ids:
        await safe_answer_callback(callback, "❌ У вас нет прав для выполнения этой команды.")
        return
    
    try:
        menu_service = MenuServiceGoogleTabs()
        menu_service.generate_menu_json()
        
        await safe_answer_callback(
            callback,
            "✅ Меню успешно загружено из Google Sheets и обновлено."
        )
        bot_logger.info(f"Menu updated from Google Sheets by admin {user.id}")
        
    except Exception as e:
        logger.error(f"Error uploading menu from Google Sheets: {e}", exc_info=True)
        await safe_answer_callback(callback, "❌ Произошла ошибка при загрузке меню.")

@callback_handler
async def settings_callback(callback: CallbackQuery) -> None:
    """
    Handle settings callback - show settings menu.
    
    Args: MenuServiceGoogleTabs().generate_menu_json()
        callback: Callback query from inline button
    """
    # Here should be the logic to show settings
    # For now, just return to main menu
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Загрузить меню из Google Sheets",
                    callback_data="upload_menu_google_sheets"
                )
            ]
        ]
    )
    await callback.message.answer(
        "⚙️ <b>Настройки</b>\n\n"
        "Выберите действие:",
        reply_markup=keyboard
    )
    await callback.answer()

def get_main_menu_keyboard(id: int) -> InlineKeyboardMarkup:
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
            ] #,  #Работает просто включи            
        # [
        #     InlineKeyboardButton(
        #         text="✍️ Оставить отзыв",
        #         callback_data="start_review"
        #     )
        # ]
    ]
    
    if id in admin_ids:
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

def register_command_handlers(dp: Dispatcher) -> None:
    """Register command handlers."""
    dp.message.register(start_command, CommandStart())    
    # Review message handler (must be registered with state filter)
    dp.message.register(handle_review_message, ReviewStates.waiting_for_review)
    
    # Callback handlers
    dp.callback_query.register(settings_callback, F.data == "settings")
    dp.callback_query.register(upload_menu_google_sheets_callback, F.data == "upload_menu_google_sheets")
    dp.callback_query.register(get_referral_link_callback, F.data == "get_referral_link")
    dp.callback_query.register(start_review_callback, F.data == "start_review")
    dp.callback_query.register(cancel_review_callback, F.data == "cancel_review")