# RUN (test_app.py in background first before running pytest)
# - python -m pytest -p no:cacheprovider tests -sv
# - python -m pytest -p no:cacheprovider tests -svk 'not update_success'
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

def test_app_update_success(payload, verbose):
    if verbose:
        print(f'\nProper: {payload}')
    assert requests.post(payload['url'], json=payload['payload']).json().get('status') == 'OK'

def test_app_update_failure(payload, verbose):

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

def test_app_update_postError_success(payload, verbose):
    if verbose:
        print(f'\nInvalid database: ')
    configVars = loadSecrets()
    payloadTestEnv = {
        'DATABASE_NAME': 'INVALID'
    }

    response = requests.get('http://{}:{}/{}?'.format(configVars['LOCALHOST'], configVars['TEST_PORT'], 'setEnv')
        + '&'.join([f'{i[0]}={i[1]}' for i in payloadTestEnv.items()])).json()
    assert response.get('status') == 'OK'
    
    response = requests.post(payload['url'], json=payload['payload']).json()
    assert response.get('status') == 'NOT_OK' and response.get('ERROR') == 'Error posted successfully!'

if __name__ == '__main__':
    from flask import request
    
    DEBUG_MODE = True
    configVars = loadSecrets()
    os.environ['DATABASE_NAME'] = configVars['TEST_DATABASE_NAME']
    os.environ['DATABASE_SHEET'] = configVars['TEST_DATABASE_SHEET']

    @app.route('/setEnv', methods=['GET'])
    def _setEnv():
        if request.method == 'GET':
            try:
                for key, val in request.args.items():
                    os.environ[key] = val
                    print(f'Key-{key} set to {val} successfully ..')
                return {'status': 'OK'}, 200
            except Exception as error:
                print(f'=====TEST ERROR=====\n{error}\n=====ERROR END=====')
                return {'status': 'NOT_OK', 'ERROR': error}, 503
        else:
            return {'status': 'NOT_OK', 'ERROR': 'Nothing here!'}, 404

    app.run(debug=DEBUG_MODE, host='0.0.0.0', port=int(configVars['TEST_PORT']))
