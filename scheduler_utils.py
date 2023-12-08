from utils import updateSheet
import pendulum
import logging
from timeit import default_timer
import shutil
import time
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
    # databaseName = os.environ['DATABASE_NAME'] + '-Test'
    databaseName = os.environ['DATABASE_NAME']
    databaseSheet = os.environ['DATABASE_SHEET']
    
    t1 = default_timer()
    count = 1
    while count <= 3:
        try:
            response = updateSheet(databaseName, databaseSheet)
            break
        except Exception as e:
            logger.info(f'[{pendulum.now().to_datetime_string()}] Error = ' + str(type(e)))
            logger.info(f'[{pendulum.now().to_datetime_string()}] Attempt {count}: Retrying in 60s')
            if os.path.exists('logs/error.txt'):
                shutil.copyfile('logs/error.txt', 'logs/error_old.txt')
            with open('logs/error.txt', 'w') as file:
                file.write(f'[{pendulum.now().to_datetime_string()}] ' + str(e))
            time.sleep(30)
            count += 1
    timeTaken = default_timer()-t1
    if timeTaken < 100:
        executionTime = f'{timeTaken:.3}'
    else:
        executionTime = int(timeTaken)
    if response['status'] == 'OK':
        logger.info(f'[{pendulum.now().to_datetime_string()}] Sheet updated in {executionTime}s')
    else:
        logger.info(f'[{pendulum.now().to_datetime_string()}] Unable to update sheet: {response}')