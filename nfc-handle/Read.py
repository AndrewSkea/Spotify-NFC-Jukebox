#!/usr/bin/env python

import RPi.GPIO as GPIO
import os
from mfrc522 import SimpleMFRC522

GPIO.setwarnings(False)
reader = SimpleMFRC522()

while True:
    try:
        # Check if raspotify is running
        output = subprocess.check_output("spotify-cli devices", shell=True)
        output = output.decode("utf-8")
        running = True if "raspotify" in output else False
        if not running:
            # Start raspotify
            service_out = subprocess.check_output("sudo service raspotify restart", shell=True)
            print(service_out.decode("utf-8"))
            
        # Read from card
        print("Place RFID Card on reader")
        id, text = reader.read()
        shuffle_cmd = "spotify-cli shuffle on"
        play_cmd = "spotify-cli play --device \"raspotify\" --uri_string \"{}\"".format(text)
        print(play_cmd)
        _cmd = os.system(play_cmd)
        print("Play command ran with exit code %d" % _cmd)
        _scmd = os.system(shuffle_cmd)
    finally:
        GPIO.cleanup()
