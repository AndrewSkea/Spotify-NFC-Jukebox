from multiprocessing import Pool, context
from multiprocessing.context import TimeoutError
import time
import json
import os
import requests
from flask import Flask, render_template, Response, jsonify, request, flash, redirect, url_for

from utils import make_all_access, get_sonos_room, timeout, restart_sonos_api, start_read_service, stop_read_service, update_sonos_room_from_settings, update_spotify_app_auth_from_settings, update_spotify_auth_from_settings
from constants import *

try:
    from mfrc522 import SimpleMFRC522
    reader = SimpleMFRC522()
except ModuleNotFoundError as e:
    print(e)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'UERAIJFajjdlierjlefwkfjelmm982374EFA'
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

global text_to_write

make_all_access(RASPOTIFY_FILE)
make_all_access(SONOS_SETTINGS_FILE)
make_all_access(SETTINGS_FILE)
log_constants()
restart_sonos_api()



@app.after_request
def add_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] =  "Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With"
    response.headers['Access-Control-Allow-Methods'] =  "POST, GET, PUT, OPTIONS"
    return response

@app.route("/check-write-progress", methods=['GET'])
def check_write_progress():
    global text_to_write
    print("Trying to write: " + text_to_write)
    cid, text_in, status = None, None, "Place RFID card on reader until confirmation here"
    for _ in range(20):
        cid, text_in = reader.write_no_block(text_to_write)
        if cid and text_in:
            break
            
    if cid and text_in:
        print("Successfully written {} to {}".format(cid, text_in))
        start_read_service()
        status = "success"
    return {"status": status, "id": cid, "uri": text_in}


@app.route('/write-uri/<spotify_uri>', methods=['POST'])
def write_uri(spotify_uri):
    print(spotify_uri)
    if spotify_uri.strip() == "stop":
        spotify_uri = "pause"
    spotify_uri += max(8-len(spotify_uri), 0) * " "
    global text_to_write
    text_to_write = spotify_uri
    print("Reading endpoint called")
    stop_read_service()
    ret = check_write_progress()
    return ret
    
    

@app.route("/check-read-progress", methods=['GET'])
def check_read_progress():
    cid, text, status = None, None, "Place RFID card on reader until confirmation here"
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

        with open(SETTINGS_FILE, "r+") as jsonFile:
            data = json.load(jsonFile)

        data["spotify_username"] = username
        data["spotify_password"] = password

        with open(SETTINGS_FILE, "w+") as jsonFile:
            json.dump(data, jsonFile)
        update_spotify_auth_from_settings()
        flash('Updated authentication for Spotify')
        return redirect(url_for('index'))
    else:
        return {"status": "invaliad input for username or password"}


@app.route('/update-spotify-app-auth', methods=['POST'])
def update_spotify_app_auth():
    client_id = request.form['spotify-client-id']
    client_secret = request.form['spotify-client-secret']
    if client_id != "" and client_secret != "":

        with open(SETTINGS_FILE, "r+") as jsonFile:
            data = json.load(jsonFile)

        data["spotify_client_id"] = client_id
        data["spotify_client_secret"] = client_secret

        with open(SETTINGS_FILE, "w+") as jsonFile:
            json.dump(data, jsonFile)
        update_spotify_app_auth_from_settings()
        flash('Updated authentication for Spotify App')
        return redirect(url_for('index'))
    else:
        return {"status": "invaliad input for client_id or client_secret"}


@app.route('/update-sonos', methods=['POST'])
def update_sonos_room():
    sonos_room = request.form['sonos-room']
    if sonos_room != "":
        with open(SETTINGS_FILE, "r+") as jsonFile:
            data = json.load(jsonFile)

        data["sonos_room"] = sonos_room

        with open(SETTINGS_FILE, "w+") as jsonFile:
            json.dump(data, jsonFile)
        update_sonos_room_from_settings()
        flash('Updated Sonos Room preference')
        return redirect(url_for('index'))
    else:
        return {"status": "invaliad input for sonos_room"}


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
