import time
import win32api
import win32con


def send_key(hwnd, vk):
    win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, vk, 0)
    time.sleep(0.02)
    win32api.PostMessage(hwnd, win32con.WM_KEYUP, vk, 0)