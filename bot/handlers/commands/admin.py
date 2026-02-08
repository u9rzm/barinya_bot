"""Admin commands handlers."""
import logging
from datetime import datetime
from aiogram import Dispatcher, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram.filters import Command
from shared.services.menu_service import MenuServiceGoogleTabs
from shared.services.cached_statistics_service import CachedStatisticsService
from shared.services.statistics_scheduler import refresh_statistics_now, get_scheduler_status
from shared.services.loyalty_service import LoyaltyService
from shared.database import get_async_session
from shared.logging_config import get_logger, get_bot_logger
from bot.error_handlers import callback_handler, safe_answer_callback
from .utils import admin_ids

logger = get_logger(__name__)
bot_logger = get_bot_logger()


def is_admin_message(message: Message) -> bool:
    """Check if message is from admin."""
    return message.from_user and message.from_user.id in admin_ids


async def safe_edit_message(callback: CallbackQuery, text: str, reply_markup: InlineKeyboardMarkup = None) -> None:
    """Safely edit message with fallback to new message."""
    try:
        await callback.message.edit_text(text, reply_markup=reply_markup)
    except Exception:
        # Fallback to new message if edit fails (e.g., message too old)
        await callback.message.answer(text, reply_markup=reply_markup)

@callback_handler
async def upload_menu_google_sheets_callback(callback: CallbackQuery) -> None:
    """
    Handle /upload_menu_google_sheets command - upload menu from Google Sheets.
    
    Args:
        callback: Callback query from inline button
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
async def statistics_callback(callback: CallbackQuery) -> None:
    """
    Handle statistics callback - show application statistics.
    
    Args:
        callback: Callback query from inline button
    """
    user = callback.from_user
    if not user or user.id not in admin_ids:
        await safe_answer_callback(callback, "❌ У вас нет прав для выполнения этой команды.")
        return
    
    try:
        # Get cached statistics
        overall_stats = await CachedStatisticsService.get_overall_statistics()
        
        if not overall_stats:
            await safe_answer_callback(callback, "❌ Не удалось получить статистику. Попробуйте позже.")
            return
        
        # Format statistics message
        message = (
            "📊 <b>Статистика приложения</b>\n\n"
            
            "👥 <b>Пользователи:</b>\n"
            f"• Всего пользователей: {overall_stats.users.total_users}\n"
            f"• Активных пользователей: {overall_stats.users.active_users}\n"
            f"• С подключенными кошельками: {overall_stats.users.users_with_wallets}\n"
            f"• Без кошельков: {overall_stats.users.users_without_wallets}\n"
            f"• Новых сегодня: {overall_stats.users.new_users_today}\n"
            f"• Новых за неделю: {overall_stats.users.new_users_this_week}\n"
            f"• Новых за месяц: {overall_stats.users.new_users_this_month}\n\n"
            
            "🎯 <b>Программа лояльности:</b>\n"
            f"• Всего выдано баллов: {overall_stats.loyalty.total_points_issued:.1f}\n"
            f"• Всего потрачено баллов: {overall_stats.loyalty.total_points_redeemed:.1f}\n"
            f"• Активный баланс баллов: {overall_stats.loyalty.active_points_balance:.1f}\n"
            f"• Средний баланс на пользователя: {overall_stats.loyalty.average_points_per_user:.1f}\n"
            f"• Транзакций сегодня: {overall_stats.loyalty.points_transactions_today}\n"
            f"• Транзакций за неделю: {overall_stats.loyalty.points_transactions_this_week}\n"
            f"• Транзакций за месяц: {overall_stats.loyalty.points_transactions_this_month}\n\n"
            
            # "🛒 <b>Заказы:</b>\n"
            # f"• Всего заказов: {overall_stats.orders.total_orders}\n"
            # f"• Завершенных: {overall_stats.orders.completed_orders}\n"
            # f"• В ожидании: {overall_stats.orders.pending_orders}\n"
            # f"• Отмененных: {overall_stats.orders.cancelled_orders}\n"
            # f"• Общая выручка: {overall_stats.orders.total_revenue:.2f} ₽\n"
            # f"• Средний чек: {overall_stats.orders.average_order_value:.2f} ₽\n"
            # f"• Заказов сегодня: {overall_stats.orders.orders_today}\n"
            # f"• Заказов за неделю: {overall_stats.orders.orders_this_week}\n"
            # f"• Заказов за месяц: {overall_stats.orders.orders_this_month}\n\n"
            
            f"📅 <i>Обновлено: {overall_stats.generated_at.strftime('%d.%m.%Y %H:%M')}</i>"
        )
            
        # Create keyboard with additional statistics options
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="📈 Детальная статистика",
                            callback_data="detailed_statistics"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="🏆 Топ пользователей",
                            callback_data="top_users"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="💳 Статистика кошельков",
                            callback_data="wallet_statistics"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="🔄 Обновить",
                            callback_data="statistics"
                        ),
                        InlineKeyboardButton(
                            text="⚡ Принудительно",
                            callback_data="force_refresh_statistics"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="← Назад к настройкам",
                            callback_data="settings"
                        )
                    ]
                ]
            )
            
        await safe_edit_message(callback, message, keyboard)
        await callback.answer()
            
        bot_logger.info(f"Statistics viewed by admin {user.id}")
            
    except Exception as e:
        logger.error(f"Error getting statistics: {e}", exc_info=True)
        await safe_answer_callback(callback, "❌ Произошла ошибка при получении статистики.")


@callback_handler
async def detailed_statistics_callback(callback: CallbackQuery) -> None:
    """
    Handle detailed statistics callback - show loyalty level distribution.
    
    Args:
        callback: Callback query from inline button
    """
    user = callback.from_user
    if not user or user.id not in admin_ids:
        await safe_answer_callback(callback, "❌ У вас нет прав для выполнения этой команды.")
        return
    
    try:
        level_distribution = await CachedStatisticsService.get_loyalty_level_distribution()
        
        if not level_distribution:
            await safe_answer_callback(callback, "❌ Не удалось получить детальную статистику.")
            return
        
        message = "📊 <b>Детальная статистика по уровням лояльности:</b>\n\n"
        
        for level_name, data in level_distribution.items():
            message += (
                f"🎯 <b>{level_name}</b>\n"
                f"• Порог: {data['threshold']:.0f} ₽\n"
                f"• Ставка баллов: {data['points_rate']:.1f}%\n"
                f"• Пользователей: {data['user_count']}\n"
                f"• Средний баланс баллов: {data['avg_points']:.1f}\n"
                f"• Общая сумма трат: {data['total_spent']:.2f} ₽\n\n"
            )
            
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="← Назад к статистике",
                            callback_data="statistics"
                        )
                    ]
                ]
            )
            
            await safe_edit_message(callback, message, keyboard)
            await callback.answer()
            
    except Exception as e:
        logger.error(f"Error getting detailed statistics: {e}", exc_info=True)
        await safe_answer_callback(callback, "❌ Произошла ошибка при получении детальной статистики.")


@callback_handler
async def top_users_callback(callback: CallbackQuery) -> None:
    """
    Handle top users callback - show top users by loyalty points.
    
    Args:
        callback: Callback query from inline button
    """
    user = callback.from_user
    if not user or user.id not in admin_ids:
        await safe_answer_callback(callback, "❌ У вас нет прав для выполнения этой команды.")
        return
    
    try:
        top_users = await CachedStatisticsService.get_top_users_by_points(limit=10)
        
        if not top_users:
            await safe_answer_callback(callback, "❌ Не удалось получить топ пользователей.")
            return
        
        message = "🏆 <b>Топ-10 пользователей по баллам лояльности:</b>\n\n"
        
        for i, user_data in enumerate(top_users, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            message += (
                f"{medal} <b>ID:</b> {user_data['telegram_id']}\n"
                f"   • Баллы: {user_data['loyalty_points']:.1f}\n"
                f"   • Потрачено: {user_data['total_spent']:.2f} ₽\n"
                f"   • Уровень: {user_data['level_name']}\n\n"
            )
            
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="← Назад к статистике",
                            callback_data="statistics"
                        )
                    ]
                ]
            )
            
            await safe_edit_message(callback, message, keyboard)
            await callback.answer()
            
    except Exception as e:
        logger.error(f"Error getting top users: {e}", exc_info=True)
        await safe_answer_callback(callback, "❌ Произошла ошибка при получении топа пользователей.")


@callback_handler
async def wallet_statistics_callback(callback: CallbackQuery) -> None:
    """
    Handle wallet statistics callback - show wallet connection statistics.
    
    Args:
        callback: Callback query from inline button
    """
    user = callback.from_user
    if not user or user.id not in admin_ids:
        await safe_answer_callback(callback, "❌ У вас нет прав для выполнения этой команды.")
        return
    
    try:
        wallet_stats = await CachedStatisticsService.get_wallet_connection_stats()
        
        if not wallet_stats:
            await safe_answer_callback(callback, "❌ Не удалось получить статистику кошельков.")
            return
        
        message = (
            "💳 <b>Статистика подключения кошельков:</b>\n\n"
            f"• Всего пользователей: {wallet_stats['total_users']}\n"
            f"• С подключенными кошельками: {wallet_stats['users_with_wallets']}\n"
            f"• Без кошельков: {wallet_stats['users_without_wallets']}\n"
            f"• Процент подключения: {wallet_stats['connection_rate_percent']}%\n"
            f"• Новых подключений за неделю: {wallet_stats['recent_connections_week']}\n"
        )
            
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="← Назад к статистике",
                            callback_data="statistics"
                        )
                    ]
                ]
            )
            
        await safe_edit_message(callback, message, keyboard)
        await callback.answer()
            
    except Exception as e:
        logger.error(f"Error getting wallet statistics: {e}", exc_info=True)
        await safe_answer_callback(callback, "❌ Произошла ошибка при получении статистики кошельков.")


@callback_handler
async def force_refresh_statistics_callback(callback: CallbackQuery) -> None:
    """
    Handle force refresh statistics callback - refresh cache and show statistics.
    
    Args:
        callback: Callback query from inline button
    """
    user = callback.from_user
    if not user or user.id not in admin_ids:
        await safe_answer_callback(callback, "❌ У вас нет прав для выполнения этой команды.")
        return
    
    try:
        # Show loading message
        await safe_answer_callback(callback, "🔄 Обновляем статистику...")
        
        # Force refresh all statistics
        results = await refresh_statistics_now()
        
        # Check if refresh was successful
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        
        if successful < total:
            await safe_answer_callback(
                callback, 
                f"⚠️ Статистика обновлена частично ({successful}/{total}). "
                f"Некоторые данные могут быть устаревшими."
            )
        else:
            await safe_answer_callback(callback, "✅ Статистика успешно обновлена!")
        
        # Show updated statistics
        callback.data = "statistics"
        await statistics_callback(callback)
        
        bot_logger.info(f"Statistics force refreshed by admin {user.id}: {results}")
        
    except Exception as e:
        logger.error(f"Error force refreshing statistics: {e}", exc_info=True)
        await safe_answer_callback(callback, "❌ Произошла ошибка при обновлении статистики.")


@callback_handler
async def loyalty_management_callback(callback: CallbackQuery) -> None:
    """
    Handle loyalty management callback - show loyalty program management menu.
    
    Args:
        callback: Callback query from inline button
    """
    user = callback.from_user
    if not user or user.id not in admin_ids:
        await safe_answer_callback(callback, "❌ У вас нет прав для выполнения этой команды.")
        return
    
    try:
        async with get_async_session() as db:
            loyalty_service = LoyaltyService(db)
            levels = await loyalty_service.get_levels()
            
            message = "🎯 <b>Управление программой лояльности</b>\n\n"
            message += "<b>Текущие уровни:</b>\n"
            
            for level in levels:
                message += (
                    f"• <b>{level.name}</b>\n"
                    f"  Порог: {level.threshold:.0f} ₽\n"
                    f"  Ставка баллов: {level.points_rate:.1f}%\n\n"
                )
            
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="➕ Добавить уровень",
                            callback_data="add_loyalty_level"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="✏️ Редактировать уровни",
                            callback_data="edit_loyalty_levels"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="← Назад к настройкам",
                            callback_data="settings"
                        )
                    ]
                ]
            )
            
            await safe_edit_message(callback, message, keyboard)
            await callback.answer()
            
    except Exception as e:
        logger.error(f"Error getting loyalty management: {e}", exc_info=True)
        await safe_answer_callback(callback, "❌ Произошла ошибка при получении данных программы лояльности.")


@callback_handler
async def edit_loyalty_levels_callback(callback: CallbackQuery) -> None:
    """
    Handle edit loyalty levels callback - show list of levels for editing.
    
    Args:
        callback: Callback query from inline button
    """
    user = callback.from_user
    if not user or user.id not in admin_ids:
        await safe_answer_callback(callback, "❌ У вас нет прав для выполнения этой команды.")
        return
    
    try:
        async with get_async_session() as db:
            loyalty_service = LoyaltyService(db)
            levels = await loyalty_service.get_levels()
            
            if not levels:
                await safe_answer_callback(callback, "❌ Нет уровней для редактирования.")
                return
            
            message = "✏️ <b>Выберите уровень для редактирования:</b>\n\n"
            
            keyboard_buttons = []
            for level in levels:
                message += f"• <b>{level.name}</b> (порог: {level.threshold:.0f} ₽, ставка: {level.points_rate:.1f}%)\n"
                keyboard_buttons.append([
                    InlineKeyboardButton(
                        text=f"✏️ {level.name}",
                        callback_data=f"edit_level_{level.id}"
                    )
                ])
            
            keyboard_buttons.append([
                InlineKeyboardButton(
                    text="← Назад",
                    callback_data="loyalty_management"
                )
            ])
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
            
            await safe_edit_message(callback, message, keyboard)
            await callback.answer()
            
    except Exception as e:
        logger.error(f"Error getting loyalty levels for editing: {e}", exc_info=True)
        await safe_answer_callback(callback, "❌ Произошла ошибка при получении уровней лояльности.")


@callback_handler
async def edit_level_callback(callback: CallbackQuery) -> None:
    """
    Handle edit specific level callback - show level editing options.
    
    Args:
        callback: Callback query from inline button
    """
    user = callback.from_user
    if not user or user.id not in admin_ids:
        await safe_answer_callback(callback, "❌ У вас нет прав для выполнения этой команды.")
        return
    
    try:
        # Extract level_id from callback data
        level_id = int(callback.data.split("_")[-1])
        
        async with get_async_session() as db:
            loyalty_service = LoyaltyService(db)
            level = await loyalty_service.get_level_by_id(level_id)
            
            if not level:
                await safe_answer_callback(callback, "❌ Уровень не найден.")
                return
            
            message = (
                f"✏️ <b>Редактирование уровня: {level.name}</b>\n\n"
                f"<b>Текущие параметры:</b>\n"
                f"• Название: {level.name}\n"
                f"• Порог: {level.threshold:.0f} ₽\n"
                f"• Ставка баллов: {level.points_rate:.1f}%\n"
                f"• Порядок: {level.order}\n\n"
                f"<i>Для редактирования используйте команды:</i>\n"
                f"<pre><code>/edit_level_name_{level.id}</code></pre> Новое название\n"
                f"<pre><code>/edit_level_threshold_{level.id}</code></pre> 1000\n"
                f"<pre><code>/edit_level_rate_{level.id}</code></pre> 5.5"
            )
            
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="🗑️ Удалить уровень",
                            callback_data=f"delete_level_{level.id}"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="← Назад к списку",
                            callback_data="edit_loyalty_levels"
                        )
                    ]
                ]
            )
            
            await safe_edit_message(callback, message, keyboard)
            await callback.answer()
            
    except Exception as e:
        logger.error(f"Error editing level: {e}", exc_info=True)
        await safe_answer_callback(callback, "❌ Произошла ошибка при редактировании уровня.")


@callback_handler
async def delete_level_callback(callback: CallbackQuery) -> None:
    """
    Handle delete level callback - delete a loyalty level.
    
    Args:
        callback: Callback query from inline button
    """
    user = callback.from_user
    if not user or user.id not in admin_ids:
        await safe_answer_callback(callback, "❌ У вас нет прав для выполнения этой команды.")
        return
    
    try:
        # Extract level_id from callback data
        level_id = int(callback.data.split("_")[-1])
        
        async with get_async_session() as db:
            loyalty_service = LoyaltyService(db)
            level = await loyalty_service.get_level_by_id(level_id)
            
            if not level:
                await safe_answer_callback(callback, "❌ Уровень не найден.")
                return
            
            # Try to delete the level
            success = await loyalty_service.delete_level(level_id)
            
            if success:
                await safe_answer_callback(
                    callback, 
                    f"✅ Уровень '{level.name}' успешно удален."
                )
                bot_logger.info(f"Loyalty level {level.name} deleted by admin {user.id}")
                
                # Return to levels list by recreating the callback with edit_loyalty_levels data
                callback.data = "edit_loyalty_levels"
                await edit_loyalty_levels_callback(callback)
            else:
                await safe_answer_callback(
                    callback, 
                    f"❌ Невозможно удалить уровень '{level.name}'. "
                    f"К нему привязаны пользователи."
                )
            
    except Exception as e:
        logger.error(f"Error deleting level: {e}", exc_info=True)
        await safe_answer_callback(callback, "❌ Произошла ошибка при удалении уровня.")


@callback_handler
async def add_loyalty_level_callback(callback: CallbackQuery) -> None:
    """
    Handle add loyalty level callback - show instructions for adding a new level.
    
    Args:
        callback: Callback query from inline button
    """
    user = callback.from_user
    if not user or user.id not in admin_ids:
        await safe_answer_callback(callback, "❌ У вас нет прав для выполнения этой команды.")
        return
    
    message = (
        "➕ <b>Добавление нового уровня лояльности</b>\n\n"
        "<i>Для создания нового уровня используйте команду:</i>\n"
        "<code>/create_level Название Порог Ставка</code>\n\n"
        "<b>Пример:</b>\n"
        "<code>/create_level Золотой 5000 7.5</code>\n\n"
        "<b>Параметры:</b>\n"
        "• <b>Название</b> - название уровня\n"
        "• <b>Порог</b> - минимальная сумма трат для достижения уровня (в рублях)\n"
        "• <b>Ставка</b> - процент начисления баллов (например, 5.0 = 5%)"
    )
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="← Назад",
                    callback_data="loyalty_management"
                )
            ]
        ]
    )
    
    await safe_edit_message(callback, message, keyboard)
    await callback.answer()


@callback_handler
async def settings_callback(callback: CallbackQuery) -> None:
    """
    Handle settings callback - show settings menu.    
    Args:
        callback: Callback query from inline button
    """
    # Here should be the logic to show settings
    # For now, just return to main menu
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📊 Статистика",
                    callback_data="statistics"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎯 Программа лояльности",
                    callback_data="loyalty_management"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💾 Статус кеша",
                    callback_data="cache_status"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📥Загрузить меню из Google Sheets",
                    callback_data="upload_menu_google_sheets"
                )
            ]
        ]
    )
    await safe_edit_message(
        callback,
        "⚙️ <b>Настройки</b>\n\n"
        "Выберите действие:",
        keyboard
    )
    await callback.answer()

@callback_handler
async def cache_status_callback(callback: CallbackQuery) -> None:
    """
    Handle cache status callback - show cache status information.
    
    Args:
        callback: Callback query from inline button
    """
    user = callback.from_user
    if not user or user.id not in admin_ids:
        await safe_answer_callback(callback, "❌ У вас нет прав для выполнения этой команды.")
        return
    
    try:
        # Get cache status
        cache_status = await CachedStatisticsService.get_cache_status()
        scheduler_status = get_scheduler_status()
        
        message = "💾 <b>Статус кеша статистики</b>\n\n"
        
        # Cache information
        message += f"📊 <b>Кешированные данные:</b> {cache_status['total_cached']}\n"
        message += f"⏱️ <b>TTL кеша:</b> {cache_status['cache_ttl_minutes']} минут\n\n"
        
        # Scheduler information
        if scheduler_status:
            message += "🔄 <b>Планировщик обновлений:</b>\n"
            message += f"• Статус: {'🟢 Работает' if scheduler_status['is_running'] else '🔴 Остановлен'}\n"
            message += f"• Интервал: {scheduler_status['refresh_interval_minutes']:.0f} минут\n"
            
            if scheduler_status['last_refresh']:
                last_refresh = datetime.fromisoformat(scheduler_status['last_refresh'])
                message += f"• Последнее обновление: {last_refresh.strftime('%d.%m.%Y %H:%M')}\n"
            
            if scheduler_status['next_refresh']:
                next_refresh = datetime.fromisoformat(scheduler_status['next_refresh'])
                message += f"• Следующее обновление: {next_refresh.strftime('%d.%m.%Y %H:%M')}\n"
        else:
            message += "🔄 <b>Планировщик:</b> 🔴 Не запущен\n"
        
        message += "\n<b>Детали кеша:</b>\n"
        
        # Cache details
        for stats_type, info in cache_status['cached_statistics'].items():
            cached_at = datetime.fromisoformat(info['cached_at'])
            expires_at = datetime.fromisoformat(info['expires_at'])
            ttl_minutes = info['ttl'] // 60 if info['ttl'] > 0 else 0
            
            message += f"• <b>{stats_type}</b>:\n"
            message += f"  Кеширован: {cached_at.strftime('%H:%M')}\n"
            message += f"  Истекает: {expires_at.strftime('%H:%M')}\n"
            message += f"  Осталось: {ttl_minutes} мин\n\n"
        
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🔄 Обновить статус",
                        callback_data="cache_status"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="⚡ Принудительное обновление",
                        callback_data="force_refresh_statistics"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="← Назад к настройкам",
                        callback_data="settings"
                    )
                ]
            ]
        )
        
        await safe_edit_message(callback, message, keyboard)
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error getting cache status: {e}", exc_info=True)
        await safe_answer_callback(callback, "❌ Произошла ошибка при получении статуса кеша.")


async def create_level_command(message: Message) -> None:
    """
    Handle /create_level command - create a new loyalty level.
    
    Args:
        message: Message with command and parameters
    """
    user = message.from_user
    if not user or user.id not in admin_ids:
        await message.answer("❌ У вас нет прав для выполнения этой команды.")
        return
    
    try:
        # Parse command arguments
        args = message.text.split()[1:]  # Skip the command itself
        if len(args) != 3:
            await message.answer(
                "❌ Неверный формат команды.\n"
                "Используйте: <code>/create_level Название Порог Ставка</code>\n"
                "Пример: <code>/create_level Золотой 5000 7.5</code>"
            )
            return
        
        name = args[0]
        threshold = float(args[1])
        points_rate = float(args[2])
        
        async with get_async_session() as db:
            loyalty_service = LoyaltyService(db)
            level = await loyalty_service.create_level(name, threshold, points_rate)
            
            await message.answer(
                f"✅ Уровень лояльности создан:\n"
                f"• Название: {level.name}\n"
                f"• Порог: {level.threshold:.0f} ₽\n"
                f"• Ставка баллов: {level.points_rate:.1f}%"
            )
            
            bot_logger.info(f"Loyalty level {level.name} created by admin {user.id}")
            
    except ValueError:
        await message.answer("❌ Неверный формат чисел. Порог и ставка должны быть числами.")
    except Exception as e:
        logger.error(f"Error creating loyalty level: {e}", exc_info=True)
        await message.answer("❌ Произошла ошибка при создании уровня лояльности.")


async def edit_level_name_command(message: Message) -> None:
    """
    Handle /edit_level_name_X command - edit loyalty level name.
    
    Args:
        message: Message with command and parameters
    """
    user = message.from_user
    if not user or user.id not in admin_ids:
        await message.answer("❌ У вас нет прав для выполнения этой команды.")
        return
    
    try:
        # Parse command to get level_id and new name
        command_parts = message.text.split()
        if len(command_parts) < 2:
            await message.answer("❌ Укажите новое название уровня.")
            return
        
        level_id = int(command_parts[0].split("_")[-1])
        new_name = " ".join(command_parts[1:])
        
        async with get_async_session() as db:
            loyalty_service = LoyaltyService(db)
            level = await loyalty_service.update_level(level_id, name=new_name)
            
            if level:
                await message.answer(f"✅ Название уровня изменено на: {level.name}")
                bot_logger.info(f"Loyalty level {level.id} name updated by admin {user.id}")
            else:
                await message.answer("❌ Уровень не найден.")
            
    except ValueError:
        await message.answer("❌ Неверный формат команды.")
    except Exception as e:
        logger.error(f"Error editing level name: {e}", exc_info=True)
        await message.answer("❌ Произошла ошибка при изменении названия уровня.")


async def edit_level_threshold_command(message: Message) -> None:
    """
    Handle /edit_level_threshold_X command - edit loyalty level threshold.
    
    Args:
        message: Message with command and parameters
    """
    user = message.from_user
    if not user or user.id not in admin_ids:
        await message.answer("❌ У вас нет прав для выполнения этой команды.")
        return
    
    try:
        # Parse command to get level_id and new threshold
        command_parts = message.text.split()
        if len(command_parts) != 2:
            await message.answer("❌ Укажите новый порог (число).")
            return
        
        level_id = int(command_parts[0].split("_")[-1])
        new_threshold = float(command_parts[1])
        
        async with get_async_session() as db:
            loyalty_service = LoyaltyService(db)
            level = await loyalty_service.update_level(level_id, threshold=new_threshold)
            
            if level:
                await message.answer(f"✅ Порог уровня '{level.name}' изменен на: {level.threshold:.0f} ₽")
                bot_logger.info(f"Loyalty level {level.id} threshold updated by admin {user.id}")
            else:
                await message.answer("❌ Уровень не найден.")
            
    except ValueError:
        await message.answer("❌ Неверный формат числа.")
    except Exception as e:
        logger.error(f"Error editing level threshold: {e}", exc_info=True)
        await message.answer("❌ Произошла ошибка при изменении порога уровня.")


async def edit_level_rate_command(message: Message) -> None:
    """
    Handle /edit_level_rate_X command - edit loyalty level points rate.
    
    Args:
        message: Message with command and parameters
    """
    user = message.from_user
    if not user or user.id not in admin_ids:
        await message.answer("❌ У вас нет прав для выполнения этой команды.")
        return
    
    try:
        # Parse command to get level_id and new rate
        command_parts = message.text.split()
        if len(command_parts) != 2:
            await message.answer("❌ Укажите новую ставку баллов (число).")
            return
        
        level_id = int(command_parts[0].split("_")[-1])
        new_rate = float(command_parts[1])
        
        async with get_async_session() as db:
            loyalty_service = LoyaltyService(db)
            level = await loyalty_service.update_level(level_id, points_rate=new_rate)
            
            if level:
                await message.answer(f"✅ Ставка баллов уровня '{level.name}' изменена на: {level.points_rate:.1f}%")
                bot_logger.info(f"Loyalty level {level.id} rate updated by admin {user.id}")
            else:
                await message.answer("❌ Уровень не найден.")
            
    except ValueError:
        await message.answer("❌ Неверный формат числа.")
    except Exception as e:
        logger.error(f"Error editing level rate: {e}", exc_info=True)
        await message.answer("❌ Произошла ошибка при изменении ставки баллов.")


def register_admin_handlers(dp: Dispatcher) -> None:
    """Register admin command handlers."""
    # Callback handlers
    dp.callback_query.register(settings_callback, F.data == "settings")
    dp.callback_query.register(upload_menu_google_sheets_callback, F.data == "upload_menu_google_sheets")
    dp.callback_query.register(statistics_callback, F.data == "statistics")
    dp.callback_query.register(detailed_statistics_callback, F.data == "detailed_statistics")
    dp.callback_query.register(top_users_callback, F.data == "top_users")
    dp.callback_query.register(wallet_statistics_callback, F.data == "wallet_statistics")
    dp.callback_query.register(force_refresh_statistics_callback, F.data == "force_refresh_statistics")
    dp.callback_query.register(cache_status_callback, F.data == "cache_status")
    
    # Loyalty management callbacks
    dp.callback_query.register(loyalty_management_callback, F.data == "loyalty_management")
    dp.callback_query.register(edit_loyalty_levels_callback, F.data == "edit_loyalty_levels")
    dp.callback_query.register(edit_level_callback, F.data.startswith("edit_level_"))
    dp.callback_query.register(delete_level_callback, F.data.startswith("delete_level_"))
    dp.callback_query.register(add_loyalty_level_callback, F.data == "add_loyalty_level")
    
    # Command handlers with admin check
    dp.message.register(
        create_level_command, 
        Command("create_level"),
        lambda message: is_admin_message(message)
    )
    
    # Dynamic command handlers (using text filters)
    dp.message.register(
        edit_level_name_command, 
        lambda message: (message.text and 
                        message.text.startswith("/edit_level_name_") and 
                        is_admin_message(message))
    )
    dp.message.register(
        edit_level_threshold_command, 
        lambda message: (message.text and 
                        message.text.startswith("/edit_level_threshold_") and 
                        is_admin_message(message))
    )
    dp.message.register(
        edit_level_rate_command, 
        lambda message: (message.text and 
                        message.text.startswith("/edit_level_rate_") and 
                        is_admin_message(message))
    )