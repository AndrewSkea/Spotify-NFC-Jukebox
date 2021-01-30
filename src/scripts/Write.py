from time import sleep
import json
import sys
import os
from mfrc522 import SimpleMFRC522
import RPi.GPIO as GPIO
import requests

GPIO.setwarnings(False)
reader = SimpleMFRC522()
text = "stopping"
try:
    while True:
        print("Hold a tag near the reader")
        cid, text_in = reader.write_no_block(text)
        while not cid:
            cid, text_in = reader.write_no_block(text)
            sleep(0.5)
        past_cid = cid
        print(cid, text_in)
        sleep(5)
except KeyboardInterrupt:
    GPIO.cleanup()
    raise
except Exception as e:
    print("FAILURE: {}".format(e))

