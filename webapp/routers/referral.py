"""Referral API endpoints."""
import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import get_db
from shared.services.user_service import UserService
from shared.services.referral_service import ReferralService
from webapp.middleware.auth import get_current_telegram_user
from webapp.schemas import ReferralStatsResponse, ReferralInfoResponse, UserProfileResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/referral", tags=["referral"])


@router.get("/link", response_model=dict)
async def get_referral_link(
    request: Request,
    db: AsyncSession = Depends(get_db),
    telegram_user: dict = Depends(get_current_telegram_user)
):
    """
    Get user's referral link.
    
    Returns the referral link for the authenticated user to share with others.
    Validates: Requirements 5.1
    """
    try:
        user_service = UserService(db)
        referral_service = ReferralService(db)
        
        # Get user by telegram_id
        user = await user_service.get_user_by_telegram_id(telegram_user['telegram_id'])
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get referral link
        referral_link = await referral_service.get_referral_link(user.id)
        referral_code = await referral_service.generate_referral_code(user.id)
        
        return {
            "referral_link": referral_link,
            "referral_code": referral_code,
            "user_id": user.id
        }
        
    except Exception as e:
        logger.error(f"Error getting referral link: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/stats", response_model=ReferralStatsResponse)
async def get_referral_stats(
    request: Request,
    db: AsyncSession = Depends(get_db),
    telegram_user: dict = Depends(get_current_telegram_user)
):
    """
    Get user's referral statistics.
    
    Returns complete referral statistics including total referrals, earned points,
    and detailed information about each referred user.
    Validates: Requirements 5.5, 7.3
    """
    try:
        user_service = UserService(db)
        referral_service = ReferralService(db)
        
        # Get user by telegram_id
        user = await user_service.get_user_by_telegram_id(telegram_user['telegram_id'])
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get referral statistics
        stats = await referral_service.get_referral_stats(user.id)
        
        # Convert to response format
        referrals_response = []
        for referral_info in stats.referrals:
            referrals_response.append(
                ReferralInfoResponse(
                    user=UserProfileResponse.model_validate(referral_info["user"]),
                    earned_from_user=referral_info["earned_from_user"]
                )
            )
        
        return ReferralStatsResponse(
            total_referrals=stats.total_referrals,
            total_earned=stats.total_earned,
            referrals=referrals_response
        )
        
    except Exception as e:
        logger.error(f"Error getting referral stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")