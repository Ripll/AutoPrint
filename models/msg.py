from utils.msg import MsgModel
from lang import Lang
from aiogram import types
from datetime import datetime, timedelta
from models.items import Document, Task, Printer
from models.db import User


class DocumentMsg(MsgModel):
    async def def_msg(self, doc_id):
        doc = await Document().get(doc_id)
        msg = ""
        if doc['converted']:
            msg += "🛑 <b>Файл автоматично конвертований в PDF, перевірте коректність</b>\n\n"
        msg += f"🛒 Файл у кошику, тисніть /print для друку\n\n" \
               f"<code>Ціна: {doc.get_price():.2f}грн.</code>"

        kb = types.InlineKeyboardMarkup()
        kb.row(types.InlineKeyboardButton(text="Налаштування",
                                          callback_data=f"to_msg:DocumentMsg:settings:{doc['id']}"),
               types.InlineKeyboardButton(text="Видалити",
                                          callback_data=f"document:del:{doc['id']}"))

        return msg, doc['file_id'], kb

    async def settings(self, doc_id):
        doc = await Document().get(doc_id)
        msg = f"Налаштування:\n\n" \
              f"<b>Кількість копій:</b> {doc['copies']}\n" \
              f"<b>Сторінок на листі:</b> {doc['pages_on_list']}\n" \
              f"<b>Діапазон:</b> {(doc['range'], 'Всі сторінки')[doc['range'] is None]}\n\n" \
              f"Натсніть на те, що хочете змінити 👇"
        kb = types.InlineKeyboardMarkup()
        kb.row(types.InlineKeyboardButton(text="К-сть копій",
                                          callback_data=f"to_msg:DocumentMsg:edit:{doc_id}:copies"),
               types.InlineKeyboardButton(text="Сторінок на листі",
                                          callback_data=f"to_msg:DocumentMsg:edit:{doc_id}:pages_on_list"))
        kb.add(types.InlineKeyboardButton(text="Діапазон", callback_data=f"to_state:enter_range:{doc_id}"))
        kb.add(types.InlineKeyboardButton(text="🔙 Зберегти", callback_data=f"to_msg:DocumentMsg:def_msg:{doc_id}"))
        return msg, doc['file_id'], kb

    async def edit(self, doc_id, edit_type):
        doc = await Document().get(doc_id)
        msg = "Налаштування:\n\n"

        kb = types.InlineKeyboardMarkup()
        if edit_type == "copies":
            msg += f"<b>Кількість копій:</b> {doc['copies']}"
            kb.row(types.InlineKeyboardButton(text="-",
                                              callback_data=f"document:set_copies:{doc['id']}:{doc['copies'] - 1}"),
                   types.InlineKeyboardButton(text="+",
                                              callback_data=f"document:set_copies:{doc['id']}:{doc['copies'] + 1}"))
        elif edit_type == "pages_on_list":
            msg += f"<b>Сторінок на листі:</b> {doc['pages_on_list']}"
            kb.row(*[types.InlineKeyboardButton(text=str(i),
                                                callback_data=f"document:set_pages_on_list:{doc_id}:{i}") for i in
                     [1, 2, 4, 6]])
        kb.add(types.InlineKeyboardButton(text="🔙 Зберегти", callback_data=f"to_msg:DocumentMsg:settings:{doc_id}"))

        return msg, doc['file_id'], kb


class CartMsg(MsgModel):
    async def def_msg(self):
        if not await Document().db.count_documents({"chat_id": self.user['chat_id'], "task_id": None}):
            msg = "Кошик порожній"
            kb = None
        else:
            msg = "Документы до друку:\n\n"
            price = 0
            async for i in Document().db.find({"chat_id": self.user['chat_id'],
                                               "task_id": None}):
                doc = await Document().find_obj({"id": i['id']})
                msg += f"<b>{doc['name']}</b> -> <i>{doc.get_price():.2f}грн.</i>\n"
                price += doc.get_price()

            price_with_disc = round(self.user.get_price_with_discount(price), 2)
            msg += f"\nВсього до сплаты: <b>{price_with_disc:.2f}грн.</b>" \
                   f" <i>(знижка {price - price_with_disc:.0f}грн)</i>\n\n" \
                   f"Все вірно?"
            kb = types.InlineKeyboardMarkup()
            kb.add(types.InlineKeyboardButton(text="Так, продовжити", callback_data="create_task"))
            kb.add(types.InlineKeyboardButton(text="Ні, змінити", switch_inline_query_current_chat="docs"))

        return msg, kb


class TaskMsg(MsgModel):
    async def def_msg(self, t_id):
        task = await Task().get(t_id)
        msg = f"Супер!\n\n" \
              f"Обов'язково сплати рахунок натиснувши кнопку <b>\"Сплатити\"</b> та друкуй на зручній тобі" \
              f" точці ввівши код <b>{t_id}</b>\n\n" \
              f"<a href='{task['img_link']}'>&#8203;</a>"
        kb = types.InlineKeyboardMarkup()
        kb.row(types.InlineKeyboardButton(text="Сплатити", url=task['payment_url']),
               types.InlineKeyboardButton(text="Найближча точка", switch_inline_query_current_chat=""))

        return msg, kb


