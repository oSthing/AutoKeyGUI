import win32con

KEY_MAP = {chr(i): i for i in range(0x41, 0x5B)}
KEY_MAP.update({str(i): 0x30 + i for i in range(10)})
KEY_MAP.update({
    'ENTER': win32con.VK_RETURN,
    'SPACE': win32con.VK_SPACE,
    'TAB': win32con.VK_TAB,
    'ESC': win32con.VK_ESCAPE,
    'BACKSPACE': win32con.VK_BACK,
    'DELETE': win32con.VK_DELETE,
    'UP': win32con.VK_UP,
    'DOWN': win32con.VK_DOWN,
    'LEFT': win32con.VK_LEFT,
    'RIGHT': win32con.VK_RIGHT,
    'SHIFT': win32con.VK_SHIFT,
    'CTRL': win32con.VK_CONTROL,
    'ALT': win32con.VK_MENU,
    'F1': win32con.VK_F1,
    'F2': win32con.VK_F2,
    'F3': win32con.VK_F3,
    'F4': win32con.VK_F4,
    'F5': win32con.VK_F5,
    'F6': win32con.VK_F6,
    'F7': win32con.VK_F7,
    'F8': win32con.VK_F8,
    'F9': win32con.VK_F9,
    'F10': win32con.VK_F10,
    'F11': win32con.VK_F11,
    'F12': win32con.VK_F12,
})