import multiprocessing.pool
import functools
import subprocess
import json

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

GPIO.setwarnings(False)
reader = SimpleMFRC522()

def timeout(max_timeout):
    """Timeout decorator, parameter in seconds."""
    def timeout_decorator(item):
        """Wrap the original function."""
        @functools.wraps(item)
        def func_wrapper(*args, **kwargs):
            """Closure for function."""
            pool = multiprocessing.pool.ThreadPool(processes=1)
            async_result = pool.apply_async(item, args, kwargs)
            # raises a TimeoutError if execution exceeds max_timeout
            return async_result.get(max_timeout)
        return func_wrapper
    return timeout_decorator


def stop_read_service():
    output = subprocess.check_output("pm2 stop read-service", shell=True)
    output = output.decode("utf-8")
    return True if "stopped" in output else False


def start_read_service():
    output = subprocess.check_output("pm2 start read-service", shell=True)
    output = output.decode("utf-8")
    return True if "started" in output else False


def update_files_from_settings():
    with open("settings.json", "r") as jsonFile:
        data = json.load(jsonFile)
    username = data["spotify_username"]
    password = data["spotify_password"]
    client_id = data["spotify_client_id"]
    client_secret = data["spotify_username"]
    sonos_room = data["sonos_room"]

    # Update the username and password for raspotify
    lines = open('/etc/default/raspotify').read().splitlines()
    line_to_rep = None
    for i, line in enumerate(lines):
        print(line)
        if line.startswith("OPTIONS"):
            print(line)
            line_to_rep = i
    lines[line_to_rep-1] = "OPTIONS=\" --username {} --password {}\"".format(username, password)
    open('/etc/default/raspotify','w').write('\n'.join(lines))

    # Update spotify-cli auth
    cmd = "spotify-cli config --set-app-client-id {} --set-app-client-secret {} --set-redirect-port 5555".format(client_id, client_secret)
    output = subprocess.check_output(cmd, shell=True)

    # Update settings.json in sonos-http-app
    with open("../node-sonos-http-api/presets/presets.json", "r") as jsonFile:
        data = json.load(jsonFile)

    data["players"] = [
        {
        "roomName": sonos_room,
        "volume": 10
        }
    ]

    with open("../node-sonos-http-api/presets/presets.json", "w") as jsonFile:
        json.dump(data, jsonFile)

    'spotify: {"clientId": "{}", "clientSecret": "{}" }'.format(client_id, client_secret)

