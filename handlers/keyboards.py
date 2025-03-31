import json
import  emoji
from config import admin
from database.models import Session
from filters import session
from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton, ForceReply)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from callback_factories import WorkCD


def main_kb(session: Session):
    main = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='News for you 📰',
                                     callback_data=WorkCD(menu='for_u', action='for_u').pack()),
                InlineKeyboardButton(text='All sources 🌍',
                                     callback_data=WorkCD(menu='all_sources', action='all_sources').pack())
            ],
            [
                InlineKeyboardButton(text='Contact support 🆘',
                                     url=admin),
                InlineKeyboardButton(text='Tip Me💰 ',
                                     callback_data=WorkCD(menu='tips', action='tips').pack())
            ]
        ]
    )
    return main

def news_menu_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="📋 Main Page", callback_data="open_menu")
    return builder.as_markup()

def exit_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(
                text="Main Page 🏠",
                callback_data=WorkCD(menu="main", action="start").pack()
            )
        ]]
    )


async def sources_kb(sites):
    builder = InlineKeyboardBuilder()
    for site_name, site_id in sites:
        builder.button(
            text=site_name,
            callback_data=WorkCD(
                menu="sources",
                action="show_news",
                arg=site_id
            ).pack()
        )
    builder.adjust(1)
    builder.row(InlineKeyboardButton(
        text="Main Page 🏠",
        callback_data=WorkCD(menu="main", action="start").pack()
    ))
    return builder.as_markup()


async def news_kb(site, user):
    """Клавиатура для новостей с кнопкой подписки"""
    builder = InlineKeyboardBuilder()
    is_subscribed = site.name in (user.subscriptions or [])

    builder.button(
        text="❌ Unsubscribe" if is_subscribed else "✅ Subscribe",
        callback_data=WorkCD(
            menu="sources",
            action="unsubscribe" if is_subscribed else "subscribe",
            arg=site.id
        ).pack()
    )

    builder.row(InlineKeyboardButton(
        text="Main Page 🏠",
        callback_data=WorkCD(menu="main", action="start").pack()
    ))

    return builder.as_markup()