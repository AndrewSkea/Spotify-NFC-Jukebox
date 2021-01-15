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
base_url = "http://localhost:5005/{}".format(room_name)
play_url = base_url + "/spotify/now/"
stop_url = base_url + "/stop"


try:
    while True:
        print("Hold a tag near the reader")
        cid, text = reader.read_no_block()
        while not cid:
            cid, text = reader.read_no_block()
            sleep(0.5)
        past_cid = cid
        print("ID: %s\nText: %s" % (cid,text))
        print("Perform action")
        if text == "stop":
            req = requests.get(stop_url)
            print("Response: {}".format(req.content))
        elif "spotify" in text:
            req = requests.get(play_url + text)
            print("Response: {}".format(req.content))
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
