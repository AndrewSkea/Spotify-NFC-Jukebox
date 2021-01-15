from multiprocessing import Pool, context
from multiprocessing.context import TimeoutError
import time
import json
import os
import requests
from flask import Flask, render_template, Response, jsonify, request, flash, redirect, url_for

from utils import get_sonos_room, timeout, start_read_service, stop_read_service, update_files_from_settings
from constants import *

try:
    from mfrc522 import SimpleMFRC522
    reader = SimpleMFRC522()
except ModuleNotFoundError as e:
    print(e)

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
        print("worker: is read")
        nfc_id, text = reader.read()
        start_read_service()
        print("Done: ID:{} Text:{}".format(nfc_id, text))
        return [nfc_id, text]
    else:
        print("worker: is not read")
        reader.write(str(spotify_uri))
        start_read_service()
        print("Done: {}".format(spotify_uri))
        return [spotify_uri]
        

@app.route("/check-nfc-progress", methods=['GET'])
def check_progress():
    status_resp = "Place RFID Card on Reader"
    if pool_result.ready():
        print("Pool is ready")
        try:
            ret = pool_result.get(timeout=1)
            print(ret)
            ret = ret[0] if ret else None
            if ret is not None:
                print("check_progress: " + str(ret))
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
    

@app.route("/check-read-progress", methods=['GET'])
def check_read_progress():
    cid, text, status = None, None, "Place RFID Card on Reader"
    for _ in range(10):
        cid, text = reader.read_no_block()
        if cid:
            break
            
    if cid and text:
        start_read_service()
        status = "success"
    return {"status": status, "id": cid, "uri": text}


@app.route('/read-uri', methods=['GET'])
def read_uri():
    print("Reading endpoint called")
    stop_read_service()
    ret = check_read_progress()
    return ret


@app.route('/get-zone-list', methods=['GET'])
def read_zone_list():
    try:
        req = requests.get("http://localhost:5005/zones")
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
    try: 
        req = requests.get("http://localhost:5005/{}/state".format(get_sonos_room()))
    except requests.exceptions.RequestException as e:
        req = None
    if req and req.json():
        j = req.json()
        to_ret = {
            "cur_track_title": j["currentTrack"].get("title", ""),
            "cur_track_artist": j["currentTrack"].get("artist", ""),
            "next_track_title": j["nextTrack"].get("title", ""),
            "next_track_artist": j["nextTrack"].get("artist", "")
        }
        ret = {"status": "success", "state": to_ret}
    return jsonify(ret)


@app.route('/next-song', methods=['POST'])
def next_song():
    req = requests.get("http://localhost:5005/{}/next".format(get_sonos_room()))
    if req.json():
        return req.json()

@app.route('/update-auth', methods=['POST'])
def update_spotify_auth():
    username = request.form['spotify-username']
    password = request.form['spotify-password']
    if username != "" and password != "":

        with open(SETTINGS_FILE, "r") as jsonFile:
            data = json.load(jsonFile)

        data["spotify_username"] = username
        data["spotify_password"] = password

        with open(SETTINGS_FILE, "w") as jsonFile:
            json.dump(data, jsonFile)
        update_files_from_settings()
        flash('Updated authentication for Spotify')
        return redirect(url_for('index'))
    else:
        return {"status": "invaliad input for username or password"}


@app.route('/update-spotify-app-auth', methods=['POST'])
def update_spotify_app_auth():
    client_id = request.form['spotify-client-id']
    client_secret = request.form['spotify-client-secret']
    if client_id != "" and client_secret != "":

        with open(SETTINGS_FILE, "r") as jsonFile:
            data = json.load(jsonFile)

        data["spotify_client_id"] = client_id
        data["spotify_client_secret"] = client_secret

        with open(SETTINGS_FILE, "w") as jsonFile:
            json.dump(data, jsonFile)
        update_files_from_settings()
        flash('Updated authentication for Spotify App')
        return redirect(url_for('index'))
    else:
        return {"status": "invaliad input for client_id or client_secret"}


@app.route('/update-sonos', methods=['POST'])
def update_sonos_room():
    sonos_room = request.form['sonos-room']
    if sonos_room != "":
        with open(SETTINGS_FILE, "r") as jsonFile:
            data = json.load(jsonFile)

        data["sonos_room"] = sonos_room

        with open(SETTINGS_FILE, "w") as jsonFile:
            json.dump(data, jsonFile)
        update_files_from_settings()
        flash('Updated Sonos Room preference')
        return redirect(url_for('index'))
    else:
        return {"status": "invaliad input for sonos_room"}


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
