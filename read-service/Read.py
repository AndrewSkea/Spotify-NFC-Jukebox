#!/usr/bin/env python
import subprocess
import RPi.GPIO as GPIO
import os
import requests
import json
from mfrc522 import SimpleMFRC522

GPIO.setwarnings(False)
reader = SimpleMFRC522()

with open("../jukebox-web/settings.json", "r") as jsonFile:
    data = json.load(jsonFile)
    
room_name = data["sonos_room"]
base_url = "http://localhost:5005/{}".format(room_name)
play_url = base_url + "/spotify/now/"


def ensure_shuffle():
    requests.get(base_url + "/repeat/on")
    requests.get(base_url = "/shuffle/on")
    req = requests.get(base_url = "/state")
    if req.json():
        return req["playMode"]["shuffle"] == "true"
    else:
        return False

while True:
    try:
        # Check if raspotify is running
        # output = subprocess.check_output("spotify-cli devices", shell=True)
        # output = output.decode("utf-8")
        # running = True if "raspotify" in output else False
        # if not running:
        #     # Start raspotify
        #     service_out = subprocess.check_output("sudo service raspotify restart", shell=True)
        #     print(service_out.decode("utf-8"))
            
        # Read from card
        ensure_shuffle()
        print("Place RFID Card on reader")
        card_id, text = reader.read()
        if text:
            ensure_shuffle()
            req = requests.get(base_url + text)
            if req.status_code  < 400:
                break
            else:
                status = "Can't find URI"

        # shuffle_cmd = "spotify-cli shuffle on"
        # play_cmd = "spotify-cli play --device \"raspotify\" --uri_string \"{}\"".format(text)
        # print(play_cmd)
        # _cmd = os.system(play_cmd)
        # print("Play command ran with exit code %d" % _cmd)
        # _scmd = os.system(shuffle_cmd)
    finally:
        GPIO.cleanup()
