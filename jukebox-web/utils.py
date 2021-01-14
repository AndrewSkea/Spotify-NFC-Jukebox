import multiprocessing.pool
import functools
import subprocess
import json
import os

def get_room_name():
    with open("/home/pi/sonos-spotify-jukebox/jukebox-web/settings.json", "r") as jsonFile:
        data = json.load(jsonFile)
    return data["sonos_room"]


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
    os.system("pm2 restart sonos-api-service")


def restart_raspotify_service():
    output = subprocess.check_output("sudo service raspotify restart", shell=True)
    output = output.decode("utf-8")
    return True if "" in output else False


def stop_read_service():
    print("Stopping read service")
    os.system("pm2 stop read-service")


def start_read_service():
    print("Starting read service")
    os.system("pm2 start read-service")


def restart_all_services():
    restart_sonos_api()
    restart_raspotify_service()
    stop_read_service()
    start_read_service()


def insert_line(file_path, match_string, insert_string):
    with open(file_path, 'r+') as fd:
        contents = fd.readlines()
        if match_string in contents[-1]:  # Handle last line to prevent IndexError
            contents.append(insert_string)
        else:
            for index, line in enumerate(contents):
                if match_string in line and insert_string not in contents[index + 1]:
                    contents.insert(index + 1, insert_string)
                    break
        fd.seek(0)
        fd.writelines(contents)


def update_files_from_settings():
    with open("settings.json", "r") as jsonFile:
        data = json.load(jsonFile)
    username = data["spotify_username"]
    password = data["spotify_password"]
    client_id = data["spotify_client_id"]
    client_secret = data["spotify_client_secret"]
    sonos_room = data["sonos_room"]

    # Update the username and password for raspotify
    lines = open('/etc/default/raspotify').read().splitlines()
    line_to_rep = None
    for i, line in enumerate(lines):
        print(line)
        if line.startswith("OPTIONS"):
            print(line)
            line_to_rep = i
    ln = 'OPTIONS=" --username {} --password {}"'.format(username, password)
    if line_to_rep is None:
        lines.append(ln)
    else:
        lines[line_to_rep-1] = ln
    open('/etc/default/raspotify','w').write('\n'.join(lines))
    restart_raspotify_service()

    # Update spotify-cli auth
    cmd = "spotify-cli config --set-app-client-id {} --set-app-client-secret {} --set-redirect-port 5555".format(client_id, client_secret)
    output = subprocess.check_output(cmd, shell=True)
    print(output)

    # Update presets.json && settings.json in node-sonos-http-app
    # Update presets for sonos room
    js = { "players": [{"roomName": sonos_room, "volume": 15}],"playMode": { "shuffle": "true", "repeat": "all", "crossfade": "false" }, "pauseOthers": "false" }
    open("/home/pi/sonos-spotify-jukebox/node-sonos-http-api/presets/example.json", "w").write(str(js))

    # Update client id and secret in settings.js
    match_string = 'announceVolume: 40,'
    insert_string = {"clientId": '"' + client_id + '"', "clientSecret": '"' + client_secret + '"'}
    insert_string = 'spotify: {},\n'.format(str(insert_string))
    print(insert_string)
    insert_line("/home/pi/sonos-spotify-jukebox/node-sonos-http-api/settings.js", match_string, insert_string)
    restart_sonos_api()
