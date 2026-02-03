"""Bot FSM states."""
from aiogram.fsm.state import State, StatesGroup


class ReviewStates(StatesGroup):
    """States for review collection."""
    waiting_for_review = State()