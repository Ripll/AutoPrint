from config import logger, bot, geocoder
from .models.db import User
from .models.items import Printer, Document
from .models.msg import DocumentMsg, PrinterMsg
from aiogram import types
from geopy.distance import vincenty
from lang import Lang


class InlineSearchHandler:
    user: User

    def __init__(self, message: types.InlineQuery):
        self.message = message
        self.location = message.location
        self.query = message.query
        self.q_id = message.id

        self.off = int(message.offset) if message.offset else 0
        self.max_res = 10
        self.next_offset = self.off + self.max_res
        self.pos = []

    @logger.catch
    async def handle(self):
        self.user = await User(self.message.from_user).create()
        result = []
        if self.query == "docs":
            async for i in Document().db.find({"chat_id": self.user['chat_id'],
                                               "task_id": None}).skip(self.off).limit(self.max_res):
                title = i["name"]
                desc = "Налаштування файлу"

                click_text = types.InputTextMessageContent(Lang.inline_send_file, parse_mode="html")

                result.append(types.InlineQueryResultArticle(id="doc_"+str(i["id"]),
                                                             title=title,
                                                             input_message_content=click_text,
                                                             description=desc))
        else:
            if self.query:
                res = await geocoder.get_geo_by_addr(self.query)
                self.pos = [float(i) for i in res['Point']['pos'].split()]
            elif self.location:
                self.pos = [self.location.longitude, self.location.latitude]
            temp_result = []
            async for doc in Printer.db.find({}):
                temp_result.append(doc)
            if self.pos:
                temp_result = sorted(temp_result,
                                     key=lambda x: vincenty((self.pos[0], self.pos[1]), (x['geo'][0], x['geo'][1])).km)

            for i in temp_result[self.off:self.off+self.max_res]:
                msg, kb = await PrinterMsg(self.user).def_msg(i['id'])
                title = i["name"]
                desc = i['desc']

                if self.pos:
                    dist = vincenty((self.pos[0], self.pos[1]), (i['geo'][0], i['geo'][1])).km
                    msg += f"\n\n📍 {dist:.2f}км. від тебе"
                    title += f"  (📍 {dist:.2f}км. від тебе)"

                click_text = types.InputTextMessageContent(msg, parse_mode="html")

                result.append(types.InlineQueryResultArticle(id="p_" + str(i["_id"]),
                                                             title=title,
                                                             thumb_url=i['img_link'],
                                                             input_message_content=click_text,
                                                             description=desc,
                                                             reply_markup=kb))

        if not result and self.off == 0:
            t = Lang.inline_empty_result
            result.append(types.InlineQueryResultArticle(id="1_1",
                                                         title=t,
                                                         description=t,
                                                         input_message_content=types.InputTextMessageContent(
                                                                    message_text=t)))
            self.next_offset = None
        await bot.answer_inline_query(self.q_id, result, cache_time=1, next_offset=self.next_offset)


class ProcessChosen:
    def __init__(self, message):
        self.message = message

    async def handle(self):
        cmd, object_id = self.message.result_id.split("_")
        if cmd == "doc":
            user = await User(self.message.from_user).create()
            msg, file_id, kb = await DocumentMsg(user).def_msg(object_id)
            await bot.send_document(user['chat_id'], file_id, caption=msg, reply_markup=kb, parse_mode="html")
