import aiohttp.connector
from kwork import Kwork
import asyncio
import json
import os
from dotenv import load_dotenv
from pprint import pprint
import pandas as pd
from pymongo import MongoClient
from loguru import logger
from datetime import datetime, timedelta
import aiohttp
import requests

load_dotenv()


async def main():

    while True:
        # -- checking configuration
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

        except Exception as e:
            logger.error(
                f'Error while getting configuration from mongo db: {e}')

        if config['search_on_market'] is False:
            logger.info(
                'Search on market is disabled. Waiting for a minute...')
            await asyncio.sleep(70)
            continue
        # -- END checking configuration

        logger.info(
            f"Started kwork parser with: {os.environ.get('LOGIN')}, {os.environ.get('PASSWD')}, {os.environ.get('PHONE_LAST')}")
        api = Kwork(
            login=os.environ.get('LOGIN'),
            password=os.environ.get('PASSWD'),
            phone_last=os.environ.get('PHONE_LAST')
        )

        categories = await api.get_categories()
        it_category_id = [el for el in categories if 'IT' in el.name][0].id
        logger.info(f'IT category id: {it_category_id}')

        all_projs = await api.get_projects(categories_ids=[it_category_id])

        projs_contain_telegram_n_bot = []
        for el in all_projs:
            el['full_text'] = el['title'] + ' ' + el['description']
            el['created_at'] = datetime.utcnow()
            if ('telegram' in el['full_text'] or 'tg' in el['full_text'] or 'телеграм' in el['full_text'] or 'тг' in el['full_text']) and \
                    ('бот' in el['full_text'] or 'bot' in el['full_text']):
                projs_contain_telegram_n_bot.append(el)

        # sending projects to mongo db
        try:
            client = MongoClient(os.environ.get('MONGO_URI'))
            db = client['kwork_db']
            collection = db['projects']

            for project in projs_contain_telegram_n_bot:
                collection.update_one({'id': project['id']}, {
                                      '$set': project}, upsert=True)
        except Exception as e:
            logger.error(f'Error while adding to mongo db: {e}')
        # -- END sending projects to mongo db

        await api.close()

        # -- getting last projects from mongo db
        try:
            client = MongoClient(os.environ.get('MONGO_URI'))
            db = client['kwork_db']
            collection = db['projects']
            now = datetime.utcnow()
            one_minute_ago = now - timedelta(minutes=1)
            recent_projects = collection.find(
                {'created_at': {'$gte': one_minute_ago}})

            for project in recent_projects:  # send request to aiogram_bot
                project['_id'] = ""
                project['created_at'] = ""
                logger.info(f'Sending project to aiogram_bot: {project}')

                # send request to aiogram_bot

                url = 'http://aiogram_bot:64783/event'
                data = {'service': 'kwork', 'project': project}
                requests.post(url, json=data)

        except Exception as e:
            logger.error(f'Error while getting from mongo db: {e}')
        # -- END getting last projects from mongo db

        logger.info(f'All data were added to database. Waiting for a minute...')
        await asyncio.sleep(70)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
