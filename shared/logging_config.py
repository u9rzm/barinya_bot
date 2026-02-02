"""Centralized logging configuration for the application."""
import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Optional
from shared.config import settings

class LoggerSetup:
    """Centralized logger setup and configuration."""
    
    def __init__(self):
        """Initialize logger setup."""
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)        
        
        # Define log levels
        self.log_levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }
    
    def setup_logging(self) -> None:
        """Setup comprehensive logging configuration."""
        # Get log level from settings
        log_level = self.log_levels.get(settings.log_level.upper())
        print(f"log_level: {log_level}")
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        simple_formatter = logging.Formatter(
            fmt='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(simple_formatter)
        root_logger.addHandler(console_handler)
        
        # Main application log file with rotation
        app_handler = logging.handlers.RotatingFileHandler(
            filename=self.log_dir / 'app.log',
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        app_handler.setLevel(log_level)
        app_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(app_handler)
        
        # Error log file (only errors and critical)
        error_handler = logging.handlers.RotatingFileHandler(
            filename=self.log_dir / "errors.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=10,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(error_handler)
        
        # Setup specific loggers
        self._setup_specific_loggers(detailed_formatter)
        
        # Log startup message
        logger = logging.getLogger(__name__)
        logger.info(f"Logging system initialized with level: {settings.log_level}")
        logger.info(f"Log files location: {self.log_dir.absolute()}")
    
    def _setup_specific_loggers(self, formatter: logging.Formatter) -> None:
        """Setup specific loggers for different components."""
        
        # Transaction logger for loyalty points and financial operations
        transaction_logger = logging.getLogger("transactions")
        transaction_handler = logging.handlers.RotatingFileHandler(
            filename=self.log_dir / "transactions.log",
            maxBytes=50 * 1024 * 1024,  # 50MB
            backupCount=20,
            encoding='utf-8'
        )
        transaction_handler.setLevel(logging.INFO)
        transaction_handler.setFormatter(formatter)
        transaction_logger.addHandler(transaction_handler)
        transaction_logger.setLevel(logging.INFO)
        transaction_logger.propagate = False  # Don't propagate to root logger
        
        # Admin actions logger
        admin_logger = logging.getLogger("admin_actions")
        admin_handler = logging.handlers.RotatingFileHandler(
            filename=self.log_dir / "admin_actions.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=10,
            encoding='utf-8'
        )
        admin_handler.setLevel(logging.INFO)
        admin_handler.setFormatter(formatter)
        admin_logger.addHandler(admin_handler)
        admin_logger.setLevel(logging.INFO)
        admin_logger.propagate = False
        
        # Security logger for authentication and authorization events
        security_logger = logging.getLogger("security")
        security_handler = logging.handlers.RotatingFileHandler(
            filename=self.log_dir / "security.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=10,
            encoding='utf-8'
        )
        security_handler.setLevel(logging.WARNING)
        security_handler.setFormatter(formatter)
        security_logger.addHandler(security_handler)
        security_logger.setLevel(logging.WARNING)
        security_logger.propagate = False
        
        # Bot interactions logger
        bot_logger = logging.getLogger("bot_interactions")
        bot_handler = logging.handlers.RotatingFileHandler(
            filename=self.log_dir / "bot_interactions.log",
            maxBytes=20 * 1024 * 1024,  # 20MB
            backupCount=10,
            encoding='utf-8'
        )
        bot_handler.setLevel(logging.INFO)
        bot_handler.setFormatter(formatter)
        bot_logger.addHandler(bot_handler)
        bot_logger.setLevel(logging.INFO)
        bot_logger.propagate = False
        
        # Notification logger
        notification_logger = logging.getLogger("notifications")
        notification_handler = logging.handlers.RotatingFileHandler(
            filename=self.log_dir / "notifications.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        notification_handler.setLevel(logging.INFO)
        notification_handler.setFormatter(formatter)
        notification_logger.addHandler(notification_handler)
        notification_logger.setLevel(logging.INFO)
        notification_logger.propagate = False


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def get_transaction_logger() -> logging.Logger:
    """Get the transaction logger for financial operations."""
    return logging.getLogger("transactions")


def get_admin_logger() -> logging.Logger:
    """Get the admin actions logger."""
    return logging.getLogger("admin_actions")


def get_security_logger() -> logging.Logger:
    """Get the security logger for auth events."""
    return logging.getLogger("security")


def get_bot_logger() -> logging.Logger:
    """Get the bot interactions logger."""
    return logging.getLogger("bot_interactions")


def get_notification_logger() -> logging.Logger:
    """Get the notification logger."""
    return logging.getLogger("notifications")


# Global logger setup instance
logger_setup = LoggerSetup()


def setup_logging() -> None:
    """Setup logging configuration - call this once at application startup."""
    logger_setup.setup_logging()


# Convenience function for logging transactions
def log_transaction(
    user_id: int,
    action: str,
    amount: float,
    reason: str,
    order_id: Optional[int] = None,
    referrer_id: Optional[int] = None,
    **kwargs
) -> None:
    """
    Log a transaction with structured data.
    
    Args:
        user_id: User ID involved in transaction
        action: Type of action (add_points, deduct_points, referral_reward, etc.)
        amount: Amount of points/money involved
        reason: Reason for the transaction
        order_id: Related order ID if applicable
        referrer_id: Referrer ID for referral transactions
        **kwargs: Additional metadata
    """
    transaction_logger = get_transaction_logger()
    
    log_data = {
        "user_id": user_id,
        "action": action,
        "amount": amount,
        "reason": reason,
    }
    
    if order_id:
        log_data["order_id"] = order_id
    if referrer_id:
        log_data["referrer_id"] = referrer_id
    
    # Add any additional metadata
    log_data.update(kwargs)
    
    # Create structured log message
    log_message = " | ".join([f"{k}={v}" for k, v in log_data.items()])
    transaction_logger.info(f"TRANSACTION: {log_message}")


def log_admin_action(
    admin_id: int,
    action: str,
    target_type: str,
    target_id: Optional[int] = None,
    details: Optional[str] = None,
    **kwargs
) -> None:
    """
    Log an admin action with structured data.
    
    Args:
        admin_id: Telegram ID of the admin
        action: Action performed (create_promo, set_level, etc.)
        target_type: Type of target (user, menu_item, promotion, etc.)
        target_id: ID of the target if applicable
        details: Additional details about the action
        **kwargs: Additional metadata
    """
    admin_logger = get_admin_logger()
    
    log_data = {
        "admin_id": admin_id,
        "action": action,
        "target_type": target_type,
    }
    
    if target_id:
        log_data["target_id"] = target_id
    if details:
        log_data["details"] = details
    
    # Add any additional metadata
    log_data.update(kwargs)
    
    # Create structured log message
    log_message = " | ".join([f"{k}={v}" for k, v in log_data.items()])
    admin_logger.info(f"ADMIN_ACTION: {log_message}")


def log_security_event(
    event_type: str,
    telegram_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    details: Optional[str] = None,
    **kwargs
) -> None:
    """
    Log a security event.
    
    Args:
        event_type: Type of security event (auth_failure, invalid_token, etc.)
        telegram_id: Telegram ID if applicable
        ip_address: IP address if applicable
        details: Additional details
        **kwargs: Additional metadata
    """
    security_logger = get_security_logger()
    
    log_data = {
        "event_type": event_type,
    }
    
    if telegram_id:
        log_data["telegram_id"] = telegram_id
    if ip_address:
        log_data["ip_address"] = ip_address
    if details:
        log_data["details"] = details
    
    # Add any additional metadata
    log_data.update(kwargs)
    
    # Create structured log message
    log_message = " | ".join([f"{k}={v}" for k, v in log_data.items()])
    security_logger.warning(f"SECURITY_EVENT: {log_message}")