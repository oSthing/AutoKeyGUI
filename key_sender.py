import time
import win32api
import win32con


def key_down(hwnd, vk):
    win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, vk, 0)


def key_up(hwnd, vk):
    win32api.PostMessage(hwnd, win32con.WM_KEYUP, vk, 0)


def tap_key(hwnd, vk, delay=0.02):
    key_down(hwnd, vk)
    time.sleep(delay)
    key_up(hwnd, vk)