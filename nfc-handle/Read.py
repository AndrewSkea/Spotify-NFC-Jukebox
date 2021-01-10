#!/usr/bin/env python

import RPi.GPIO as GPIO
import os
from mfrc522 import SimpleMFRC522

GPIO.setwarnings(False)
reader = SimpleMFRC522()

while True:
    try:
        print("Place RFID Card on reader")
        id, text = reader.read()
        shuffle_cmd = "spotify-cli shuffle on"
        play_cmd = "spotify-cli play --uri_string {}".format(text)
        print(play_cmd)
        _cmd = os.system(play_cmd)
        print("Play command ran with exit code %d" % _cmd)
        _scmd = os.system(shuffle_cmd)
    finally:
        GPIO.cleanup()
