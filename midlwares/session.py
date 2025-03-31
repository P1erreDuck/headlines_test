from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from database import Client
from database.models import Session
from loader import get_db


class SessionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        db = get_db()
        session: Session = await db.get(Session, key={'user_id': event.from_user.id})
        data['session'] = session
        return await handler(event, data)