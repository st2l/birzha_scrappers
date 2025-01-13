from loguru import logger
from kwork import KworkBot, types, Kwork
import requests
import os
from pymongo import MongoClient
import asyncio
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
load_dotenv()


async def get_configuration_from_mongo():
    try:
        client = MongoClient(os.getenv('MONGO_URI'))
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

        return config

    except Exception as e:
        logger.error(
            f'Error while getting configuration from mongo db: {e}')


async def run_bot():
    logger.info(f'Setting up a connection for bot...')
    logger.info(
        f'{os.getenv("LOGIN")} {os.getenv("PASSWD")} {os.getenv("PHONE_LAST")}')
    bot = KworkBot(
        login=os.getenv('LOGIN'),
        password=os.getenv('PASSWD'),
        phone_last=os.getenv('PHONE_LAST')
    )

    @bot.message_handler(text_contains='а')
    async def message_recieved(message: types.Message):
        try:
            logger.info(f'Recvd messsage!')
            config = await get_configuration_from_mongo()
            logger.info(f'mongo conf -> {config}')
            if config['automatic_answers'] is False:
                url = 'http://aiogram_bot:64783/event'
                data = {'service': 'kwork_message', 'message': {'text': message.text}}
                requests.post(url, json=data)
            else:
                # TODO: write automatic answers
                return

        except Exception as e:
            logger.error(f'Error while sending message: {e}')

    try:
        await bot.run_bot()
    except Exception as e:
        logger.error(f'Error while running pykwork bot -> {e}')


if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_bot())
