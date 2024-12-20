from kwork import Kwork
import asyncio
import json
import os
from dotenv import load_dotenv
from pprint import pprint
import pandas as pd
from pymongo import MongoClient
from loguru import logger

load_dotenv()


async def main():

    while True:

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
            if ('telegram' in el['full_text'] or 'tg' in el['full_text'] or 'телеграм' in el['full_text'] or 'тг' in el['full_text']) and \
                    ('бот' in el['full_text'] or 'bot' in el['full_text']):
                projs_contain_telegram_n_bot.append(el)

        logger.info(
            f'Projects that has "telegram" and "bot" mentioned:\n{projs_contain_telegram_n_bot}')

        # CHATGPT
        try:
            client = MongoClient(os.environ.get('MONGO_URI'))
            db = client['kwork_db']
            collection = db['projects']

            for project in projs_contain_telegram_n_bot:
                collection.update_one({'id': project['id']}, {
                                      '$set': project}, upsert=True)
        except Exception as e:
            logger.error(f'Error while adding to mongo db: {e}')
        # -- END CHATGPT

        await api.close()

        logger.info(f'All data were added to database. Waiting for a minute...')
        await asyncio.sleep(60)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
