"""Notification service for sending messages through Telegram bot."""
import asyncio
import logging
from typing import Optional

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError, TelegramBadRequest, TelegramForbiddenError
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.models import User, Promotion, LoyaltyLevel
from shared.logging_config import get_logger, get_notification_logger

logger = get_logger(__name__)
notification_logger = get_notification_logger()


class NotificationService:
    """Service for sending notifications through Telegram bot."""
    
    def __init__(self, bot: Bot, db: AsyncSession):
        """
        Initialize notification service.
        
        Args:
            bot: Aiogram Bot instance
            db: Database session
        """
        self.bot = bot
        self.db = db
        self.max_retries = 3
        self.retry_delay = 1.0  # seconds
    
    async def send_message(
        self,
        telegram_id: int,
        message: str,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
        retry_count: int = 0
    ) -> bool:
        """
        Send a message to a user with error handling and retry logic.
        
        Args:
            telegram_id: Telegram user ID
            message: Message text to send
            reply_markup: Optional inline keyboard markup
            retry_count: Current retry attempt (internal use)
            
        Returns:
            True if message was sent successfully, False otherwise
        """
        try:
            await self.bot.send_message(
                chat_id=telegram_id,
                text=message,
                reply_markup=reply_markup,
                parse_mode="HTML"
            )
            notification_logger.info(f"Message sent successfully to user {telegram_id}")
            return True
            
        except TelegramForbiddenError:
            # User blocked the bot - mark as inactive
            notification_logger.warning(f"User {telegram_id} blocked the bot")
            await self._deactivate_user_by_telegram_id(telegram_id)
            return False
            
        except TelegramBadRequest as e:
            # Bad request - don't retry
            notification_logger.error(f"Bad request when sending to {telegram_id}: {e}")
            return False
            
        except TelegramAPIError as e:
            # Other Telegram API errors - retry if possible
            if retry_count < self.max_retries:
                notification_logger.warning(
                    f"Telegram API error for user {telegram_id}, retrying ({retry_count + 1}/{self.max_retries}): {e}"
                )
                await asyncio.sleep(self.retry_delay * (2 ** retry_count))  # Exponential backoff
                return await self.send_message(telegram_id, message, reply_markup, retry_count + 1)
            else:
                notification_logger.error(f"Failed to send message to {telegram_id} after {self.max_retries} retries: {e}")
                return False
                
        except Exception as e:
            # Unexpected errors
            notification_logger.error(f"Unexpected error sending message to {telegram_id}: {e}")
            return False
    
    async def send_promotion(self, telegram_id: int, promotion: Promotion) -> bool:
        """
        Send a promotion message to a user with formatted content.
        
        Args:
            telegram_id: Telegram user ID
            promotion: Promotion object to send
            
        Returns:
            True if message was sent successfully, False otherwise
        """
        # Format promotion message
        message = self._format_promotion_message(promotion)
        
        # Create inline keyboard with Mini App button
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="🍽️ Открыть меню",
                web_app={"url": f"https://t.me/your_bot_name/menu"}  # TODO: Replace with actual Mini App URL
            )]
        ])
        
        return await self.send_message(telegram_id, message, keyboard)
    
    async def send_level_up_notification(
        self,
        telegram_id: int,
        new_level: LoyaltyLevel
    ) -> bool:
        """
        Send a level up notification to a user.
        
        Args:
            telegram_id: Telegram user ID
            new_level: New loyalty level achieved
            
        Returns:
            True if message was sent successfully, False otherwise
        """
        message = (
            f"🎉 <b>Поздравляем!</b>\n\n"
            f"Вы достигли нового уровня лояльности: <b>{new_level.name}</b>!\n\n"
            f"Теперь вы получаете <b>{new_level.points_rate}%</b> баллов с каждого заказа.\n\n"
            f"Продолжайте делать заказы и получайте еще больше преимуществ! 🚀"
        )
        
        # Create inline keyboard with profile button
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="👤 Мой профиль",
                web_app={"url": f"https://t.me/your_bot_name/profile"}  # TODO: Replace with actual Mini App URL
            )]
        ])
        
        return await self.send_message(telegram_id, message, keyboard)
    
    async def send_referral_reward_notification(
        self,
        telegram_id: int,
        amount: float,
        referee_name: str
    ) -> bool:
        """
        Send a referral reward notification to a user.
        
        Args:
            telegram_id: Telegram user ID
            amount: Amount of points earned
            referee_name: Name of the referee who made the order
            
        Returns:
            True if message was sent successfully, False otherwise
        """
        message = (
            f"💰 <b>Реферальная награда!</b>\n\n"
            f"Ваш друг <b>{referee_name}</b> сделал заказ!\n"
            f"Вы получили <b>{amount:.2f}</b> баллов лояльности.\n\n"
            f"Приглашайте больше друзей и зарабатывайте еще больше! 🎯"
        )
        
        # Create inline keyboard with referral stats button
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="📊 Статистика рефералов",
                web_app={"url": f"https://t.me/your_bot_name/referrals"}  # TODO: Replace with actual Mini App URL
            )]
        ])
        
        return await self.send_message(telegram_id, message, keyboard)
    
    async def broadcast_to_active_users(
        self,
        message: str,
        reply_markup: Optional[InlineKeyboardMarkup] = None
    ) -> dict[str, int]:
        """
        Broadcast a message to all active users with error logging.
        
        Args:
            message: Message text to broadcast
            reply_markup: Optional inline keyboard markup
            
        Returns:
            Dictionary with statistics: {"sent": int, "failed": int, "total": int}
        """
        # Get all active users
        result = await self.db.execute(
            select(User).where(User.is_active == True)
        )
        active_users = list(result.scalars().all())
        
        notification_logger.info(f"Starting broadcast to {len(active_users)} active users")
        
        sent_count = 0
        failed_count = 0
        
        # Send messages with controlled concurrency to avoid rate limits
        semaphore = asyncio.Semaphore(10)  # Limit to 10 concurrent requests
        
        async def send_to_user(user: User) -> bool:
            async with semaphore:
                success = await self.send_message(user.telegram_id, message, reply_markup)
                if success:
                    return True
                else:
                    notification_logger.warning(f"Failed to send broadcast message to user {user.telegram_id}")
                    return False
        
        # Create tasks for all users
        tasks = [send_to_user(user) for user in active_users]
        
        # Execute all tasks and collect results
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Count successful and failed sends
        for result in results:
            if isinstance(result, Exception):
                notification_logger.error(f"Unexpected error in broadcast task: {result}")
                failed_count += 1
            elif result:
                sent_count += 1
            else:
                failed_count += 1
        
        stats = {
            "sent": sent_count,
            "failed": failed_count,
            "total": len(active_users)
        }
        
        notification_logger.info(
            f"Broadcast completed: {sent_count} sent, {failed_count} failed, {len(active_users)} total"
        )
        
        return stats
    
    def _format_promotion_message(self, promotion: Promotion) -> str:
        """
        Format a promotion into a message string.
        
        Args:
            promotion: Promotion object to format
            
        Returns:
            Formatted message string
        """
        start_date = promotion.start_date.strftime("%d.%m.%Y")
        end_date = promotion.end_date.strftime("%d.%m.%Y")
        
        message = (
            f"🎉 <b>{promotion.title}</b>\n\n"
            f"{promotion.description}\n\n"
            f"📅 <b>Период действия:</b> {start_date} - {end_date}\n\n"
            f"Не упустите возможность! Переходите в меню и делайте заказ! 🍽️"
        )
        
        return message
    
    async def _deactivate_user_by_telegram_id(self, telegram_id: int) -> None:
        """
        Deactivate user when they block the bot.
        
        Args:
            telegram_id: Telegram user ID to deactivate
        """
        try:
            result = await self.db.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            
            if user:
                user.is_active = False
                await self.db.flush()
                logger.info(f"Deactivated user {telegram_id} due to bot blocking")
            else:
                logger.warning(f"User with telegram_id {telegram_id} not found for deactivation")
                
        except Exception as e:
            logger.error(f"Error deactivating user {telegram_id}: {e}")