"""Tests for user and loyalty services."""
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from sqlalchemy.ext.asyncio import AsyncSession

from shared.models import LoyaltyLevel, User, Order, OrderStatus
from shared.services import UserService, LoyaltyService, ReferralService


@pytest.fixture
async def default_loyalty_level(db_session: AsyncSession) -> LoyaltyLevel:
    """Create a default loyalty level for testing."""
    level = LoyaltyLevel(
        name = "Bronze",
        threshold=0.0,
        points_rate=5.0,
        order=1
    )
    db_session.add(level)
    await db_session.commit()
    await db_session.refresh(level)
    return level


@pytest.fixture
async def user_service(db_session: AsyncSession) -> UserService:
    """Create UserService instance."""
    return UserService(db_session)


@pytest.fixture
async def loyalty_service(db_session: AsyncSession) -> LoyaltyService:
    """Create LoyaltyService instance."""
    return LoyaltyService(db_session)


@pytest.fixture
async def referral_service(db_session: AsyncSession) -> ReferralService:
    """Create ReferralService instance."""
    return ReferralService(db_session)


class TestUserService:
    """Tests for UserService."""
    
    async def test_create_user(
        self,
        user_service: UserService,
        db_session: AsyncSession,
        default_loyalty_level: LoyaltyLevel,
    ):
        """Test creating a new user."""
        user = await user_service.create_user(
            telegram_id=123456789,
            username= "testuser",
            first_name= "Test",
            last_name= "User",
        )
        await db_session.commit()
        
        assert user.id is not None
        assert user.telegram_id == 123456789
        assert user.username == "testuser"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.is_active is True
        assert user.loyalty_points == 0.0
        assert user.total_spent == 0.0
        assert user.referral_code is not None
        assert len(user.referral_code) == 8
        assert user.loyalty_level_id == default_loyalty_level.id
    
    async def test_create_user_with_referrer(
        self,
        user_service: UserService,
        db_session: AsyncSession,
        default_loyalty_level: LoyaltyLevel,
    ):
        """Test creating a user with a referrer."""
        # Create referrer
        referrer = await user_service.create_user(
            telegram_id=111111111,
            username= "referrer",
        )
        await db_session.commit()
        
        # Create referee
        referee = await user_service.create_user(
            telegram_id=222222222,
            username= "referee",
            referrer_id=referrer.id,
        )
        await db_session.commit()
        
        assert referee.referrer_id == referrer.id
    
    async def test_get_user_by_telegram_id(
        self,
        user_service: UserService,
        db_session: AsyncSession,
        default_loyalty_level: LoyaltyLevel,
    ):
        """Test getting user by telegram ID."""
        # Create user
        created_user = await user_service.create_user(
            telegram_id=333333333,
            username= "findme",
        )
        await db_session.commit()
        
        # Find user
        found_user = await user_service.get_user_by_telegram_id(333333333)
        
        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.telegram_id == 333333333
    
    async def test_update_user_status(
        self,
        user_service: UserService,
        db_session: AsyncSession,
        default_loyalty_level: LoyaltyLevel,
    ):
        """Test updating user active status."""
        # Create user
        user = await user_service.create_user(
            telegram_id=444444444,
            username= "statustest",
        )
        await db_session.commit()
        
        assert user.is_active is True
        
        # Deactivate user
        await user_service.update_user_status(user.id, False)
        await db_session.commit()
        
        # Verify status changed
        updated_user = await user_service.get_user_by_telegram_id(444444444)
        assert updated_user.is_active is False
    
    async def test_get_user_referrals(
        self,
        user_service: UserService,
        db_session: AsyncSession,
        default_loyalty_level: LoyaltyLevel,
    ):
        # """Test getting users referrals."""
        # Create referrer
        referrer = await user_service.create_user(
            telegram_id=555555555,
            username= "referrer2",
        )
        await db_session.commit()
        
        # Create referees
        referee1 = await user_service.create_user(
            telegram_id=666666666,
            username= "referee1",
            referrer_id=referrer.id,
        )
        referee2 = await user_service.create_user(
            telegram_id=777777777,
            username= "referee2",
            referrer_id=referrer.id,
        )
        await db_session.commit()
        
        # Get referrals
        referrals = await user_service.get_user_referrals(referrer.id)
        
        assert len(referrals) == 2
        referral_ids = {r.id for r in referrals}
        assert referee1.id in referral_ids
        assert referee2.id in referral_ids
    
    async def test_set_user_level(
        self,
        user_service: UserService,
        loyalty_service: LoyaltyService,
        db_session: AsyncSession,
        default_loyalty_level: LoyaltyLevel,
    ):
        # """Test manually setting user's loyalty level."""
        # Create another level
        silver_level = await loyalty_service.create_level(
            name= "Silver",
            threshold=1000.0,
            points_rate=7.0,
        )
        await db_session.commit()
        
        # Create user
        user = await user_service.create_user(
            telegram_id=888888888,
            username= "leveltest",
        )
        await db_session.commit()
        
        assert user.loyalty_level_id == default_loyalty_level.id
        
        # Set to silver level
        await user_service.set_user_level(user.id, silver_level.id)
        await db_session.commit()
        
        # Verify level changed
        updated_user = await user_service.get_user_by_telegram_id(888888888)
        assert updated_user.loyalty_level_id == silver_level.id


