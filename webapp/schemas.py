"""Pydantic schemas for API responses."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class LoyaltyLevelResponse(BaseModel):
    """Loyalty level response schema."""
    id: int
    name: str
    threshold: float
    points_rate: float
    order: int
    
    class Config:
        from_attributes = True


class UserProfileResponse(BaseModel):
    """User profile response schema."""
    id: int
    telegram_id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    loyalty_points: float
    total_spent: float
    loyalty_level: LoyaltyLevelResponse
    referral_code: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserStatsResponse(BaseModel):
    """User statistics response schema."""
    loyalty_points: float
    total_spent: float
    loyalty_level: LoyaltyLevelResponse
    total_referrals: int
    created_at: datetime
    next_level: Optional[LoyaltyLevelResponse] = None
    progress_to_next_level: Optional[float] = None


class PointsTransactionResponse(BaseModel):
    """Points transaction response schema."""
    id: int
    amount: float
    reason: str
    order_id: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ReferralInfoResponse(BaseModel):
    """Referral info response schema."""
    user: UserProfileResponse
    earned_from_user: float


class ReferralStatsResponse(BaseModel):
    """Referral statistics response schema."""
    total_referrals: int
    total_earned: float
    referrals: list[ReferralInfoResponse]


class MenuCategoryResponse(BaseModel):
    """Menu category response schema."""
    id: int
    name: str
    order: int
    
    class Config:
        from_attributes = True


class MenuItemResponse(BaseModel):
    """Menu item response schema."""
    id: int
    name: str
    description: Optional[str]
    price: float
    image_url: Optional[str]
    category_id: int
    is_available: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MenuCategoryWithItemsResponse(BaseModel):
    """Menu category with items response schema."""
    id: int
    name: str
    order: int
    items: list[MenuItemResponse]
    
    class Config:
        from_attributes = True


class OrderItemResponse(BaseModel):
    """Order item response schema."""
    id: int
    menu_item_id: int
    quantity: int
    price: float
    menu_item: MenuItemResponse
    
    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    """Order response schema."""
    id: int
    user_id: int
    total_amount: float
    status: str
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemResponse]
    
    class Config:
        from_attributes = True



class OrderCreateRequest(BaseModel):
    """Order creation request schema."""
    items: list[dict]  # [{"menu_item_id": int, "quantity": int, "price": float}]
    total_amount: float