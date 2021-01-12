import multiprocessing.pool
import functools

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



# import subprocess


# import RPi.GPIO as GPIO
# from mfrc522 import SimpleMFRC522

# GPIO.setwarnings(False)
# reader = SimpleMFRC522()

# @timeout(30)
# def write_spotify_uri(spotify_uri):
#     output = subprocess.check_output("sudo service nfc_read stop", shell=True)
#     print(output.decode("utf-8"))
#     reader.write(str(spotify_uri))
#     output = subprocess.check_output("sudo service nfc_read start", shell=True)
#     print(output.decode("utf-8"))
#     return True

# @timeout(30)
# def read_spotify_uri():
#     cid, text = reader.read()
#     return cid, text