class TestLoyaltyService:
    """Tests for LoyaltyService."""
    
    async def test_add_points(
        self,
        user_service: UserService,
        loyalty_service: LoyaltyService,
        db_session: AsyncSession,
        default_loyalty_level: LoyaltyLevel,
    ):
        """Test adding loyalty points."""
        # Create user
        user = await user_service.create_user(
            telegram_id=999999999,
            username= "pointstest",
        )
        await db_session.commit()
        
        # Add points
        await loyalty_service.add_points(
            user_id=user.id,
            amount=100.0,
            reason="Test points",
        )
        await db_session.commit()
        
        # Verify points added
        balance = await loyalty_service.get_points_balance(user.id)
        assert balance == 100.0
    
    async def test_deduct_points(
        self,
        user_service: UserService,
        loyalty_service: LoyaltyService,
        db_session: AsyncSession,
        default_loyalty_level: LoyaltyLevel,
    ):
        """Test deducting loyalty points."""
        # Create user
        user = await user_service.create_user(
            telegram_id=101010101,
            username= "deducttest",
        )
        await db_session.commit()
        
        # Add points first
        await loyalty_service.add_points(
            user_id=user.id,
            amount=200.0,
            reason="Initial points",
        )
        await db_session.commit()
        
        # Deduct points
        await loyalty_service.deduct_points(
            user_id=user.id,
            amount=50.0,
            reason="Test deduction",
        )
        await db_session.commit()
        
        # Verify points deducted
        balance = await loyalty_service.get_points_balance(user.id)
        assert balance == 150.0
    
    async def test_get_points_history(
        self,
        user_service: UserService,
        loyalty_service: LoyaltyService,
        db_session: AsyncSession,
        default_loyalty_level: LoyaltyLevel,
    ):
        """Test getting points transaction history."""
        # Create user
        user = await user_service.create_user(
            telegram_id=121212121,
            username= "historytest",
        )
        await db_session.commit()
        
        # Add multiple transactions
        await loyalty_service.add_points(user.id, 100.0, "First transaction")
        await loyalty_service.add_points(user.id, 50.0, "Second transaction")
        await loyalty_service.deduct_points(user.id, 25.0, "Third transaction")
        await db_session.commit()
        
        # Get history
        history = await loyalty_service.get_points_history(user.id)
        
        assert len(history) == 3
        # Should be ordered by date descending (newest first)
        assert history[0].reason == "Third transaction"
        assert history[0].amount == -25.0
        assert history[1].reason == "Second transaction"
        assert history[1].amount == 50.0
        assert history[2].reason == "First transaction"
        assert history[2].amount == 100.0
    
    async def test_calculate_level_for_user(
        self,
        user_service: UserService,
        loyalty_service: LoyaltyService,
        db_session: AsyncSession,
        default_loyalty_level: LoyaltyLevel,
    ):
        """Test calculating appropriate loyalty level."""
        # Create additional levels
        silver_level = await loyalty_service.create_level(
            name= "Silver",
            threshold=1000.0,
            points_rate=7.0,
        )
        gold_level = await loyalty_service.create_level(
            name= "Gold",
            threshold=5000.0,
            points_rate=10.0,
        )
        await db_session.commit()
        
        # Create user
        user = await user_service.create_user(
            telegram_id=131313131,
            username= "calctest",
        )
        await db_session.commit()
        
        # Test with 0 spent (should be bronze)
        level = await loyalty_service.calculate_level_for_user(user.id)
        assert level.id == default_loyalty_level.id
        
        # Update total spent to 1500
        from sqlalchemy import select
        result = await db_session.execute(select(User).where(User.id == user.id))
        user_obj = result.scalar_one()
        user_obj.total_spent = 1500.0
        await db_session.commit()
        
        # Should be silver
        level = await loyalty_service.calculate_level_for_user(user.id)
        assert level.id == silver_level.id
        
        # Update total spent to 6000
        result = await db_session.execute(select(User).where(User.id == user.id))
        user_obj = result.scalar_one()
        user_obj.total_spent = 6000.0
        await db_session.commit()
        
        # Should be gold
        level = await loyalty_service.calculate_level_for_user(user.id)
        assert level.id == gold_level.id
    
    async def test_create_level(
        self,
        loyalty_service: LoyaltyService,
        db_session: AsyncSession,
        default_loyalty_level: LoyaltyLevel,
    ):
        """Test creating a new loyalty level."""
        level = await loyalty_service.create_level(
            name= "Platinum",
            threshold=10000.0,
            points_rate=15.0,
        )
        await db_session.commit()
        
        assert level.id is not None
        assert level.name == "Platinum"
        assert level.threshold == 10000.0
        assert level.points_rate == 15.0
        assert level.order == 2  # Should be second after default
    
    async def test_get_levels(
        self,
        loyalty_service: LoyaltyService,
        db_session: AsyncSession,
        default_loyalty_level: LoyaltyLevel,
    ):
        """Test getting all loyalty levels."""
        # Create additional levels
        await loyalty_service.create_level("Silver", 1000.0, 7.0)
        await loyalty_service.create_level("Gold", 5000.0, 10.0)
        await db_session.commit()
        
        # Get all levels
        levels = await loyalty_service.get_levels()
        
        assert len(levels) == 3
        # Should be ordered by threshold ascending
        assert levels[0].name == "Bronze"
        assert levels[1].name == "Silver"
        assert levels[2].name == "Gold"