class LcMsg(MsgModel):
    async def def_msg(self):
        msg = f"Привіт, <b>{self.user['full_name']}</b>!\n" \
              f"Твоя знижка: {self.user['discount']:.0f}%"
        kb = types.InlineKeyboardMarkup()
        kb.row(types.InlineKeyboardButton(text="Історія друку", callback_data="to_msg:LcMsg:history"),
               types.InlineKeyboardButton(text="Як заробити знижку?", callback_data="show_msg:loyalty_program"))
        return msg, kb

    async def history(self):
        msg = "Останні 10 замовлень:\n\n"
        async for i in Task().db.find({"chat_id": self.user['chat_id']}).sort("create_date", -1).limit(10):
            if not i['paid']:
                status = f"<a href='{i['payment_url']}'>чекає на оплату {i['price']:.2f}грн</a>"
            elif i['paid'] and not i['print_date']:
                status = "🔄 сплачено. Чекає друку"
            elif i['print_date']:
                status = "✅ надруковано"
            else:
                status = "помилка..."
            msg += f"<b>{i['id']}</b> -> {status}\n"

        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton(text=Lang.back_btn, callback_data="to_msg:LcMsg:def_msg"))

        return msg, kb


class PrinterMsg(MsgModel):
    async def def_msg(self, p_id, kb_type=False):
        pr = await Printer().get(p_id)
        msg = f"<b>{pr['name']}</b>\n\n" \
              f"<i>{pr['desc']}</i>" \
              f"<a href='{pr['img_link']}'>&#8203;</a>"

        kb = types.InlineKeyboardMarkup(row_width=2)
        if not kb_type:
            kb.add(types.InlineKeyboardButton(text="🗺 Як знайти?", callback_data=f"printer:geo:{pr['id']}"))
            if self.user.is_admin():
                msg += f"\n\n<code>ID: {pr['id']}</code>"
                kb.row(types.InlineKeyboardButton(text="Змінити",
                                                  callback_data=f"to_msg:PrinterMsg:def_msg:{pr['id']}:edit"),
                       types.InlineKeyboardButton(text="Видалити",
                                                  callback_data=f"to_msg:PrinterMsg:def_msg:{pr['id']}:delete"))
        elif kb_type == "edit":
            kb.add(*[types.InlineKeyboardButton(text=i,
                                                callback_data=f"to_state:add_printer:{i}:1:{pr['id']}") for i in
                     pr.get_all_params()])
            kb.add(
                types.InlineKeyboardButton(text=Lang.back_btn, callback_data=f"to_msg:PrinterMsg:def_msg:{pr['id']}"))
        elif kb_type == "delete":
            msg += "\n\nВи впевнені що хочете видалити цю точку?"
            kb.add(types.InlineKeyboardButton(text="Так, видалити!", callback_data=f"printer:del:{pr['id']}"))
            kb.add(
                types.InlineKeyboardButton(text=Lang.back_btn, callback_data=f"to_msg:PrinterMsg:def_msg:{pr['id']}"))
        return msg, kb


class AdminStatMsg(MsgModel):
    async def def_msg(self):
        msg = f"Всього користувачів: {await self.user.db.count_documents({})}" \
              f" (+{await self.user.db.count_documents({'create_date': {'$gt': datetime.now()-timedelta(days=7)}})}/тиждень)\n" \
              f"Надруковано : {await Task.db.count_documents({'print_date': {'$lt': datetime.now()}})}" \
              f" (+{await Task.db.count_documents({'print_date': {'$gt': datetime.now()-timedelta(days=7)}})}/тиждень)"
        kb = None
        return msg, kb


class AdminUserMsg(MsgModel):
    async def def_msg(self, u_id):
        user = await User(u_id).create()
        msg = f"Ім'я: {user.get_mention()}\n" \
              f"Нікнейм: @{user['username']}\n\n" \
              f"Знижка: {user['discount']}%"
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton(text="Замовлення",
                                          switch_inline_query_current_chat=f"tasks:{user['chat_id']}"),
               types.InlineKeyboardButton(text="Змінити знижку",
                                          callback_data=f"to_state:set_user_disc:{user['chat_id']}"))
        return msg, kb


class AdminTaskMsg(MsgModel):
    async def def_msg(self, t_id):
        task = await Task().get(t_id)
        user = await User(task['chat_id']).create()
        msg = f"Користувач: {user.get_mention()}\n" \
              f"Номер: {task['id']}\n" \
              f"Сторінок до друку: {task['pages']}\n" \
              f"Ціна: {task['price']}грн.\n\n"
        kb = types.InlineKeyboardMarkup()
        kb.row(types.InlineKeyboardButton(text=('❌ Не сплачено', '✅ Сплачено')[task['paid']],
                                          callback_data=f"task:{t_id}:change_paid"),
               types.InlineKeyboardButton(text=('Не надруковано', '📑 Надруковано')[bool(task['print_date'])],
                                          callback_data=f"task:{t_id}:change_print_date")
               )
        kb.row(types.InlineKeyboardButton(text="Перерахувати", callback_data=f"task:{t_id}:calculate"),
               types.InlineKeyboardButton(text="Файли", switch_inline_query_current_chat=f"files:{t_id}"))

        return msg, kb