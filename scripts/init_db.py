"""Initialize database with seed data."""
import asyncio
import logging

from shared.database import AsyncSessionLocal, init_db
from shared.models import LoyaltyLevel, MenuCategory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_seed_data():
    """Create initial seed data for the database."""
    async with AsyncSessionLocal() as session:
        try:
            # Create default loyalty levels
            levels = [
                LoyaltyLevel(
                    name="Bronze",
                    threshold=0.0,
                    points_rate=5.0,
                    order=1
                ),
                LoyaltyLevel(
                    name="Silver",
                    threshold=1000.0,
                    points_rate=7.0,
                    order=2
                ),
                LoyaltyLevel(
                    name="Gold",
                    threshold=5000.0,
                    points_rate=10.0,
                    order=3
                ),
                LoyaltyLevel(
                    name="Platinum",
                    threshold=10000.0,
                    points_rate=15.0,
                    order=4
                ),
            ]
            
            session.add_all(levels)
            logger.info(f"Created {len(levels)} loyalty levels")
            
            # Create default menu categories
            categories = [
                MenuCategory(name="Напитки", order=1),
                MenuCategory(name="Коктейли", order=2),
                MenuCategory(name="Закуски", order=3),
                MenuCategory(name="Горячие блюда", order=4),
                MenuCategory(name="Десерты", order=5),
            ]
            
            session.add_all(categories)
            logger.info(f"Created {len(categories)} menu categories")
            
            await session.commit()
            logger.info("Seed data created successfully")
            
        except Exception as e:
            logger.error(f"Error creating seed data: {e}")
            await session.rollback()
            raise


async def main():
    """Main function to initialize database."""
    logger.info("Initializing database...")
    
    # Create tables
    await init_db()
    logger.info("Database tables created")
    
    # Create seed data
    await create_seed_data()
    logger.info("Database initialization complete")


if __name__ == "__main__":
    asyncio.run(main())