class TestReferralService:
    """Tests for ReferralService."""
    
    async def test_generate_referral_code(
        self,
        user_service: UserService,
        referral_service: ReferralService,
        db_session: AsyncSession,
        default_loyalty_level: LoyaltyLevel,
    ):
        """Test generating referral code for a user."""
        # Create user
        user = await user_service.create_user(
            telegram_id=141414141,
            username= "refcodetest",
        )
        await db_session.commit()
        
        # Get referral code
        code = await referral_service.generate_referral_code(user.id)
        
        assert code is not None
        assert len(code) == 8
        assert code == user.referral_code
    
    async def test_get_referral_link(
        self,
        user_service: UserService,
        referral_service: ReferralService,
        db_session: AsyncSession,
        default_loyalty_level: LoyaltyLevel,
    ):
        """Test getting referral link for a user."""
        # Create user
        user = await user_service.create_user(
            telegram_id=151515151,
            username= "reflinktest",
        )
        await db_session.commit()
        
        # Get referral link
        link = await referral_service.get_referral_link(user.id)
        
        assert link is not None
        assert "t.me" in link
        assert user.referral_code in link
        assert link.startswith("https://")
    
    async def test_register_referral(
        self,
        user_service: UserService,
        referral_service: ReferralService,
        db_session: AsyncSession,
        default_loyalty_level: LoyaltyLevel,
    ):
        """Test registering a referral relationship."""
        # Create referrer
        referrer = await user_service.create_user(
            telegram_id=161616161,
            username= "referrer3",
        )
        await db_session.commit()
        
        # Create referee without referrer
        referee = await user_service.create_user(
            telegram_id=171717171,
            username= "referee3",
        )
        await db_session.commit()
        
        assert referee.referrer_id is None
        
        # Register referral
        await referral_service.register_referral(
            referee_id=referee.id,
            referral_code=referrer.referral_code,
        )
        await db_session.commit()
        
        # Verify referral relationship
        from sqlalchemy import select
        result = await db_session.execute(select(User).where(User.id == referee.id))
        updated_referee = result.scalar_one()
        assert updated_referee.referrer_id == referrer.id
    
    async def test_register_referral_self_referral_rejected(
        self,
        user_service: UserService,
        referral_service: ReferralService,
        db_session: AsyncSession,
        default_loyalty_level: LoyaltyLevel,
    ):
        """Test that self-referral is rejected."""
        # Create user
        user = await user_service.create_user(
            telegram_id=181818181,
            username= "selfreferrer",
        )
        await db_session.commit()
        
        # Try to use own referral code
        with pytest.raises(ValueError, match="Cannot use your own referral code"):
            await referral_service.register_referral(
                referee_id=user.id,
                referral_code=user.referral_code,
            )
    
    async def test_register_referral_invalid_code(
        self,
        user_service: UserService,
        referral_service: ReferralService,
        db_session: AsyncSession,
        default_loyalty_level: LoyaltyLevel,
    ):
        """Test that invalid referral code is rejected."""
        # Create user
        user = await user_service.create_user(
            telegram_id=191919191,
            username= "invalidref",
        )
        await db_session.commit()
        
        # Try to use invalid referral code
        with pytest.raises(ValueError, match="Invalid referral code"):
            await referral_service.register_referral(
                referee_id=user.id,
                referral_code="INVALID1",
            )
    
    async def test_process_referral_reward(
        self,
        user_service: UserService,
        referral_service: ReferralService,
        loyalty_service: LoyaltyService,
        db_session: AsyncSession,
        default_loyalty_level: LoyaltyLevel,
    ):
        """Test processing referral reward for an order."""
        # Create referrer
        referrer = await user_service.create_user(
            telegram_id=202020202,
            username= "referrer4",
        )
        await db_session.commit()
        
        # Create referee with referrer
        referee = await user_service.create_user(
            telegram_id=212121212,
            username= "referee4",
            referrer_id=referrer.id,
        )
        await db_session.commit()
        
        # Create an order for referee
        order = Order(
            user_id=referee.id,
            total_amount=1000.0,
            status=OrderStatus.COMPLETED.value,
        )
        db_session.add(order)
        await db_session.commit()
        await db_session.refresh(order)
        
        # Get initial referrer points
        initial_points = await loyalty_service.get_points_balance(referrer.id)
        
        # Process referral reward (1% of 1000 = 10)
        await referral_service.process_referral_reward(
            order_id=order.id,
            referee_id=referee.id,
            order_amount=1000.0,
        )
        await db_session.commit()
        
        # Verify referrer received 1% reward
        final_points = await loyalty_service.get_points_balance(referrer.id)
        assert final_points == initial_points + 10.0
        
        # Verify transaction was recorded
        history = await loyalty_service.get_points_history(referrer.id)
        assert len(history) == 1
        assert history[0].amount == 10.0
        assert "Referral reward" in history[0].reason
    
    async def test_process_referral_reward_no_referrer(
        self,
        user_service: UserService,
        referral_service: ReferralService,
        loyalty_service: LoyaltyService,
        db_session: AsyncSession,
        default_loyalty_level: LoyaltyLevel,
    ):
        """Test that no reward is processed if user has no referrer."""
        # Create user without referrer
        user = await user_service.create_user(
            telegram_id=222222223,
            username= "noreferrer",
        )
        await db_session.commit()
        
        # Create an order
        order = Order(
            user_id=user.id,
            total_amount=1000.0,
            status=OrderStatus.COMPLETED.value,
        )
        db_session.add(order)
        await db_session.commit()
        await db_session.refresh(order)
        
        # Process referral reward (should do nothing)
        await referral_service.process_referral_reward(
            order_id=order.id,
            referee_id=user.id,
            order_amount=1000.0,
        )
        await db_session.commit()
        
        # No error should occur, just no reward processed
    
    async def test_get_referral_stats(
        self,
        user_service: UserService,
        referral_service: ReferralService,
        db_session: AsyncSession,
        default_loyalty_level: LoyaltyLevel,
    ):
        """Test getting referral statistics."""
        # Create referrer
        referrer = await user_service.create_user(
            telegram_id=232323232,
            username= "referrer5",
        )
        await db_session.commit()
        
        # Create referees
        referee1 = await user_service.create_user(
            telegram_id=242424242,
            username= "referee5a",
            referrer_id=referrer.id,
        )
        referee2 = await user_service.create_user(
            telegram_id=252525252,
            username= "referee5b",
            referrer_id=referrer.id,
        )
        await db_session.commit()
        
        # Create orders and process rewards
        order1 = Order(
            user_id=referee1.id,
            total_amount=1000.0,
            status=OrderStatus.COMPLETED.value,
        )
        order2 = Order(
            user_id=referee2.id,
            total_amount=2000.0,
            status=OrderStatus.COMPLETED.value,
        )
        db_session.add(order1)
        db_session.add(order2)
        await db_session.commit()
        await db_session.refresh(order1)
        await db_session.refresh(order2)
        
        await referral_service.process_referral_reward(
            order_id=order1.id,
            referee_id=referee1.id,
            order_amount=1000.0,
        )
        await referral_service.process_referral_reward(
            order_id=order2.id,
            referee_id=referee2.id,
            order_amount=2000.0,
        )
        await db_session.commit()
        
        # Get referral stats
        stats = await referral_service.get_referral_stats(referrer.id)
        
        assert stats.total_referrals == 2
        assert stats.total_earned == 30.0  # 10 + 20
        assert len(stats.referrals) == 2
    
    async def test_get_referral_stats_no_referrals(
        self,
        user_service: UserService,
        referral_service: ReferralService,
        db_session: AsyncSession,
        default_loyalty_level: LoyaltyLevel,
    ):
        """Test getting referral stats for user with no referrals."""
        # Create user without referrals
        user = await user_service.create_user(
            telegram_id=262626262,
            username= "norefs",
        )
        await db_session.commit()
        
        # Get stats
        stats = await referral_service.get_referral_stats(user.id)
        
        assert stats.total_referrals == 0
        assert stats.total_earned == 0.0
        assert len(stats.referrals) == 0
    
    @given(st.lists(
        st.tuples(
            st.integers(min_value=100000000, max_value=999999999),  # telegram_id
            st.text(min_size=3, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))  # username
        ),
        min_size=2,
        max_size=10,
        unique_by=lambda x: x[0]  # Ensure unique telegram_ids
    ))
    @settings(
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        max_examples=10,  # Reduce examples to avoid database conflicts
        deadline=None  # Remove deadline for async tests
    )
    @pytest.mark.asyncio
    async def test_property_referral_codes_are_unique_per_user(
        self,
        user_service: UserService,
        referral_service: ReferralService,
        db_session: AsyncSession,
        default_loyalty_level: LoyaltyLevel,
        user_data_list,
    ):
        """
        Feature: telegram-bar-bot, Property 20: Referral codes are unique per user
        
        Property test that verifies referral codes are unique across all users.
        For any set of users, all generated referral codes should be unique.
        """
        try:
            # Create users from generated data
            created_users = []
            for telegram_id, username in user_data_list:
                user = await user_service.create_user(
                    telegram_id=telegram_id,
                    username=username,
                )
                created_users.append(user)
            
            await db_session.commit()
            
            # Collect all referral codes
            referral_codes = []
            for user in created_users:
                code = await referral_service.generate_referral_code(user.id)
                referral_codes.append(code)
            
            # Verify all codes are unique
            assert len(referral_codes) == len(set(referral_codes)), \
                f"Referral codes are not unique: {referral_codes}"
            
            # Verify each code is 8 characters long (as per implementation)
            for code in referral_codes:
                assert len(code) == 8, f"Referral code {code} is not 8 characters long"
                assert code.isalnum(), f"Referral code {code} contains non-alphanumeric characters"
        
        except Exception as e:
            # Rollback on any error to clean up the session
            await db_session.rollback()
            raise e
        finally:
            # Clean up created users to avoid conflicts in subsequent examples
            try:
                from sqlalchemy import delete
                from shared.models import User
                await db_session.execute(delete(User).where(User.telegram_id.in_([tid for tid, _ in user_data_list])))
                await db_session.commit()
            except Exception:
                await db_session.rollback()



