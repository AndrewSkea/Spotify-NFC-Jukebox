from time import sleep
import time
import json
import sys
import os
from mfrc522 import SimpleMFRC522
import RPi.GPIO as GPIO
import requests
import RPi.GPIO as GPIO

def button_callback(channel):
    print("Button was pushed!")

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(8, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
reader = SimpleMFRC522()

past_cid = None
CURRENT_DIR = os.path.dirname(__file__)
SETTINGS_FILE = os.path.abspath(os.path.join(CURRENT_DIR, '..', 'config', 'settings.json'))
data = None

room_name = "Living Room"
base_url = "http://localhost:8081"
play_url = base_url + "/play"
shuffle_url = base_url + "/shuffle"
flush_url = base_url + "/flush"
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


def do_flush():
    _print(flush_url)
    req = requests.get(flush_url)
    _print("Flush Response: {}".format(req.content))


def play(uri):
    uri = uri.strip()
    if "playlist" in uri:
        uri = "spotify:user:" + uri
    url = "{}/{}".format(play_url, uri)
    _print(url)
    do_flush()
    do_shuffle()
    req = requests.get(url)
    _print("Play Response: {}".format(req.content))


def read_rfid(callback):
    print("Reading RFID tag")
    _print("Hold a tag near the reader")
    start_time = time.time()
    cid, text = reader.read_no_block()
    while not cid and (time.time() - start_time) < 5:
        cid, text = reader.read_no_block()
        sleep(0.5)
    if not cid or not text:
        return None
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
    time.sleep(5)
    return None


def read_pause_button(callback):
    print("Doing PAUSE")
    do_pause()
    time.sleep(5)
    return None


GPIO.add_event_detect(10,GPIO.RISING,callback=read_rfid)
GPIO.add_event_detect(8,GPIO.RISING,callback=read_pause_button)
message = input("Press enter to quit\n\n")
GPIO.cleanup()
