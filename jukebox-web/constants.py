import os


CURRENT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))
SETTINGS_FILE = os.path.abspath(os.path.join(CURRENT_DIR, 'settings.json'))
if not os.path.exists(SETTINGS_FILE):
    with open(SETTINGS_FILE, "w+") as f:
        f.write("{}")
PI_HOME = os.path.abspath(os.path.join(CURRENT_DIR, '..', '..'))
PRESETS_FILE = os.path.abspath(os.path.join(PI_HOME, 'node-sonos-https-api', 'presets', 'example.json'))
SONOS_SETTINGS_FILE = os.path.abspath(os.path.join(PI_HOME, 'node-sonos-https-api', 'settings.js'))
RASPOTIFY_FILE = "/etc/default/raspotify"


def log_constants():
    print(CURRENT_DIR)
    print(SETTINGS_FILE)
    print(PI_HOME)
    print(PRESETS_FILE)
    print(SONOS_SETTINGS_FILE)

