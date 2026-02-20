from aiogram.fsm.state import State, StatesGroup

class CardPaymentStates(StatesGroup):
    waiting_for_username = State()
    waiting_for_payment_screenshot = State()

class ReviewStates(StatesGroup):
    waiting_for_review = State()
    waiting_for_rating = State()

class BroadcastStates(StatesGroup):
    waiting_for_broadcast_text = State()

class StarsOrderStates(StatesGroup):
    waiting_for_stars_amount = State()