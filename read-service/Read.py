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
SETTINGS_FILE = os.path.abspath(os.path.join(CURRENT_DIR, '..', 'config', 'settings.json'))
data = None

room_name = "Living Room"
base_url = "http://localhost:8081"
# base_url = base_url.replace(" ", "%20")
play_url = base_url + "/play"
shuffle_url = base_url + "/shuffle"
pause_url = base_url + "/pause"
next_url = base_url + "/next"

def _print(msg):
    print(msg)
    sys.stdout.flush()


def do_pause():
    _print(pause_url)
    req = requests.get(pause_url)
    _print("Pause Response: {}".format(req.content))


def do_next():
    _print(next_url)
    req = requests.get(next_url)
    _print("Next Response: {}".format(req.content))
    

def do_shuffle():
    _print(shuffle_url)
    req = requests.get(shuffle_url)
    _print("Shuffle Response: {}".format(req.content))
    

def play(uri):
    uri = uri.strip()
    if "playlist" in uri:
        uri = "spotify:user:" + uri
    url = "{}/{}".format(play_url, uri)
    _print(url)
    do_shuffle()
    req = requests.get(url)
    _print("Play Response: {}".format(req.content))
    do_next() # So it doesn't start with the same one each time


_print("Base URL: ".format(base_url))
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
        if text == "pause":
            do_pause()
        elif text == "next":
            do_next()
        elif "spotify" in text:
            play(text)
        else:
            _print("Not valid text: {}".format(text))

        while cid and cid == past_cid:
            sleep(3)
            _print("Checking")
            for i in range(10):
                cid, text = reader.read_no_block()
                if cid:
                    break
        _print("Card removed, pausing music")
        do_pause()
        
except KeyboardInterrupt:
    GPIO.cleanup()
    raise
except Exception as e:
    _print("FAILURE: {}".format(e))
