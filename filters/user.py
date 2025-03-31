import unicodedata
from typing import Union
from emoji.core import demojize
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from database import models
from loader import get_db


class UserFilter(BaseFilter):
    async def __call__(self, tg_object: Union[Message, CallbackQuery]) -> bool:
        db = get_db()
        usr = tg_object.from_user
        user = await db.get(models.User, key={'id': usr.id})
        if not user:
            await db.insert(
                models.User,
                id=usr.id,
                full_name=unicodedata.normalize('NFKD', demojize(usr.full_name)),
                username=usr.username,
            )
        else:
            await db.update(
                models.User,
                key={'id': usr.id},
                full_name=unicodedata.normalize('NFKD', demojize(usr.full_name)),
                username=usr.username,
            )
        return True
