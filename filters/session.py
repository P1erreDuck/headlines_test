import unicodedata
from typing import Union
from emoji.core import demojize
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from database import models
from loader import get_db


class SessionFilter(BaseFilter):
    async def __call__(self, tg_object: Union[Message, CallbackQuery]) -> bool:
        db = get_db()
        usr = tg_object.from_user
        session = await db.get(models.Session, key={'user_id': usr.id})
        if not session:
            await db.insert(
                models.Session,
                user_id=usr.id
            )
        return True
