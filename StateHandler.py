from utils.state_helper import StateHelper
from lang import Lang
from config import bot, ALLOWED_FORMATS, img_uploader, logger, DataBase
from aiogram import types
from aiogram.dispatcher import Dispatcher
from models.msg import *
from models.items import *
from models.db import User
from utils.broadcast import broadcaster
from utils.types_utils import *
import re


class StateHandler(StateHelper):
    async def start(self):
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("Доступні формати", callback_data="show_msg:allowed_formats"))
        await self.send_msg(Lang.start_msg, kb)
        await self.to_state("wait_doc")

    async def wait_doc(self):
        if self.first:
            msg = "Головне меню"
            kb = self.kb()
            kb.add(*self.btn(Lang.menu_btns))
            if self.user.is_admin():
                kb.add(self.btn(Lang.admin_btn))
            await self.send_msg(msg, kb)
        elif self.message.document:
            document_type = self.message.document.file_name.split(".")[-1]

            if self.message.document.file_size/1000000 > 10:
                await self.send_msg(Lang.error_filesize_msg)
                return
            if document_type not in ALLOWED_FORMATS:
                kb = types.InlineKeyboardMarkup()
                kb.add(types.InlineKeyboardButton("Доступні формати", callback_data="show_msg:allowed_formats"))
                await self.send_msg(Lang.error_fileformat_msg, kb)
                return
            else:
                await bot.send_chat_action(self.chat_id, "upload_document")
                doc = await Document.new(self.message.document, self.message.from_user)
                msg, file_id, kb = await DocumentMsg(self.user).def_msg(doc['id'])
                await bot.send_document(self.chat_id,
                                        caption=msg,
                                        document=file_id,
                                        reply_markup=kb,
                                        parse_mode="html")
        elif self.message.text == Lang.menu_btns[0]:
            msg, kb = await LcMsg(self.user).def_msg()
            await self.send_msg(msg, kb)
        elif self.message.text == Lang.menu_btns[1] or self.message.text == "/print":
            msg, kb = await CartMsg(self.user).def_msg()
            await self.send_msg(msg, kb)
        elif self.message.text == Lang.menu_btns[2]:
            await self.send_msg(Lang.how_to_print)
        elif self.message.text == Lang.menu_btns[3]:
            kb = types.InlineKeyboardMarkup()
            kb.add(types.InlineKeyboardButton(text="Всі точки", switch_inline_query_current_chat=""))
            await self.send_msg(Lang.info_msg, kb)
        elif self.user.is_admin() and self.message.text == Lang.admin_btn:
            await self.to_state("admin_panel")
        else:
            await self.send_msg(Lang.error_msg)

    async def enter_range(self, d_id):
        doc = await Document().get(d_id)
        if self.first:
            kb = self.kb()
            kb.add(*self.btn([Lang.all_btn, Lang.back_btn]))
            msg = f"Відправте мені новий діапазон для <b>{doc['name']}</b>" \
                  f" <i>(Всього сторінок {doc['all_pages']})</i>:\n\n" \
                  "Для вводу діапазону сторінок використовується дефіс. " \
                  "Відокремлюйте кожну сторінку або діапазон комою і пробілом (наприклад, <i>4, 7, 15-34, 56</i>)."
            await self.send_msg(msg, kb)
        else:
            if self.message.text == Lang.back_btn:
                pass
            elif self.message.text == Lang.all_btn:
                doc['range'] = None
                await doc.save()
            elif await doc.set_range(self.message.text):
                pass
            else:
                await self.send_msg("Невірний формат. Спробуйте ще раз:")
                return
            kb = self.kb()
            kb.add(*self.btn(Lang.menu_btns))
            if self.user.is_admin():
                kb.add(self.btn(Lang.admin_btn))
            await self.send_msg("Збережено!", kb)
            msg, file_id, kb = await DocumentMsg(self.user).def_msg(doc['id'])
            await bot.send_document(self.user['chat_id'],
                                    file_id,
                                    caption=msg,
                                    reply_markup=kb,
                                    parse_mode='html')
            self.user['state'] = "wait_doc"

    async def add_printer(self, step=None, edit=False, p_id=None):
        steps = Printer().get_all_params()

        if not step:
            step = steps[0]

        next_state = steps[steps.index(step)+1] if step != steps[-1] else 'start'
        success = False

        if not self.first and self.message:
            if self.message.text == Lang.back_btn:
                await self.to_state(f"add_printer:{steps[max(0, steps.index(step)-1)]}")
                return
            elif self.message.text == Lang.cancel_btn:
                await self.to_state("start")
                return
            elif self.message.text == Lang.skip_btn:
                self.saver[step] = None
                await self.to_state(f"add_printer:{next_state}")
                return

        kb = self.kb()
        kb.add(*self.btn([Lang.back_btn, Lang.cancel_btn]))

        if self.first and step == "img_link":
            await self.send_msg("Відправте фото:", kb)
        elif step == "img_link" and self.message.photo:
            file = await bot.get_file(self.message.photo[-1].file_id)
            result_img = await img_uploader.upload(bot.get_file_url(file.file_path))
            self.saver['img_link'] = result_img
            success = True

        elif self.first and step == "name":
            await self.send_msg("Введіть назву локації:", kb)
        elif step == "name" and self.message.text:
            self.saver['name'] = self.message.text
            success = True

        elif self.first and step == "desc":
            await self.send_msg("Введіть опис локації:", kb)
        elif step == "desc" and self.message.text:
            self.saver['desc'] = self.message.text
            success = True

        elif self.first and step == "geo":
            await self.send_msg("Відправте геолокацію точки:", kb)
        elif step == "geo" and self.message.location:
            self.saver['geo'] = [self.message.location.longitude, self.message.location.latitude]
            success = True
        else:
            await self.send_msg(Lang.error_msg)

        if not self.first and success:
            if not edit:
                if next_state == 'start':
                    data = {}
                    for i in steps:
                        try:
                            data[i] = self.saver[i]
                        except Exception as e:
                            logger.info(e)
                    item = await Printer().create(**data)
                    msg, kb = await PrinterMsg(self.user).def_msg(item['id'])
                    await self.send_msg(msg, kb)
                    await self.to_state("start")
                else:
                    await self.to_state("add_printer:"+next_state)
            else:
                pr = await Printer().get(p_id)
                pr[step] = self.saver[step]
                await pr.save()
                await self.to_state("start")

    async def admin_panel(self):
        if self.first:
            msg = "Адмін панель"
            kb = self.kb()
            kb.add(*self.btn(Lang.admin_btns))
            kb.add(self.btn(Lang.back_btn))
            await self.send_msg(msg, kb)
        elif self.message.text == Lang.admin_btns[0]:  # Додати принтер
            await self.to_state("add_printer")
        elif self.message.text == Lang.admin_btns[1]:  # Броадкаст
            await self.to_state("broadcast")
        elif self.message.text == Lang.admin_btns[2]:  # Статистика
            msg, kb = await AdminStatMsg(self.user).def_msg()
            await self.send_msg(msg, kb)
        elif self.message.text == Lang.admin_btns[3]:  # Пошук задачі
            await self.to_state("find_task")
        elif self.message.text == Lang.admin_btns[4]:  # Пошук користувача
            await self.to_state("find_user")
        elif self.message.text == Lang.back_btn:
            await self.to_state("start")
        else:
            await self.send_msg(Lang.error_msg)

    async def broadcast(self):
        if self.first:
            msg = "Введіть повідомлення для броадкасту:"
            kb = self.kb()
            kb.add(self.btn(Lang.back_btn))
            await self.send_msg(msg, kb)
        elif self.message.text == Lang.back_btn:
            await self.to_state("admin_panel")
        else:
            dp = Dispatcher.get_current()
            dp.loop.create_task(broadcaster(self.message.text))
            await self.to_state("admin_panel")

    async def find_user(self):
        if self.first:
            msg = "Для пошуку введіть один з ідентифікаторів на вибір:\n" \
                  "  <b>- Нікнейм\n" \
                  "  - Логін\n" \
                  "  - ID</b>"
            kb = self.kb()
            kb.add(self.btn(Lang.back_btn))
            await self.send_msg(msg, kb)
        elif self.message.text == Lang.back_btn:
            await self.to_state("admin_panel")
        else:
            if is_int(self.message.text):
                user = await DataBase['users'].find_one({"chat_id": int(self.message.text)})
            else:
                user = await DataBase['users'].find_one({'username': re.compile(self.message.text, re.IGNORECASE)})
                if not user:
                    user = await DataBase['users'].find_one({'full_name': re.compile(self.message.text, re.IGNORECASE)})

            if not user:
                await self.send_msg("Користувача не знайдено")
                return

            msg, kb = await AdminUserMsg(self.user).def_msg(user['chat_id'])
            await self.send_msg(msg, kb)

    async def find_task(self):
        if self.first:
            msg = "Для пошуку введіть ID завдання:"
            kb = self.kb()
            kb.add(self.btn(Lang.back_btn))
            await self.send_msg(msg, kb)
        elif self.message.text == Lang.back_btn:
            await self.to_state("admin_panel")
        elif self.message.text and self.message.text.isdigit():
            task = await Task.db.find_one({"id": self.message.text})
            if task:
                msg, kb = await AdminTaskMsg(self.user).def_msg(task['id'])
                await self.send_msg(msg, kb)
            else:
                await self.send_msg("Задачі не знайдено.")
        else:
            await self.send_msg(Lang.error_msg)

    async def set_user_disc(self, u_id):
        user = await User(int(u_id)).create()
        if self.first:
            msg = f"Вкажіть нову знижку для {user['full_name']}:"
            kb = self.kb()
            kb.add(self.btn(Lang.back_btn))
            await self.send_msg(msg, kb)
        elif is_float(self.message.text) and 0 <= float(self.message.text) <= 100:
            await self.send_msg("Успішно змінено!")
            user['discount'] = float(self.message.text)
            await user.save()
            await self.to_state("admin_panel")
            msg, kb = await AdminUserMsg(self.user).def_msg(user['chat_id'])
            await self.send_msg(msg, kb)
        else:
            await self.send_msg(Lang.error_msg)
