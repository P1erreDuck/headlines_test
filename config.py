import os
from dataclasses import dataclass


@dataclass
class BotConfig:
    token: str
    project: str
    admins: list


@dataclass
class DBConfig:
    host: str = os.getenv('DB_HOST', '_____')
    username: str = os.getenv('DB_USER', '_____')
    password: str = os.getenv('DB_PASSWORD', '_____')
    database: str = os.getenv('DB_NAME', 'headlines_news')


db_config = DBConfig(
    host='postgres', #localhost для локального запуска / postgres для Docker
    username='postgres',
    password='_____',
    database='headlines_news',
)

bot_config = BotConfig(
    token="_____",
    project='headlines_news',
    admins=[00000]
)

admin = 'https://t.me/00000'
