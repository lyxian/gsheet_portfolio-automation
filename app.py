# from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request
import traceback
import requests
import os

from utils import loadSecrets, updateSheet, postError

configVars = loadSecrets()
DEBUG_MODE = os.environ.get("DEBUG_MODE", True)

if not configVars:
    configVars = {
        'DATABASE_NAME': os.getenv('DATABASE_NAME', None),
        'DATABASE_SHEET': os.getenv('DATABASE_SHEET', None),
        'PASSWORD': os.getenv('PASSWORD', None),
    }

app = Flask(__name__)
app.configVars = configVars

@app.route("/stop", methods=["GET", "POST"])
def stop():
    if request.method == 'POST':
        password = os.getenv('PASSWORD', '1234')
        if 'password' in request.json and str(request.json['password']) == password:
            shutdown_hook = request.environ.get("werkzeug.server.shutdown")
            try:
                shutdown_hook()
                print("--End--")
            except:
                pass
            return {'status': 'OK'}, 200
        else:
            return {'ERROR': 'Wrong password!'}, 400
    else:
        return {'ERROR': 'Nothing here!'}, 404

@app.route("/getIP", methods=["GET"])
def _getIP():
    if request.method == "GET":
        URL = 'https://api.ipify.org?format=json'
        return requests.get(URL).json(), 200

@app.route('/update', methods=['GET', 'POST'])
def _update():
    if request.method == 'POST':
        password = os.getenv('PASSWORD') if not app.configVars else app.configVars['PASSWORD']
        if 'password' in request.json and request.json['password'] == int(password):
            try:
                # Trigger update
                response = updateSheet(app.configVars)
                if response['status'] == 'OK':
                    return {'status': 'OK'}, 200
                else:
                    return response, 401
            except Exception:
                error = traceback.format_exc().strip()
                try:
                    response = postError(error)
                    if response:
                        print(f'=====APP ERROR=====\n{error}\n=====ERROR END=====')
                        return {'status': 'NOT_OK', 'ERROR': 'Error posted successfully!'}, 503
                    else:
                        # INTERNAL SERVER ERROR
                        return {'status': 'NOT_OK', 'ERROR': 'Unknown error!'}, 500
                except Exception as e:
                    print(f'=====APP ERROR=====\n{error}\n=====ERROR END=====')
                    print(f'=====LOG ERROR=====\n{e.__repr__()}\n=====ERROR END=====')
                    return {'status': 'NOT_OK', 'ERROR': e.__repr__()}, 503
        else:
            return {'status': 'NOT_OK', 'ERROR': 'Wrong password!'}, 401
    else:
        return {'status': 'NOT_OK', 'ERROR': 'Nothing here!'}, 404

if __name__ == "__main__":
    app.run(debug=DEBUG_MODE, host="0.0.0.0", port=int(os.environ.get("PORT", 5005)))
