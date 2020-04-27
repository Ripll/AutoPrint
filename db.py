from utils.db import FromUserModel
from config import ADMINS, DataBase


class User(FromUserModel):
    db = DataBase["users"]

    default_data = {
        "state": "start"
    }

    def upd_data(self):
        self.db_object['username'] = self.from_user.username
        self.db_object['full_name'] = self.from_user.full_name

    def is_admin(self):
        return self['chat_id'] in ADMINS


class Saver(FromUserModel):
    db = DataBase["saver"]

    default_data = {}
