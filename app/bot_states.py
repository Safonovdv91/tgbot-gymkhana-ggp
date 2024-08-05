from aiogram.fsm.state import StatesGroup, State


class BotStates(StatesGroup):
    Get_betting_nickname = State()
    Get_betting_time = State()
    Get_betting_sure = State()
