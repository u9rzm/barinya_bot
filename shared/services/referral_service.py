"""Referral service for managing referral system."""
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from shared.models import User, PointsTransaction
from shared.config import settings


class ReferralStats:
    """Referral statistics data class."""
    
    def __init__(
        self,
        total_referrals: int,
        total_earned: float,
        referrals: list[dict],
    ):
        """Initialize referral stats."""
        self.total_referrals = total_referrals
        self.total_earned = total_earned
        self.referrals = referrals


class ReferralService:
    """Service for managing referral system."""
    
    def __init__(self, db: AsyncSession):
        """Initialize referral service with database session."""
        self.db = db
    
    async def generate_referral_code(self, user_id: int) -> str:
        """
        Generate or retrieve referral code for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            User's referral code
        """
        # Get user
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one()
        
        # Return existing referral code
        return user.referral_code
    
    async def get_referral_link(self, user_id: int) -> str:
        """
        Get referral link for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Telegram bot referral link with user's referral code
        """
        # Get user's referral code
        referral_code = await self.generate_referral_code(user_id)
        
        # Get bot username from token (format: bot_id:token)
        bot_token = settings.telegram_bot_token
        bot_id = bot_token.split(':')[0]
        
        # Format: https://t.me/bot_username?start=REFERRAL_CODE
        # For now, we'll use a generic format since we don't have bot username
        # In production, this should be configured or fetched from Telegram API
        return f"https://t.me/ghsfgjfsfhdfsqef_bot?start={referral_code}"
    
    async def register_referral(
        self,
        referee_id: int,
        referral_code: str,
    ) -> None:
        """
        Register a referral relationship between users.
        Validates that user is not using their own referral code.
        
        Args:
            referee_id: ID of the user being referred
            referral_code: Referral code used for registration
            
        Raises:
            ValueError: If user tries to use their own referral code
            ValueError: If referral code is invalid
        """
        # Get referee user
        result = await self.db.execute(
            select(User).where(User.id == referee_id)
        )
        referee = result.scalar_one()
        
        # Check if user is trying to use their own code
        if referee.referral_code == referral_code:
            raise ValueError("Cannot use your own referral code")
        
        # Find referrer by referral code
        result = await self.db.execute(
            select(User).where(User.referral_code == referral_code)
        )
        referrer = result.scalar_one_or_none()
        
        if referrer is None:
            raise ValueError("Invalid referral code")
        
        # Set referrer relationship
        referee.referrer_id = referrer.id
        await self.db.flush()
    
    async def process_referral_reward(
        self,
        order_id: int,
        referee_id: int,
        order_amount: float,
    ) -> None:
        """
        Process referral reward for an order.
        Awards 1% of order amount to referrer as loyalty points.
        
        Args:
            order_id: Order ID
            referee_id: ID of the user who made the order (referee)
            order_amount: Total amount of the order
        """
        # Get referee user with referrer relationship
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.referrer))
            .where(User.id == referee_id)
        )
        referee = result.scalar_one()
        
        # Check if user has a referrer
        if referee.referrer_id is None:
            return
        
        # Calculate 1% reward
        reward_amount = order_amount * 0.01
        
        # Get referrer
        result = await self.db.execute(
            select(User).where(User.id == referee.referrer_id)
        )
        referrer = result.scalar_one()
        
        # Add points to referrer
        referrer.loyalty_points += reward_amount
        
        # Create transaction record
        transaction = PointsTransaction(
            user_id=referrer.id,
            amount=reward_amount,
            reason=f"Referral reward from order #{order_id}",
            order_id=order_id,
        )
        self.db.add(transaction)
        await self.db.flush()
    
    async def get_referral_stats(self, user_id: int) -> ReferralStats:
        """
        Get referral statistics for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            ReferralStats object with total referrals, total earned, and list of referrals
        """
        # Get all users referred by this user
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.loyalty_level))
            .where(User.referrer_id == user_id)
        )
        referees = list(result.scalars().all())
        
        # Calculate total earned from referrals
        # Get all transactions for this user with reason containing "Referral reward"
        result = await self.db.execute(
            select(func.sum(PointsTransaction.amount))
            .where(
                PointsTransaction.user_id == user_id,
                PointsTransaction.reason.like("Referral reward%")
            )
        )
        total_earned = result.scalar() or 0.0
        
        # Build referral info list
        referrals = []
        for referee in referees:
            # Get earned from this specific referee
            # We need to join with Order to filter by referee's orders
            from shared.models import Order
            result = await self.db.execute(
                select(func.sum(PointsTransaction.amount))
                .join(Order, PointsTransaction.order_id == Order.id)
                .where(
                    PointsTransaction.user_id == user_id,
                    PointsTransaction.reason.like("Referral reward%"),
                    Order.user_id == referee.id
                )
            )
            earned_from_user = result.scalar() or 0.0
            
            referrals.append({
                "user": referee,
                "earned_from_user": earned_from_user,
            })
        
        return ReferralStats(
            total_referrals=len(referees),
            total_earned=total_earned,
            referrals=referrals,
        )
