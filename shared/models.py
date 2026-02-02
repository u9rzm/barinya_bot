"""Database models for the application."""
from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import ForeignKey, String, Float, Integer, Boolean, DateTime, Text, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from shared.database import Base
from pydantic import BaseModel

class OrderStatus(str, Enum):
    """Order status enumeration."""
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class User(Base):
    """User model."""
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    wallet: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    loyalty_points: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_spent: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    loyalty_level_id: Mapped[int] = mapped_column(Integer, ForeignKey("loyalty_levels.id"), nullable=False)
    referrer_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=True)
    referral_code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow, 
        nullable=False
    )
    
    # Relationships
    loyalty_level: Mapped["LoyaltyLevel"] = relationship("LoyaltyLevel", foreign_keys=[loyalty_level_id])
    referrer: Mapped[Optional["User"]] = relationship("User", remote_side=[id], foreign_keys=[referrer_id])
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="user")
    points_transactions: Mapped[list["PointsTransaction"]] = relationship(
        "PointsTransaction", 
        back_populates="user"
    )

class LoyaltyLevel(Base):
    """Loyalty level model."""
    __tablename__ = "loyalty_levels"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    threshold: Mapped[float] = mapped_column(Float, nullable=False)
    points_rate: Mapped[float] = mapped_column(Float, nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow, 
        nullable=False
    )


class PointsTransaction(Base):
    """Points transaction model."""
    __tablename__ = "points_transactions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    order_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("orders.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="points_transactions")
    order: Mapped[Optional["Order"]] = relationship("Order", foreign_keys=[order_id])


class Order(Base):
    """Order model."""
    __tablename__ = "orders"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default=OrderStatus.PENDING.value, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow, 
        nullable=False
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    """Order item model."""
    __tablename__ = "order_items"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey("orders.id"), index=True, nullable=False)
    menu_item_id: Mapped[int] = mapped_column(Integer, ForeignKey("menu_items.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="items")
    menu_item: Mapped["MenuItem"] = relationship("MenuItem")


class MenuItem(Base):
    """Menu item model."""
    __tablename__ = "menu_items"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("menu_categories.id"), index=True, nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow, 
        nullable=False
    )
    
    # Relationships
    category: Mapped["MenuCategory"] = relationship("MenuCategory", back_populates="items")


class MenuCategory(Base):
    """Menu category model."""
    __tablename__ = "menu_categories"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Relationships
    items: Mapped[list["MenuItem"]] = relationship("MenuItem", back_populates="category")


class Promotion(Base):
    """Promotion model."""
    __tablename__ = "promotions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
