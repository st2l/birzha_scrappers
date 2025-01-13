from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiohttp import web
from loguru import logger
import asyncio
import handlers
import events
import os


# LOAD environment variables
API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')
USER_ID = int(os.getenv('TELEGRAM_USER_ID'))

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# import routers
dp.include_router(handlers.handler_router)


async def main():
    try:
        logger.info(
            f'Starting polling with auth token -> {API_TOKEN} and user -> {USER_ID}')
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f'Error in main() aiogram_bot -> {e}')


async def handle_event(request):  # function to handle incoming events
    logger.info(f'REQUEST - {request}')
    data = await request.json()

    if data['service'] == 'kwork':
        await events.kwork_event_handler(bot, data, USER_ID)
    elif data['service'] == 'kwork_message':
        await events.kwork_message_event_handler(bot, data, USER_ID)

    return web.Response(text="Event received", status=200)


if __name__ == '__main__':

    try:
        # Initialize web application
        app = web.Application()

        # Add route for handling incoming events
        app.router.add_post('/event', handle_event)

        loop = asyncio.get_event_loop()
        loop.create_task(main())
        loop.create_task(web._run_app(app, host='0.0.0.0', port=64783))

        loop.run_forever()
    except Exception as e:
        logger.error(f'Error while trying to start -> {e}')
