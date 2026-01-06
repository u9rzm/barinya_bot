"""Administrative commands handlers."""
import logging
from typing import Optional

from aiogram import Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession

from shared.config import settings
from shared.database import get_async_session
from shared.services import (
    MenuService_db, PromotionService, UserService, 
    LoyaltyService, NotificationService
)
from shared.models import MenuCategory
from shared.logging_config import get_logger, log_admin_action
from bot.error_handlers import (
    admin_command_handler, 
    callback_handler, 
    safe_send_message, 
    safe_answer_callback
)

logger = get_logger(__name__)


class AdminStates(StatesGroup):
    """States for admin operations."""
    waiting_for_item_name = State()
    waiting_for_item_description = State()
    waiting_for_item_price = State()
    waiting_for_item_category = State()
    waiting_for_item_image_url = State()
    
    waiting_for_edit_item_id = State()
    waiting_for_edit_field = State()
    waiting_for_edit_value = State()
    
    waiting_for_promo_title = State()
    waiting_for_promo_description = State()
    waiting_for_promo_start_date = State()
    waiting_for_promo_end_date = State()
    
    waiting_for_broadcast_message = State()
    
    waiting_for_level_username = State()
    waiting_for_level_name = State()


def is_admin(user_id: int) -> bool:
    """Check if user is admin."""
    return user_id in settings.admin_ids_list


@admin_command_handler("add_menu_item")
async def admin_add_item_command(message: Message, state: FSMContext) -> None:
    """
    Handle /admin_add_item command.
    
    Args:
        message: Incoming message
        state: FSM context
    """
    if not message.from_user or not is_admin(message.from_user.id):
        await safe_send_message(message, "❌ У вас нет прав администратора.")
        return
    
    await safe_send_message(
        message,
        "📝 <b>Добавление новой позиции в меню</b>\n\n"
        "Введите название позиции:"
    )
    await state.set_state(AdminStates.waiting_for_item_name)


async def process_item_name(message: Message, state: FSMContext) -> None:
    """Process item name input."""
    if not message.text:
        await message.answer("❌ Пожалуйста, введите текст.")
        return
    
    await state.update_data(item_name=message.text)
    await message.answer("Введите описание позиции:")
    await state.set_state(AdminStates.waiting_for_item_description)


async def process_item_description(message: Message, state: FSMContext) -> None:
    """Process item description input."""
    if not message.text:
        await message.answer("❌ Пожалуйста, введите текст.")
        return
    
    await state.update_data(item_description=message.text)
    await message.answer("Введите цену позиции (только число):")
    await state.set_state(AdminStates.waiting_for_item_price)


async def process_item_price(message: Message, state: FSMContext) -> None:
    """Process item price input."""
    if not message.text:
        await message.answer("❌ Пожалуйста, введите число.")
        return
    
    try:
        price = float(message.text)
        if price <= 0:
            await message.answer("❌ Цена должна быть больше нуля.")
            return
    except ValueError:
        await message.answer("❌ Пожалуйста, введите корректное число.")
        return
    
    await state.update_data(item_price=price)
    
    # Get available categories
    try:
        async with get_async_session() as db:
            menu_service = MenuService(db)
            categories = await menu_service.get_categories()
            
            if not categories:
                await message.answer("❌ Нет доступных категорий. Создайте категорию сначала.")
                await state.clear()
                return
            
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text=cat.name, callback_data=f"select_category_{cat.id}")]
                    for cat in categories
                ]
            )
            
            await message.answer("Выберите категорию:", reply_markup=keyboard)
            await state.set_state(AdminStates.waiting_for_item_category)
            
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        await message.answer("❌ Ошибка получения категорий.")
        await state.clear()


async def process_category_selection(callback: CallbackQuery, state: FSMContext) -> None:
    """Process category selection."""
    if not callback.data or not callback.data.startswith("select_category_"):
        await callback.answer("❌ Ошибка выбора категории.")
        return
    
    category_id = int(callback.data.split("_")[-1])
    await state.update_data(item_category_id=category_id)
    
    await callback.message.answer(
        "Введите URL изображения (или отправьте 'нет' если изображения нет):"
    )
    await callback.answer()
    await state.set_state(AdminStates.waiting_for_item_image_url)


async def process_item_image_url(message: Message, state: FSMContext) -> None:
    """Process item image URL input."""
    if not message.text:
        await message.answer("❌ Пожалуйста, введите URL или 'нет'.")
        return
    
    image_url = None if message.text.lower() in ['нет', 'no', '-'] else message.text
    
    # Get all data and create item
    data = await state.get_data()
    
    try:
        async with get_async_session() as db:
            menu_service = MenuService(db)
            
            item = await menu_service.create_menu_item({
                'name': data['item_name'],
                'description': data['item_description'],
                'price': data['item_price'],
                'category_id': data['item_category_id'],
                'image_url': image_url,
                'is_available': True
            })
            
            await db.commit()
            
            await message.answer(
                f"✅ <b>Позиция добавлена!</b>\n\n"
                f"📝 Название: {item.name}\n"
                f"💰 Цена: {item.price:.2f} руб.\n"
                f"📋 Описание: {item.description}\n"
                f"🖼️ Изображение: {'Да' if item.image_url else 'Нет'}"
            )
            
    except Exception as e:
        logger.error(f"Error creating menu item: {e}")
        await message.answer("❌ Ошибка создания позиции.")
    
    await state.clear()


