import os
import json


CURRENT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))
SETTINGS_FILE = os.path.abspath(os.path.join(CURRENT_DIR, 'settings.json'))
APP_HOME = os.path.abspath(os.path.join(CURRENT_DIR, '..'))
SONOS_SETTINGS_FILE = os.path.abspath(os.path.join(APP_HOME, 'sonos-service', 'settings.json'))

SONOS_BASE_URL = "http://localhost:8081"
STATE_URL = SONOS_BASE_URL + "/state"
NEXT_URL = SONOS_BASE_URL + "/next"

if not os.path.exists(SONOS_SETTINGS_FILE):
    with open(SONOS_SETTINGS_FILE, "w+") as f:
        f.write(str({"Room": "Living Room"}))


def __log_constant(const):
    print("----------\nPath: {}\nExists: {}\nRead:{}\nWrite:{}\nExecute:{}\n----------".format(
            const, os.access(const, os.F_OK), os.access(const, os.R_OK), 
            os.access(const, os.W_OK), os.access(const, os.X_OK)
        )
    )

def log_constants():
    l = [CURRENT_DIR, SETTINGS_FILE, APP_HOME, SONOS_SETTINGS_FILE]
    [__log_constant(c) for c in l]

