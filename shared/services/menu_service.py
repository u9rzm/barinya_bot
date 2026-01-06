"""Menu service for managing menu items and categories."""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from shared.models import MenuItem, MenuCategory


class MenuService_db:
    """Service for managing menu items and categories."""
    
    def __init__(self, db: AsyncSession):
        """Initialize menu service with database session."""
        self.db = db
    
    async def get_menu(self) -> list[MenuCategory]:
        """
        Get all menu categories with their available items.
        
        Returns:
            List of MenuCategory objects with their items loaded
        """
        result = await self.db.execute(
            select(MenuCategory)
            .options(selectinload(MenuCategory.items))
            .order_by(MenuCategory.order.asc())
        )
        categories = list(result.scalars().all())
        
        # Filter to only include available items
        for category in categories:
            category.items = [item for item in category.items if item.is_available]
        
        return categories
    
    async def get_menu_item(self, item_id: int) -> Optional[MenuItem]:
        """
        Get a specific menu item by ID.
        
        Args:
            item_id: Menu item ID
            
        Returns:
            MenuItem object or None if not found
        """
        result = await self.db.execute(
            select(MenuItem)
            .options(selectinload(MenuItem.category))
            .where(MenuItem.id == item_id)
        )
        return result.scalar_one_or_none()
    

    
    async def update_menu_item(
        self,
        item_id: int,
        name: Optional[str] = None,
        price: Optional[float] = None,
        category_id: Optional[int] = None,
        description: Optional[str] = None,
        image_url: Optional[str] = None,
        is_available: Optional[bool] = None,
    ) -> MenuItem:
        """
        Update an existing menu item.
        
        Args:
            item_id: Menu item ID
            name: Optional new name
            price: Optional new price
            category_id: Optional new category ID
            description: Optional new description
            image_url: Optional new image URL
            is_available: Optional new availability status
            
        Returns:
            Updated MenuItem object
        """
        result = await self.db.execute(
            select(MenuItem).where(MenuItem.id == item_id)
        )
        menu_item = result.scalar_one()
        
        # Update only provided fields
        if name is not None:
            menu_item.name = name
        if price is not None:
            menu_item.price = price
        if category_id is not None:
            menu_item.category_id = category_id
        if description is not None:
            menu_item.description = description
        if image_url is not None:
            menu_item.image_url = image_url
        if is_available is not None:
            menu_item.is_available = is_available
        
        await self.db.flush()
        await self.db.refresh(menu_item)
        
        return menu_item
    
    async def delete_menu_item(self, item_id: int) -> None:
        """
        Soft delete a menu item by setting is_available to False.
        
        Args:
            item_id: Menu item ID
        """
        result = await self.db.execute(
            select(MenuItem).where(MenuItem.id == item_id)
        )
        menu_item = result.scalar_one()
        menu_item.is_available = False
        await self.db.flush()
    
    async def get_menu_by_category(self, category_id: int) -> list[MenuItem]:
        """
        Get all available menu items for a specific category.
        
        Args:
            category_id: Category ID
            
        Returns:
            List of available MenuItem objects in the category
        """
        result = await self.db.execute(
            select(MenuItem)
            .where(
                MenuItem.category_id == category_id,
                MenuItem.is_available == True
            )
            .order_by(MenuItem.name.asc())
        )
        return list(result.scalars().all())
    
    async def get_categories(self) -> list[MenuCategory]:
        """
        Get all menu categories.
        
        Returns:
            List of MenuCategory objects
        """
        result = await self.db.execute(
            select(MenuCategory).order_by(MenuCategory.order.asc())
        )
        return list(result.scalars().all())
    
    async def create_menu_item(
        self,
        name: str,
        price: float,
        category_id: int,
        description: str = None,
        image_url: str = None,
        is_available: bool = True,
    ) -> MenuItem:
        """
        Create a new menu item.
        
        Args:
            name: Menu item name
            price: Menu item price
            category_id: Category ID
            description: Optional description
            image_url: Optional image URL
            is_available: Whether item is available
            
        Returns:
            Created MenuItem object
        """
        menu_item = MenuItem(
            name=name,
            price=price,
            category_id=category_id,
            description=description,
            image_url=image_url,
            is_available=is_available,
        )
        
        self.db.add(menu_item)
        await self.db.flush()
        await self.db.refresh(menu_item)
        
        return menu_item

#GOOGLE TABS
import csv
import json
import os
import httplib2
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import re
from pathlib import Path
from shared.config import settings
from shared.logging_config import get_logger


logger = get_logger(__name__)

def get_service_sacc(sheet_id, sheet_list_name):
    # Берем ключ доступа из credentials.json для доступа к google sheet
    creds_json: str = settings.google_sheets_credentials_file
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    
    # авторизуемся и создаем сервис
    creds_service = ServiceAccountCredentials.from_json_keyfile_name(creds_json, scopes).authorize(httplib2.Http())
    service = build('sheets', 'v4', http=creds_service)
        # получаем данные из таблицы
    try:
        resp = service.spreadsheets().values().batchGet(
            spreadsheetId=sheet_id, 
            ranges=[sheet_list_name]
        ).execute()
        
        values = resp.get('valueRanges', [{}])[0].get('values', [])
        
        # проверяем, что есть данные
        if not values or len(values) < 2:
            return []
    # возвращает dict (key value) всех значений из таблицы google sheet по id
        headers = values[0]
        return [dict(zip(headers, row + [''] * (len(headers) - len(row)))) for row in values[1:]]
        
    except Exception as e:        
        logger.error(f"Ошибка при получении данных из Google Sheets: {e}")

import json
from pathlib import Path

class MenuServiceGoogleTabs:
    def __init__(self):
        self.sheet_id = settings.google_sheets_spreadsheet_id
        self.sheet_list_name = 'menu'
        self.service = get_service_sacc(self.sheet_id, self.sheet_list_name)
        self.menu_path = Path(settings.path_menu)

    def generate_menu_json(self):
        path = Path(self.menu_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        menu: dict = {}

        for row in self.service:
            category = row["category"]
            subcategory = row["subcategory"]

            # category
            menu.setdefault(category, {})
            menu[category].setdefault(subcategory, {})

            current_level = menu[category][subcategory]

            # собираем sub_1, sub_2, sub_3 ...
            sub_levels = sorted(
                k for k in row.keys()
                if k.startswith("sub_") and row[k]
            )

            for level in sub_levels:
                value = row[level]
                current_level.setdefault(value, {})
                current_level = current_level[value]

            # items
            current_level.setdefault("items", []).append({
                "name": row.get("name"),
                "weight": row.get("weight"),
                "price": row.get("price"),
                "description": row.get("description"),
            })

        with open(self.menu_path, "w", encoding="utf-8") as f:
            json.dump(menu, f, ensure_ascii=False, indent=4)
