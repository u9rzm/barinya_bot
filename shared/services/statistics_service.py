"""Statistics service for providing summary data about users, wallets, and loyalty program."""
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from dataclasses import dataclass

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from shared.models import User, LoyaltyLevel, PointsTransaction, Order, OrderStatus


@dataclass
class UserStatistics:
    """User statistics data class."""
    total_users: int
    active_users: int
    users_with_wallets: int
    users_without_wallets: int
    new_users_today: int
    new_users_this_week: int
    new_users_this_month: int


@dataclass
class LoyaltyStatistics:
    """Loyalty program statistics data class."""
    total_points_issued: float
    total_points_redeemed: float
    active_points_balance: float
    users_by_level: Dict[str, int]
    average_points_per_user: float
    points_transactions_today: int
    points_transactions_this_week: int
    points_transactions_this_month: int


@dataclass
class OrderStatistics:
    """Order statistics data class."""
    total_orders: int
    completed_orders: int
    pending_orders: int
    cancelled_orders: int
    total_revenue: float
    average_order_value: float
    orders_today: int
    orders_this_week: int
    orders_this_month: int


@dataclass
class OverallStatistics:
    """Overall statistics combining all metrics."""
    users: UserStatistics
    loyalty: LoyaltyStatistics
    orders: OrderStatistics
    generated_at: datetime


