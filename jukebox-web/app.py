from multiprocessing import Pool, context
from multiprocessing.context import TimeoutError
import time
import json
from flask import Flask, render_template, Response, jsonify

from utils import timeout, start_read_service, stop_read_service, update_files_from_settings

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

GPIO.setwarnings(False)
reader = SimpleMFRC522()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'UERAIJFajjdlierjlefwkfjelmm982374EFA'
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

global pool_result

@app.after_request
def add_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] =  "Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With"
    response.headers['Access-Control-Allow-Methods'] =  "POST, GET, PUT, OPTIONS"
    return response


@timeout(30)
def worker(spotify_uri):
    print('Starting {}'.format(spotify_uri))
    stop_read_service()
    reader.write(str(spotify_uri))
    start_read_service()
    print("Done: {}".format(spotify_uri))
    return spotify_uri


@app.route("/check-write-progress", methods=['GET'])
def check_progress():
    status_resp = "Place RFID Card on Reader"
    if pool_result.ready():
        try:
            ret = pool_result.get(timeout=1)[0]
            if ret is not None:
                status_resp = "Written {} to RFID card".format(ret)
        except context.TimeoutError:
            status_resp = "Write operation has timed out!"
    return jsonify({"status": status_resp})


@app.route('/write-uri/<spotify_uri>', methods=['POST'])
def write_uri(spotify_uri):
    pool = Pool()
    global pool_result
    pool_result = pool.map_async(worker, [spotify_uri])
    return Response("{'status':'started'}", status=202, mimetype='application/json')


def update_spotify_auth(username, password):
    if username != "" and password != "":

        with open("settings.json", "r") as jsonFile:
            data = json.load(jsonFile)

        data["spotify_username"] = username
        data["spotify_password"] = password

        with open("settings.json", "w") as jsonFile:
            json.dump(data, jsonFile)
        update_files_from_settings()
    else:
        return {"status": "invaliad input for username or password"}


def update_spotify_app_auth(client_id, client_secret):
    if client_id != "" and client_secret != "":

        with open("settings.json", "r") as jsonFile:
            data = json.load(jsonFile)

        data["spotify_client_id"] = client_id
        data["spotify_client_secret"] = client_secret

        with open("settings.json", "w") as jsonFile:
            json.dump(data, jsonFile)
        update_files_from_settings()
    else:
        return {"status": "invaliad input for client_id or client_secret"}


def update_sonos_room(sonos_room):
    if sonos_room != "":
        with open("settings.json", "r") as jsonFile:
            data = json.load(jsonFile)

        data["sonos_room"] = sonos_room

        with open("settings.json", "w") as jsonFile:
            json.dump(data, jsonFile)
        update_files_from_settings()
    else:
        return {"status": "invaliad input for sonos_room"}


@app.route('/', methods=['GET'])
def sessions():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
