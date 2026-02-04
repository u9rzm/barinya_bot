"""Referral system commands handlers."""
import logging
from aiogram import Dispatcher, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from shared.config import settings
from shared.database import get_async_session
from shared.services import UserService, ReferralService
from shared.logging_config import get_logger
from bot.error_handlers import callback_handler

logger = get_logger(__name__)

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

def register_referral_handlers(dp: Dispatcher) -> None:
    """Register referral command handlers."""
    dp.callback_query.register(get_referral_link_callback, F.data == "get_referral_link")