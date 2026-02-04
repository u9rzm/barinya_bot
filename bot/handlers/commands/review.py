"""Review system commands handlers."""
import logging
from aiogram import Dispatcher, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from shared.config import settings
from shared.logging_config import get_logger, get_bot_logger, log_user_action, log_review_debug
from bot.error_handlers import (
    bot_command_handler, 
    callback_handler, 
    safe_send_message
)
from bot.states import ReviewStates
from .utils import get_main_menu_keyboard

logger = get_logger(__name__)
bot_logger = get_bot_logger()

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

def register_review_handlers(dp: Dispatcher) -> None:
    """Register review command handlers."""
    # Review message handler (must be registered with state filter)
    dp.message.register(handle_review_message, ReviewStates.waiting_for_review)
    
    # Callback handlers
    dp.callback_query.register(start_review_callback, F.data == "start_review")
    dp.callback_query.register(cancel_review_callback, F.data == "cancel_review")