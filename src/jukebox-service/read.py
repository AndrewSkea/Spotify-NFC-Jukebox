from time import sleep
import sys
from mfrc522 import SimpleMFRC522
import RPi.GPIO as GPIO
import requests
import multiprocessing as mp
from multiprocessing import current_process

from cli.commands.devices import devices
from cli.commands.shuffle import shuffle
from cli.commands.play import play
from cli.commands.pause import pause
from cli.commands.next import _next

from utils import is_sonos

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(18,GPIO.OUT)

def flash_led():
    return True
    # GPIO.output(18,GPIO.HIGH)
    # sleep(0.5)
    # GPIO.output(18,GPIO.LOW)


class ReadService(mp.Process):
    def __init__(self):
        mp.Process.__init__(self)
        self.reader = SimpleMFRC522()
        self.base_url = "http://localhost:8081"
        self.play_url = self.base_url + "/play"
        self.shuffle_url = self.base_url + "/shuffle"
        self.flush_url = self.base_url + "/flush"
        self.pause_url = self.base_url + "/pause"
        self.next_url = self.base_url + "/next"
        self.past_cid = None

    def _print(self, msg):
        cur = current_process()
        print("par:{}.this:{}.name:{} | {}".format(cur._parent_pid, cur.pid, cur.name, msg))
        sys.stdout.flush()

    def make_request(self, url):
        try:
            self._print("Request to: " + url)
            req = requests.get(url)
            # flash_led()
            self._print("Response: {}".format(req.content))
            return True
        except:
            self._print("Response: FAILED - no connection")
            return False

    def do_pause(self):
        if is_sonos():
            pause()
        else:
            self.make_request(self.pause_url)

    def do_next(self):
        if is_sonos():
            _next()
        else:
            self.make_request(self.next_url)
        
    def do_shuffle(self):
        if is_sonos():
            shuffle()
        else:
            self.make_request(self.shuffle_url)
        
    def do_flush(self):
        if is_sonos():
            pass
        else:
            self.make_request(self.flush_url)
    
    def play(self, uri):
        uri = uri.strip()
        self.do_flush()
        self.do_shuffle()
        if is_sonos():
            play(keyword=uri, play_type="uri", shuffle=True)
        else:
            if "playlist" in uri:
                uri = "spotify:user:" + uri
            self._print("URI: " + uri)
            url = "{}/{}".format(self.play_url, uri)
            self.make_request(url)

    def run(self):
        self._print("Started run with base url: {}".format(self.base_url))
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
