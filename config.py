from aiogram import Bot
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient
from requests import get
from utils.imgbb import IMGBB
from utils.yandex_geocode import YandexGeocoder


img_uploader = IMGBB("56e5d580e7577a258456ac2c0d0c4fe4")

uri = "mongodb://user:Ololosha123@45.76.32.134:27017/admin"

geocoder = YandexGeocoder("8b35930e-d3b0-4a7b-aa34-fa235b7b9959")

API_TOKEN = '902390770:AAE3lD53537k7tM5e9kGWuaT6lfFGJrZiG4'
ADMINS = [152950074]
ALLOWED_FORMATS = ['pdf', 'doc', 'docx', 'odt', 'ott', 'stw', 'sdw', 'sxw', 'xls', 'xlsx', 'ods', 'ots', 'sdc', 'sxc',
                   'ppt', 'pptx', 'odp', 'pps', 'ppsx', 'sxi', 'jpg', 'jpeg', 'png', 'tif', 'tiff']

# Initialize bot
bot = Bot(token=API_TOKEN)

LIST_PRICE = 0.5

DataBase = AsyncIOMotorClient(uri, retryWrites=False, io_loop=bot.loop).get_database("print")

ip = get('https://api.ipify.org').text

# webhook settings
WEBHOOK_HOST = "0.0.0.0"
WEBHOOK_PORT = 8443
WEBHOOK_PATH = f'/{API_TOKEN}'
WEBHOOK_URL = f"https://{ip}:{WEBHOOK_PORT}{WEBHOOK_PATH}"
SSL_CERT = "webhook.cert"
SSL_PRIV = "webhook.key"

