from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import BaseFilter
from aiogram.types import Message


class ChatTypeFilter(BaseFilter):
    def __init__(self, chat_type):
        self.chat_type = chat_type

    async def __call__(self, msg: Message, *args, **kwargs):
        return msg.chat.type == self.chat_type


class UserStates(StatesGroup):
    set_balance = State()
    set_target = State()

    get_name_operation = State()
    get_sum_operation = State()
    confirm_operation = State()


