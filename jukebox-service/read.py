from time import sleep
import sys
from mfrc522 import SimpleMFRC522
import RPi.GPIO as GPIO
import requests
import multiprocessing as mp

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(18,GPIO.OUT)

def flash_led():
    GPIO.output(18,GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(18,GPIO.LOW)


class ReadService(mp.Process):
    def __init__(self):
        mp.Process.__init__(self)
        self.reader = SimpleMFRC522()
        self.base_url = "http://localhost:8081"
        self.play_url = base_url + "/play"
        self.shuffle_url = base_url + "/shuffle"
        self.flush_url = base_url + "/flush"
        self.pause_url = base_url + "/pause"
        self.next_url = base_url + "/next"
        self.past_cid = None

    def _print(self, msg):
        print(msg)
        sys.stdout.flush()

    def make_request(self, url):
        _print("Request to: " + url)
        req = requests.get(url)
        flash_led()
        _print("Response: {}".format(req.content))

    def do_pause(self):
        self.make_request(self.pause_url)

    def do_next(self):
        self.make_request(self.next_url)
        
    def do_shuffle(self):
        self.make_request(self.shuffle_url)
        
    def do_flush(self):
        self.make_request(self.flush_url)
    
    def play(self, uri):
        uri = uri.strip(self)
        if "playlist" in uri:
            uri = "spotify:user:" + uri
        url = "{}/{}".format(play_url, uri)
        do_flush()
        do_shuffle()
        self.make_request(url)

    def run(self):
        self._print("Started run with base url: ".format(self.base_url))
        try:
            while True:
                self._print("Hold a tag near the reader")
                cid, text = self.reader.read_no_block()
                while not cid:
                    cid, text = self.reader.read_no_block()
                    sleep(0.5)
                self.past_cid = cid
                text = text.replace(" ", "")
                self._print("ID: %s\nText: %s" % (cid,text))
                if text == "pause":
                    self.do_pause()
                elif text == "next":
                    self.do_next()
                elif "spotify" in text:
                    self.play(text)
                else:
                    self._print("Not valid text: {}".format(text))

                while cid and cid == self.past_cid:
                    sleep(3)
                    self._print("Checking")
                    for i in range(10):
                        cid, text = self.reader.read_no_block()
                        if cid:
                            break
                self._print("Card removed, pausing music")
                self.do_pause()
                
        except KeyboardInterrupt:
            GPIO.cleanup()
            raise
        except Exception as e:
            self._print("FAILURE: {}".format(e))
