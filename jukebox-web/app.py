from multiprocessing import Pool, context
from multiprocessing.context import TimeoutError
import time
import json
import requests
from flask import Flask, render_template, Response, jsonify, request

from utils import get_room_name, timeout, start_read_service, stop_read_service, update_files_from_settings

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
def worker(spotify_uri="", is_read=False):
    print('Starting {}'.format(spotify_uri))
    stop_read_service()
    if is_read:
        nfc_id, text = reader.read()
        start_read_service()
        print("Done: ID:{} Text:{}".format(nfc_id, text))
        return [nfc_id, text]
    else:
        reader.write(str(spotify_uri))
        start_read_service()
        print("Done: {}".format(spotify_uri))
        return [spotify_uri]


@app.route("/check-nfc-progress", methods=['GET'])
def check_progress():
    status_resp = "Place RFID Card on Reader"
    if pool_result.ready():
        try:
            ret = pool_result.get(timeout=1)[0]
            if ret is not None:
                if len(ret) == 1:
                    status_resp = "Written {} to RFID card".format(ret)
                if len(ret) == 2:
                    status_resp = "Read URI:{} from RFID card with ID: {}".format(ret[1], ret[0])
        except context.TimeoutError:
            status_resp = "Write operation has timed out!"
    return jsonify({"status": status_resp})


@app.route('/write-uri/<spotify_uri>', methods=['POST'])
def write_uri(spotify_uri):
    pool = Pool()
    global pool_result
    pool_result = pool.map_async(worker, [spotify_uri])
    return Response("{'status':'started'}", status=202, mimetype='application/json')


@app.route('/read-uri', methods=['GET'])
def read_uri():
    pool = Pool()
    global pool_result
    pool_result = pool.map_async(worker, ["", True])
    return Response("{'status':'started'}", status=202, mimetype='application/json')


@app.route('/get-zone-list', methods=['GET'])
def read_zone_list():
    req = requests.get("http://localhost:5005/zones")
    try:
        members = req.json()["members"]
        zone_list = []
        for mem in members:
            zone_list.append(mem["roomName"])
        return {"status": "success", "room_names": zone_list}
    except:
        return {"status": "failed"}


@app.route('/get-current-status', methods=['GET'])
def read_current_state():
    ret = {"status": "failed"}
    req = requests.get("http://localhost:5005/{}/state".format(get_room_name()))
    if req.json():
        j = req.json()
        to_ret = {
            "cur_playing_title": j["current_track"]["title"],
            "cur_playing_artist": j["current_track"]["artist"],
            "next_playing_title": j["nextTrack"]["title"],
            "next_playing_artist": j["nextTrack"]["artist"]
        }
        ret = {"status": "success", "state": to_ret}
    return ret


@app.route('/next-song', methods=['POST'])
def next_song():
    req = requests.get("http://localhost:5005/{}/next".format(get_room_name()))
    if req.json():
        return req.json()

@app.route('/update-auth', methods=['POST'])
def update_spotify_auth():
    username = request.form['spotify-username']
    password = request.form['spotify-password']
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


@app.route('/update-spotify-app-auth', methods=['POST'])
def update_spotify_app_auth():
    client_id = request.form['spotify-client-id']
    client_secret = request.form['spotify-client-secret']
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


@app.route('/update-sonos', methods=['POST'])
def update_sonos_room(sonos_room):
    sonos_room = request.form['sonos-room']
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
