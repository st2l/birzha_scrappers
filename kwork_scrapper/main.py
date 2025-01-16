import aiohttp.connector
from kwork import Kwork, KworkBot, types
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


async def get_configuration_from_mongo():
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

        return config

    except Exception as e:
        logger.error(
            f'Error while getting configuration from mongo db: {e}')


async def main():

    time_to_wait = 60 * 5
    while True:
        await asyncio.sleep(time_to_wait)
        # -- checking configuration
        config = await get_configuration_from_mongo()

        if config['search_on_market'] is False:
            logger.info(
                'Search on market is disabled. Waiting for a minute...')
            await asyncio.sleep(time_to_wait)
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

        try:
            all_projs = await api.get_projects(categories_ids=[it_category_id])
        except Exception as e:
            logger.error(f'Error in fetching all_projs -> {e}')
            continue

        projs_contain_telegram_n_bot = []
        for el in all_projs:
            el['full_text'] = el['title'] + ' ' + el['description']
            el['created_at'] = datetime.now().timestamp()
            if ('telegram' in el['full_text'] or 'tg' in el['full_text'] or 'телеграм' in el['full_text'] or 'тг' in el['full_text']) and \
                    ('бот' in el['full_text'] or 'bot' in el['full_text']):
                projs_contain_telegram_n_bot.append(el)

        # sending projects to mongo db
        try:
            client = MongoClient(os.environ.get('MONGO_URI'))
            db = client['kwork_db']
            collection = db['projects']

            for project in projs_contain_telegram_n_bot:
                if collection.find_one({'id': project['id']}):
                    continue
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
            now = datetime.now().timestamp()
            one_minute_ago = (datetime.now() - timedelta(minutes=time_to_wait)).timestamp()
            recent_projects = [
                el for el in collection.find(
                    {'created_at': {'$gte': one_minute_ago}})
            ]
            logger.info(f'Len in recent_porjects -> {len(recent_projects)}')
            logger.info(f'timestamp -> {now}')

            for project in recent_projects:  # send request to aiogram_bot
                logger.info(f'Smth is going on in recent_projects')
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


if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    loop.create_task(main())

    loop.run_forever()
