import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

reader = SimpleMFRC522()

try:
        print("Place tag near reader")
        id, text = reader.read()
        print("ID: {} Text: {}".format(id, text))
finally:
        GPIO.cleanup()
