"""Cached statistics service for providing cached summary data."""
from typing import Dict, Any, Optional
from datetime import datetime

from shared.database import get_async_session
from shared.services.statistics_service import (
    StatisticsService, 
    OverallStatistics,
    UserStatistics,
    LoyaltyStatistics,
    OrderStatistics
)
from shared.services.cache_service import (
    cache_statistics,
    get_cached_statistics,
    invalidate_statistics_cache
)
from shared.logging_config import get_logger

logger = get_logger(__name__)


class CachedStatisticsService:
    """Service for providing cached statistics with automatic refresh."""
    
    @staticmethod
    async def get_overall_statistics(force_refresh: bool = False) -> Optional[OverallStatistics]:
        """
        Get overall statistics from cache or database.
        
        Args:
            force_refresh: If True, bypass cache and fetch fresh data
            
        Returns:
            OverallStatistics object or None if error
        """
        cache_key = "overall"
        
        # Try to get from cache first (unless force refresh)
        if not force_refresh:
            cached_data = await get_cached_statistics(cache_key)
            if cached_data:
                try:
                    return OverallStatistics(
                        users=UserStatistics(**cached_data["users"]),
                        loyalty=LoyaltyStatistics(**cached_data["loyalty"]),
                        orders=OrderStatistics(**cached_data["orders"]),
                        generated_at=datetime.fromisoformat(cached_data["generated_at"])
                    )
                except Exception as e:
                    logger.warning(f"Failed to parse cached statistics: {e}")
                    # Continue to fetch fresh data
        
        # Fetch fresh data from database
        try:
            async with get_async_session() as db:
                stats_service = StatisticsService(db)
                overall_stats = await stats_service.get_overall_statistics()
                
                # Cache the data
                cache_data = {
                    "users": {
                        "total_users": overall_stats.users.total_users,
                        "active_users": overall_stats.users.active_users,
                        "users_with_wallets": overall_stats.users.users_with_wallets,
                        "users_without_wallets": overall_stats.users.users_without_wallets,
                        "new_users_today": overall_stats.users.new_users_today,
                        "new_users_this_week": overall_stats.users.new_users_this_week,
                        "new_users_this_month": overall_stats.users.new_users_this_month,
                    },
                    "loyalty": {
                        "total_points_issued": overall_stats.loyalty.total_points_issued,
                        "total_points_redeemed": overall_stats.loyalty.total_points_redeemed,
                        "active_points_balance": overall_stats.loyalty.active_points_balance,
                        "users_by_level": overall_stats.loyalty.users_by_level,
                        "average_points_per_user": overall_stats.loyalty.average_points_per_user,
                        "points_transactions_today": overall_stats.loyalty.points_transactions_today,
                        "points_transactions_this_week": overall_stats.loyalty.points_transactions_this_week,
                        "points_transactions_this_month": overall_stats.loyalty.points_transactions_this_month,
                    },
                    "orders": {
                        "total_orders": overall_stats.orders.total_orders,
                        "completed_orders": overall_stats.orders.completed_orders,
                        "pending_orders": overall_stats.orders.pending_orders,
                        "cancelled_orders": overall_stats.orders.cancelled_orders,
                        "total_revenue": overall_stats.orders.total_revenue,
                        "average_order_value": overall_stats.orders.average_order_value,
                        "orders_today": overall_stats.orders.orders_today,
                        "orders_this_week": overall_stats.orders.orders_this_week,
                        "orders_this_month": overall_stats.orders.orders_this_month,
                    },
                    "generated_at": overall_stats.generated_at.isoformat()
                }
                
                await cache_statistics(cache_key, cache_data)
                logger.info("Overall statistics cached successfully")
                
                return overall_stats
                
        except Exception as e:
            logger.error(f"Failed to fetch overall statistics: {e}", exc_info=True)
            return None
    
    @staticmethod
    async def get_loyalty_level_distribution(force_refresh: bool = False) -> Optional[Dict[str, Dict[str, Any]]]:
        """
        Get loyalty level distribution from cache or database.
        
        Args:
            force_refresh: If True, bypass cache and fetch fresh data
            
        Returns:
            Dictionary with level distribution or None if error
        """
        cache_key = "loyalty_distribution"
        
        # Try to get from cache first (unless force refresh)
        if not force_refresh:
            cached_data = await get_cached_statistics(cache_key)
            if cached_data:
                return cached_data
        
        # Fetch fresh data from database
        try:
            async with get_async_session() as db:
                stats_service = StatisticsService(db)
                distribution = await stats_service.get_loyalty_level_distribution()
                
                # Cache the data
                await cache_statistics(cache_key, distribution)
                logger.info("Loyalty level distribution cached successfully")
                
                return distribution
                
        except Exception as e:
            logger.error(f"Failed to fetch loyalty level distribution: {e}", exc_info=True)
            return None
    
    @staticmethod
    async def get_top_users_by_points(limit: int = 10, force_refresh: bool = False) -> Optional[list[Dict[str, Any]]]:
        """
        Get top users by points from cache or database.
        
        Args:
            limit: Number of top users to return
            force_refresh: If True, bypass cache and fetch fresh data
            
        Returns:
            List of user data dictionaries or None if error
        """
        cache_key = f"top_users_{limit}"
        
        # Try to get from cache first (unless force refresh)
        if not force_refresh:
            cached_data = await get_cached_statistics(cache_key)
            if cached_data:
                return cached_data
        
        # Fetch fresh data from database
        try:
            async with get_async_session() as db:
                stats_service = StatisticsService(db)
                top_users = await stats_service.get_top_users_by_points(limit=limit)
                
                # Cache the data
                await cache_statistics(cache_key, top_users)
                logger.info(f"Top {limit} users cached successfully")
                
                return top_users
                
        except Exception as e:
            logger.error(f"Failed to fetch top users: {e}", exc_info=True)
            return None
    
    @staticmethod
    async def get_wallet_connection_stats(force_refresh: bool = False) -> Optional[Dict[str, Any]]:
        """
        Get wallet connection statistics from cache or database.
        
        Args:
            force_refresh: If True, bypass cache and fetch fresh data
            
        Returns:
            Dictionary with wallet statistics or None if error
        """
        cache_key = "wallet_stats"
        
        # Try to get from cache first (unless force refresh)
        if not force_refresh:
            cached_data = await get_cached_statistics(cache_key)
            if cached_data:
                return cached_data
        
        # Fetch fresh data from database
        try:
            async with get_async_session() as db:
                stats_service = StatisticsService(db)
                wallet_stats = await stats_service.get_wallet_connection_stats()
                
                # Cache the data
                await cache_statistics(cache_key, wallet_stats)
                logger.info("Wallet connection stats cached successfully")
                
                return wallet_stats
                
        except Exception as e:
            logger.error(f"Failed to fetch wallet connection stats: {e}", exc_info=True)
            return None
    
    @staticmethod
    async def refresh_all_statistics() -> Dict[str, bool]:
        """
        Refresh all cached statistics.
        
        Returns:
            Dictionary with refresh status for each statistic type
        """
        results = {}
        
        # Refresh overall statistics
        overall_stats = await CachedStatisticsService.get_overall_statistics(force_refresh=True)
        results["overall"] = overall_stats is not None
        
        # Refresh loyalty level distribution
        distribution = await CachedStatisticsService.get_loyalty_level_distribution(force_refresh=True)
        results["loyalty_distribution"] = distribution is not None
        
        # Refresh top users
        top_users = await CachedStatisticsService.get_top_users_by_points(force_refresh=True)
        results["top_users_10"] = top_users is not None
        
        # Refresh wallet stats
        wallet_stats = await CachedStatisticsService.get_wallet_connection_stats(force_refresh=True)
        results["wallet_stats"] = wallet_stats is not None
        
        logger.info(f"Statistics refresh completed: {results}")
        return results
    
    @staticmethod
    async def invalidate_cache(stats_type: Optional[str] = None) -> None:
        """
        Invalidate statistics cache.
        
        Args:
            stats_type: Specific statistics type to invalidate, or None for all
        """
        await invalidate_statistics_cache(stats_type)
        logger.info(f"Statistics cache invalidated: {stats_type or 'all'}")
    
    @staticmethod
    async def get_cache_status() -> Dict[str, Any]:
        """
        Get cache status information.
        
        Returns:
            Dictionary with cache information
        """
        from shared.services.cache_service import get_statistics_cache_info
        
        cache_info = await get_statistics_cache_info()
        
        return {
            "cached_statistics": cache_info,
            "total_cached": len(cache_info),
            "cache_ttl_minutes": 30
        }