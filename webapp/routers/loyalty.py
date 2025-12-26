"""Loyalty API endpoints."""
import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import get_db
from shared.services.user_service import UserService
from shared.services.loyalty_service import LoyaltyService
from webapp.middleware.auth import get_current_telegram_user
from webapp.schemas import PointsTransactionResponse, LoyaltyLevelResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/loyalty", tags=["loyalty"])


@router.get("/balance", response_model=dict)
async def get_loyalty_balance(
    request: Request,
    db: AsyncSession = Depends(get_db),
    telegram_user: dict = Depends(get_current_telegram_user)
):
    """
    Get user's current loyalty points balance.
    
    Returns the current loyalty points balance for the authenticated user.
    Validates: Requirements 3.4
    """
    try:
        user_service = UserService(db)
        loyalty_service = LoyaltyService(db)
        
        # Get user by telegram_id
        user = await user_service.get_user_by_telegram_id(telegram_user['telegram_id'])
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get current balance
        balance = await loyalty_service.get_points_balance(user.id)
        logger.info(f"User {user.id} balance: {balance}")
        return {
            "balance": balance,
            "user_id": user.id
        }
        logger.info(f"User {user.id} balance: {balance}")
        
    except Exception as e:
        logger.error(f"Error getting loyalty balance: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/history", response_model=list[PointsTransactionResponse])
async def get_loyalty_history(
    request: Request,
    db: AsyncSession = Depends(get_db),
    telegram_user: dict = Depends(get_current_telegram_user)
):
    """
    Get user's loyalty points transaction history.
    
    Returns all points transactions for the authenticated user, ordered by date (newest first).
    Validates: Requirements 3.5
    """
    try:
        user_service = UserService(db)
        loyalty_service = LoyaltyService(db)
        
        # Get user by telegram_id
        user = await user_service.get_user_by_telegram_id(telegram_user['telegram_id'])
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get transaction history
        transactions = await loyalty_service.get_points_history(user.id)
        
        return [PointsTransactionResponse.model_validate(t) for t in transactions]
        
    except Exception as e:
        logger.error(f"Error getting loyalty history: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/levels", response_model=list[LoyaltyLevelResponse])
async def get_loyalty_levels(
    request: Request,
    db: AsyncSession = Depends(get_db),
    telegram_user: dict = Depends(get_current_telegram_user)
):
    """
    Get all available loyalty levels.
    
    Returns all loyalty levels with their thresholds and benefits.
    Validates: Requirements 4.3
    """
    try:
        loyalty_service = LoyaltyService(db)
        
        # Get all levels
        levels = await loyalty_service.get_levels()
        
        return [LoyaltyLevelResponse.model_validate(level) for level in levels]
        
    except Exception as e:
        logger.error(f"Error getting loyalty levels: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")