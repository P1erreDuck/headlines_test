from aiogram import F
from aiogram.types import CallbackQuery
from aiogram.filters import StateFilter
import random
from urllib.parse import urlparse
from sqlalchemy import select, and_
from aiogram.exceptions import TelegramBadRequest

from callback_factories import WorkCD
from database import Client
from database.models import Site, User
from handlers.routers import private_user
from handlers.keyboards import main_kb, sources_kb, news_menu_kb


@private_user.callback_query(WorkCD.filter(F.action == 'for_u'), StateFilter("*"))
async def news_for_you(callback: CallbackQuery, callback_data: WorkCD, db: Client):
    try:
        async with db.AsyncSession() as session:
            user = await session.get(User, callback.from_user.id)

            if not user.subscriptions:
                await callback.answer("You have no subscriptions", show_alert=True)
                stmt = select(Site.name, Site.id).distinct()
                result = await session.execute(stmt)
                sites = result.all()

                try:
                    await callback.message.edit_text(
                        "Select interesting sources:",
                        reply_markup=await sources_kb(sites)
                    )
                except TelegramBadRequest:
                    await callback.message.answer(
                        "Select interesting sources:",
                        reply_markup=await sources_kb(sites)
                    )
                return

            stmt = select(Site).where(
                and_(
                    Site.name.in_(user.subscriptions),
                    Site.news != None
                )
            )
            result = await session.execute(stmt)
            sites = result.scalars().all()

            if not sites:
                await callback.answer("No news available", show_alert=True)
                return

            all_news = []
            for site in sites:
                if not isinstance(site.news, list):
                    continue

                for news_item in site.news:
                    all_news.append({
                        'title': news_item['title'],
                        'url': news_item['url'],
                        'source': site.name
                    })

            selected_news = random.sample(all_news, min(5, len(all_news)))

            message_text = "📰 News based on your subscriptions:\n\n"
            for i, news_item in enumerate(selected_news, 1):
                try:
                    url = news_item['url']
                    domain = urlparse(url).netloc.replace('www.', '')
                    message_text += f"{i}. {news_item['title']}\n<a href='{news_item['url']}'>{domain}</a>\n\n"
                except Exception:
                    continue

            try:
                await callback.message.edit_text(
                    text=message_text,
                    reply_markup=news_menu_kb(),
                    disable_web_page_preview=True,
                    parse_mode='HTML'
                )
            except TelegramBadRequest:
                print("Error")
    except Exception as e:
        print(f"Error: {str(e)}", exc_info=True)
