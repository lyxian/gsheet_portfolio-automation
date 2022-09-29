### GOOGLE SHEETS API ###
from oauth2client.service_account import ServiceAccountCredentials
from cryptography.fernet import Fernet
import requests
import pendulum
import gspread
import yaml
import json
import time
import re
import os

DATETIME_FORMAT = {
    'numberFormat': {
        'type': 'DATE_TIME', 
        'pattern': 'd mmm yyyy, ham/pm'
    }
}

def retrieveKey():
    required = ['APP_NAME', 'APP_PASS', 'STORE_PASS', 'STORE_URL']
    if all(param in os.environ for param in required):
        payload = {
            'url': '{}/{}'.format(os.getenv('STORE_URL'), 'getPass'),
            'payload': {
                'password': int(os.getenv('STORE_PASS')),
                'app': os.getenv('APP_NAME'),
                'key': int(os.getenv('APP_PASS'))
            }
        }
        response = requests.post(payload['url'], json=payload['payload']).json()
        if response.get('status') == 'OK':
            return response.get('KEY')
        else:
            raise Exception('Bad response from KEY_STORE, please try again ..')
    else:
        raise Exception('No key store found, please check config ..')

def postError(error):
    required = ['APP_NAME', 'APP_PASS', 'STORE_PASS', 'STORE_URL']
    if all(param in os.environ for param in required):
        payload = {
            'url': '{}/{}'.format(os.getenv('STORE_URL'), 'postError'),
            'payload': {
                'password': int(os.getenv('STORE_PASS')),
                'app': os.getenv('APP_NAME'),
                'key': int(os.getenv('APP_PASS')),
                'error': error,
            }
        }
        response = requests.post(payload['url'], json=payload['payload']).json()
        if response.get('status') == 'OK':
            return response
        else:
            raise Exception('Bad response from KEY_STORE, please try again ..')
    else:
        raise Exception('No key store found, please check config ..')

def loadData():
    configPath = 'secrets.yaml'
    if os.path.exists(configPath):
        with open(configPath) as file:
            data = yaml.safe_load(file)
        return data
    else:
        return {}

def getCredentials():
    key = bytes(retrieveKey(), 'utf-8')
    encrypted = bytes(os.getenv('SECRET_GOOGLE'), 'utf-8')
    return json.loads(Fernet(key).decrypt(encrypted))

def spreadSheetClient():
    scope = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        getCredentials(), scope)
    client = gspread.authorize(creds)
    return client

def openWorkbook_key(client, key):
    return client.open_by_key(key)

def openWorkbook_name(client, name):
    return client.open(name)
    
def newWorksheet(wb, query):
    last = len(wb.worksheets())
    try:
        return wb.duplicate_sheet(source_sheet_id=wb.sheet1.id, insert_sheet_index=last, new_sheet_name=query)
    except:
        sheet = [i for i in wb.worksheets() if i.title.lower()
                 == query.lower()][0]
        if sheet.get_all_records() == []:
            wb.del_worksheet(sheet)
            return wb.duplicate_sheet(source_sheet_id=wb.sheet1.id, insert_sheet_index=last, new_sheet_name=query)
        else:
            return sheet

def sheetPayload(data):
    payload = [['=NOW()' if '/' in i else i for i in data[0].keys()]]
    for i in data:
        payload_i = [pendulum.from_format(j, 'DD MMM YYYY, hA').format('M/D/YYYY H:mm:ss') if re.search(r'AM$|PM$', str(j)) else j for j in i.values()]
        if payload_i[0] == 'transact_value':
            payload_i[1] = '=SUM(SGX!M2:M46)'
            payload_i[2] = '=SUM(ETC!M2:M46)'
            payload_i[3] = '=C2*$C$5'
        elif payload_i[0] == 'market_value':
            payload_i[1] = '=SUM(SGX!S2:S46)'
            payload_i[2] = '=SUM(ETC!S2:S46)'
            payload_i[3] = '=C3*$C$5'
            payload_i[4] = '=LEN(E2)'
        elif payload_i[0] == 'profit':
            payload_i[1] = '=B3-B2'
            payload_i[2] = '=C3-C2'
            payload_i[3] = '=D3-D2'
        elif payload_i[0] == 1:
            payload_i[2] = '=GOOGLEFINANCE("CURRENCY:USDSGD")'
        payload += [payload_i]
    return payload

def updateSheet(configVars):
    client = spreadSheetClient()
    wb = openWorkbook_name(client, configVars['DATABASE_NAME'])
    sheet = wb.worksheet(configVars['DATABASE_SHEET'])
    data = sheet.get_all_records()

    headers = list(data[0].keys())
    profit_headers = headers[-3:]
    reset_header = headers[4]

    # Refresh sheet -> add '-' in 'DateTime >>'
    data[0][reset_header] += '-'
    payload = sheetPayload(data)
    sheet.update(payload, raw=False)
    sheet.format(f'F2:F{len(data)+1}', DATETIME_FORMAT)
    time.sleep(15)

    # Get profits
    profit_columns = [i for i in headers if 'SGD' in i]
    profits = {col.split(' (SGD)')[0]: data[2][col] for col in profit_columns}
    profits[profit_headers[0]] = profit_headers[0]

    # Transform data
    # - keep unaffected rows (index = 4)
    # - insert new 
    unaffected = data[4:]

    tmp = {}
    for i in range(4):
        if i == 0:
            tmp = {key: data[i][key] for key in data[i].keys()}
            for k, v in profits.items():
                data[i][k] = v
        else:
            tmp1 = {key: data[i][key] for key in data[i].keys()}
            for k, v in tmp.items():
                if k in profits.keys():
                    data[i][k] = v
            tmp = tmp1
    
    for k in tmp.keys():
        if k not in profits.keys():
            tmp[k] = ''

    new_data = data[:4] + [tmp] + unaffected
    payload = sheetPayload(new_data)

    try:
        response = sheet.update(payload, raw=False)
        sheet.format(f'F2:F{len(data)+2}', DATETIME_FORMAT)
        return {
            'status': 'OK',
            'result': response
        }
    except Exception as e:
        return {
            'status': 'NOT_OK',
            'result': e.args[0]['message'][:100]
        }

if __name__ == '__main__':
    if 1:
        configVars = loadData()
        response = updateSheet(configVars)
        print(response['status'], response['result'])
    else:
        with open('sample.json') as file:
            data = json.load(file)