import csv
from pathlib import Path
from fastapi import APIRouter

router = APIRouter(prefix="/api/menu", tags=["menu"])

MENU_PATH = Path("webapp/data/menu.csv")
@router.get("")
async def get_menu():
    menu = {}
    with open(MENU_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            menu.setdefault(row["category"], {}) \
                .setdefault(row["subcategory"], []) \
                .append({
                    "name": row["name"],
                    "price": row["price"]
                })
    return menu
