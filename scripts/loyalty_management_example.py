#!/usr/bin/env python3
"""
Example script demonstrating loyalty management functionality.
This script shows how to create, edit, and manage loyalty levels.
"""
import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.database import get_async_session
from shared.services.loyalty_service import LoyaltyService


async def main():
    """Main function to demonstrate loyalty management."""
    print("🎯 Демонстрация управления программой лояльности\n")
    
    try:
        async with get_async_session() as db:
            loyalty_service = LoyaltyService(db)
            
            print("="*50)
            print("📋 ТЕКУЩИЕ УРОВНИ ЛОЯЛЬНОСТИ")
            print("="*50)
            
            # Get current levels
            levels = await loyalty_service.get_levels()
            
            if levels:
                for level in levels:
                    print(f"\n🎯 {level.name}")
                    print(f"   ID: {level.id}")
                    print(f"   Порог: {level.threshold:.0f} ₽")
                    print(f"   Ставка баллов: {level.points_rate:.1f}%")
                    print(f"   Порядок: {level.order}")
            else:
                print("Уровни лояльности не найдены.")
            
            print("\n" + "="*50)
            print("➕ СОЗДАНИЕ НОВОГО УРОВНЯ")
            print("="*50)
            
            # Create a new level (example)
            try:
                new_level = await loyalty_service.create_level(
                    name="Тестовый",
                    threshold=999999,  # High threshold to avoid conflicts
                    points_rate=15.0
                )
                print(f"\n✅ Создан новый уровень:")
                print(f"   Название: {new_level.name}")
                print(f"   ID: {new_level.id}")
                print(f"   Порог: {new_level.threshold:.0f} ₽")
                print(f"   Ставка: {new_level.points_rate:.1f}%")
                
                print("\n" + "="*50)
                print("✏️ РЕДАКТИРОВАНИЕ УРОВНЯ")
                print("="*50)
                
                # Update the level
                updated_level = await loyalty_service.update_level(
                    level_id=new_level.id,
                    name="Тестовый Обновленный",
                    threshold=888888,
                    points_rate=12.5
                )
                
                if updated_level:
                    print(f"\n✅ Уровень обновлен:")
                    print(f"   Название: {updated_level.name}")
                    print(f"   Порог: {updated_level.threshold:.0f} ₽")
                    print(f"   Ставка: {updated_level.points_rate:.1f}%")
                
                print("\n" + "="*50)
                print("🗑️ УДАЛЕНИЕ УРОВНЯ")
                print("="*50)
                
                # Delete the test level
                success = await loyalty_service.delete_level(new_level.id)
                
                if success:
                    print(f"\n✅ Тестовый уровень успешно удален")
                else:
                    print(f"\n❌ Не удалось удалить уровень (возможно, к нему привязаны пользователи)")
                
            except Exception as e:
                print(f"❌ Ошибка при работе с тестовым уровнем: {e}")
            
            print("\n" + "="*50)
            print("📊 ИТОГОВОЕ СОСТОЯНИЕ")
            print("="*50)
            
            # Show final state
            final_levels = await loyalty_service.get_levels()
            
            print(f"\nВсего уровней: {len(final_levels)}")
            for level in final_levels:
                print(f"• {level.name} (порог: {level.threshold:.0f}₽, ставка: {level.points_rate:.1f}%)")
            
            print("\n" + "="*50)
            print("🔍 ПОИСК УРОВНЯ ПО ID")
            print("="*50)
            
            if final_levels:
                first_level = final_levels[0]
                found_level = await loyalty_service.get_level_by_id(first_level.id)
                
                if found_level:
                    print(f"\n✅ Найден уровень по ID {first_level.id}:")
                    print(f"   Название: {found_level.name}")
                    print(f"   Порог: {found_level.threshold:.0f} ₽")
                    print(f"   Ставка: {found_level.points_rate:.1f}%")
                else:
                    print(f"\n❌ Уровень с ID {first_level.id} не найден")
            
            print("\n✅ Демонстрация завершена успешно!")
            
    except Exception as e:
        print(f"❌ Ошибка при демонстрации: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())