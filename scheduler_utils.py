from utils import updateSheet
import pendulum
import logging
from timeit import default_timer
import os

if not os.path.exists('logs'):
    os.mkdir('logs')

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
file_handler = logging.FileHandler(filename='logs/scheduler.log', mode='a', encoding='utf-8')
logger.addHandler(file_handler)
logger.info(f'\n[{pendulum.now().to_datetime_string()}] Starting scheduler ..')


def runUpdateSheet():
    logger.info(f'[{pendulum.now().to_datetime_string()}] Updating sheet ..')
    databaseName = os.environ['DATABASE_NAME'] + '-Test'
    # databaseName = os.environ['DATABASE_NAME']
    databaseSheet = os.environ['DATABASE_SHEET']
    
    t1 = default_timer()
    response = updateSheet(databaseName, databaseSheet)
    executionTime = f'{(default_timer()-t1):.3}'
    if response['status'] == 'OK':
        logger.info(f'[{pendulum.now().to_datetime_string()}] Sheet updated in {executionTime}s')
    else:
        logger.info(f'[{pendulum.now().to_datetime_string()}] Unable to update sheet: {response}')