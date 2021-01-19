import os
import json


CURRENT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))
APP_HOME = os.path.abspath(os.path.join(CURRENT_DIR, '..'))
SETTINGS_FILE = os.path.abspath(os.path.join(APP_HOME, 'config', 'settings.json'))


SONOS_BASE_URL = "http://localhost:8081"
STATE_URL = SONOS_BASE_URL + "/state"
NEXT_URL = SONOS_BASE_URL + "/next"
PLAY_URL = SONOS_BASE_URL + "/play"
PAUSE_URL = SONOS_BASE_URL + "/pause"
DEVICES_URL = SONOS_BASE_URL + "/devices"

if not os.path.exists(SETTINGS_FILE):
    with open(SETTINGS_FILE, "w+") as f:
        json.dump({"sonos_room": "Living Room"}, f)


def __log_constant(const):
    print("----------\nPath: {}\nExists: {}\nRead:{}\nWrite:{}\nExecute:{}\n----------".format(
            const, os.access(const, os.F_OK), os.access(const, os.R_OK), 
            os.access(const, os.W_OK), os.access(const, os.X_OK)
        )
    )

def log_constants():
    l = [CURRENT_DIR, APP_HOME, SETTINGS_FILE]
    [__log_constant(c) for c in l]

