from utils import loadData
import requests

configVars = loadData()

url = 'http://{}:{}/update'.format(configVars['LOCALHOST'], configVars['PORT'])
payload = {'password': configVars['PASSWORD']}

response = requests.post(url, json=payload)
if response.ok:
    print(response.json())
else:
    print(response.content)