async def admin_create_promo_command(message: Message, state: FSMContext) -> None:
    """
    Handle /admin_create_promo command.
    
    Args:
        message: Incoming message
        state: FSM context
    """
    if not message.from_user or not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав администратора.")
        return
    
    await message.answer(
        "🎉 <b>Создание новой акции</b>\n\n"
        "Введите заголовок акции:"
    )
    await state.set_state(AdminStates.waiting_for_promo_title)


async def process_promo_title(message: Message, state: FSMContext) -> None:
    """Process promotion title input."""
    if not message.text:
        await message.answer("❌ Пожалуйста, введите текст.")
        return
    
    await state.update_data(promo_title=message.text)
    await message.answer("Введите описание акции:")
    await state.set_state(AdminStates.waiting_for_promo_description)


async def process_promo_description(message: Message, state: FSMContext) -> None:
    """Process promotion description input."""
    if not message.text:
        await message.answer("❌ Пожалуйста, введите текст.")
        return
    
    await state.update_data(promo_description=message.text)
    await message.answer(
        "Введите дату начала акции в формате ГГГГ-ММ-ДД ЧЧ:ММ\n"
        "Например: 2024-12-20 10:00"
    )
    await state.set_state(AdminStates.waiting_for_promo_start_date)


async def process_promo_start_date(message: Message, state: FSMContext) -> None:
    """Process promotion start date input."""
    if not message.text:
        await message.answer("❌ Пожалуйста, введите дату.")
        return
    
    try:
        from datetime import datetime
        start_date = datetime.strptime(message.text, "%Y-%m-%d %H:%M")
        await state.update_data(promo_start_date=start_date)
        
        await message.answer(
            "Введите дату окончания акции в формате ГГГГ-ММ-ДД ЧЧ:ММ\n"
            "Например: 2024-12-25 23:59"
        )
        await state.set_state(AdminStates.waiting_for_promo_end_date)
        
    except ValueError:
        await message.answer("❌ Неверный формат даты. Используйте ГГГГ-ММ-ДД ЧЧ:ММ")


async def process_promo_end_date(message: Message, state: FSMContext) -> None:
    """Process promotion end date input."""
    if not message.text:
        await message.answer("❌ Пожалуйста, введите дату.")
        return
    
    try:
        from datetime import datetime
        end_date = datetime.strptime(message.text, "%Y-%m-%d %H:%M")
        
        data = await state.get_data()
        start_date = data['promo_start_date']
        
        if end_date <= start_date:
            await message.answer("❌ Дата окончания должна быть позже даты начала.")
            return
        
        # Create promotion
        async with get_async_session() as db:
            promotion_service = PromotionService(db)
            
            promotion = await promotion_service.create_promotion({
                'title': data['promo_title'],
                'description': data['promo_description'],
                'start_date': start_date,
                'end_date': end_date,
                'image_url': None
            })
            
            await db.commit()
            
            # Ask if admin wants to broadcast immediately
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="📢 Отправить сейчас",
                            callback_data=f"broadcast_promo_{promotion.id}"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="⏰ Отправить позже",
                            callback_data="broadcast_later"
                        )
                    ]
                ]
            )
            
            await message.answer(
                f"✅ <b>Акция создана!</b>\n\n"
                f"🎉 {promotion.title}\n"
                f"📝 {promotion.description}\n"
                f"📅 С {start_date.strftime('%d.%m.%Y %H:%M')} "
                f"по {end_date.strftime('%d.%m.%Y %H:%M')}\n\n"
                "Отправить уведомление пользователям?",
                reply_markup=keyboard
            )
            
    except ValueError:
        await message.answer("❌ Неверный формат даты. Используйте ГГГГ-ММ-ДД ЧЧ:ММ")
    except Exception as e:
        logger.error(f"Error creating promotion: {e}")
        await message.answer("❌ Ошибка создания акции.")
    
    await state.clear()


async def broadcast_promo_callback(callback: CallbackQuery) -> None:
    """Handle promotion broadcast callback."""
    if not callback.data or not callback.data.startswith("broadcast_promo_"):
        await callback.answer("❌ Ошибка.")
        return
    
    promotion_id = int(callback.data.split("_")[-1])
    
    try:
        async with get_async_session() as db:
            promotion_service = PromotionService(db)
            await promotion_service.broadcast_promotion(promotion_id)
            
        await callback.message.answer("✅ Рассылка запущена!")
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error broadcasting promotion: {e}")
        await callback.answer("❌ Ошибка рассылки.")


async def admin_broadcast_command(message: Message, state: FSMContext) -> None:
    """
    Handle /admin_broadcast command.
    
    Args:
        message: Incoming message
        state: FSM context
    """
    if not message.from_user or not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав администратора.")
        return
    
    await message.answer(
        "📢 <b>Рассылка сообщения</b>\n\n"
        "Введите текст сообщения для рассылки всем активным пользователям:"
    )
    await state.set_state(AdminStates.waiting_for_broadcast_message)


