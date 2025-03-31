import asyncio
from aiogram import F
from aiogram.types import CallbackQuery
from aiogram.filters import StateFilter
import random
from urllib.parse import urlparse
from sqlalchemy import select, and_
from aiogram.exceptions import TelegramBadRequest
from callback_factories import WorkCD
from database import Client
from database.models import Site, User, Session
from handlers.routers import private_user
from handlers.keyboards import main_kb, sources_kb


@private_user.callback_query(WorkCD.filter(F.menu == 'tips'))
async def tip_me_handler(callback: CallbackQuery):
    await callback.answer(f"💕💖❤️Thank you!❤️💖💕", show_alert=True)




