from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from database import Client
from config import db_config, bot_config  # Импортируем конфиги здесь


class DBMiddleware(BaseMiddleware):
    def __init__(self, db_config, bot_config):  # Теперь принимает конфиги
        self.db_config = db_config
        self.bot_config = bot_config
        self.client = Client(
            host=db_config.host,
            username=db_config.username,
            password=db_config.password,
            name=bot_config.project
        )

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        data['db'] = self.client
        return await handler(event, data)