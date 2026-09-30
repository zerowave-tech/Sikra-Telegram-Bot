from aiogram.fsm.state import State, StatesGroup

class Ask(StatesGroup):
    waiting = State()