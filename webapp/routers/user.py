"""User API endpoints."""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import get_db
from shared.services.user_service import UserService
from shared.services.loyalty_service import LoyaltyService
from webapp.middleware.auth import get_current_telegram_user
from webapp.schemas import UserProfileResponse, UserStatsResponse, LoyaltyLevelResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/user", tags=["user"])


@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(
    request: Request,
    db: AsyncSession = Depends(get_db),
    telegram_user: dict = Depends(get_current_telegram_user)
):
    """
    Get user profile information.    
    Returns complete user profile including loyalty level and points.
    Validates: Requirements 7.1
    """
    try:
        user_service = UserService(db)
        
        # Get user by telegram_id
        user = await user_service.get_user_by_telegram_id(telegram_user['telegram_id'])
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserProfileResponse.model_validate(user)
        
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/stats", response_model=UserStatsResponse)
async def get_user_stats(
    request: Request,
    db: AsyncSession = Depends(get_db),
    telegram_user: dict = Depends(get_current_telegram_user)
):
    """
    Get aggregated user statistics.
    
    Returns user statistics including loyalty data, referral count, and progress.
    Validates: Requirements 7.1
    """
    try:
        user_service = UserService(db)
        loyalty_service = LoyaltyService(db)
        
        # Get user by telegram_id
        user = await user_service.get_user_by_telegram_id(telegram_user['telegram_id'])
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get referrals count
        referrals = await user_service.get_user_referrals(user.id)
        total_referrals = len(referrals)
        
        # Get all loyalty levels to calculate next level and progress
        all_levels = await loyalty_service.get_levels()
        
        # Find next level
        next_level: Optional[LoyaltyLevelResponse] = None
        progress_to_next_level: Optional[float] = None
        
        # Sort levels by threshold
        sorted_levels = sorted(all_levels, key=lambda x: x.threshold)
        
        # Find the next level after current user's level
        for level in sorted_levels:
            if level.threshold > user.total_spent:
                next_level = LoyaltyLevelResponse.model_validate(level)
                # Calculate progress percentage
                current_threshold = user.loyalty_level.threshold
                next_threshold = level.threshold
                progress = ((user.total_spent - current_threshold) / 
                           (next_threshold - current_threshold)) * 100
                progress_to_next_level = max(0, min(100, progress))
                break
        
        return UserStatsResponse(
            loyalty_points=user.loyalty_points,
            total_spent=user.total_spent,
            loyalty_level=LoyaltyLevelResponse.model_validate(user.loyalty_level),
            total_referrals=total_referrals,
            created_at=user.created_at,
            next_level=next_level,
            progress_to_next_level=progress_to_next_level
        )
        
    except Exception as e:
        logger.error(f"Error getting user stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")