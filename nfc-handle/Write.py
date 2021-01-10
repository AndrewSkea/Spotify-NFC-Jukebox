#!/usr/bin/env python

import sys
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

GPIO.setwarnings(False)
reader = SimpleMFRC522()

try:
    text = sys.argv[1]
    print("Writing {} - Now place your tag to write".format(text))
    reader.write(str(text))
    print("Written")
finally:
    GPIO.cleanup()