class TestMenuService:
    """Tests for MenuService."""
    
    @pytest.fixture
    async def menu_category(self, db_session: AsyncSession):
        """Create a test menu category."""
        from shared.models import MenuCategory
        category = MenuCategory(
            name= "Drinks",
            order=1,
        )
        db_session.add(category)
        await db_session.commit()
        await db_session.refresh(category)
        return category
    
    @pytest.fixture
    async def menu_service(self, db_session: AsyncSession):
        """Create MenuService instance."""
        from shared.services import MenuService
        return MenuService(db_session)
    
    async def test_create_menu_item(
        self,
        menu_service,
        menu_category,
        db_session: AsyncSession,
        ):
        """Test creating a menu item."""
        item = await menu_service.create_menu_item(
            name= "Coffee",
            price= 5.99,
            category_id= menu_category.id,
            description= "Fresh brewed coffee",
            image_url= "https://example.com/coffee.jpg",
            )
        await db_session.commit()
        
        assert item.id is not None
        assert item.name == "Coffee"
        assert item.price == 5.99
        assert item.category_id == menu_category.id
        assert item.description == "Fresh brewed coffee"
        assert item.image_url == "https://example.com/coffee.jpg"
        assert item.is_available is True
    
    async def test_get_menu_item(
        self,
        menu_service,
        menu_category,
        db_session: AsyncSession,
    ):
        """Test getting a menu item by ID."""
        # Create item
        created_item = await menu_service.create_menu_item(
            name= "Tea",
            price= 3.99,
            category_id= menu_category.id
        )
        await db_session.commit()
        
        # Get item
        item = await menu_service.get_menu_item(created_item.id)
        
        assert item is not None
        assert item.id == created_item.id
        assert item.name == "Tea"
        assert item.price == 3.99
    
    async def test_update_menu_item(
        self,
        menu_service,
        menu_category,
        db_session: AsyncSession,
    ):
        """Test updating a menu item."""
        # Create item
        item = await menu_service.create_menu_item(
            name= "Juice",
            price= 4.99,
            category_id= menu_category.id
        )
        await db_session.commit()
        
        # Update item
        updated_item = await menu_service.update_menu_item(
            item_id=item.id,
            name= "Fresh Juice",
            price= 5.99,
            description= "Freshly squeezed",
        )
        await db_session.commit()
        
        assert updated_item.name == "Fresh Juice"
        assert updated_item.price == 5.99
        assert updated_item.description == "Freshly squeezed"
    
    async def test_delete_menu_item(
        self,
        menu_service,
        menu_category,
        db_session: AsyncSession,
    ):
        """Test soft deleting a menu item."""
        # Create item
        item = await menu_service.create_menu_item(
            name= "Soda",
            price= 2.99,
            category_id= menu_category.id
        )
        await db_session.commit()
        
        assert item.is_available is True
        
        # Delete item
        await menu_service.delete_menu_item(item.id)
        await db_session.commit()
        
        # Verify item is marked unavailable
        deleted_item = await menu_service.get_menu_item(item.id)
        assert deleted_item is not None
        assert deleted_item.is_available is False
    
    async def test_get_menu_by_category(
        self,
        menu_service,
        menu_category,
        db_session: AsyncSession,
    ):
        """Test getting menu items by category."""
        # Create items
        item1 = await menu_service.create_menu_item(
            name= "Coffee",
            price= 5.99,
            category_id= menu_category.id
        )
        item2 = await menu_service.create_menu_item(
            name= "Tea",
            price= 3.99,
            category_id= menu_category.id
        )
        item3 = await menu_service.create_menu_item(
            name= "Unavailable Item",
            price= 1.99,
            category_id= menu_category.id,
            is_available= False
        )
        await db_session.commit()
        
        # Get items by category
        items = await menu_service.get_menu_by_category(menu_category.id)
        
        assert len(items) == 2
        item_names = {item.name for item in items}
        assert "Coffee" in item_names
        assert "Tea" in item_names
        assert "Unavailable Item" not in item_names
    
    async def test_get_menu(
        self,
        menu_service,
        db_session: AsyncSession,
    ):
        """Test getting full menu with categories."""
        from shared.models import MenuCategory
        
        # Create categories
        drinks_cat = MenuCategory(name= "Drinks", order=1)
        food_cat = MenuCategory(name= "Food", order=2)
        db_session.add(drinks_cat)
        db_session.add(food_cat)
        await db_session.commit()
        await db_session.refresh(drinks_cat)
        await db_session.refresh(food_cat)
        
        # Create items
        await menu_service.create_menu_item(
            name= "Coffee",
            price= 5.99,
            category_id= drinks_cat.id
        )
        await menu_service.create_menu_item(
            name= "Burger",
            price= 12.99,
            category_id= food_cat.id
        )
        await menu_service.create_menu_item(
            name= "Unavailable",
            price= 1.99,
            category_id= drinks_cat.id,
            is_available= False
        )
        await db_session.commit()
        
        # Get full menu
        menu = await menu_service.get_menu()
        
        assert len(menu) == 2
        assert menu[0].name == "Drinks"
        assert menu[1].name == "Food"
        
        # Check items (only available ones)
        drinks_items = menu[0].items
        assert len(drinks_items) == 1
        assert drinks_items[0].name == "Coffee"
        
        food_items = menu[1].items
        assert len(food_items) == 1
        assert food_items[0].name == "Burger"


