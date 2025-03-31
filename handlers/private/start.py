from typing import Union

from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, StateFilter

from callback_factories import WorkCD
from database import Client
from database.models import Session
from handlers import keyboards as kb
from handlers.routers import private_user


@private_user.message(CommandStart(), StateFilter("*"))
@private_user.callback_query(WorkCD.filter(F.menu == 'main'), StateFilter("*"))
async def cmd_start(tg_object: Union[Message, CallbackQuery], session: Session, db: Client, state: FSMContext):
    await state.clear()
    print(session)

    text = (
        f"💼 Welcome to your personalized news feed!\n"
            f"Stay informed with a stream of updates curated specifically for you. 🎯\n"
            f"Filter out the noise, focus on what matters, and make every update count. ⚡️\n"
    )

    await tg_object.answer(
        text, reply_markup=kb.main_kb(session)
    ) if isinstance(tg_object, Message) else await tg_object.message.edit_text(
        text, reply_markup=kb.main_kb(session)
    )