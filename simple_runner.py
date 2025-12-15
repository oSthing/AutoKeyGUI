import time
from key_sender import send_key
from keymap import KEY_MAP




def run_simple(hwnd, key, interval, speed):
    while True:
        if key in KEY_MAP:
            send_key(hwnd, KEY_MAP[key])
        time.sleep(interval / speed)