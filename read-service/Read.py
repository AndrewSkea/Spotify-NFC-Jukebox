from time import sleep
import json
import sys
import os
from mfrc522 import SimpleMFRC522
import RPi.GPIO as GPIO
import requests

GPIO.setwarnings(False)
reader = SimpleMFRC522()

past_cid = None
CURRENT_DIR = os.path.dirname(__file__)
SETTINGS_FILE = os.path.abspath(os.path.join(CURRENT_DIR, '..', 'jukebox-web', 'settings.json'))
data = None

while data is None:
    try:
        with open(SETTINGS_FILE, "r") as jsonFile:
            data = json.load(jsonFile)
    except Exception:
        print("No settings file")
    sleep(5)

room_name = data["sonos_room"] or "Living Room"
base_url = "http://localhost:8081/{}".format(room_name)
base_url = base_url.replace(" ", "%20")
play_url = base_url + "/play/"
pause_url = base_url + "/pause"
next_url = base_url + "/next"

def play_playlist(uri):
    url = "{}{}".format(play_url, uri.strip())
    print(url)
    req = requests.get(url)
    print("Play Response: {}".format(req.content))


def do_pause():
    print(pause_url)
    req = requests.get(pause_url)
    print("Pause Response: {}".format(req.content))


def do_next():
    print(next_url)
    req = requests.get(next_url)
    print("Next Response: {}".format(req.content))


try:
    while True:
        print("Hold a tag near the reader")
        cid, text = reader.read_no_block()
        while not cid:
            cid, text = reader.read_no_block()
            sleep(0.5)
        past_cid = cid
        text = text.replace(" ", "")
        print("ID: %s\nText: %s" % (cid,text))

        print("Perform action")
        if text == "pause":
            do_pause()
        elif text == "next":
            do_next()
        elif "spotify" in text:
            play_playlist(text)
        else:
            print("Not valid text: {}".format(text))

        while cid and cid == past_cid:
            sleep(3)
            print("Checking")
            for i in range(10):
                cid, text = reader.read_no_block()
                if cid:
                    break
        print("Card removed, sleeping 5 seconds before next read")
        sleep(5)
        
except KeyboardInterrupt:
    GPIO.cleanup()
    raise
except Exception as e:
    print("FAILURE: {}".format(e))
