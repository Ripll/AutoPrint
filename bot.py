from aiogram import executor, types, Dispatcher
from StateHandler import StateHandler
from CallbackHandler import CallbackHandler
from InlineSearchHandler import InlineSearchHandler, ProcessChosen
from models.db import User
from config import bot, logger
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from lang import Lang

dp = Dispatcher(bot)
logger_middleware = LoggingMiddleware()
logger_middleware.logger = logger

dp.middleware.setup(logger_middleware)


@dp.message_handler(lambda x: x.text in [Lang.inline_send_file, Lang.inline_empty_result] or x.reply_markup)
async def pass_msg_with_btns(message):
    pass


@dp.message_handler(commands=['start'])
async def start_cmd_handler(message: types.Message):
    user = await User(message.from_user).create()
    user['state'] = "start"
    await StateHandler(user, message, first=True)


@dp.message_handler(content_types=['text', 'photo', 'location', 'document'])
async def all_msg_handler(message: types.Message):
    user = await User(message.from_user).create()
    await StateHandler(user, message)


# Use multiple registrators. Handler will execute when one of the filters is OK
@dp.callback_query_handler()
async def inline_kb_answer_callback_handler(query: types.CallbackQuery):
    user = await User(query.from_user).create()
    await CallbackHandler(user, query)


@dp.inline_handler()
async def inline_search_handler(message: types.InlineQuery):
    await InlineSearchHandler(message).handle()


@dp.chosen_inline_handler()
async def choosen_handler(message: types.ChosenInlineResult):
    await ProcessChosen(message).handle()


if __name__ == "__main__":
    executor.start_polling(dp)