class TestPromotionService:
    """Tests for PromotionService."""
    
    @pytest.fixture
    async def promotion_service(self, db_session: AsyncSession):
        """Create PromotionService instance."""
        from shared.services import PromotionService
        return PromotionService(db_session)
    
    async def test_create_promotion(
        self,
        promotion_service,
        db_session: AsyncSession,
    ):
        """Test creating a promotion."""
        from datetime import datetime, timedelta
        
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=7)
        
        promotion = await promotion_service.create_promotion(
            title="Happy Hour",
            description= "50% off all drinks",
            start_date=start_date,
            end_date=end_date,
            image_url= "https://example.com/promo.jpg",
        )
        await db_session.commit()
        
        assert promotion.id is not None
        assert promotion.title == "Happy Hour"
        assert promotion.description == "50% off all drinks"
        assert promotion.start_date == start_date
        assert promotion.end_date == end_date
        assert promotion.image_url == "https://example.com/promo.jpg"
    
    async def test_create_promotion_invalid_dates(
        self,
        promotion_service,
        db_session: AsyncSession,
    ):
        """Test that creating promotion with invalid dates raises error."""
        from datetime import datetime, timedelta
        
        start_date = datetime.utcnow()
        end_date = start_date - timedelta(days=1)  # End before start
        
        with pytest.raises(ValueError, match="End date must be after start date"):
            await promotion_service.create_promotion(
                title="Invalid Promo",
                description= "This should fail",
                start_date=start_date,
                end_date=end_date,
            )
    
    async def test_get_active_promotions(
        self,
        promotion_service,
        db_session: AsyncSession,
    ):
        """Test getting active promotions."""
        from datetime import datetime, timedelta
        
        now = datetime.utcnow()
        
        # Create active promotion
        active_promo = await promotion_service.create_promotion(
            title="Active Promo",
            description= "Currently active",
            start_date=now - timedelta(days=1),
            end_date=now + timedelta(days=7),
        )
        
        # Create future promotion
        future_promo = await promotion_service.create_promotion(
            title="Future Promo",
            description= "Starts tomorrow",
            start_date=now + timedelta(days=1),
            end_date=now + timedelta(days=8),
        )
        
        # Create past promotion
        past_promo = await promotion_service.create_promotion(
            title="Past Promo",
            description= "Already ended",
            start_date=now - timedelta(days=10),
            end_date=now - timedelta(days=3),
        )
        
        await db_session.commit()
        
        # Get active promotions
        active_promotions = await promotion_service.get_active_promotions()
        
        assert len(active_promotions) == 1
        assert active_promotions[0].id == active_promo.id
        assert active_promotions[0].title == "Active Promo"
    
    async def test_broadcast_promotion(
        self,
        promotion_service,
        user_service: UserService,
        db_session: AsyncSession,
        default_loyalty_level: LoyaltyLevel,
    ):
        """Test getting telegram IDs for promotion broadcast."""
        from datetime import datetime, timedelta
        
        # Create users
        active_user1 = await user_service.create_user(
            telegram_id=301010101,
            username= "active1",
        )
        active_user2 = await user_service.create_user(
            telegram_id=302020202,
            username= "active2",
        )
        inactive_user = await user_service.create_user(
            telegram_id=303030303,
            username= "inactive",
        )
        await db_session.commit()
        
        # Deactivate one user
        await user_service.update_user_status(inactive_user.id, False)
        await db_session.commit()
        
        # Create promotion
        promotion = await promotion_service.create_promotion(
            title="Broadcast Test",
            description= "Test broadcast",
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=7),
        )
        await db_session.commit()
        
        # Get telegram IDs for broadcast
        telegram_ids = await promotion_service.broadcast_promotion(promotion.id)
        
        assert len(telegram_ids) == 2
        assert 301010101 in telegram_ids
        assert 302020202 in telegram_ids
        assert 303030303 not in telegram_ids


