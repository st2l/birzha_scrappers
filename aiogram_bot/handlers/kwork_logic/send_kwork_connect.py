from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from loguru import logger
from . import texts
from random import randint

send_kwork_connect_router = Router()


async def get_random_kwork_text(type_of_task: str):
    try:

        connect_text = ''
        random_idx = -1
        if type_of_task == 'aiogram':
            random_idx = randint(
                0, len(texts.aiogram_telethon_bot_creation_templates) - 1)
            connect_text = texts.aiogram_telethon_bot_creation_templates[
                random_idx
            ]
        elif type_of_task == 'telethon':
            random_idx = randint(
                0, len(texts.people_telethon_bot_creation_templates) - 1)
            connect_text = texts.people_telethon_bot_creation_templates[
                random_idx
            ]

        return connect_text, random_idx

    except Exception as e:
        logger.error(f'Error in get_kwork_text -> {e}')


async def get_kwork_text_by_type_b_index(type_of_task: str, random_idx: int):
    try:

        connect_text = ''
        if type_of_task == 'aiogram':
            connect_text = texts.aiogram_telethon_bot_creation_templates[
                random_idx
            ]
        elif type_of_task == 'telethon':
            connect_text = texts.people_telethon_bot_creation_templates[
                random_idx
            ]

        return connect_text

    except Exception as e:
        logger.error(f'Error in get_kwork_text_by_type_b_index -> {e}')


@send_kwork_connect_router.callback_query(F.data.contains('send_kwork_connect'))
async def send_kwork_connect_callback(query: CallbackQuery):
    try:

        project_id = query.data.split('_')[-1]
        logger.info(f'Retrieved connect to Kwork project {project_id}')

        await query.answer('')
        await query.message.answer(
            text=f'Хорошо. Отправлям отклик на проект с id -> {project_id}\nВыберите, какой тип ТЗ больше подходит.',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text='ТЗ aiogram бота', callback_data=f'kwork_connect_technical_task_{project_id}_aiogram')],
                [InlineKeyboardButton(text='ТЗ telethon бота (имитация человека)',
                                      callback_data=f'kwork_connect_technical_task_{project_id}_telethon')],
            ])
        )

    except Exception as e:
        logger.error(f'Error in send_kwork_connect_callback -> {e}')


@send_kwork_connect_router.callback_query(F.data.contains('kwork_connect_technical_task'))
async def kwork_connect_technical_task_callback(query: CallbackQuery):
    try:
        project_id = query.data.split('_')[-2]
        task_type = query.data.split('_')[-1]
        logger.info(
            f'Retrieved connect to Kwork project {project_id} with task type {task_type}')

        # gathering needed template (text)
        connect_text, random_idx = await get_random_kwork_text(task_type)

        await query.answer('')
        await query.message.answer(
            text=f'Отлично! Теперь отправьте ТЗ для проекта с id -> {project_id} и типом ТЗ -> {task_type}\n' +
            'Текст отклика:\n' + f'```{connect_text}```',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='АВТОМАТИЧЕСКИ отправить ТЗ',
                                      callback_data=f'confirm_auto_kwork_connect_send_{project_id}_{task_type}_{random_idx}')],
                [InlineKeyboardButton(text='Отправить ТЗ самостоятельно (ссылка на заказ)',
                                      url=f'https://kwork.ru/new_offer?project={project_id}')]
            ]),
            parse_mode='Markdown'
        )

    except Exception as e:
        logger.error(f'Error in kwork_connect_technical_task_callback -> {e}')


@send_kwork_connect_router.callback_query(F.data.contains('confirm_auto_kwork_connect_send'))
async def confirm_auto_kwork_connect_send_callback(query: CallbackQuery):
    try:
        project_id = query.data.split('_')[-3]
        task_type = query.data.split('_')[-2]
        random_idx = query.data.split('_')[-1]
        logger.info(
            f'Retrieved connect to Kwork project {project_id} with task type {task_type}')

        # gathering needed template (text)
        connect_text = await get_random_kwork_text(
            type_of_task=task_type,
            random_idx=random_idx
        )

        # TODO: write realization of sending message to Kwork
        await query.answer('')
        await query.message.answer(
            text=f'Отлично! Отправляем отклик на проект с id -> {project_id} и типом ТЗ -> {task_type}\n' +
            'Текст отклика:\n' + f'```{connect_text}```',
            parse_mode='Markdown'
        )
    
    except Exception as e:
        logger.error(f'Error in confirm_auto_kwork_connect_send_callback -> {e}')
