from ..models.db import User


class MsgModel:
    user: User

    def __init__(self, user: User):
        self.user = user
