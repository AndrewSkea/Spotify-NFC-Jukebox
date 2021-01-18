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
SETTINGS_FILE = os.path.abspath(os.path.join(CURRENT_DIR, '..', 'jukebox-service', 'settings.json'))
data = None

room_name = "Living Room"
base_url = "http://localhost:8081"
# base_url = base_url.replace(" ", "%20")
play_url = base_url + "/play"
pause_url = base_url + "/pause"
next_url = base_url + "/next"

def _print(msg):
    print(msg)
    sys.stdout.flush()

_print(base_url)


def do_pause():
    _print(pause_url)
    req = requests.get(pause_url)
    _print("Pause Response: {}".format(req.content))


def do_next():
    _print(next_url)
    req = requests.get(next_url)
    _print("Next Response: {}".format(req.content))
    
    
def play_playlist(uri):
    url = "{}/spotify:user:{}".format(play_url, uri.strip())
    _print(url)
    req = requests.get(url)
    _print("Play Response: {}".format(req.content))
    do_next() # So it doesn't start with the same one each time


try:
    while True:
        _print("Hold a tag near the reader")
        cid, text = reader.read_no_block()
        while not cid:
            cid, text = reader.read_no_block()
            sleep(0.5)
        past_cid = cid
        text = text.replace(" ", "")
        _print("ID: %s\nText: %s" % (cid,text))

        _print("Perform action")
        if text == "pause":
            do_pause()
        elif text == "next":
            do_next()
        elif "playlist" in text:
            play_playlist(text)
        else:
            _print("Not valid text: {}".format(text))

        while cid and cid == past_cid:
            sleep(3)
            _print("Checking")
            for i in range(10):
                cid, text = reader.read_no_block()
                if cid:
                    break
        _print("Card removed, sleeping 5 seconds before next read")
        do_pause()
        
except KeyboardInterrupt:
    GPIO.cleanup()
    raise
except Exception as e:
    _print("FAILURE: {}".format(e))
