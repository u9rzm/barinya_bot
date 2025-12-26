"""initial_schema

Revision ID: 001
Revises: 
Create Date: 2024-12-09 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create loyalty_levels table
    op.create_table(
        'loyalty_levels',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('threshold', sa.Float(), nullable=False),
        sa.Column('points_rate', sa.Float(), nullable=False),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create menu_categories table
    op.create_table(
        'menu_categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('telegram_id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=255), nullable=True),
        sa.Column('first_name', sa.String(length=255), nullable=True),
        sa.Column('last_name', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('loyalty_points', sa.Float(), nullable=False),
        sa.Column('total_spent', sa.Float(), nullable=False),
        sa.Column('loyalty_level_id', sa.Integer(), nullable=False),
        sa.Column('referrer_id', sa.Integer(), nullable=True),
        sa.Column('referral_code', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['loyalty_level_id'], ['loyalty_levels.id'], ),
        sa.ForeignKeyConstraint(['referrer_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_telegram_id'), 'users', ['telegram_id'], unique=True)
    op.create_index(op.f('ix_users_referral_code'), 'users', ['referral_code'], unique=True)

    # Create menu_items table
    op.create_table(
        'menu_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('image_url', sa.String(length=500), nullable=True),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('is_available', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['category_id'], ['menu_categories.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_menu_items_category_id'), 'menu_items', ['category_id'], unique=False)

    # Create orders table
    op.create_table(
        'orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('total_amount', sa.Float(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_orders_user_id'), 'orders', ['user_id'], unique=False)

    # Create promotions table
    op.create_table(
        'promotions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('image_url', sa.String(length=500), nullable=True),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create order_items table
    op.create_table(
        'order_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('menu_item_id', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['menu_item_id'], ['menu_items.id'], ),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_order_items_order_id'), 'order_items', ['order_id'], unique=False)

    # Create points_transactions table
    op.create_table(
        'points_transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('reason', sa.String(length=255), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_points_transactions_user_id'), 'points_transactions', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_points_transactions_user_id'), table_name='points_transactions')
    op.drop_table('points_transactions')
    op.drop_index(op.f('ix_order_items_order_id'), table_name='order_items')
    op.drop_table('order_items')
    op.drop_table('promotions')
    op.drop_index(op.f('ix_orders_user_id'), table_name='orders')
    op.drop_table('orders')
    op.drop_index(op.f('ix_menu_items_category_id'), table_name='menu_items')
    op.drop_table('menu_items')
    op.drop_index(op.f('ix_users_referral_code'), table_name='users')
    op.drop_index(op.f('ix_users_telegram_id'), table_name='users')
    op.drop_table('users')
    op.drop_table('menu_categories')
    op.drop_table('loyalty_levels')
