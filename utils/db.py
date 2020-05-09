from config import logger, DataBase
from pymongo.collection import Collection
from random import choice
import string


class FromUserModel:
    default_data: dict
    db_object: dict

    db: Collection
    chat_id = None
    from_user = None

    def __init__(self, from_user):
        self.from_user = from_user

    async def create(self):
        if type(self.from_user) == int:
            self.chat_id = self.from_user
        else:
            self.chat_id = self.from_user.id

        self.db_object = await self.db.find_one({"chat_id": self.chat_id})

        while not self.db_object:
            logger.info(f"New user? {self.chat_id}")
            to_insert = self.default_data
            to_insert['chat_id'] = self.chat_id

            await self.db.update_one({'chat_id': self.chat_id}, {"$set": to_insert}, upsert=True)
            self.db_object = await self.db.find_one({"chat_id": self.chat_id})

        if self.from_user:
            self.upd_data()

        return self

    def __setitem__(self, name, value):
        self.db_object[name] = value

    def __getitem__(self, name):
        if name not in self.db_object.keys():
            try:
                self[name] = self.default_data[name]
            except Exception as e:
                return None
        return self.db_object[name]

    def __eq__(self, other):
        return self['chat_id'] == other['chat_id']

    def upd_data(self):
        pass

    async def save(self):
        await self.db.update_one({"_id": self.db_object['_id']},
                                 {"$set": self.db_object},
                                 upsert=True)


class ItemField:
    default = None

    def __init__(self, default=None):
        self.default = default


class ItemModel:
    _reserved_names = ["db"]
    db: Collection
    _db_object: dict

    async def create(self, **kwargs):

        temp_id = await self.gen_db_id()
        data = {"id": temp_id}

        for i in self.get_all_params():
            data[i] = kwargs.get(i, self.__class__.__dict__[i].default)

        await self.db.insert_one(data)
        self._db_object = await self.db.find_one({"id": temp_id})
        return self

    async def get(self, item_id):
        self._db_object = await self.db.find_one({"id": item_id})

        if self._db_object:
            for i in self.get_all_params():
                self._db_object[i] = self._db_object.get(i, self.__class__.__dict__[i])
            return self
        else:
            return None

    async def find_obj(self, args: dict):
        self._db_object = await self.db.find_one(args)
        if self._db_object:
            return self
        else:
            return None

    async def gen_db_id(self):
        while True:
            random = ''.join([choice(string.ascii_letters
                                     + string.digits) for n in range(5)])
            if not await self.db.find_one({"id": random}):
                return random

    def get_all_params(self):
        result = []
        for i in self.__class__.__dict__:
            if isinstance(self.__class__.__dict__[i], ItemField):
                result.append(i)
        return result

    def __setitem__(self, name, value):
        self._db_object[name] = value

    def __getitem__(self, name):
        if name not in self._db_object.keys():
            try:
                self[name] = self.__dict__[name]
            except Exception as e:
                logger.exception(e)
                raise Exception("Error get {}".format(name))

        return self._db_object[name]

    async def save(self):
        await self.db.update_one({"_id": self._db_object['_id']},
                                 {"$set": self._db_object},
                                 upsert=True)

    async def delete(self):
        await self.db.delete_one({"_id": self._db_object['_id']})
