import aiohttp
import asyncio

from aiogram.utils.keyboard import InlineKeyboardBuilder
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, func, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from database.models import Site, User
from config import db_config
from typing import List, Dict, Tuple
import random

import logging
from urllib.parse import urlparse
from handlers.keyboards import news_menu_kb

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def fetch_latest_headlines(http_session: aiohttp.ClientSession, site: Site) -> List[Dict[str, str]]:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept-Language": "en-US,en;q=0.9,ru;q=0.8"
    }

    for attempt in range(3):
        try:
            async with http_session.get(site.url, headers=headers, timeout=10) as response:
                response.raise_for_status()
                soup = BeautifulSoup(await response.text(), 'html.parser')

                headlines = []
                for headline in soup.find_all(site.tag)[:15]:
                    title = headline.get_text(strip=True)

                    link = headline.find_parent('a')
                    url = ""
                    if link and link.get('href'):
                        href = link['href']

                        if href.startswith("http") or href.startswith("https"):
                            url = href
                        elif href.startswith("/"):
                            url = f"{site.base_url.rstrip('/')}{href}"
                        else:
                            url = ""

                    if title and url:
                        headlines.append({"title": title, "url": url})

                return headlines

        except Exception as e:
            if attempt < 2:
                await asyncio.sleep(random.uniform(1, 3))
                continue
            return []


async def update_news_in_db(db_session, site: Site, new_headlines: List[Dict[str, str]]) -> Tuple[
    List[Dict[str, str]], List[Dict[str, str]]]:
    current_news = site.news or []

    existing_titles = {n['title'] for n in current_news}
    existing_urls = {n['url'] for n in current_news}

    added_news = [
        news for news in new_headlines
        if news['title'] not in existing_titles and news['url'] not in existing_urls
    ]

    updated_news = added_news + current_news
    removed_news = updated_news[15:] if len(updated_news) > 15 else []
    final_news = updated_news[:15]

    site.news = final_news
    db_session.commit()

    return added_news, removed_news


async def process_site(db_session, http_session: aiohttp.ClientSession, site: Site, bot=None) -> Dict:
    result = {
        'site_name': site.name,
        'added': [],
        'removed': [],
        'error': None
    }

    try:
        new_headlines = await fetch_latest_headlines(http_session, site)
        if not new_headlines:
            result['error'] = "ERROR"
            return result

        added, removed = await update_news_in_db(db_session, site, new_headlines)
        result['added'] = added
        result['removed'] = removed

        if added and bot:
            await send_new_news_to_subscribers(bot, db_session, site.name, added)

    except Exception as e:
        result['error'] = str(e)

    return result


async def send_new_news_to_subscribers(bot, db_session, site_name: str, new_news: List[Dict[str, str]]):
    try:
        sql = text("""
            SELECT id, full_name, username, subscriptions 
            FROM "user" 
            WHERE EXISTS (
                SELECT 1 
                FROM jsonb_array_elements_text(subscriptions::jsonb) AS elem
                WHERE elem = :site_name
            )
        """)

        result = db_session.execute(sql, {'site_name': site_name})
        subscribers_data = result.fetchall()

        if not subscribers_data or not new_news:
            return

        for user_data in subscribers_data:
            user_id = user_data[0]

            try:
                for news_item in new_news[:-1]:
                    domain = urlparse(news_item['url']).netloc.replace('www.', '')
                    message_text = f"{news_item['title']}\n<a href='{news_item['url']}'>{domain}</a>"
                    await bot.send_message(
                        chat_id=user_id,
                        text=message_text,
                        disable_web_page_preview=True,
                        parse_mode='HTML'
                    )

                last_news = new_news[-1]
                domain = urlparse(last_news['url']).netloc.replace('www.', '')
                message_text = f"{last_news['title']}\n<a href='{last_news['url']}'>{domain}</a>"
                await bot.send_message(
                    chat_id=user_id,
                    text=message_text,
                    reply_markup=news_menu_kb(),
                    disable_web_page_preview=True,
                    parse_mode='HTML'
                )

            except Exception as e:
                print(f"Error {user_id}: {e}")

    except Exception as e:
        print(f"Error: {e}")


async def main(bot=None):
    DATABASE_URL = f"postgresql://{db_config.username}:{db_config.password}@{db_config.host}/{db_config.database}"

    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        db.connection()

        sites = db.query(Site).all()
        if not sites:
            return

        async with aiohttp.ClientSession() as http_session:
            semaphore = asyncio.Semaphore(3)

            async def process(site):
                async with semaphore:
                    return await process_site(db, http_session, site, bot)

            tasks = [process(site) for site in sites]
            results = await asyncio.gather(*tasks)

            for res in results:
                if res['error']:
                    print(f"{res['site_name']}: Ошибка - {res['error']}")
                else:
                    print(f"{res['site_name']}: Добавлено {len(res['added'])}")

    except SQLAlchemyError as e:
        print(f"Error: {str(e)}")
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
