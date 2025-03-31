import json
import os
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from telebot import TeleBot

from config import bot_config, db_config
from database.client import Client


logging.basicConfig(level=logging.INFO)

# Инициализация бота aiogram
bot = Bot(token=bot_config.token, default=DefaultBotProperties(parse_mode='HTML'))
dp = Dispatcher()
storage = MemoryStorage()


sync_bot = TeleBot(token=bot_config.token, parse_mode='HTML')

def get_db():

    return Client(
        username=db_config.username,
        password=db_config.password,
        host=db_config.host,
        name=db_config.database
    )