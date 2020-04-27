from models.db import User, Saver
from aiogram import types
from config import bot


class StateHelper:
    user: User
    saver: Saver
    chat_id: int = 0
    options: list

    def __init__(self, user: User, message: types.Message = None, first: bool = False):
        self.user = user
        self.message = message
        self.first = first

    def __await__(self):
        return self.async_init().__await__()

    async def async_init(self):
        self.saver = await Saver(self.user['chat_id']).create()
        if self.message:
            self.chat_id = self.message.chat.id

        await self.execute(self.first)
        await self.user.save()
        await self.saver.save()

    async def execute(self, first):
        self.first = first
        options = self.user["state"].split(":")[1:]
        await getattr(self, self.user["state"].split(":")[0])(*options)

    async def to_state(self, state, first=True):
        self.user['state'] = state
        await self.execute(first=first)

    @staticmethod
    def kb():
        return types.ReplyKeyboardMarkup(row_width=2,
                                         resize_keyboard=True)

    @staticmethod
    def btn(btns):
        if type(btns) == str:
            return types.KeyboardButton(btns)
        else:
            return [types.KeyboardButton(i) for i in btns]

    async def send_msg(self, msg, kb=None, chat_id=None, disable_web_page_preview=False):
        await bot.send_message((self.user['chat_id'], chat_id)[bool(chat_id)],
                               text=msg, reply_markup=kb, parse_mode="html",
                               disable_web_page_preview=disable_web_page_preview)
