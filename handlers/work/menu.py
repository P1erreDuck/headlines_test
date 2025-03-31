from aiogram import F
from aiogram.types import CallbackQuery
from aiogram.filters import StateFilter
from sqlalchemy import select, and_
from aiogram.exceptions import TelegramBadRequest
from urllib.parse import urlparse

from callback_factories import WorkCD
from database import Client
from database.models import Site, User, Session
from handlers.routers import private_user
from handlers.keyboards import main_kb, sources_kb


@private_user.callback_query(F.data == "open_menu")
async def open_menu_handler(callback: CallbackQuery, session: Session):
    try:
        await callback.answer()

        markup = main_kb(session)

        await callback.message.answer(
            "📋 Main Page:",
            reply_markup=markup
        )

        try:
            await callback.message.edit_reply_markup(reply_markup=None)
        except TelegramBadRequest:
            pass
    except Exception as e:

        print(f"Error: {e}")