async def process_broadcast_message(message: Message, state: FSMContext) -> None:
    """Process broadcast message input."""
    if not message.text:
        await message.answer("❌ Пожалуйста, введите текст сообщения.")
        return
    
    try:
        async with get_async_session() as db:
            notification_service = NotificationService(db)
            await notification_service.broadcast_to_active_users(message.text)
            
        await message.answer("✅ Рассылка запущена!")
        
    except Exception as e:
        logger.error(f"Error broadcasting message: {e}")
        await message.answer("❌ Ошибка рассылки.")
    
    await state.clear()


async def admin_set_level_command(message: Message, state: FSMContext) -> None:
    """
    Handle /admin_set_level command.
    
    Args:
        message: Incoming message
        state: FSM context
    """
    if not message.from_user or not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав администратора.")
        return
    
    await message.answer(
        "👑 <b>Назначение уровня пользователю</b>\n\n"
        "Введите username пользователя (без @):"
    )
    await state.set_state(AdminStates.waiting_for_level_username)


async def process_level_username(message: Message, state: FSMContext) -> None:
    """Process username input for level assignment."""
    if not message.text:
        await message.answer("❌ Пожалуйста, введите username.")
        return
    
    username = message.text.lstrip('@')
    
    try:
        async with get_async_session() as db:
            user_service = UserService(db)
            user = await user_service.get_user_by_username(username)
            
            if not user:
                await message.answer(f"❌ Пользователь @{username} не найден.")
                await state.clear()
                return
            
            await state.update_data(target_user_id=user.id, target_username=username)
            
            # Get available levels
            loyalty_service = LoyaltyService(db)
            levels = await loyalty_service.get_levels()
            
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(
                        text=f"{level.name} (от {level.threshold:.0f} руб.)",
                        callback_data=f"assign_level_{level.id}"
                    )]
                    for level in levels
                ]
            )
            
            await message.answer(
                f"Выберите уровень для пользователя @{username}:",
                reply_markup=keyboard
            )
            await state.set_state(AdminStates.waiting_for_level_name)
            
    except Exception as e:
        logger.error(f"Error getting user for level assignment: {e}")
        await message.answer("❌ Ошибка поиска пользователя.")
        await state.clear()


async def assign_level_callback(callback: CallbackQuery, state: FSMContext) -> None:
    """Handle level assignment callback."""
    if not callback.data or not callback.data.startswith("assign_level_"):
        await callback.answer("❌ Ошибка.")
        return
    
    level_id = int(callback.data.split("_")[-1])
    data = await state.get_data()
    
    try:
        async with get_async_session() as db:
            user_service = UserService(db)
            loyalty_service = LoyaltyService(db)
            notification_service = NotificationService(db)
            
            # Assign level
            await user_service.set_user_level(data['target_user_id'], level_id)
            
            # Get level info and user info
            level = await loyalty_service.get_level_by_id(level_id)
            user = await user_service.get_user_by_id(data['target_user_id'])
            
            # Send notification to user
            await notification_service.send_level_up_notification(
                user.telegram_id, level
            )
            
            await db.commit()
            
            await callback.message.answer(
                f"✅ Пользователю @{data['target_username']} назначен уровень '{level.name}'"
            )
            await callback.answer()
            
    except Exception as e:
        logger.error(f"Error assigning level: {e}")
        await callback.answer("❌ Ошибка назначения уровня.")
    
    await state.clear()


def register_admin_handlers(dp: Dispatcher) -> None:
    """Register admin handlers."""
    # Commands
    dp.message.register(admin_add_item_command, Command("admin_add_item"))
    dp.message.register(admin_create_promo_command, Command("admin_create_promo"))
    dp.message.register(admin_broadcast_command, Command("admin_broadcast"))
    dp.message.register(admin_set_level_command, Command("admin_set_level"))
    
    # FSM handlers
    dp.message.register(process_item_name, AdminStates.waiting_for_item_name)
    dp.message.register(process_item_description, AdminStates.waiting_for_item_description)
    dp.message.register(process_item_price, AdminStates.waiting_for_item_price)
    dp.message.register(process_item_image_url, AdminStates.waiting_for_item_image_url)
    
    dp.message.register(process_promo_title, AdminStates.waiting_for_promo_title)
    dp.message.register(process_promo_description, AdminStates.waiting_for_promo_description)
    dp.message.register(process_promo_start_date, AdminStates.waiting_for_promo_start_date)
    dp.message.register(process_promo_end_date, AdminStates.waiting_for_promo_end_date)
    
    dp.message.register(process_broadcast_message, AdminStates.waiting_for_broadcast_message)
    
    dp.message.register(process_level_username, AdminStates.waiting_for_level_username)
    
    # Callback handlers
    dp.callback_query.register(process_category_selection, F.data.startswith("select_category_"))
    dp.callback_query.register(broadcast_promo_callback, F.data.startswith("broadcast_promo_"))
    dp.callback_query.register(assign_level_callback, AdminStates.waiting_for_level_name, F.data.startswith("assign_level_"))