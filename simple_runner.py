import time
from key_sender import key_down, key_up
from keymap import KEY_MAP


def run_simple(hwnd, keys, interval):
    # keys: ['CTRL', 'C']
    while True:
        for k in keys:
            if k in KEY_MAP:
                key_down(hwnd, KEY_MAP[k])
        time.sleep(0.05)
        for k in reversed(keys):
            if k in KEY_MAP:
                key_up(hwnd, KEY_MAP[k])
        time.sleep(interval)