class StatisticsService:
    """Service for generating various statistics about the application."""
    
    def __init__(self, db: AsyncSession):
        """Initialize statistics service with database session."""
        self.db = db
    
    async def get_user_statistics(self) -> UserStatistics:
        """
        Get comprehensive user statistics.
        
        Returns:
            UserStatistics object with all user-related metrics
        """
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=now.weekday())
        month_start = today_start.replace(day=1)
        
        # Total users count
        total_users_result = await self.db.execute(
            select(func.count(User.id))
        )
        total_users = total_users_result.scalar()
        
        # Active users count
        active_users_result = await self.db.execute(
            select(func.count(User.id)).where(User.is_active == True)
        )
        active_users = active_users_result.scalar()
        
        # Users with wallets
        users_with_wallets_result = await self.db.execute(
            select(func.count(User.id)).where(
                and_(User.wallet.isnot(None), User.wallet != "")
            )
        )
        users_with_wallets = users_with_wallets_result.scalar()
        
        # Users without wallets
        users_without_wallets = total_users - users_with_wallets
        
        # New users today
        new_users_today_result = await self.db.execute(
            select(func.count(User.id)).where(User.created_at >= today_start)
        )
        new_users_today = new_users_today_result.scalar()
        
        # New users this week
        new_users_week_result = await self.db.execute(
            select(func.count(User.id)).where(User.created_at >= week_start)
        )
        new_users_this_week = new_users_week_result.scalar()
        
        # New users this month
        new_users_month_result = await self.db.execute(
            select(func.count(User.id)).where(User.created_at >= month_start)
        )
        new_users_this_month = new_users_month_result.scalar()
        
        return UserStatistics(
            total_users=total_users,
            active_users=active_users,
            users_with_wallets=users_with_wallets,
            users_without_wallets=users_without_wallets,
            new_users_today=new_users_today,
            new_users_this_week=new_users_this_week,
            new_users_this_month=new_users_this_month,
        )
    
    async def get_loyalty_statistics(self) -> LoyaltyStatistics:
        """
        Get comprehensive loyalty program statistics.
        
        Returns:
            LoyaltyStatistics object with all loyalty-related metrics
        """
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=now.weekday())
        month_start = today_start.replace(day=1)
        
        # Total points issued (positive transactions)
        points_issued_result = await self.db.execute(
            select(func.coalesce(func.sum(PointsTransaction.amount), 0))
            .where(PointsTransaction.amount > 0)
        )
        total_points_issued = float(points_issued_result.scalar())
        
        # Total points redeemed (negative transactions)
        points_redeemed_result = await self.db.execute(
            select(func.coalesce(func.sum(func.abs(PointsTransaction.amount)), 0))
            .where(PointsTransaction.amount < 0)
        )
        total_points_redeemed = float(points_redeemed_result.scalar())
        
        # Active points balance (sum of all user balances)
        active_balance_result = await self.db.execute(
            select(func.coalesce(func.sum(User.loyalty_points), 0))
        )
        active_points_balance = float(active_balance_result.scalar())
        
        # Users by loyalty level
        users_by_level_result = await self.db.execute(
            select(LoyaltyLevel.name, func.count(User.id))
            .join(User, User.loyalty_level_id == LoyaltyLevel.id)
            .group_by(LoyaltyLevel.id, LoyaltyLevel.name)
        )
        users_by_level = {name: count for name, count in users_by_level_result.all()}
        
        # Average points per user
        total_users_result = await self.db.execute(
            select(func.count(User.id))
        )
        total_users = total_users_result.scalar()
        average_points_per_user = active_points_balance / total_users if total_users > 0 else 0.0
        
        # Points transactions today
        transactions_today_result = await self.db.execute(
            select(func.count(PointsTransaction.id))
            .where(PointsTransaction.created_at >= today_start)
        )
        points_transactions_today = transactions_today_result.scalar()
        
        # Points transactions this week
        transactions_week_result = await self.db.execute(
            select(func.count(PointsTransaction.id))
            .where(PointsTransaction.created_at >= week_start)
        )
        points_transactions_this_week = transactions_week_result.scalar()
        
        # Points transactions this month
        transactions_month_result = await self.db.execute(
            select(func.count(PointsTransaction.id))
            .where(PointsTransaction.created_at >= month_start)
        )
        points_transactions_this_month = transactions_month_result.scalar()
        
        return LoyaltyStatistics(
            total_points_issued=total_points_issued,
            total_points_redeemed=total_points_redeemed,
            active_points_balance=active_points_balance,
            users_by_level=users_by_level,
            average_points_per_user=average_points_per_user,
            points_transactions_today=points_transactions_today,
            points_transactions_this_week=points_transactions_this_week,
            points_transactions_this_month=points_transactions_this_month,
        )
    
    async def get_order_statistics(self) -> OrderStatistics:
        """
        Get comprehensive order statistics.
        
        Returns:
            OrderStatistics object with all order-related metrics
        """
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=now.weekday())
        month_start = today_start.replace(day=1)
        
        # Total orders
        total_orders_result = await self.db.execute(
            select(func.count(Order.id))
        )
        total_orders = total_orders_result.scalar()
        
        # Orders by status
        completed_orders_result = await self.db.execute(
            select(func.count(Order.id))
            .where(Order.status == OrderStatus.COMPLETED.value)
        )
        completed_orders = completed_orders_result.scalar()
        
        pending_orders_result = await self.db.execute(
            select(func.count(Order.id))
            .where(Order.status == OrderStatus.PENDING.value)
        )
        pending_orders = pending_orders_result.scalar()
        
        cancelled_orders_result = await self.db.execute(
            select(func.count(Order.id))
            .where(Order.status == OrderStatus.CANCELLED.value)
        )
        cancelled_orders = cancelled_orders_result.scalar()
        
        # Total revenue (completed orders only)
        total_revenue_result = await self.db.execute(
            select(func.coalesce(func.sum(Order.total_amount), 0))
            .where(Order.status == OrderStatus.COMPLETED.value)
        )
        total_revenue = float(total_revenue_result.scalar())
        
        # Average order value
        average_order_value = total_revenue / completed_orders if completed_orders > 0 else 0.0
        
        # Orders today
        orders_today_result = await self.db.execute(
            select(func.count(Order.id))
            .where(Order.created_at >= today_start)
        )
        orders_today = orders_today_result.scalar()
        
        # Orders this week
        orders_week_result = await self.db.execute(
            select(func.count(Order.id))
            .where(Order.created_at >= week_start)
        )
        orders_this_week = orders_week_result.scalar()
        
        # Orders this month
        orders_month_result = await self.db.execute(
            select(func.count(Order.id))
            .where(Order.created_at >= month_start)
        )
        orders_this_month = orders_month_result.scalar()
        
        return OrderStatistics(
            total_orders=total_orders,
            completed_orders=completed_orders,
            pending_orders=pending_orders,
            cancelled_orders=cancelled_orders,
            total_revenue=total_revenue,
            average_order_value=average_order_value,
            orders_today=orders_today,
            orders_this_week=orders_this_week,
            orders_this_month=orders_this_month,
        )
    
    async def get_overall_statistics(self) -> OverallStatistics:
        """
        Get comprehensive statistics combining all metrics.
        
        Returns:
            OverallStatistics object with all application metrics
        """
        user_stats = await self.get_user_statistics()
        loyalty_stats = await self.get_loyalty_statistics()
        order_stats = await self.get_order_statistics()
        
        return OverallStatistics(
            users=user_stats,
            loyalty=loyalty_stats,
            orders=order_stats,
            generated_at=datetime.utcnow(),
        )
    
    async def get_user_growth_trend(self, days: int = 30) -> Dict[str, int]:
        """
        Get user registration trend for the specified number of days.
        
        Args:
            days: Number of days to analyze (default: 30)
            
        Returns:
            Dictionary with date strings as keys and user counts as values
        """
        end_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = end_date - timedelta(days=days)
        
        # Get daily user registrations
        result = await self.db.execute(
            select(
                func.date(User.created_at).label('date'),
                func.count(User.id).label('count')
            )
            .where(User.created_at >= start_date)
            .group_by(func.date(User.created_at))
            .order_by(func.date(User.created_at))
        )
        
        # Convert to dictionary with string dates
        trend_data = {}
        for row in result.all():
            date_str = row.date.strftime('%Y-%m-%d')
            trend_data[date_str] = row.count
        
        # Fill missing dates with 0
        current_date = start_date
        while current_date < end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            if date_str not in trend_data:
                trend_data[date_str] = 0
            current_date += timedelta(days=1)
        
        return trend_data
    
    async def get_loyalty_level_distribution(self) -> Dict[str, Dict[str, Any]]:
        """
        Get detailed distribution of users across loyalty levels.
        
        Returns:
            Dictionary with level names as keys and level details as values
        """
        result = await self.db.execute(
            select(
                LoyaltyLevel.name,
                LoyaltyLevel.threshold,
                LoyaltyLevel.points_rate,
                func.count(User.id).label('user_count'),
                func.coalesce(func.avg(User.loyalty_points), 0).label('avg_points'),
                func.coalesce(func.sum(User.total_spent), 0).label('total_spent')
            )
            .join(User, User.loyalty_level_id == LoyaltyLevel.id)
            .group_by(LoyaltyLevel.id, LoyaltyLevel.name, LoyaltyLevel.threshold, LoyaltyLevel.points_rate)
            .order_by(LoyaltyLevel.threshold)
        )
        
        distribution = {}
        for row in result.all():
            distribution[row.name] = {
                'threshold': row.threshold,
                'points_rate': row.points_rate,
                'user_count': row.user_count,
                'avg_points': float(row.avg_points),
                'total_spent': float(row.total_spent),
            }
        
        return distribution
    
    async def get_top_users_by_points(self, limit: int = 10) -> list[Dict[str, Any]]:
        """
        Get top users by loyalty points balance.
        
        Args:
            limit: Number of top users to return (default: 10)
            
        Returns:
            List of user data dictionaries
        """
        result = await self.db.execute(
            select(
                User.telegram_id,
                User.loyalty_points,
                User.total_spent,
                LoyaltyLevel.name.label('level_name')
            )
            .join(LoyaltyLevel, User.loyalty_level_id == LoyaltyLevel.id)
            .where(User.is_active == True)
            .order_by(User.loyalty_points.desc())
            .limit(limit)
        )
        
        top_users = []
        for row in result.all():
            top_users.append({
                'telegram_id': row.telegram_id,
                'loyalty_points': row.loyalty_points,
                'total_spent': row.total_spent,
                'level_name': row.level_name,
            })
        
        return top_users
    
    async def get_wallet_connection_stats(self) -> Dict[str, Any]:
        """
        Get detailed statistics about wallet connections.
        
        Returns:
            Dictionary with wallet connection statistics
        """
        # Total users
        total_users_result = await self.db.execute(
            select(func.count(User.id))
        )
        total_users = total_users_result.scalar()
        
        # Users with wallets
        users_with_wallets_result = await self.db.execute(
            select(func.count(User.id))
            .where(and_(User.wallet.isnot(None), User.wallet != ""))
        )
        users_with_wallets = users_with_wallets_result.scalar()
        
        # Users without wallets
        users_without_wallets = total_users - users_with_wallets
        
        # Wallet connection rate
        connection_rate = (users_with_wallets / total_users * 100) if total_users > 0 else 0.0
        
        # Recent wallet connections (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_connections_result = await self.db.execute(
            select(func.count(User.id))
            .where(
                and_(
                    User.wallet.isnot(None),
                    User.wallet != "",
                    User.updated_at >= week_ago
                )
            )
        )
        recent_connections = recent_connections_result.scalar()
        
        return {
            'total_users': total_users,
            'users_with_wallets': users_with_wallets,
            'users_without_wallets': users_without_wallets,
            'connection_rate_percent': round(connection_rate, 2),
            'recent_connections_week': recent_connections,
        }