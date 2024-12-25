from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from loguru import logger
from pymongo import MongoClient
import os


kwork_settings_router = Router()


async def create_kb():
    try:
        client = MongoClient(os.environ.get('MONGO_URI'))
        db = client['kwork_db']
        collection = db['configurations']

        config = collection.find_one({'name': 'kwork_settings'})
        if not config:
            # Create default configuration if it does not exist
            default_config = {
                'name': 'kwork_settings',
                'search_on_market': True,
                'automatic_answers': False,
            }
            collection.insert_one(default_config)
            config = default_config

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text=f'Поиск на бирже -> {"АКТИВЕН" if config["search_on_market"] else "ВЫКЛЮЧЕН"}', callback_data='change_search_on_market_kwork')],
            [InlineKeyboardButton(
                text=f'Автоматические ответы -> {"АКТИВЕН" if config["automatic_answers"] else "ВЫКЛЮЧЕН"}', callback_data='change_automatic_answers_kwork')],
        ])
        return kb
    except Exception as e:
        logger.error(f'Error in create_kb (kwork_settings_callback) -> {e}')


@kwork_settings_router.callback_query(F.data == 'kwork_settings')
async def kwork_settings_callback(query: CallbackQuery):
    try:
        await query.message.answer(
            text='**Настройки kwork**',
            parse_mode='Markdown',
            reply_markup=await create_kb()
        )
        await query.answer()
    except Exception as e:
        logger.error(f'Error in kwork_settings_callback -> {e}')
