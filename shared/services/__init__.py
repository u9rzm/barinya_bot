"""Services package."""
from shared.services.user_service import UserService
from shared.services.loyalty_service import LoyaltyService
from shared.services.referral_service import ReferralService, ReferralStats
from shared.services.menu_service import MenuService_db, MenuServiceGoogleTabs
from shared.services.promotion_service import PromotionService
from shared.services.order_service import OrderService, OrderItemCreate
from shared.services.notification_service import NotificationService
from shared.services.statistics_service import (
    StatisticsService,
    UserStatistics,
    LoyaltyStatistics,
    OrderStatistics,
    OverallStatistics,
)
from shared.services.cached_statistics_service import CachedStatisticsService
from shared.services.statistics_scheduler import (
    StatisticsScheduler,
    start_statistics_scheduler,
    stop_statistics_scheduler,
    refresh_statistics_now,
    get_scheduler_status,
)



__all__ = [
    "UserService",
    "LoyaltyService",
    "ReferralService",
    "ReferralStats",
    "MenuServiceGoogleTabs",
    "MenuService_db",
    "PromotionService",
    "OrderService",
    "OrderItemCreate",
    "NotificationService",
    "StatisticsService",
    "UserStatistics",
    "LoyaltyStatistics",
    "OrderStatistics",
    "OverallStatistics",
    "CachedStatisticsService",
    "StatisticsScheduler",
    "start_statistics_scheduler",
    "stop_statistics_scheduler",
    "refresh_statistics_now",
    "get_scheduler_status",
]
