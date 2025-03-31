from aiogram import F
from aiogram.enums import parse_mode
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select
from urllib.parse import urlparse
from aiogram.exceptions import TelegramBadRequest

from callback_factories import WorkCD
from database import Client
from database.models import Site, Session, User

from handlers.routers import private_user
from handlers.keyboards import sources_kb, news_kb, main_kb


@private_user.callback_query(WorkCD.filter(F.action == 'all_sources'), StateFilter("*"))
async def all_sources(callback: CallbackQuery, callback_data: WorkCD, db: Client):
    try:
        async with db.AsyncSession() as session:
            stmt = select(Site.name, Site.id).distinct()
            result = await session.execute(stmt)
            sites = result.all()
            markup = await sources_kb(sites)

            try:
                await callback.message.edit_text("Select a source:", reply_markup=markup)
            except:
                await callback.message.answer("Select a source:", reply_markup=markup)
    except Exception as e:
        print(f"Error: {str(e)}")
        await callback.answer("Error loading sources", show_alert=True)


@private_user.callback_query(WorkCD.filter(F.action == 'show_news'), StateFilter("*"))
async def show_site_news(callback: CallbackQuery, callback_data: WorkCD, db: Client):
    try:
        async with db.AsyncSession() as session:
            site = await session.get(Site, int(callback_data.arg))
            user = await session.get(User, callback.from_user.id)

            if not site or not user:
                await callback.answer("Error loading data", show_alert=True)
                return

            valid_news = []
            for news_item in site.news[:10]:
                if isinstance(news_item, dict) and 'title' in news_item and 'url' in news_item:
                    valid_news.append(news_item)

            if not valid_news:
                await callback.answer("No news available", show_alert=True)
                return

            message_text = f"📰 Latest news from {site.name}:\n\n"
            for i, news_item in enumerate(valid_news, 1):
                domain = urlparse(news_item['url']).netloc.replace('www.', '')
                message_text += f"{i}. {news_item['title']}\n<a href='{news_item['url']}'>{domain}</a>\n\n"

            markup = await news_kb(site, user)

            try:
                await callback.message.edit_text(
                    text=message_text,
                    reply_markup=markup,
                    disable_web_page_preview=True,
                    parse_mode='HTML'
                )
            except:
                await callback.message.answer(
                    text=message_text,
                    reply_markup=markup,
                    disable_web_page_preview=True,
                    parse_mode='HTML'
                )
    except Exception as e:
        print(f"Error: {e}")
        await callback.answer("Error loading news", show_alert=True)


@private_user.callback_query(
    WorkCD.filter(F.action.in_(['subscribe', 'unsubscribe'])),
    StateFilter("*")
)
async def handle_subscription(callback: CallbackQuery, callback_data: WorkCD, db: Client):
    try:
        async with db.AsyncSession() as session:
            site = await session.get(Site, int(callback_data.arg))
            user = await session.get(User, callback.from_user.id, with_for_update=True)

            subs = user.subscriptions.copy() if user.subscriptions else []
            if callback_data.action == 'subscribe':
                if site.name not in subs:
                    subs.append(site.name)
                    await callback.answer(f"🔔 Subscribed to {site.name}!")
                    print(user.subscriptions)
            else:
                if site.name in subs:
                    subs.remove(site.name)
                    await callback.answer(f"🔕 Unsubscribed from {site.name}")
                    print(user.subscriptions)

            user.subscriptions = subs
            await session.commit()

            await show_site_news(callback, callback_data, db)
    except Exception as e:
        print(f"Error: {str(e)}")
        await callback.answer("Subscription error", show_alert=True)
