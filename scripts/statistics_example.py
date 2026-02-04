#!/usr/bin/env python3
"""
Example script demonstrating the usage of StatisticsService.
This script shows how to use the statistics service to get various metrics.
"""
import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.database import get_async_session
from shared.services.statistics_service import StatisticsService


async def main():
    """Main function to demonstrate statistics service usage."""
    print("📊 Демонстрация сервиса статистики\n")
    
    try:
        async with get_async_session() as db:
            stats_service = StatisticsService(db)
            
            # Get overall statistics
            print("🔄 Получение общей статистики...")
            overall_stats = await stats_service.get_overall_statistics()
            
            print("\n" + "="*50)
            print("📊 ОБЩАЯ СТАТИСТИКА ПРИЛОЖЕНИЯ")
            print("="*50)
            
            # User statistics
            print(f"\n👥 ПОЛЬЗОВАТЕЛИ:")
            print(f"   Всего пользователей: {overall_stats.users.total_users}")
            print(f"   Активных пользователей: {overall_stats.users.active_users}")
            print(f"   С подключенными кошельками: {overall_stats.users.users_with_wallets}")
            print(f"   Без кошельков: {overall_stats.users.users_without_wallets}")
            print(f"   Новых сегодня: {overall_stats.users.new_users_today}")
            print(f"   Новых за неделю: {overall_stats.users.new_users_this_week}")
            print(f"   Новых за месяц: {overall_stats.users.new_users_this_month}")
            
            # Loyalty statistics
            print(f"\n🎯 ПРОГРАММА ЛОЯЛЬНОСТИ:")
            print(f"   Всего выдано баллов: {overall_stats.loyalty.total_points_issued:.1f}")
            print(f"   Всего потрачено баллов: {overall_stats.loyalty.total_points_redeemed:.1f}")
            print(f"   Активный баланс баллов: {overall_stats.loyalty.active_points_balance:.1f}")
            print(f"   Средний баланс на пользователя: {overall_stats.loyalty.average_points_per_user:.1f}")
            print(f"   Транзакций сегодня: {overall_stats.loyalty.points_transactions_today}")
            print(f"   Транзакций за неделю: {overall_stats.loyalty.points_transactions_this_week}")
            print(f"   Транзакций за месяц: {overall_stats.loyalty.points_transactions_this_month}")
            
            # Order statistics
            print(f"\n🛒 ЗАКАЗЫ:")
            print(f"   Всего заказов: {overall_stats.orders.total_orders}")
            print(f"   Завершенных: {overall_stats.orders.completed_orders}")
            print(f"   В ожидании: {overall_stats.orders.pending_orders}")
            print(f"   Отмененных: {overall_stats.orders.cancelled_orders}")
            print(f"   Общая выручка: {overall_stats.orders.total_revenue:.2f} ₽")
            print(f"   Средний чек: {overall_stats.orders.average_order_value:.2f} ₽")
            print(f"   Заказов сегодня: {overall_stats.orders.orders_today}")
            print(f"   Заказов за неделю: {overall_stats.orders.orders_this_week}")
            print(f"   Заказов за месяц: {overall_stats.orders.orders_this_month}")
            
            print(f"\n📅 Обновлено: {overall_stats.generated_at.strftime('%d.%m.%Y %H:%M:%S')}")
            
            # Get loyalty level distribution
            print("\n" + "="*50)
            print("📈 ДЕТАЛЬНАЯ СТАТИСТИКА ПО УРОВНЯМ ЛОЯЛЬНОСТИ")
            print("="*50)
            
            level_distribution = await stats_service.get_loyalty_level_distribution()
            
            for level_name, data in level_distribution.items():
                print(f"\n🎯 {level_name}:")
                print(f"   Порог: {data['threshold']:.0f} ₽")
                print(f"   Ставка баллов: {data['points_rate']:.1f}%")
                print(f"   Пользователей: {data['user_count']}")
                print(f"   Средний баланс баллов: {data['avg_points']:.1f}")
                print(f"   Общая сумма трат: {data['total_spent']:.2f} ₽")
            
            # Get top users
            print("\n" + "="*50)
            print("🏆 ТОП-10 ПОЛЬЗОВАТЕЛЕЙ ПО БАЛЛАМ ЛОЯЛЬНОСТИ")
            print("="*50)
            
            top_users = await stats_service.get_top_users_by_points(limit=10)
            
            for i, user_data in enumerate(top_users, 1):
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i:2d}."
                print(f"{medal} ID: {user_data['telegram_id']}")
                print(f"    Баллы: {user_data['loyalty_points']:.1f}")
                print(f"    Потрачено: {user_data['total_spent']:.2f} ₽")
                print(f"    Уровень: {user_data['level_name']}")
                print()
            
            # Get wallet statistics
            print("="*50)
            print("💳 СТАТИСТИКА ПОДКЛЮЧЕНИЯ КОШЕЛЬКОВ")
            print("="*50)
            
            wallet_stats = await stats_service.get_wallet_connection_stats()
            
            print(f"\nВсего пользователей: {wallet_stats['total_users']}")
            print(f"С подключенными кошельками: {wallet_stats['users_with_wallets']}")
            print(f"Без кошельков: {wallet_stats['users_without_wallets']}")
            print(f"Процент подключения: {wallet_stats['connection_rate_percent']}%")
            print(f"Новых подключений за неделю: {wallet_stats['recent_connections_week']}")
            
            # Get user growth trend
            print("\n" + "="*50)
            print("📈 ТРЕНД РОСТА ПОЛЬЗОВАТЕЛЕЙ (ПОСЛЕДНИЕ 7 ДНЕЙ)")
            print("="*50)
            
            growth_trend = await stats_service.get_user_growth_trend(days=7)
            
            for date_str, count in sorted(growth_trend.items()):
                print(f"{date_str}: {count} новых пользователей")
            
            print("\n✅ Демонстрация завершена успешно!")
            
    except Exception as e:
        print(f"❌ Ошибка при получении статистики: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())