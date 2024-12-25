from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from loguru import logger

start_router = Router()

kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Настройки kwork',
                         callback_data='kwork_settings')],
])


@start_router.message(Command('start'))
async def start_handler(message: Message):
    try:

        await message.answer(text='Привет! Выбери сервис для просмотра настроек.', reply_markup=kb)

    except Exception as e:
        logger.error(f'Error in start_handler -> {e}')
