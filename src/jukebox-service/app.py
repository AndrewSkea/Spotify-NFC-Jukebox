import threading
import time
import json
import os
import requests
from flask import Flask, send_from_directory, render_template, Response, jsonify, request, flash, redirect, url_for

from read import ReadService, flash_led
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

make_all_access(SETTINGS_FILE)
log_constants()
restart_sonos_api()

read_proc = None

global start_readservice_thread
start_readservice_thread = None

global read_thread
read_thread = None

global write_thread
write_thread = None


def stop_read():
    global read_proc
    print("Stopping read service")
    ret = False
    print(read_proc)
    if read_proc:
        read_proc.terminate()
        read_proc.kill()
        time.sleep(0.1)
        read_proc.join(timeout=1.0)
        print("Terminating read")
        time.sleep(0.1)
        print(read_proc)
        if not read_proc.is_alive():
            print("Terminated")
            ret = True
    return ret
    
    
def start_read():
    t = time.time()
    start_readservice_thread = StartReadServiceThread()
    start_readservice_thread.start()
    print(time.time() - t)
    return True


class StartReadServiceThread(threading.Thread):
    def __init__(self):
        super().__init__()

    def run(self):
        time.sleep(5)
        global read_proc
        print("Starting read service")
        ret = False
        if read_proc:
            read_proc.terminate()
            read_proc.join(timeout=1.0)
        read_proc = ReadService()
        read_proc.start()
        time.sleep(0.1)
        if read_proc.is_alive():
            ret = True
        return ret


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
            t = time.time() - self.init_time
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
            t = time.time() - self.init_time
            self.cid, self.text = reader.write_no_block(self.write_text)
            self.status = "Place RFID card on reader until confirmation here. (timeout in {}s)".format(int(30-t))
            time.sleep(0.1)
        self.status = "complete"


@app.route("/check-write-progress", methods=['GET'])
def check_write_progress():
    global write_thread
    print("check write, cid: {}, text: {}, status: {}".format(write_thread.cid, write_thread.text, write_thread.status))
    if write_thread.cid:
        flash_led()
        data = {
            "status": "complete",
            "cid": write_thread.cid,
            "uri": write_thread.text
        }
        write_thread = None
        start_read()
        return data
    else:
        return {"status": write_thread.status, "id": "", "uri": ""}


@app.route('/write-uri/<spotify_uri>', methods=['POST'])
def write_uri(spotify_uri):
    print("Writing endpoint called with spot_uri: {}".format(spotify_uri))
    if str(spotify_uri).strip() == "stop":
        spotify_uri = "pause"
    spotify_uri += max(8-len(spotify_uri), 0) * " "

    stop_read()
    global write_thread
    write_thread = WriteThread(spotify_uri)
    write_thread.start()
    return check_write_progress()
    
    

@app.route("/check-read-progress", methods=['GET'])
def check_read_progress():
    global read_thread
    print("check read, cid: {}, text: {}, status: {}".format(read_thread.cid, read_thread.text, read_thread.status))
    if read_thread.cid:
        flash_led()
        data = {
            "status": "complete",
            "cid": read_thread.cid,
            "uri": read_thread.text
        }
        read_thread = None
        start_read()
        return data
    else:
        print("check read, no cid, status: {}".format(read_thread.status))
        return {"status": read_thread.status, "id": "", "uri": ""}


@app.route('/read-uri', methods=['GET'])
def read_uri():
    print("Reading endpoint called")
    stop_read()
    global read_thread
    read_thread = ReadThread()
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
        is_paused = True if j.get("state", "") == "paused" else False
        to_ret = {
            "title": j["playing"].get("title", ""),
            "album": j["playing"].get("album", ""),
            "artist": j["playing"].get("artist", ""),
            "is_paused": is_paused
        }
        ret = {"status": "success", "state": to_ret}
    return jsonify(ret)


@app.route('/next-song', methods=['GET'])
def next_song():
    req = requests.get(NEXT_URL)
    if req.status_code < 400:
        return {"status": "success"}
    return {"status": "failure"}
    

@app.route('/pause-song', methods=['GET'])
def pause_song():
    req = requests.get(PAUSE_URL)
    if req.status_code < 400:
        return {"status": "success"}
    return {"status": "failure"}
    
    
@app.route('/play-song', methods=['GET'])
def play_song():
    req = requests.get(PLAY_URL)
    if req.status_code < 400:
        return {"status": "success"}
    return {"status": "failure"}


@app.route('/update-sonos', methods=['POST'])
def update_sonos_room():
    sonos_room = request.form['sonos-room']
    if sonos_room != "":
        with open(SETTINGS_FILE, "r+") as jsonFile:
            data = json.load(jsonFile)

        data["sonos_room"] = sonos_room

        with open(SETTINGS_FILE, "w+") as jsonFile:
            json.dump(data, jsonFile)
        restart_sonos_api()
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
    
    
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                          'favicon.ico',mimetype='image/vnd.microsoft.icon')


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

if __name__ == '__main__':
    read_proc = ReadService()
    read_proc.start()
    app.run(debug=True, host='0.0.0.0', port=8000, use_reloader=False)
