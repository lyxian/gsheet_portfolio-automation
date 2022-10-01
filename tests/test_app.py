# RUN (test_app.py in background first before running pytest)
# - python -m pytest -p no:cacheprovider tests -sv
# - pytest .. (if __init__.py exists in tests dir)

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import loadSecrets
from app import app

from copy import deepcopy
import requests
import pytest

@pytest.fixture
def payload():
    '''Returns valid payload for /getPass'''
    configVars = loadSecrets()
    return {
        'url': 'http://{}:{}/{}'.format(configVars['LOCALHOST'], configVars['TEST_PORT'], 'update'),
        'payload': {
            'password': configVars['PASSWORD'],
        }
    }

@pytest.fixture
def verbose():
    '''Returns default verbose setting'''
    return False

def test_app_getPass_success(payload, verbose):
    if verbose:
        print(f'\nProper: {payload}')
    assert requests.post(payload['url'], json=payload['payload']).json().get('status') == 'OK'

def test_app_getPass_failure(payload, verbose):

    # Wrong password
    tmp = deepcopy(payload)
    tmp['payload']['password'] = 1234
    response = requests.post(tmp['url'], json=tmp['payload']).json()
    if verbose:
        print(f'\nWrong password: {tmp}')
    assert response.get('status') == 'NOT_OK' and response.get('ERROR') == 'Wrong password!'
    
    # Wrong method
    response = requests.get(payload['url']).json()
    if verbose:
        print(f'Wrong method: GET')
    assert response.get('status') == 'NOT_OK' and response.get('ERROR') == 'Nothing here!'

if __name__ == '__main__':
    
    DEBUG_MODE = True
    configVars = loadSecrets()
    configVars['DATABASE_NAME'] = configVars['TEST_DATABASE_NAME']
    configVars['DATABASE_SHEET'] = configVars['TEST_DATABASE_SHEET']

    app.configVars = configVars    
    app.run(debug=DEBUG_MODE, host='0.0.0.0', port=int(configVars['TEST_PORT']))