class TestOrderService:
    """Tests for OrderService."""
    
    @pytest.fixture
    async def order_service(self, db_session: AsyncSession):
        """Create OrderService instance."""
        from shared.services import OrderService
        return OrderService(db_session)
    
    @pytest.fixture
    async def menu_category(self, db_session: AsyncSession):
        """Create a test menu category."""
        from shared.models import MenuCategory
        category = MenuCategory(
            name= "Test Category",
            order=1,
        )
        db_session.add(category)
        await db_session.commit()
        await db_session.refresh(category)
        return category
    
    @pytest.fixture
    async def menu_item(self, db_session: AsyncSession, menu_category):
        """Create a test menu item."""
        from shared.models import MenuItem
        item = MenuItem(
            name= "Test Item",
            description= "Test description",
            price= 10.99,
            category_id= menu_category.id,
            is_available= True,
        )
        db_session.add(item)
        await db_session.commit()
        await db_session.refresh(item)
        return item
    
    async def test_create_order(
        self,
        order_service,
        user_service: UserService,
        menu_item,
        db_session: AsyncSession,
        default_loyalty_level: LoyaltyLevel,
    ):
        """Test creating a new order."""
        from shared.services import OrderItemCreate
        
        # Create user
        user = await user_service.create_user(
            telegram_id=400000001,
            username= "orderuser",
        )
        await db_session.commit()
        
        # Create order items
        items = [
            OrderItemCreate(
                menu_item_id=menu_item.id,
                quantity=2,
                price= 10.99,
            )
        ]
        
        # Create order
        order = await order_service.create_order(
            user_id=user.id,
            items=items,
            total_amount=21.98,
        )
        await db_session.commit()
        
        # Refresh order to get the items
        await db_session.refresh(order)
        
        assert order.id is not None
        assert order.user_id == user.id
        assert order.total_amount == 21.98
        assert order.status == "PENDING"
        
        # Get order with items loaded
        loaded_order = await order_service.get_order_by_id(order.id)
        assert len(loaded_order.items) == 1
        assert loaded_order.items[0].menu_item_id == menu_item.id
        assert loaded_order.items[0].quantity == 2
        assert loaded_order.items[0].price == 10.99
    
    async def test_create_order_invalid_amount(
        self,
        order_service,
        user_service: UserService,
        menu_item,
        db_session: AsyncSession,
        default_loyalty_level: LoyaltyLevel,
    ):
        """Test that creating order with invalid amount raises error."""
        from shared.services import OrderItemCreate
        
        # Create user
        user = await user_service.create_user(
            telegram_id=400000002,
            username= "orderuser2",
        )
        await db_session.commit()
        
        # Create order items
        items = [
            OrderItemCreate(
                menu_item_id=menu_item.id,
                quantity=1,
                price= 10.99,
            )
        ]
        
        # Try to create order with zero amount
        with pytest.raises(ValueError, match="Order amount must be greater than zero"):
            await order_service.create_order(
                user_id=user.id,
                items=items,
                total_amount=0.0,
            )
        
        # Try to create order with negative amount
        with pytest.raises(ValueError, match="Order amount must be greater than zero"):
            await order_service.create_order(
                user_id=user.id,
                items=items,
                total_amount=-10.0,
            )
    
    async def test_create_order_invalid_user(
        self,
        order_service,
        menu_item,
        db_session: AsyncSession,
    ):
        """Test that creating order with invalid user raises error."""
        from shared.services import OrderItemCreate
        
        # Create order items
        items = [
            OrderItemCreate(
                menu_item_id=menu_item.id,
                quantity=1,
                price= 10.99,
            )
        ]
        
        # Try to create order with non-existent user
        with pytest.raises(ValueError, match="User not found"):
            await order_service.create_order(
                user_id=99999,
                items=items,
                total_amount=10.99,
            )
    
    async def test_create_order_invalid_menu_item(
        self,
        order_service,
        user_service: UserService,
        db_session: AsyncSession,
        default_loyalty_level: LoyaltyLevel,
    ):
        """Test that creating order with invalid menu item raises error."""
        from shared.services import OrderItemCreate
        
        # Create user
        user = await user_service.create_user(
            telegram_id=400000003,
            username= "orderuser3",
        )
        await db_session.commit()
        
        # Create order items with non-existent menu item
        items = [
            OrderItemCreate(
                menu_item_id=99999,
                quantity=1,
                price= 10.99,
            )
        ]
        
        # Try to create order
        with pytest.raises(ValueError, match="Menu item 99999 not found"):
            await order_service.create_order(
                user_id=user.id,
                items=items,
                total_amount=10.99,
            )
    
    async def test_get_order_by_id(
        self,
        order_service,
        user_service: UserService,
        menu_item,
        db_session: AsyncSession,
        default_loyalty_level: LoyaltyLevel,
    ):
        """Test getting order by ID."""
        from shared.services import OrderItemCreate
        
        # Create user
        user = await user_service.create_user(
            telegram_id=400000004,
            username= "orderuser4",
        )
        await db_session.commit()
        
        # Create order
        items = [
            OrderItemCreate(
                menu_item_id=menu_item.id,
                quantity=1,
                price= 10.99,
            )
        ]
        
        created_order = await order_service.create_order(
            user_id=user.id,
            items=items,
            total_amount=10.99,
        )
        await db_session.commit()
        
        # Get order by ID
        order = await order_service.get_order_by_id(created_order.id)
        
        assert order is not None
        assert order.id == created_order.id
        assert order.user_id == user.id
        assert order.total_amount == 10.99
        assert len(order.items) == 1
        assert order.user is not None
        assert order.user.id == user.id
    
    async def test_get_order_by_id_not_found(
        self,
        order_service,
        db_session: AsyncSession,
    ):
        """Test getting non-existent order returns None."""
        order = await order_service.get_order_by_id(99999)
        assert order is None
    
    async def test_get_user_orders(
        self,
        order_service,
        user_service: UserService,
        menu_item,
        db_session: AsyncSession,
        default_loyalty_level: LoyaltyLevel,
    ):
        """Test getting all orders for a user."""
        from shared.services import OrderItemCreate
        
        # Create user
        user = await user_service.create_user(
            telegram_id=400000005,
            username= "orderuser5",
        )
        await db_session.commit()
        
        # Create multiple orders
        items = [
            OrderItemCreate(
                menu_item_id=menu_item.id,
                quantity=1,
                price= 10.99,
            )
        ]
        
        order1 = await order_service.create_order(
            user_id=user.id,
            items=items,
            total_amount=10.99,
        )
        order2 = await order_service.create_order(
            user_id=user.id,
            items=items,
            total_amount=15.99,
        )
        await db_session.commit()
        
        # Get user orders
        orders = await order_service.get_user_orders(user.id)
        
        assert len(orders) == 2
        # Should be ordered by creation date descending (newest first)
        assert orders[0].id == order2.id
        assert orders[1].id == order1.id
    
    async def test_process_order_rewards(
        self,
        order_service,
        user_service: UserService,
        loyalty_service: LoyaltyService,
        menu_item,
        db_session: AsyncSession,
        default_loyalty_level: LoyaltyLevel,
    ):
        """Test processing order rewards (loyalty points and referral)."""
        from shared.services import OrderItemCreate
        
        # Create user
        user = await user_service.create_user(
            telegram_id=400000006,
            username= "orderuser6",
        )
        await db_session.commit()
        
        # Create order
        items = [
            OrderItemCreate(
                menu_item_id=menu_item.id,
                quantity=1,
                price= 10.99,
            )
        ]
        
        order = await order_service.create_order(
            user_id=user.id,
            items=items,
            total_amount=100.0,
        )
        await db_session.commit()
        
        # Get initial user state
        initial_points = await loyalty_service.get_points_balance(user.id)
        from sqlalchemy import select
        result = await db_session.execute(select(User).where(User.id == user.id))
        user_before = result.scalar_one()
        initial_total_spent = user_before.total_spent
        
        # Process order rewards
        await order_service.process_order_rewards(order.id)
        await db_session.commit()
        
        # Verify loyalty points were awarded (5% of 100 = 5 points)
        final_points = await loyalty_service.get_points_balance(user.id)
        expected_points = initial_points + (100.0 * 0.05)  # 5% rate from default level
        assert final_points == expected_points
        
        # Verify total spent was updated
        result = await db_session.execute(select(User).where(User.id == user.id))
        user_after = result.scalar_one()
        assert user_after.total_spent == initial_total_spent + 100.0
        
        # Verify order status was updated
        updated_order = await order_service.get_order_by_id(order.id)
        assert updated_order.status == "COMPLETED"
        
        # Verify transaction was recorded
        history = await loyalty_service.get_points_history(user.id)
        assert len(history) == 1
        assert history[0].amount == 5.0
        assert f"Order #{order.id} completion" in history[0].reason
    
    async def test_process_order_rewards_with_referral(
        self,
        order_service,
        user_service: UserService,
        loyalty_service: LoyaltyService,
        referral_service: ReferralService,
        menu_item,
        db_session: AsyncSession,
        default_loyalty_level: LoyaltyLevel,
    ):
        """Test processing order rewards with referral bonus."""
        from shared.services import OrderItemCreate
        
        # Create referrer
        referrer = await user_service.create_user(
            telegram_id=400000007,
            username= "referrer",
        )
        await db_session.commit()
        
        # Create referee with referrer
        referee = await user_service.create_user(
            telegram_id=400000008,
            username= "referee",
            referrer_id=referrer.id,
        )
        await db_session.commit()
        
        # Create order for referee
        items = [
            OrderItemCreate(
                menu_item_id=menu_item.id,
                quantity=1,
                price= 10.99,
            )
        ]
        
        order = await order_service.create_order(
            user_id=referee.id,
            items=items,
            total_amount=100.0,
        )
        await db_session.commit()
        
        # Get initial referrer points
        initial_referrer_points = await loyalty_service.get_points_balance(referrer.id)
        
        # Process order rewards
        await order_service.process_order_rewards(order.id)
        await db_session.commit()
        
        # Verify referrer received 1% reward (1% of 100 = 1 point)
        final_referrer_points = await loyalty_service.get_points_balance(referrer.id)
        assert final_referrer_points == initial_referrer_points + 1.0
        
        # Verify referral transaction was recorded
        referrer_history = await loyalty_service.get_points_history(referrer.id)
        referral_transactions = [t for t in referrer_history if "Referral reward" in t.reason]
        assert len(referral_transactions) == 1
        assert referral_transactions[0].amount == 1.0
    
    async def test_process_order_rewards_invalid_order(
        self,
        order_service,
        db_session: AsyncSession,
    ):
        """Test processing rewards for non-existent order raises error."""
        with pytest.raises(ValueError, match="Order not found"):
            await order_service.process_order_rewards(99999)
    
    async def test_process_order_rewards_non_pending_order(
        self,
        order_service,
        user_service: UserService,
        menu_item,
        db_session: AsyncSession,
        default_loyalty_level: LoyaltyLevel,
    ):
        """Test processing rewards for non-pending order raises error."""
        from shared.services import OrderItemCreate
        from shared.models import OrderStatus
        
        # Create user
        user = await user_service.create_user(
            telegram_id=400000009,
            username= "orderuser9",
        )
        await db_session.commit()
        
        # Create order
        items = [
            OrderItemCreate(
                menu_item_id=menu_item.id,
                quantity=1,
                price= 10.99,
            )
        ]
        
        order = await order_service.create_order(
            user_id=user.id,
            items=items,
            total_amount=100.0,
        )
        
        # Manually set order status to completed
        order.status = OrderStatus.COMPLETED.value
        await db_session.commit()
        
        # Try to process rewards again
        with pytest.raises(ValueError, match="Order is not in pending status"):
            await order_service.process_order_rewards(order.id)


