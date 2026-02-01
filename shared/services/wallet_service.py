"""Wallet service for managing wallet operations."""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from shared.models import User
from shared.logging_config import get_logger
from shared.error_handlers import (
    DatabaseError, 
    NotFoundError, 
    ValidationError,
    retry_database_operation
)

logger = get_logger(__name__)


class WalletService:
    """Service for managing wallet operations."""
    
    def __init__(self, db: AsyncSession):
        """Initialize wallet service with database session."""
        self.db = db
    
    async def add_wallet_to_user(
        self,
        user_id: int,
        wallet_address: str
    ) -> User:
        """
        Add wallet address to user.
        
        Args:
            user_id: User ID
            wallet_address: TON wallet address to add
            
        Returns:
            Updated User object
            
        Raises:
            NotFoundError: If user not found
            ValidationError: If wallet address is invalid or already exists
            DatabaseError: If database operation fails
        """
        try:
            # Basic wallet address validation
            if not wallet_address or len(wallet_address.strip()) < 10:
                raise ValidationError(
                    "Invalid wallet address format",
                    {"wallet_address": wallet_address}
                )
            
            wallet_address = wallet_address.strip()
            
            # Check if wallet already exists for another user
            existing_wallet_user = await self.get_user_by_wallet(wallet_address)
            if existing_wallet_user and existing_wallet_user.id != user_id:
                raise ValidationError(
                    f"Wallet address {wallet_address} is already associated with another user",
                    {"wallet_address": wallet_address, "existing_user_id": existing_wallet_user.id}
                )
            
            async def _add_wallet_operation():
                # Get user
                result = await self.db.execute(
                    select(User).where(User.id == user_id)
                )
                user = result.scalar_one_or_none()
                if not user:
                    raise NotFoundError("User", user_id)
                
                old_wallet = user.wallet
                user.wallet = wallet_address
                await self.db.flush()
                await self.db.refresh(user)
                
                return user, old_wallet
            
            user, old_wallet = await retry_database_operation(_add_wallet_operation)
            
            # Log wallet addition/update
            if old_wallet:
                logger.info(f"Updated wallet for user {user_id}: {old_wallet} -> {wallet_address}")
            else:
                logger.info(f"Added wallet to user {user_id}: {wallet_address}")
            
            return user
            
        except (ValidationError, NotFoundError, DatabaseError):
            raise
        except IntegrityError as e:
            logger.error(f"Integrity error adding wallet to user {user_id}: {e}")
            raise ValidationError("Wallet addition failed due to data constraint violation")
        except SQLAlchemyError as e:
            logger.error(f"Database error adding wallet to user {user_id}: {e}")
            raise DatabaseError("Failed to add wallet to user", e)
        except Exception as e:
            logger.error(f"Unexpected error adding wallet to user {user_id}: {e}")
            raise DatabaseError("Unexpected error during wallet addition", e)
    
    async def remove_wallet_from_user(
        self,
        user_id: int
    ) -> User:
        """
        Remove wallet address from user.
        
        Args:
            user_id: User ID
            
        Returns:
            Updated User object
            
        Raises:
            NotFoundError: If user not found
            DatabaseError: If database operation fails
        """
        try:
            async def _remove_wallet_operation():
                # Get user
                result = await self.db.execute(
                    select(User).where(User.id == user_id)
                )
                user = result.scalar_one_or_none()
                if not user:
                    raise NotFoundError("User", user_id)
                
                old_wallet = user.wallet
                user.wallet = None
                await self.db.flush()
                await self.db.refresh(user)
                
                return user, old_wallet
            
            user, old_wallet = await retry_database_operation(_remove_wallet_operation)
            
            # Log wallet removal
            if old_wallet:
                logger.info(f"Removed wallet from user {user_id}: {old_wallet}")
            else:
                logger.info(f"No wallet to remove for user {user_id}")
            
            return user
            
        except (NotFoundError, DatabaseError):
            raise
        except SQLAlchemyError as e:
            logger.error(f"Database error removing wallet from user {user_id}: {e}")
            raise DatabaseError("Failed to remove wallet from user", e)
        except Exception as e:
            logger.error(f"Unexpected error removing wallet from user {user_id}: {e}")
            raise DatabaseError("Unexpected error during wallet removal", e)
    
    async def get_user_by_wallet(self, wallet_address: str) -> Optional[User]:
        """
        Get user by wallet address.
        
        Args:
            wallet_address: TON wallet address
            
        Returns:
            User object or None if not found
        """
        try:
            result = await self.db.execute(
                select(User).where(User.wallet == wallet_address)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Database error getting user by wallet {wallet_address}: {e}")
            raise DatabaseError("Failed to get user by wallet", e)
    
    async def validate_wallet_address(self, wallet_address: str) -> bool:
        """
        Validate TON wallet address format.
        
        Args:
            wallet_address: Wallet address to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not wallet_address:
            return False
        
        wallet_address = wallet_address.strip()
        
        # Basic validation - TON addresses are typically 48 characters
        # This is a simple check, you might want to add more sophisticated validation
        if len(wallet_address) < 10:
            return False
        
        # Add more specific TON address validation here if needed
        # For now, just basic length and character checks
        
        return True
    
    async def get_wallet_by_user_id(self, user_id: int) -> Optional[str]:
        """
        Get wallet address by user ID.
        
        Args:
            user_id: User ID
            
        Returns:
            Wallet address or None if not found
        """
        try:
            result = await self.db.execute(
                select(User.wallet).where(User.id == user_id)
            )
            wallet = result.scalar_one_or_none()
            return wallet
        except SQLAlchemyError as e:
            logger.error(f"Database error getting wallet for user {user_id}: {e}")
            raise DatabaseError("Failed to get wallet for user", e)