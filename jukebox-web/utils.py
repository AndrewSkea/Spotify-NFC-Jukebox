import multiprocessing.pool
import functools
import subprocess
import json
import os
from constants import *


def get_sonos_room():
    with open(SETTINGS_FILE, "r") as jsonFile:
        data = json.load(jsonFile)
    return data.get("sonos_room", "")
    

def make_all_access(file_path):
    cmd = ["sudo", "chmod", "775", file_path]
    subprocess.Popen(cmd, stdout=subprocess.PIPE)


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


def restart_sonos_api():
    print("Restarting sonos api service")
    cmd = ["sudo", "service", "sonos", "restart"]
    subprocess.Popen(cmd, stdout=subprocess.PIPE)


def restart_raspotify_service():
    print("Restarting raspotify")
    cmd = ["sudo", "service", "raspotify", "restart"]
    subprocess.Popen(cmd, stdout=subprocess.PIPE)


def stop_read_service():
    print("Stop read service")
    cmd = ["sudo", "service", "read", "stop"]
    subprocess.Popen(cmd, stdout=subprocess.PIPE)
    # print("Stopping read service: listing first")
    # cmd = "pm2 stop read-service"
    # print(cmd)
    # stream = os.popen(cmd)
    # output = stream.read()
    # print("Stopped the read service")


def start_read_service():
    print("Starting read service")
    cmd = ["sudo", "service", "read", "start"]
    subprocess.Popen(cmd, stdout=subprocess.PIPE)
    # cmd = ["pm2", "start", "read-service", "-a"]
    # subprocess.Popen(cmd, stdout=subprocess.PIPE)


def restart_all_services():
    restart_sonos_api()
    restart_raspotify_service()
    stop_read_service()
    start_read_service()


def insert_line(file_path, match_string, insert_string, del_line=None):
    with open(file_path, 'r+') as fd:
        contents = fd.readlines()
        if any([match_string in l for l in contents[-1]]):  # Handle last line to prevent IndexError
            contents.append(insert_string)
        else:
            for index, line in enumerate(contents):
                if match_string in line and insert_string not in contents[index + 1]:
                    contents.insert(index + 1, insert_string)
                    break
        fd.seek(0)
        fd.writelines(contents)
        
        
def del_line_from_list(lines, line_starts_with):
    final_list = []
    for i, line in enumerate(lines):
        if i == 0 or not line.startswith(line_starts_with):
            final_list.append(line)
    return final_list
        
        
def update_spotify_auth_from_settings():
    with open(SETTINGS_FILE, "r") as jsonFile:
        data = json.load(jsonFile)
    username = data["spotify_username"]
    password = data["spotify_password"]
    
    # Update the username and password for raspotify
    with open(RASPOTIFY_FILE, "r") as f:
        lines = f.read().splitlines()
    final_lines = del_line_from_list(lines, 'OPTIONS')
    
    final_lines.append('OPTIONS=" --username {} --password {}"'.format(username, password))
    open(RASPOTIFY_FILE,'w').write('\n'.join(final_lines))
    restart_raspotify_service()
    
    
    
def update_spotify_app_auth_from_settings():
    with open(SETTINGS_FILE, "r") as jsonFile:
        data = json.load(jsonFile)
    client_id = data["spotify_client_id"]
    client_secret = data["spotify_client_secret"]
    print(client_id)
    print(client_secret)
    
    with open(SONOS_SETTINGS_FILE, "r") as jsonFile:
        data = json.load(jsonFile)
    if not data["spotify"]:
        data["spotify"] = {}
    print(data)
    data["spotify"]["clientId"] = client_id
    data["spotify"]["clientSecret"] = client_secret
    with open(SONOS_SETTINGS_FILE, "w") as jsonFile:
        json.dump(data, jsonFile)
    
    # Update spotify-cli auth
    cmd = "spotify-cli config --set-app-client-id {} --set-app-client-secret {} --set-redirect-port 5555".format(client_id, client_secret)
    output = subprocess.check_output(cmd, shell=True)
    print(output)
    restart_sonos_api()


def update_sonos_room_from_settings():
    with open(SETTINGS_FILE, "r") as jsonFile:
        data = json.load(jsonFile)
    sonos_room = data["sonos_room"]
    # Update presets for sonos room
    js = { "players": [{"roomName": sonos_room, "volume": 15}],"playMode": { "shuffle": "true", "repeat": "all", "crossfade": "false" }, "pauseOthers": "false" }
    open(PRESETS_FILE, "w").write(str(js))
    restart_sonos_api()

