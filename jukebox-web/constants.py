import os
import json


CURRENT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))
SETTINGS_FILE = os.path.abspath(os.path.join(CURRENT_DIR, 'settings.json'))
STOP_READ_FILE = os.path.abspath(os.path.join(CURRENT_DIR, 'stop_read.sh'))
if not os.path.exists(SETTINGS_FILE):
    with open(SETTINGS_FILE, "w+") as f:
        f.write("{}")
APP_HOME = os.path.abspath(os.path.join(CURRENT_DIR, '..'))
PRESETS_FILE = os.path.abspath(os.path.join(APP_HOME, 'node-sonos-http-api', 'presets', 'example.json'))
SONOS_SETTINGS_FILE = os.path.abspath(os.path.join(APP_HOME, 'node-sonos-http-api', 'settings.json'))
RASPOTIFY_FILE = "/etc/default/raspotify"

sonos_json = {
    "port": 5005,
    "ip": "0.0.0.0",
    "securePort": 5006,
    "spotify": {
        "clientId": "your-spotify-application-clientId",
        "clientSecret": "your-spotify-application-clientSecret"
    }
}

if not os.path.exists(SONOS_SETTINGS_FILE):
    with open(SONOS_SETTINGS_FILE, "w+") as f:
        f.write(str(sonos_json))
        
else:
    with open(SETTINGS_FILE, "r+") as jsonFile:
        data = json.load(jsonFile)
        spot_id = data["spotify_client_id"]
        spot_sec = data["spotify_client_secret"]
    sonos_json["spotify"]["clientId"] = spot_id
    sonos_json["spotify"]["clientSecret"] = spot_sec
    with open(SONOS_SETTINGS_FILE, "w+") as jsonFile:
        json.dump(sonos_json, jsonFile)


def __log_constant(const):
    print("----------\nPath: {}\nExists: {}\nRead:{}\nWrite:{}\nExecute:{}\n----------".format(
            const, os.access(const, os.F_OK), os.access(const, os.R_OK), 
            os.access(const, os.W_OK), os.access(const, os.X_OK)
            )
        )

def log_constants():
    l = [CURRENT_DIR, SETTINGS_FILE, APP_HOME, PRESETS_FILE, SONOS_SETTINGS_FILE, RASPOTIFY_FILE]
    [__log_constant(c) for c in l]

