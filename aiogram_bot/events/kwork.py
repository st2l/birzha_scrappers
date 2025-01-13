from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from loguru import logger


async def kwork_event_handler(bot: Bot, data, user_id):
    logger.info(f'Recieved new project from Kwork: {data["project"]}')

    message = f"""Новый проект на бирже Kwork:
Названние: <b>{data['project']['title']}</b>
Описание: {data['project']['description']}
Ссылка: {data['project']['project_url']})
Стоимость: {data['project'].get('price', 'некорректно указан параметр')} рублей - {data['project'].get('possible_price_limit', 'некорректно указан параметр')} рублей""" \
.replace('<br>', '\n')

    await bot.send_message(chat_id=user_id, text=message, parse_mode='HTML',
                           reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                               [InlineKeyboardButton(
                                   text="Ссылка на заказ", url=data['project']['project_url'])],
                                [InlineKeyboardButton(
                                    text="Отправить отклик!", callback_data=f"send_kwork_connect_{data['project']['id']}")]
                           ]))


async def kwork_message_event_handler(bot: Bot, data, user_id):
    logger.info(f'Recieved new message from Kwork: {data["message"]}')

    message = f"""Новое сообщение на бирже Kwork:
Текст сообщения: {data['message']['text']}"""

    await bot.send_message(chat_id=user_id, text=message, parse_mode='Markdown')