class TestNotificationService:
    """Tests for NotificationService."""
    
    @pytest.fixture
    async def mock_bot(self):
        """Create a mock bot for testing."""
        from unittest.mock import AsyncMock, MagicMock
        
        bot = MagicMock()
        bot.send_message = AsyncMock()
        return bot
    
    @pytest.fixture
    async def notification_service(self, mock_bot, db_session: AsyncSession):
        """Create NotificationService instance with mock bot."""
        from shared.services import NotificationService
        return NotificationService(mock_bot, db_session)
    
    async def test_send_message_success(
        self,
        notification_service,
        mock_bot,
    ):
        """Test successful message sending."""
        # Mock successful send
        mock_bot.send_message.return_value = None
        
        # Send message
        result = await notification_service.send_message(
            telegram_id=123456789,
            message="Test message"
        )
        
        assert result is True
        mock_bot.send_message.assert_called_once_with(
            chat_id=123456789,
            text="Test message",
            reply_markup=None,
            parse_mode="HTML"
        )
    
    async def test_send_message_user_blocked_bot(
        self,
        notification_service,
        mock_bot,
        user_service: UserService,
        db_session: AsyncSession,
        default_loyalty_level: LoyaltyLevel,
    ):
        """Test handling when user blocks the bot."""
        from aiogram.exceptions import TelegramForbiddenError
        
        # Create user
        user = await user_service.create_user(
            telegram_id=123456789,
            username= "testuser",
        )
        await db_session.commit()
        
        # Mock bot blocked error
        mock_bot.send_message.side_effect = TelegramForbiddenError(
            method="sendMessage",
            message="Forbidden: bot was blocked by the user"
        )
        
        # Send message
        result = await notification_service.send_message(
            telegram_id=123456789,
            message="Test message"
        )
        
        assert result is False
        
        # Verify user was deactivated
        await db_session.refresh(user)
        assert user.is_active is False
    
    async def test_send_promotion(
        self,
        notification_service,
        mock_bot,
        db_session: AsyncSession,
    ):
        """Test sending promotion message."""
        from shared.models import Promotion
        from datetime import datetime, timedelta
        
        # Create promotion
        promotion = Promotion(
            title="Test Promotion",
            description= "This is a test promotion",
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=7),
        )
        
        # Mock successful send
        mock_bot.send_message.return_value = None
        
        # Send promotion
        result = await notification_service.send_promotion(
            telegram_id=123456789,
            promotion=promotion
        )
        
        assert result is True
        
        # Verify message was sent with correct format
        mock_bot.send_message.assert_called_once()
        call_args = mock_bot.send_message.call_args
        
        assert call_args[1]["chat_id"] == 123456789
        assert "Test Promotion" in call_args[1]["text"]
        assert "This is a test promotion" in call_args[1]["text"]
        assert call_args[1]["reply_markup"] is not None
    
    async def test_send_level_up_notification(
        self,
        notification_service,
        mock_bot,
        default_loyalty_level: LoyaltyLevel,
    ):
        """Test sending level up notification."""
        # Mock successful send
        mock_bot.send_message.return_value = None
        
        # Send level up notification
        result = await notification_service.send_level_up_notification(
            telegram_id=123456789,
            new_level=default_loyalty_level
        )
        
        assert result is True
        
        # Verify message was sent with correct format
        mock_bot.send_message.assert_called_once()
        call_args = mock_bot.send_message.call_args
        
        assert call_args[1]["chat_id"] == 123456789
        assert "Поздравляем!" in call_args[1]["text"]
        assert default_loyalty_level.name in call_args[1]["text"]
        assert str(default_loyalty_level.points_rate) in call_args[1]["text"]
        assert call_args[1]["reply_markup"] is not None
    
    async def test_send_referral_reward_notification(
        self,
        notification_service,
        mock_bot,
    ):
        """Test sending referral reward notification."""
        # Mock successful send
        mock_bot.send_message.return_value = None
        
        # Send referral reward notification
        result = await notification_service.send_referral_reward_notification(
            telegram_id=123456789,
            amount=5.50,
            referee_name= "John Doe"
        )
        
        assert result is True
        
        # Verify message was sent with correct format
        mock_bot.send_message.assert_called_once()
        call_args = mock_bot.send_message.call_args
        
        assert call_args[1]["chat_id"] == 123456789
        assert "Реферальная награда!" in call_args[1]["text"]
        assert "John Doe" in call_args[1]["text"]
        assert "5.50" in call_args[1]["text"]
        assert call_args[1]["reply_markup"] is not None
    
    async def test_broadcast_to_active_users(
        self,
        notification_service,
        mock_bot,
        user_service: UserService,
        db_session: AsyncSession,
        default_loyalty_level: LoyaltyLevel,
    ):
        """Test broadcasting message to active users."""
        # Create users
        active_user1 = await user_service.create_user(
            telegram_id=111111111,
            username= "active1",
        )
        active_user2 = await user_service.create_user(
            telegram_id=222222222,
            username= "active2",
        )
        inactive_user = await user_service.create_user(
            telegram_id=333333333,
            username= "inactive",
        )
        await db_session.commit()
        
        # Deactivate one user
        await user_service.update_user_status(inactive_user.id, False)
        await db_session.commit()
        
        # Mock successful sends
        mock_bot.send_message.return_value = None
        
        # Broadcast message
        stats = await notification_service.broadcast_to_active_users(
            message="Broadcast test message"
        )
        
        # Verify statistics
        assert stats["sent"] == 2
        assert stats["failed"] == 0
        assert stats["total"] == 2
        
        # Verify messages were sent to active users only
        assert mock_bot.send_message.call_count == 2
        
        # Get all call arguments
        call_args_list = [call[1]["chat_id"] for call in mock_bot.send_message.call_args_list]
        assert 111111111 in call_args_list
        assert 222222222 in call_args_list
        assert 333333333 not in call_args_list
    
    async def test_format_promotion_message(
        self,
        notification_service,
    ):
        """Test promotion message formatting."""
        from shared.models import Promotion
        from datetime import datetime, timedelta
        
        # Create promotion
        promotion = Promotion(
            title="Special Offer",
            description= "Get 50% off on all drinks!",
            start_date=datetime(2024, 1, 15),
            end_date=datetime(2024, 1, 22),
        )
        
        # Format message
        message = notification_service._format_promotion_message(promotion)
        
        # Verify format
        assert "Special Offer" in message
        assert "Get 50% off on all drinks!" in message
        assert "15.01.2024" in message
        assert "22.01.2024" in message
        assert "🎉" in message