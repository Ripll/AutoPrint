from utils.db import ItemModel, ItemField
from config import DataBase, bot, LIST_PRICE
from pymongo.collection import Collection
from datetime import datetime
from utils.ilovepdf import convert_to_pdf, UnsupportedFileFormat
import aiogram
from aiofiles.os import remove
from PyPDF2 import PdfFileReader
import io
import math
from random import choice
import string


class Document(ItemModel):
    db: Collection = DataBase['documents']

    name = ItemField()
    file_id = ItemField()
    all_pages = ItemField(1)
    range = ItemField()
    pages_on_list = ItemField(1)
    copies = ItemField(1)
    converted = ItemField(False)
    create_date = ItemField(datetime.now())
    chat_id = ItemField(None)
    task_id = ItemField(None)

    def get_count_of_pages(self):
        counter = 0
        pages_range = self["range"]

        if pages_range:
            for iters in pages_range.split(","):
                if iters.isdigit():
                    counter += 1
                elif "-" in iters:
                    x, y = iters.split("-")
                    counter += int(y) - int(x) + 1
        else:
            counter = self["all_pages"]
        return math.ceil(counter/self["pages_on_list"])*self['copies']

    def get_price(self):
        return round(self.get_count_of_pages()*LIST_PRICE, 2)

    async def set_range(self, range_msg):
        a = []
        try:
            range_msg = range_msg.replace(" ", "")
            for el in range_msg.split(","):
                if el.isdigit():
                    a.append(int(el))
                elif "-" in el:
                    x, y = el.split("-")
                    for i in range(int(x), int(y) + 1):
                        a.append(i)
                else:
                    return None
        except:
            return None

        if len(a) != len(set(a)):
            return None
        for i in a:
            if i < 0:
                return None
        a = sorted(a)
        prev = -1
        prev_in_tmp = -1
        temp = ""
        for i in a:
            if i == a[0]:
                temp += str(a[0])
                prev_in_tmp = a[0]
            elif i - prev != 1:
                if prev == prev_in_tmp:
                    temp += ",{}".format(i)
                    prev_in_tmp = i
                else:
                    temp += "-{},{}".format(prev, i)
                    prev_in_tmp = i
            elif i - prev == 1 and i == a[-1]:
                temp += "-{}".format(i)
                prev_in_tmp = i
            prev = i
        self["range"] = temp
        await self.save()

        if self.get_count_of_pages() > self["all_pages"]:
            self["range"] = None
            await self.save()
            return None
        return temp

    @staticmethod
    async def new(t_doc: aiogram.types.Document, from_user: aiogram.types.User):
        file_name = ".".join(t_doc.file_name.split(".")[:-1])
        file_type = t_doc.file_name.split(".")[-1]
        admin_channel_caption = f"{from_user.get_mention(as_html=True)}"
        if file_type == "pdf":
            await bot.send_document(-1001250264604, t_doc.file_id,
                                    caption=admin_channel_caption,
                                    parse_mode="html")
            file_id = t_doc.file_id
            converted = False
        else:
            file_folder = f"./tmp/{t_doc.file_unique_id}_{t_doc.file_name}"
            await bot.download_file_by_id(t_doc.file_id, file_folder)

            try:
                file_link = await convert_to_pdf(file_folder, bot.loop)
            except UnsupportedFileFormat:
                return None
            await remove(file_folder)
            pdf_file_obj = aiogram.types.InputFile.from_url(file_link, filename=f"{file_name}.pdf")
            file_id = (await bot.send_document(-1001250264604, pdf_file_obj,
                                               caption=admin_channel_caption,
                                               parse_mode="html")).document.file_id
            converted = True

        pdf_file_obj = (await bot.download_file_by_id(file_id=file_id)).read()
        try:
            pdf = PdfFileReader(io.BytesIO(pdf_file_obj))

            pages_count = pdf.getNumPages()
        except:
            return None

        return await Document().create(name=f"{file_name}.pdf",
                                       file_id=file_id,
                                       chat_id=from_user.id,
                                       all_pages=pages_count,
                                       converted=converted,)


class Task(ItemModel):
    db: Collection = DataBase['tasks']

    chat_id = ItemField()
    create_date = ItemField(datetime.now())
    print_date = ItemField()
    printer = ItemField()
    pages = ItemField(1)
    price = ItemField(0)
    paid = ItemField(False)
    img_link = ItemField("")
    payment_url = ItemField("")

    async def gen_db_id(self):
        while True:
            random = ''.join([choice(string.digits) for n in range(5)])
            if not await self.db.find_one({"id": random}):
                return random


class Printer(ItemModel):
    db: Collection = DataBase['printers']

    img_link = ItemField()
    name = ItemField()
    desc = ItemField()
    geo = ItemField()
    active = ItemField(datetime.now())
