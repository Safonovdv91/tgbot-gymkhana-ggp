from aiogram.fsm.state import State, StatesGroup


class BotStates(StatesGroup):
    Get_betting_nickname = State()
    Doing_bet = State()
    Get_betting_time = State()
    Get_betting_sure = State()

    GGP_CLASS_SUBSCRIBE = State()
    Broadcasting = State()
