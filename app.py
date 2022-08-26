# from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request
import requests
import os

from utils import loadData, updateSheet

configVars = loadData()
DEBUG_MODE = os.environ.get("PORT", True)

app = Flask(__name__)

if __name__ == "__main__":

    @app.route("/stop")
    def stop():
        shutdown_hook = request.environ.get("werkzeug.server.shutdown")
        try:
            shutdown_hook()
            return {'status': 'NOT_OK'}, 404
        except:
            pass

    @app.route("/getIP", methods=["GET"])
    def _getIP():
        if request.method == "GET":
            URL = 'https://api.ipify.org?format=json'
            return requests.get(URL).json(), 200

    @app.route('/update', methods=['POST'])
    def _update():
        if request.method == 'POST':
            password = os.getenv('PASSWORD') if not configVars else configVars['PASSWORD']
            if 'password' in request.json and request.json['password'] == int(password):
                # Trigger update
                response = updateSheet(configVars)
                if response['status'] == 'OK':
                    return {'status': 'OK'}, 200
                else:
                    return response, 401
            else:
                return {'ERROR': 'Wrong password!'}, 404
        else:
            return {'ERROR': 'Nothing here!'}, 404

    app.run(debug=DEBUG_MODE, host="0.0.0.0", port=int(os.environ.get("PORT", 5005)))
