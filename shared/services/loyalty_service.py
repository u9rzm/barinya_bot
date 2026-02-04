"""Loyalty service for managing loyalty points and levels."""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from shared.models import User, LoyaltyLevel, PointsTransaction


class LoyaltyService:
    """Service for managing loyalty points and levels."""
    
    def __init__(self, db: AsyncSession):
        """Initialize loyalty service with database session."""
        self.db = db
    
    async def add_points(
        self,
        user_id: int,
        amount: float,
        reason: str,
        order_id: Optional[int] = None,
    ) -> None:
        """
        Add loyalty points to user's account and record transaction.
        
        Args:
            user_id: User ID
            amount: Amount of points to add
            reason: Reason for adding points
            order_id: Optional order ID associated with this transaction
        """
        # Get user
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one()
        
        # Update user's points
        user.loyalty_points += amount
        
        # Create transaction record
        transaction = PointsTransaction(
            user_id=user_id,
            amount=amount,
            reason=reason,
            order_id=order_id,
        )
        self.db.add(transaction)
        await self.db.flush()
    
    async def deduct_points(
        self,
        user_id: int,
        amount: float,
        reason: str,
    ) -> None:
        """
        Deduct loyalty points from user's account and record transaction.
        
        Args:
            user_id: User ID
            amount: Amount of points to deduct
            reason: Reason for deducting points
        """
        # Get user
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one()
        
        # Update user's points (negative amount)
        user.loyalty_points -= amount
        
        # Create transaction record with negative amount
        transaction = PointsTransaction(
            user_id=user_id,
            amount=-amount,
            reason=reason,
            order_id=None,
        )
        self.db.add(transaction)
        await self.db.flush()
    
    async def get_points_balance(self, user_id: int) -> float:
        """
        Get user's current loyalty points balance.
        
        Args:
            user_id: User ID
            
        Returns:
            Current points balance
        """
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one()
        return user.loyalty_points
    
    async def get_points_history(self, user_id: int) -> list[PointsTransaction]:
        """
        Get user's points transaction history.
        
        Args:
            user_id: User ID
            
        Returns:
            List of points transactions ordered by date (newest first)
        """
        result = await self.db.execute(
            select(PointsTransaction)
            .where(PointsTransaction.user_id == user_id)
            .order_by(PointsTransaction.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def calculate_level_for_user(self, user_id: int) -> LoyaltyLevel:
        """
        Calculate the appropriate loyalty level for a user based on total spent.
        
        Args:
            user_id: User ID
            
        Returns:
            Appropriate LoyaltyLevel for the user
        """
        # Get user
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one()
        
        # Get all levels ordered by threshold descending
        result = await self.db.execute(
            select(LoyaltyLevel).order_by(LoyaltyLevel.threshold.desc())
        )
        levels = list(result.scalars().all())
        
        # Find the highest level where user's total_spent >= threshold
        for level in levels:
            if user.total_spent >= level.threshold:
                return level
        
        # If no level matches, return the lowest level
        result = await self.db.execute(
            select(LoyaltyLevel).order_by(LoyaltyLevel.threshold.asc()).limit(1)
        )
        return result.scalar_one()
    
    async def update_user_level(self, user_id: int) -> None:
        """
        Update user's loyalty level based on their total spent.
        This method calculates the appropriate level and updates the user.
        Note: Notification sending should be handled by the caller.
        
        Args:
            user_id: User ID
        """
        # Get user with current level
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.loyalty_level))
            .where(User.id == user_id)
        )
        user = result.scalar_one()
        
        # Calculate new level
        new_level = await self.calculate_level_for_user(user_id)
        
        # Update if level changed
        if user.loyalty_level_id != new_level.id:
            user.loyalty_level_id = new_level.id
            await self.db.flush()
    
    async def get_levels(self) -> list[LoyaltyLevel]:
        """
        Get all loyalty levels ordered by threshold.
        
        Returns:
            List of all loyalty levels
        """
        result = await self.db.execute(
            select(LoyaltyLevel).order_by(LoyaltyLevel.threshold.asc())
        )
        return list(result.scalars().all())
    
    async def create_level(
        self,
        name: str,
        threshold: float,
        points_rate: float,
    ) -> LoyaltyLevel:
        """
        Create a new loyalty level.
        
        Args:
            name: Level name
            threshold: Minimum total spent to reach this level
            points_rate: Points earning rate percentage (e.g., 5.0 for 5%)
            
        Returns:
            Created LoyaltyLevel object
        """
        # Get the next order number
        result = await self.db.execute(
            select(LoyaltyLevel).order_by(LoyaltyLevel.order.desc()).limit(1)
        )
        last_level = result.scalar_one_or_none()
        next_order = (last_level.order + 1) if last_level else 1
        
        # Create level
        level = LoyaltyLevel(
            name=name,
            threshold=threshold,
            points_rate=points_rate,
            order=next_order,
        )
        
        self.db.add(level)
        await self.db.flush()
        await self.db.refresh(level)
        
        return level
    
    async def get_level_by_id(self, level_id: int) -> Optional[LoyaltyLevel]:
        """
        Get loyalty level by ID.
        
        Args:
            level_id: Level ID
            
        Returns:
            LoyaltyLevel object or None if not found
        """
        result = await self.db.execute(
            select(LoyaltyLevel).where(LoyaltyLevel.id == level_id)
        )
        return result.scalar_one_or_none()
    
    async def update_level(
        self,
        level_id: int,
        name: Optional[str] = None,
        threshold: Optional[float] = None,
        points_rate: Optional[float] = None,
    ) -> Optional[LoyaltyLevel]:
        """
        Update an existing loyalty level.
        
        Args:
            level_id: Level ID to update
            name: New level name (optional)
            threshold: New threshold (optional)
            points_rate: New points rate (optional)
            
        Returns:
            Updated LoyaltyLevel object or None if not found
        """
        level = await self.get_level_by_id(level_id)
        if not level:
            return None
        
        if name is not None:
            level.name = name
        if threshold is not None:
            level.threshold = threshold
        if points_rate is not None:
            level.points_rate = points_rate
        
        await self.db.flush()
        await self.db.refresh(level)
        
        return level
    
    async def delete_level(self, level_id: int) -> bool:
        """
        Delete a loyalty level.
        Note: This will fail if there are users assigned to this level.
        
        Args:
            level_id: Level ID to delete
            
        Returns:
            True if deleted successfully, False if not found or has users
        """
        level = await self.get_level_by_id(level_id)
        if not level:
            return False
        
        # Check if any users are assigned to this level
        result = await self.db.execute(
            select(User).where(User.loyalty_level_id == level_id).limit(1)
        )
        if result.scalar_one_or_none():
            return False  # Cannot delete level with assigned users
        
        await self.db.delete(level)
        await self.db.flush()
        
        return True
    
    async def reorder_levels(self, level_orders: dict[int, int]) -> None:
        """
        Reorder loyalty levels.
        
        Args:
            level_orders: Dictionary mapping level_id to new order number
        """
        for level_id, new_order in level_orders.items():
            level = await self.get_level_by_id(level_id)
            if level:
                level.order = new_order
        
        await self.db.flush()
