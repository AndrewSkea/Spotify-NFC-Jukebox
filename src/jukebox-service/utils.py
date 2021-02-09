import multiprocessing.pool
import functools
import subprocess
import json
import os
from constants import *


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


def is_sonos():
    with open(SETTINGS_FILE, "r") as jsonFile:
        data = json.load(jsonFile)
    audio = data.get("audio", "")
    if audio == "aux":
        return False
    return True

    
def get_sonos_room():
    with open(SETTINGS_FILE, "r") as jsonFile:
        data = json.load(jsonFile)
    return data.get("sonos_room", "")
    

def make_all_access(file_path):
    cmd = ["sudo", "chmod", "775", file_path]
    subprocess.Popen(cmd, stdout=subprocess.PIPE)


def restart_sonos_api():
    print("Restarting sonos api service")
    cmd = ["sudo", "service", "sonos", "restart"]
    subprocess.Popen(cmd, stdout=subprocess.PIPE)


def stop_read_service():
    print("Stop read service")
    cmd = ["sudo", "service", "read", "stop"]
    subprocess.Popen(cmd, stdout=subprocess.PIPE)


def start_read_service():
    print("Starting read service")
    cmd = ["sudo", "service", "read", "start"]
    subprocess.Popen(cmd, stdout=subprocess.PIPE)


def restart_all_services():
    restart_sonos_api()
    stop_read_service()
    start_read_service()
