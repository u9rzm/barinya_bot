"""Promotion service for managing promotions and broadcasts."""
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.models import Promotion, User


class PromotionService:
    """Service for managing promotions."""
    
    def __init__(self, db: AsyncSession):
        """Initialize promotion service with database session."""
        self.db = db
    
    async def create_promotion(
        self,
        title: str,
        description: str,
        start_date: datetime,
        end_date: datetime,
        image_url: Optional[str] = None,
    ) -> Promotion:
        """
        Create a new promotion with date validation.
        
        Args:
            title: Promotion title
            description: Promotion description
            start_date: Promotion start date
            end_date: Promotion end date
            image_url: Optional image URL
            
        Returns:
            Created Promotion object
            
        Raises:
            ValueError: If end_date is before start_date
        """
        # Validate dates
        if end_date < start_date:
            raise ValueError("End date must be after start date")
        
        promotion = Promotion(
            title=title,
            description=description,
            start_date=start_date,
            end_date=end_date,
            image_url=image_url,
        )
        
        self.db.add(promotion)
        await self.db.flush()
        await self.db.refresh(promotion)
        
        return promotion
    
    async def get_active_promotions(self) -> list[Promotion]:
        """
        Get all currently active promotions.
        
        Returns:
            List of active Promotion objects
        """
        now = datetime.utcnow()
        result = await self.db.execute(
            select(Promotion)
            .where(
                Promotion.start_date <= now,
                Promotion.end_date >= now
            )
            .order_by(Promotion.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def broadcast_promotion(self, promotion_id: int) -> list[int]:
        """
        Get list of active user telegram IDs for promotion broadcast.
        
        Note: This method returns the list of telegram IDs that should receive
        the promotion. The actual sending of messages should be handled by
        the NotificationService.
        
        Args:
            promotion_id: Promotion ID to broadcast
            
        Returns:
            List of telegram IDs of active users
        """
        # Get all active users
        result = await self.db.execute(
            select(User.telegram_id)
            .where(User.is_active == True)
        )
        telegram_ids = [row[0] for row in result.all()]
        
        return telegram_ids
