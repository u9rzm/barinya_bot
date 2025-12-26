"""Order service for managing orders and rewards."""
from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from shared.models import Order, OrderItem, User, MenuItem, OrderStatus
from shared.services.loyalty_service import LoyaltyService
from shared.services.referral_service import ReferralService


class OrderItemCreate:
    """Data class for creating order items."""
    
    def __init__(self, menu_item_id: int, quantity: int, price: float):
        """Initialize order item creation data."""
        self.menu_item_id = menu_item_id
        self.quantity = quantity
        self.price = price


class OrderService:
    """Service for managing orders."""
    
    def __init__(self, db: AsyncSession):
        """Initialize order service with database session."""
        self.db = db
        self.loyalty_service = LoyaltyService(db)
        self.referral_service = ReferralService(db)
    
    async def create_order(
        self,
        user_id: int,
        items: List[OrderItemCreate],
        total_amount: float,
    ) -> Order:
        """
        Create a new order with validation.
        
        Args:
            user_id: User ID who is placing the order
            items: List of order items
            total_amount: Total amount of the order
            
        Returns:
            Created Order object
            
        Raises:
            ValueError: If total_amount is <= 0
            ValueError: If user doesn't exist
        """
        # Validate order amount (Requirement 9.5)
        if total_amount <= 0:
            raise ValueError("Order amount must be greater than zero")
        
        # Verify user exists
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if user is None:
            raise ValueError("User not found")
        
        # Create order
        order = Order(
            user_id=user_id,
            total_amount=total_amount,
            status=OrderStatus.PENDING.value,
        )
        
        self.db.add(order)
        await self.db.flush()  # Get order ID
        
        # Create order items
        for item_data in items:
            # Verify menu item exists
            result = await self.db.execute(
                select(MenuItem).where(MenuItem.id == item_data.menu_item_id)
            )
            menu_item = result.scalar_one_or_none()
            if menu_item is None:
                raise ValueError(f"Menu item {item_data.menu_item_id} not found")
            
            order_item = OrderItem(
                order_id=order.id,
                menu_item_id=item_data.menu_item_id,
                quantity=item_data.quantity,
                price=item_data.price,
            )
            self.db.add(order_item)
        
        await self.db.flush()
        await self.db.refresh(order)
        
        return order
    
    async def get_order_by_id(self, order_id: int) -> Optional[Order]:
        """
        Get order by ID with all related data.
        
        Args:
            order_id: Order ID
            
        Returns:
            Order object or None if not found
        """
        result = await self.db.execute(
            select(Order)
            .options(
                selectinload(Order.user),
                selectinload(Order.items).selectinload(OrderItem.menu_item)
            )
            .where(Order.id == order_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_orders(self, user_id: int) -> List[Order]:
        """
        Get all orders for a specific user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of user's orders ordered by creation date (newest first)
        """
        result = await self.db.execute(
            select(Order)
            .options(
                selectinload(Order.items).selectinload(OrderItem.menu_item)
            )
            .where(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def process_order_rewards(self, order_id: int) -> None:
        """
        Process loyalty points and referral rewards for a completed order.
        This method handles both loyalty points award and referral rewards.
        Uses database transactions for atomicity.
        
        Args:
            order_id: Order ID to process rewards for
            
        Raises:
            ValueError: If order doesn't exist or is not in PENDING status
        """
        # Get order with user and loyalty level
        result = await self.db.execute(
            select(Order)
            .options(
                selectinload(Order.user).selectinload(User.loyalty_level)
            )
            .where(Order.id == order_id)
        )
        order = result.scalar_one_or_none()
        
        if order is None:
            raise ValueError("Order not found")
        
        if order.status != OrderStatus.PENDING.value:
            raise ValueError("Order is not in pending status")
        
        # Start processing rewards within a transaction
        try:
            # 1. Update user's total spent (Requirement 3.2)
            user = order.user
            user.total_spent += order.total_amount
            
            # 2. Calculate and award loyalty points (Requirements 3.1, 3.7)
            points_rate = user.loyalty_level.points_rate
            points_to_award = order.total_amount * (points_rate / 100.0)
            
            await self.loyalty_service.add_points(
                user_id=user.id,
                amount=points_to_award,
                reason=f"Order #{order.id} completion",
                order_id=order.id,
            )
            
            # 3. Check and update loyalty level (Requirement 3.3)
            await self.loyalty_service.update_user_level(user.id)
            
            # 4. Process referral reward if applicable (Requirement 5.3)
            await self.referral_service.process_referral_reward(
                order_id=order.id,
                referee_id=user.id,
                order_amount=order.total_amount,
            )
            
            # 5. Mark order as completed
            order.status = OrderStatus.COMPLETED.value
            
            # Commit all changes
            await self.db.flush()
            
        except Exception as e:
            # Rollback will happen automatically due to session management
            raise e