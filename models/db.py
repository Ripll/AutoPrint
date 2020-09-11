from utils.db import FromUserModel
from config import ADMINS, DataBase
from datetime import datetime
from pymongo.collection import Collection


class User(FromUserModel):
    db: Collection = DataBase["users"]

    default_data = {
        "state": "start",
        "discount": 0,
        "create_date": datetime.now()
    }

    def upd_data(self):
        self.db_object['username'] = self.from_user.username
        self.db_object['full_name'] = self.from_user.full_name

    def is_admin(self):
        return self['chat_id'] in ADMINS

    def get_price_with_discount(self, price):
        return price * ((100 - self['discount']) / 100)

    def get_mention(self):
        return f"<a href='tg://user?id={self['chat_id']}'>{self['full_name']}</a>"


class Saver(FromUserModel):
    db = DataBase["saver"]

    default_data = {}
