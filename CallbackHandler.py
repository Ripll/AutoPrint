from utils.callback_helper import CallbackQueryHelper
from models.items import Document, Task, Printer
from config import img_uploader, bot
from utils.gen_img import get_image
from models.msg import TaskMsg
from utils.wfp_api import get_invoice

class CallbackHandler(CallbackQueryHelper):
    async def document(self, cmd, d_id, param=None):
        doc = await Document().get(d_id)
        if doc['task_id']:
            self.text = "Документ вже чекає друку"
            self.show_alert = True
        elif cmd == "del":
            await doc.delete()
            self.text = "Документ видалено з кошику!"
            self.show_alert = True
            await self.delete_msg()
        elif cmd == "set_copies":
            copies = int(param)
            if copies == 0:
                self.text = "Мінімальна кількість копій - одна"
                self.show_alert = True
            else:
                doc['copies'] = copies
                await doc.save()
                await self.to_msg("DocumentMsg", "edit", d_id, 'copies')
        elif cmd == "set_pages_on_list":
            pages_on_list = int(param)
            doc['pages_on_list'] = pages_on_list
            await doc.save()
            await self.to_msg("DocumentMsg", "edit", d_id, 'pages_on_list')

    async def create_task(self):
        if await Document().db.count_documents({"chat_id": self.user['chat_id'], "task_id": None}) == 0:
            self.text = "У кошику немає документів"
            self.show_alert = True
        else:
            task = await Task().create(chat_id=self.user['chat_id'])
            pages = 0
            total_price = 0
            task['img_link'] = await img_uploader.upload(get_image(task['id']))
            async for i in Document().db.find({"chat_id": self.user['chat_id'],
                                               "task_id": None}):
                doc = await Document().get(i['id'])
                doc['task_id'] = task['id']
                total_price += doc.get_price()
                pages += doc.get_count_of_pages()
                await doc.save()
            task['price'] = round(self.user.get_price_with_discount(total_price), 2)
            task['pages'] = pages
            task["payment_url"] = await get_invoice(self.user['chat_id'], task['id'], task['price'])
            await task.save()

            msg, kb = await TaskMsg(self.user).def_msg(task['id'])
            await self.edit(msg, kb)

    async def printer(self, cmd, p_id):
        pr = await Printer().get(p_id)
        if cmd == "geo":
            await bot.send_location(self.user['chat_id'], pr['geo'][1], pr['geo'][0])
        elif cmd == "del":
            await pr.delete()
            await self.delete_msg()
            self.text = "Успішно видалено!"
            self.show_alert = True


