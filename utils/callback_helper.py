from models.db import User, Saver
from aiogram import types
from config import bot
import models.msg as msg_models
from StateHandler import StateHandler
from lang import Lang


class CallbackQueryHelper:
    saver: Saver
    message = None
    text = None
    show_alert = False

    def __init__(self, user: User, reply: types.CallbackQuery):
        self.user = user
        self.reply = reply

    def __await__(self):
        return self.async_init().__await__()

    async def async_init(self):
        self.saver = await Saver(self.reply.from_user).create()
        self.message = self.reply.message

        cmd = self.reply.data.split(":")[0]
        other = self.reply.data.split(":")[1:]

        await getattr(self, cmd)(*other)

        try:
            await bot.answer_callback_query(callback_query_id=self.reply.id, text=self.text, show_alert=self.show_alert)
        except Exception as e:
            print(e)

        await self.user.save()
        await self.saver.save()


    async def to_state(self, *state):
        try:
            await bot.delete_message(
                chat_id=self.message.chat.id,
                message_id=self.message.message_id
            )
        except:
            pass
        self.user["state"] = ":".join([str(i) for i in state])
        await StateHandler(self.user, first=True)

    async def edit(self, new_msg, new_kb=None):
        if self.message:
            await bot.edit_message_text(chat_id=self.message.chat.id,
                                        message_id=self.message.message_id,
                                        text=new_msg,
                                        reply_markup=new_kb,
                                        parse_mode="html")
        else:
            await bot.edit_message_text(chat_id=None,
                                        inline_message_id=self.reply.inline_message_id,
                                        text=new_msg,
                                        reply_markup=new_kb,
                                        parse_mode="html")

    async def edit_caption(self, new_caption, new_kb=None):
        if self.message:
            await bot.edit_message_caption(
                chat_id=self.message.chat.id,
                message_id=self.message.message_id,
                caption=new_caption,
                reply_markup=new_kb,
                parse_mode="html"
            )
        else:
            await bot.edit_message_caption(chat_id=None,
                                           inline_message_id=self.reply.inline_message_id,
                                           caption=new_caption,
                                           reply_markup=new_kb,
                                           parse_mode="html")

    async def to_msg(self, msg_class, msg_method, *params):
        (returned_data) = await getattr(getattr(msg_models, msg_class)(self.user), msg_method)(*params)
        if len(returned_data) == 2:
            msg, kb = returned_data
            await self.edit(msg, kb)
        elif len(returned_data) == 3:
            caption, file_id, kb = returned_data
            await self.edit_caption(caption, kb)

    async def show_msg(self, msg_name):
        self.text = Lang.__dict__[msg_name]
        self.show_alert = True

    async def delete_msg(self):
        try:
            await bot.delete_message(
                chat_id=self.message.chat.id,
                message_id=self.message.message_id
            )
        except:
            pass

    async def skip(self):
        pass
