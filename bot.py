import filters
import asyncio
from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import db_config, bot_config
from database.build import init
from filters import UserFilter, SessionFilter
from handlers import routers
from loader import bot, dp
from midlwares import DBMiddleware, SessionMiddleware
from found_news import main as news_main


async def update_news():
    try:
        await news_main(bot)
    except Exception as e:
        print(f"Error: {e}")

async def on_startup():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(update_news, 'interval', minutes=5)
    scheduler.start()
    await update_news()


async def main():
    dp.message.middleware(DBMiddleware(db_config, bot_config))
    dp.callback_query.middleware(DBMiddleware(db_config, bot_config))

    dp.message.filter(UserFilter())
    dp.message.filter(SessionFilter())
    dp.callback_query.filter(UserFilter())
    dp.message.middleware(SessionMiddleware())
    dp.callback_query.middleware(SessionMiddleware())
    dp.include_router(routers.private_user)

    dp.startup.register(on_startup)

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        print(dp.resolve_used_update_types())
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == '__main__':
    init()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('OFF')
