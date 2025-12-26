"""User service for managing user operations."""
import secrets
import string
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from shared.models import User, LoyaltyLevel
from shared.logging_config import get_logger, log_transaction
from shared.error_handlers import (
    DatabaseError, 
    NotFoundError, 
    ValidationError,
    retry_database_operation
)

logger = get_logger(__name__)


class UserService:
    """Service for managing users."""
    
    def __init__(self, db: AsyncSession):
        """Initialize user service with database session."""
        self.db = db
    
    async def create_user(
        self,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        referrer_id: Optional[int] = None,
    ) -> User:
        """
        Create a new user with optional referrer.
        
        Args:
            telegram_id: Telegram user ID
            username: Telegram username
            first_name: User's first name
            last_name: User's last name
            referrer_id: ID of the user who referred this user
            
        Returns:
            Created User object
            
        Raises:
            ValidationError: If user already exists or referrer is invalid
            DatabaseError: If database operation fails
        """
        try:
            # Check if user already exists
            existing_user = await self.get_user_by_telegram_id(telegram_id)
            if existing_user:
                raise ValidationError(
                    f"User with telegram_id {telegram_id} already exists",
                    {"telegram_id": telegram_id}
                )
            
            # Validate referrer if provided
            if referrer_id:
                referrer = await self.get_user_by_id(referrer_id)
                if not referrer:
                    raise ValidationError(
                        f"Referrer with ID {referrer_id} not found",
                        {"referrer_id": referrer_id}
                    )
                
                # Prevent self-referral
                if referrer.telegram_id == telegram_id:
                    raise ValidationError(
                        "Users cannot refer themselves",
                        {"telegram_id": telegram_id, "referrer_id": referrer_id}
                    )
            
            async def _create_user_operation():
                # Get the default loyalty level (lowest threshold)
                result = await self.db.execute(
                    select(LoyaltyLevel).order_by(LoyaltyLevel.threshold.asc()).limit(1)
                )
                default_level = result.scalar_one_or_none()
                if not default_level:
                    raise DatabaseError("No loyalty levels found in database")
                
                # Generate unique referral code
                referral_code = await self._generate_unique_referral_code()
                
                # Create user
                user = User(
                    telegram_id=telegram_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    referrer_id=referrer_id,
                    referral_code=referral_code,
                    loyalty_level_id=default_level.id,
                    is_active=True,
                    loyalty_points=0.0,
                    total_spent=0.0,
                )
                
                self.db.add(user)
                await self.db.flush()
                await self.db.refresh(user)
                
                return user
            
            user = await retry_database_operation(_create_user_operation)
            
            # Log user creation
            logger.info(f"Created new user: telegram_id={telegram_id}, username={username}")
            if referrer_id:
                logger.info(f"User {telegram_id} referred by user {referrer_id}")
            
            return user
            
        except (ValidationError, DatabaseError):
            raise
        except IntegrityError as e:
            logger.error(f"Integrity error creating user {telegram_id}: {e}")
            raise ValidationError("User creation failed due to data constraint violation")
        except SQLAlchemyError as e:
            logger.error(f"Database error creating user {telegram_id}: {e}")
            raise DatabaseError("Failed to create user", e)
        except Exception as e:
            logger.error(f"Unexpected error creating user {telegram_id}: {e}")
            raise DatabaseError("Unexpected error during user creation", e)
    
    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """
        Get user by Telegram ID.
        
        Args:
            telegram_id: Telegram user ID
            
        Returns:
            User object or None if not found
        """
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.loyalty_level))
            .where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_referral_code(self, referral_code: str) -> Optional[User]:
        """
        Get user by referral code.
        
        Args:
            referral_code: Referral code
            
        Returns:
            User object or None if not found
        """
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.loyalty_level))
            .where(User.referral_code == referral_code)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username.
        
        Args:
            username: Telegram username
            
        Returns:
            User object or None if not found
        """
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.loyalty_level))
            .where(User.username == username)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User object or None if not found
        """
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.loyalty_level))
            .where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def update_user_status(self, user_id: int, is_active: bool) -> None:
        """
        Update user's active status.
        
        Args:
            user_id: User ID
            is_active: New active status
            
        Raises:
            NotFoundError: If user not found
            DatabaseError: If database operation fails
        """
        try:
            async def _update_status_operation():
                result = await self.db.execute(
                    select(User).where(User.id == user_id)
                )
                user = result.scalar_one_or_none()
                if not user:
                    raise NotFoundError("User", user_id)
                
                old_status = user.is_active
                user.is_active = is_active
                await self.db.flush()
                
                return old_status
            
            old_status = await retry_database_operation(_update_status_operation)
            
            # Log status change
            logger.info(f"Updated user {user_id} status: {old_status} -> {is_active}")
            
        except (NotFoundError, DatabaseError):
            raise
        except SQLAlchemyError as e:
            logger.error(f"Database error updating user {user_id} status: {e}")
            raise DatabaseError("Failed to update user status", e)
        except Exception as e:
            logger.error(f"Unexpected error updating user {user_id} status: {e}")
            raise DatabaseError("Unexpected error during status update", e)
    
    async def get_user_referrals(self, user_id: int) -> list[User]:
        """
        Get all users referred by the given user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of referred users
        """
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.loyalty_level))
            .where(User.referrer_id == user_id)
        )
        return list(result.scalars().all())
    
    async def set_user_level(self, user_id: int, level_id: int) -> None:
        """
        Set user's loyalty level manually.
        
        Args:
            user_id: User ID
            level_id: Loyalty level ID to assign
            
        Raises:
            NotFoundError: If user or level not found
            DatabaseError: If database operation fails
        """
        try:
            async def _set_level_operation():
                # Verify user exists
                user_result = await self.db.execute(
                    select(User).where(User.id == user_id)
                )
                user = user_result.scalar_one_or_none()
                if not user:
                    raise NotFoundError("User", user_id)
                
                # Verify level exists
                level_result = await self.db.execute(
                    select(LoyaltyLevel).where(LoyaltyLevel.id == level_id)
                )
                level = level_result.scalar_one_or_none()
                if not level:
                    raise NotFoundError("LoyaltyLevel", level_id)
                
                old_level_id = user.loyalty_level_id
                user.loyalty_level_id = level_id
                await self.db.flush()
                
                return old_level_id, level.name
            
            old_level_id, level_name = await retry_database_operation(_set_level_operation)
            
            # Log level change
            logger.info(f"Manually set user {user_id} level: {old_level_id} -> {level_id} ({level_name})")
            
        except (NotFoundError, DatabaseError):
            raise
        except SQLAlchemyError as e:
            logger.error(f"Database error setting user {user_id} level: {e}")
            raise DatabaseError("Failed to set user level", e)
        except Exception as e:
            logger.error(f"Unexpected error setting user {user_id} level: {e}")
            raise DatabaseError("Unexpected error during level assignment", e)
    
    async def _generate_unique_referral_code(self) -> str:
        """
        Generate a unique referral code.
        
        Returns:
            Unique referral code string
        """
        while True:
            # Generate 8-character alphanumeric code
            code = ''.join(
                secrets.choice(string.ascii_uppercase + string.digits)
                for _ in range(8)
            )
            
            # Check if code already exists
            result = await self.db.execute(
                select(User).where(User.referral_code == code)
            )
            if result.scalar_one_or_none() is None:
                return code
