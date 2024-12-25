from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiohttp import web
from loguru import logger
import asyncio
import handlers
import os


# LOAD environment variables
API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')
USER_ID = int(os.getenv('TELEGRAM_USER_ID'))

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# import routers
dp.include_router(handlers.start_router)


async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':

    # Initialize web application
    app = web.Application()

    async def handle_event(request):  # function to handle incoming events
        logger.info(f'REQUEST - {request}')
        data = await request.json()
        message = data.get('message', 'No message provided')
        await bot.send_message(USER_ID, message)
        return web.Response(text="Event received")

    # Add route for handling incoming events
    app.router.add_post('/event', handle_event)

    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.create_task(web._run_app(app, host='0.0.0.0', port=64783))

    loop.run_forever()
