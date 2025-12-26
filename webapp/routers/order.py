"""Order API endpoints."""
import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import get_db
from shared.services.user_service import UserService
from shared.services.order_service import OrderService, OrderItemCreate
from webapp.middleware.auth import get_current_telegram_user
from webapp.schemas import OrderCreateRequest, OrderResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/order", tags=["order"])


@router.post("", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreateRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    telegram_user: dict = Depends(get_current_telegram_user)
):
    """
    Create a new order and process rewards.
    
    Creates an order, awards loyalty points, and processes referral rewards.
    Validates: Requirements 3.1
    """
    try:
        user_service = UserService(db)
        order_service = OrderService(db)
        
        # Get user by telegram_id
        user = await user_service.get_user_by_telegram_id(telegram_user['telegram_id'])
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Validate order data
        if not order_data.items:
            raise HTTPException(status_code=400, detail="Order must contain at least one item")
        
        if order_data.total_amount <= 0:
            raise HTTPException(status_code=400, detail="Order amount must be greater than zero")
        
        # Convert items to OrderItemCreate objects
        order_items = []
        for item_data in order_data.items:
            if not all(key in item_data for key in ['menu_item_id', 'quantity', 'price']):
                raise HTTPException(
                    status_code=400, 
                    detail="Each item must have menu_item_id, quantity, and price"
                )
            
            order_items.append(
                OrderItemCreate(
                    menu_item_id=item_data['menu_item_id'],
                    quantity=item_data['quantity'],
                    price=item_data['price']
                )
            )
        
        # Create order
        order = await order_service.create_order(
            user_id=user.id,
            items=order_items,
            total_amount=order_data.total_amount
        )
        
        # Process rewards (loyalty points and referral rewards)
        await order_service.process_order_rewards(order.id)
        
        # Commit transaction
        await db.commit()
        
        # Refresh order to get updated data
        await db.refresh(order)
        
        # Get order with all related data for response
        complete_order = await order_service.get_order_by_id(order.id)
        
        return OrderResponse.model_validate(complete_order)
        
    except HTTPException:
        await db.rollback()
        raise
    except ValueError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating order: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/history", response_model=list[OrderResponse])
async def get_order_history(
    request: Request,
    db: AsyncSession = Depends(get_db),
    telegram_user: dict = Depends(get_current_telegram_user)
):
    """
    Get user's order history.
    
    Returns all orders for the authenticated user, ordered by date (newest first).
    Validates: Requirements 7.2
    """
    try:
        user_service = UserService(db)
        order_service = OrderService(db)
        
        # Get user by telegram_id
        user = await user_service.get_user_by_telegram_id(telegram_user['telegram_id'])
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get user's orders
        orders = await order_service.get_user_orders(user.id)
        
        return [OrderResponse.model_validate(order) for order in orders]
        
    except Exception as e:
        logger.error(f"Error getting order history: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")