from multiprocessing import Pool, context
from multiprocessing.context import TimeoutError
import time
import json
import os
import requests
from flask import Flask, render_template, Response, jsonify, request, flash, redirect, url_for

from utils import *
from constants import *

try:
    from mfrc522 import SimpleMFRC522
    reader = SimpleMFRC522()
except ModuleNotFoundError or FileNotFoundError:
    print("Module not found")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'UERAIJFajjdlierjlefwkfjelmm982374EFA'
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

make_all_access(SONOS_SETTINGS_FILE)
make_all_access(SETTINGS_FILE)
log_constants()
restart_sonos_api()

global read_thread
read_thread = None
global write_thread
write_thread = None


class ReadThread(threading.Thread):
    def __init__(self):
        self.status = "Place RFID card on reader until confirmation here"
        self.cid = None
        self.text = None
        self.init_time = time.time()
        super().__init__()

    def run(self):
        print("Starting Read")
        t = time.time() - self.init_time
        while self.cid is None and t < 30:
            self.cid, self.text = reader.read_no_block()
            self.status = "Place RFID card on reader until confirmation here. (timeout in {}s)".format(int(30-t))
            time.sleep(0.1)
        self.status = "complete"

class WriteThread(threading.Thread):
    def __init__(self, write_text):
        self.status = "Place RFID card on reader until confirmation here"
        self.cid = None
        self.text = None
        self.write_text = write_text
        self.init_time = time.time()
        super().__init__()

    def run(self):
        print("Trying to write: " + self.write_text)
        t = time.time() - self.init_time
        while self.cid is None and t < 30:
            self.cid, self.text = reader.write_no_block(self.write_text)
            self.status = "Place RFID card on reader until confirmation here. (timeout in {}s)".format(int(30-t))
            time.sleep(0.1)
        self.status = "complete"


@app.route("/check-write-progress", methods=['GET'])
def check_write_progress():
    global write_thread

    if write_thread.cid:
        data = {
            "status": "complete",
            "cid": write_thread.cid,
            "uri": write_thread.text
        }
        write_thread = None
        return data
    else:
        return {"status": write_thread.status, "id": "", "uri": ""}


@app.route('/write-uri/<spotify_uri>', methods=['POST'])
def write_uri(spotify_uri):
    print("Writing endpoint called with spot_uri: {}".format(spotify_uri))
    if spotify_uri.strip() == "stop":
        spotify_uri = "pause"
    spotify_uri += max(8-len(spotify_uri), 0) * " "

    stop_read_service()
    global write_thread
    write_thread = WriteThread(spotify_uri)
    write_thread.start()
    return check_write_progress()
    
    

@app.route("/check-read-progress", methods=['GET'])
def check_read_progress():
    global read_thread

    if read_thread.cid:
        data = {
            "status": "complete",
            "cid": read_thread.cid,
            "uri": read_thread.text
        }
        read_thread = None
        return data
    else:
        return {"status": read_thread.status, "id": "", "uri": ""}


@app.route('/read-uri', methods=['GET'])
def read_uri():
    print("Reading endpoint called")
    stop_read_service()
    global read_thread
    read_thread = ReadThread(spotify_uri)
    read_thread.start()
    return check_read_progress()


@app.route('/get-zone-list', methods=['GET'])
def read_zone_list():
    try:
        req = requests.get(DEVICES_URL)
        members = list(req.content)
        print(members)
        return {"status": "success", "room_names": members}
    except:
        return {"status": "failed"}


@app.route('/get-current-status', methods=['GET'])
def read_current_state():
    ret = {"status": "failed"}
    try: 
        req = requests.get(STATE_URL)
    except requests.exceptions.RequestException as e:
        req = None
    if req and req.json():
        j = req.json()
        to_ret = {
            "title": j["title"],
            "album": j["album"],
            "artist": j["artist"]
        }
        ret = {"status": "success", "state": to_ret}
    return jsonify(ret)


@app.route('/next-song', methods=['POST'])
def next_song():
    req = requests.get(NEXT_URL)
    if req.json():
        return req.json()
    return {}


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


@app.after_request
def add_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] =  "Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With"
    response.headers['Access-Control-Allow-Methods'] =  "POST, GET, PUT, OPTIONS"
    return response


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
