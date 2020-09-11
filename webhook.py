from config import bot, WEBHOOK_URL, WEBHOOK_PATH, WEBHOOK_HOST, WEBHOOK_PORT, SSL_CERT, SSL_PRIV, logger, DataBase
from bot import dp
from aiogram.dispatcher.webhook import get_new_configured_app
import ssl
from aiohttp import web
from utils.wfp_api import gen_answer


async def wfp_handler(request):
    data = await request.json()
    chat_id, task_id, _ = data["orderReference"].split("_")
    if data["transactionStatus"] == "Pending":
        task = await DataBase['tasks'].find_one({"id": task_id})
        paid_amount = float(data['amount'])
        if paid_amount >= task['price']:
            await bot.send_message(chat_id, f"Рахунок {task_id} сплачено!")
            await DataBase['tasks'].update_one({"_id": task['_id']},
                                               {"$set": {"paid": True}})
        else:
            await bot.send_message(chat_id, f"Недостатньо коштів для сплати {task_id} :с")
    return web.Response(text=gen_answer(data))


async def on_startup(app):
    url = WEBHOOK_URL
    certificate = open(SSL_CERT, 'r')
    await bot.set_webhook(url=url,
                          certificate=certificate)
    # insert code here to run it after start


async def on_shutdown(app):
    logger.warning('Shutting down..')
    # insert code here to run it before shutdown

    # Remove webhook (not acceptable in some cases)
    await bot.delete_webhook()

    logger.warning('Bye!')


if __name__ == '__main__':

    app = get_new_configured_app(dispatcher=dp, path=WEBHOOK_PATH)
    app.router.add_route("*", "/wfp", wfp_handler, name="wfp_handler")

    # Setup event handlers.
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    # Generate SSL context
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain(SSL_CERT, SSL_PRIV)

    # Start web-application.
    web.run_app(app, host=WEBHOOK_HOST, port=WEBHOOK_PORT, ssl_context=context)
